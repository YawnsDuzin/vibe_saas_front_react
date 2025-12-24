# 에러 처리 (Error Handling)

## 개요

FastAPI에서 **에러를 처리하고 일관된 에러 응답을 반환**하는 방법을 설명합니다.

## 1. HTTP 에러 기본

### HTTP 상태 코드

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP 상태 코드                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  2xx 성공                                                   │
│  ├── 200 OK              요청 성공                          │
│  ├── 201 Created         생성 성공                          │
│  └── 204 No Content      성공 (응답 본문 없음)              │
│                                                             │
│  4xx 클라이언트 에러                                        │
│  ├── 400 Bad Request     잘못된 요청                        │
│  ├── 401 Unauthorized    인증 필요                          │
│  ├── 403 Forbidden       권한 없음                          │
│  ├── 404 Not Found       찾을 수 없음                       │
│  ├── 409 Conflict        충돌 (중복 등)                     │
│  └── 422 Unprocessable   검증 실패                          │
│                                                             │
│  5xx 서버 에러                                              │
│  ├── 500 Internal Error  서버 내부 오류                     │
│  ├── 502 Bad Gateway     게이트웨이 오류                    │
│  └── 503 Unavailable     서비스 불가                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. HTTPException

### 기본 사용

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # 에러 발생
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return user
```

**응답 예시:**
```json
{
    "detail": "사용자를 찾을 수 없습니다."
}
```

### HTTPException 옵션

```python
from fastapi import HTTPException, status

# 기본 사용
raise HTTPException(
    status_code=404,
    detail="찾을 수 없습니다."
)

# status 모듈 사용 (가독성)
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="사용자를 찾을 수 없습니다."
)

# 헤더 추가 (인증 에러 시)
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="인증이 필요합니다.",
    headers={"WWW-Authenticate": "Bearer"}
)

# 상세 에러 정보
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": "유효성 검증 실패",
        "errors": [
            {"field": "email", "error": "이미 존재하는 이메일"},
            {"field": "username", "error": "너무 짧음"}
        ]
    }
)
```

### 자주 사용하는 에러 패턴

```python
# 404 Not Found
def get_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")
    return user

# 401 Unauthorized
def login(username: str, password: str, db: Session):
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return create_token(user)

# 403 Forbidden
def delete_post(post_id: int, current_user: User, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post.author_id != current_user.id:
        raise HTTPException(403, "삭제 권한이 없습니다.")
    db.delete(post)
    db.commit()

# 400 Bad Request
def register(user_data: UserCreate, db: Session):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "이미 등록된 이메일입니다.")
    # 사용자 생성...
```

## 3. Pydantic 검증 에러

### 자동 검증

FastAPI는 Pydantic 스키마로 요청을 자동 검증합니다.

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

@app.post("/users")
def create_user(user: UserCreate):
    # 검증 실패 시 자동으로 422 에러 발생
    ...
```

**자동 응답 (422):**
```json
{
    "detail": [
        {
            "type": "string_pattern_mismatch",
            "loc": ["body", "email"],
            "msg": "String should match pattern '^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'",
            "input": "invalid-email"
        }
    ]
}
```

### 커스텀 검증 에러

```python
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not any(c.isupper() for c in v):
            raise ValueError("대문자가 최소 1개 포함되어야 합니다.")
        return v
```

## 4. 전역 예외 핸들러

### 이 프로젝트의 예외 핸들러

```python
# app/main.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Pydantic 검증 에러 핸들러

    기본 에러 메시지를 사용자 친화적으로 변환합니다.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "입력값 검증에 실패했습니다.",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    """
    전역 예외 핸들러

    처리되지 않은 모든 예외를 잡습니다.
    """
    # 디버그 모드에서는 상세 정보 표시
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )

    # 프로덕션에서는 일반 메시지
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 내부 오류가 발생했습니다."}
    )
```

### 커스텀 예외 클래스

```python
# app/exceptions.py

class AppException(Exception):
    """애플리케이션 기본 예외"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class NotFoundError(AppException):
    """리소스를 찾을 수 없음"""
    def __init__(self, resource: str = "리소스"):
        super().__init__(
            status_code=404,
            detail=f"{resource}를 찾을 수 없습니다."
        )


class UnauthorizedError(AppException):
    """인증 필요"""
    def __init__(self, detail: str = "인증이 필요합니다."):
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(AppException):
    """권한 없음"""
    def __init__(self, detail: str = "권한이 없습니다."):
        super().__init__(
            status_code=403,
            detail=detail
        )


class ConflictError(AppException):
    """중복/충돌"""
    def __init__(self, detail: str = "이미 존재합니다."):
        super().__init__(
            status_code=409,
            detail=detail
        )
```

### 커스텀 예외 핸들러 등록

```python
# app/main.py

from app.exceptions import AppException

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )
```

### 사용 예시

```python
from app.exceptions import NotFoundError, ConflictError, ForbiddenError

class UserService:
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("사용자")
        return user

    def create_user(self, user_data: UserCreate) -> User:
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise ConflictError("이미 등록된 이메일입니다.")
        # ...

    def delete_user(self, user_id: int, current_user: User) -> None:
        user = self.get_user(user_id)
        if user.id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("삭제 권한이 없습니다.")
        # ...
```

## 5. 에러 응답 형식

### 일관된 응답 형식

```python
# 성공 응답
{
    "id": 1,
    "username": "john",
    "email": "john@example.com"
}

# 에러 응답 (단순)
{
    "detail": "사용자를 찾을 수 없습니다."
}

# 에러 응답 (상세)
{
    "detail": "입력값 검증에 실패했습니다.",
    "errors": [
        {
            "field": "body -> email",
            "message": "잘못된 이메일 형식입니다.",
            "type": "value_error"
        },
        {
            "field": "body -> password",
            "message": "비밀번호는 최소 8자 이상이어야 합니다.",
            "type": "value_error"
        }
    ]
}
```

### 에러 응답 스키마

```python
# app/schemas/error.py

from pydantic import BaseModel
from typing import List, Optional

class ErrorDetail(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[ErrorDetail]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "사용자를 찾을 수 없습니다."
                },
                {
                    "detail": "입력값 검증 실패",
                    "errors": [
                        {
                            "field": "email",
                            "message": "잘못된 형식",
                            "type": "value_error"
                        }
                    ]
                }
            ]
        }
    }
```

### 라우터에서 에러 응답 문서화

```python
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "사용자를 찾을 수 없음"
        },
        403: {
            "model": ErrorResponse,
            "description": "접근 권한 없음"
        }
    }
)
def get_user(user_id: int):
    ...
```

## 6. 로깅

### 에러 로깅

```python
import logging

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 에러 로깅
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        exc_info=True  # 스택 트레이스 포함
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류"}
    )
```

### 요청 로깅 미들웨어

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} "
        f"({process_time:.3f}s)"
    )

    return response
```

**로그 출력 예시:**
```
INFO:     POST /api/v1/auth/login → 200 (0.152s)
INFO:     GET /api/v1/users/999 → 404 (0.008s)
ERROR:    Unhandled exception: ValueError: Invalid data
```

## 7. 에러 처리 Best Practices

```
┌─────────────────────────────────────────────────────────────┐
│                    에러 처리 Best Practices                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ 적절한 상태 코드 사용                                   │
│     - 404: 리소스 없음                                      │
│     - 401: 인증 필요                                        │
│     - 403: 권한 없음                                        │
│     - 400/422: 잘못된 요청                                  │
│                                                             │
│  ✅ 사용자 친화적 메시지                                    │
│     - "사용자를 찾을 수 없습니다." ○                        │
│     - "NullPointerException" ✗                              │
│                                                             │
│  ✅ 일관된 응답 형식                                        │
│     - 모든 에러가 같은 구조                                 │
│     - {"detail": "..."} 또는 {"detail": "...", "errors": []}│
│                                                             │
│  ✅ 보안 고려                                               │
│     - 프로덕션에서 스택 트레이스 숨기기                     │
│     - 민감한 정보 노출하지 않기                             │
│                                                             │
│  ✅ 로깅                                                    │
│     - 모든 에러 로깅                                        │
│     - 디버깅을 위한 충분한 정보                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 요약

| 구성 요소 | 용도 | 예시 |
|----------|------|------|
| HTTPException | 기본 에러 발생 | `raise HTTPException(404)` |
| exception_handler | 전역 에러 처리 | `@app.exception_handler()` |
| RequestValidationError | Pydantic 검증 에러 | 자동 발생 |
| 커스텀 예외 | 재사용 가능한 에러 | `NotFoundError()` |

## 마무리

이것으로 FastAPI 백엔드 문서 시리즈를 마칩니다.

### 학습 순서 복습

```
00-getting-started     개요
01-python-basics       Python 기초
02-fastapi-fundamentals FastAPI 핵심
03-pydantic-schemas    데이터 검증
04-sqlalchemy-models   데이터베이스 모델
05-database            DB 연결
06-project-structure   프로젝트 구조
07-routers             API 엔드포인트
08-services            비즈니스 로직
09-dependencies        의존성 주입
10-authentication      JWT 인증
11-security            보안 유틸리티
12-error-handling      에러 처리 ← 현재
```

### 추가 학습 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/ko/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Pydantic 문서](https://docs.pydantic.dev/)
