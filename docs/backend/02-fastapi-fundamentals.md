# FastAPI 기초

## 개요

FastAPI는 Python으로 API를 만드는 **현대적인 웹 프레임워크**입니다. 이 문서에서는 FastAPI의 핵심 개념을 처음부터 상세히 설명합니다.

## 1. FastAPI 애플리케이션 생성

### 가장 간단한 FastAPI 앱

```python
from fastapi import FastAPI

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 루트 경로("/")에 대한 GET 요청 처리
@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**실행 방법:**
```bash
uvicorn main:app --reload

# main: 파일 이름 (main.py)
# app: FastAPI() 인스턴스 변수 이름
# --reload: 코드 변경 시 자동 재시작
```

### 이 프로젝트의 main.py 분석

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 수명 주기 관리

    시작 시: 데이터베이스 테이블 생성
    종료 시: 리소스 정리
    """
    # Startup (서버 시작 시 실행)
    print(f"🚀 {settings.app_name} 시작...")
    init_db()  # DB 테이블 생성
    print("✅ 데이터베이스 테이블 생성 완료")

    yield  # 여기서 앱이 실행됨

    # Shutdown (서버 종료 시 실행)
    print("👋 애플리케이션 종료...")


# FastAPI 앱 생성 (상세 설정)
app = FastAPI(
    title=settings.app_name,        # API 제목
    description="...",              # API 설명
    version=settings.app_version,   # 버전
    docs_url="/docs",               # Swagger UI 경로
    redoc_url="/redoc",             # ReDoc 경로
    lifespan=lifespan               # 수명 주기 핸들러
)
```

**FastAPI 설정 옵션:**
```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI() 생성 옵션                                         │
├─────────────────────────────────────────────────────────────┤
│  title        API 제목 (Swagger UI에 표시)                   │
│  description  API 설명 (마크다운 지원)                        │
│  version      API 버전                                      │
│  docs_url     Swagger UI 경로 (기본: /docs)                  │
│  redoc_url    ReDoc 경로 (기본: /redoc)                      │
│  openapi_url  OpenAPI 스키마 경로                            │
│  lifespan     시작/종료 이벤트 핸들러                         │
└─────────────────────────────────────────────────────────────┘
```

## 2. HTTP 메서드와 경로

### HTTP 메서드란?

HTTP 메서드는 클라이언트가 서버에 **어떤 작업을 요청하는지** 나타냅니다.

```
┌─────────────────────────────────────────────────────────────┐
│  HTTP 메서드                                                 │
├─────────┬───────────────────────────────────────────────────┤
│  GET    │  데이터 조회 (읽기)                                │
│  POST   │  데이터 생성 (쓰기)                                │
│  PUT    │  데이터 전체 수정                                  │
│  PATCH  │  데이터 일부 수정                                  │
│  DELETE │  데이터 삭제                                       │
└─────────┴───────────────────────────────────────────────────┘
```

### FastAPI에서 HTTP 메서드 사용

```python
from fastapi import FastAPI

app = FastAPI()

# GET - 조회
@app.get("/users")
def get_users():
    return [{"id": 1, "name": "Alice"}]

# GET - 특정 항목 조회
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

# POST - 생성
@app.post("/users")
def create_user(name: str):
    return {"id": 1, "name": name}

# PUT - 전체 수정
@app.put("/users/{user_id}")
def update_user(user_id: int, name: str):
    return {"id": user_id, "name": name}

# DELETE - 삭제
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"deleted": user_id}
```

### 경로 매개변수 (Path Parameters)

URL 경로에 포함된 변수입니다.

```python
# /users/123 → user_id = 123
@app.get("/users/{user_id}")
def get_user(user_id: int):
    #           ↑ URL의 {user_id}와 매핑됨
    return {"user_id": user_id}

# 여러 경로 매개변수
# /users/123/posts/456
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

**타입 검증 자동 수행:**
```
GET /users/abc  → 에러! (int가 아님)
GET /users/123  → 성공 (user_id = 123)
```

### 쿼리 매개변수 (Query Parameters)

URL의 `?` 뒤에 오는 매개변수입니다.

```python
# /users?skip=0&limit=10
@app.get("/users")
def get_users(skip: int = 0, limit: int = 10):
    #           ↑ ?skip=값    ↑ ?limit=값
    return {"skip": skip, "limit": limit}

# 선택적 쿼리 매개변수
from typing import Optional

@app.get("/search")
def search(
    q: str,                    # 필수
    category: Optional[str] = None  # 선택
):
    return {"query": q, "category": category}
```

**요청 예시:**
```
GET /users              → skip=0, limit=10 (기본값)
GET /users?skip=5       → skip=5, limit=10
GET /users?limit=20     → skip=0, limit=20
GET /users?skip=5&limit=20 → skip=5, limit=20
GET /search?q=test      → q="test", category=None
GET /search?q=test&category=books → q="test", category="books"
```

## 3. 요청 본문 (Request Body)

POST, PUT, PATCH 요청에서 데이터를 전송할 때 사용합니다.

### Pydantic 모델로 요청 본문 정의

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 요청 본문 스키마 정의
class UserCreate(BaseModel):
    name: str
    email: str
    age: int

# POST 요청에서 본문 받기
@app.post("/users")
def create_user(user: UserCreate):
    #            ↑ JSON → UserCreate 객체로 자동 변환
    return {
        "message": "사용자 생성됨",
        "name": user.name,
        "email": user.email
    }
```

**요청 예시:**
```bash
POST /users
Content-Type: application/json

{
    "name": "홍길동",
    "email": "hong@example.com",
    "age": 25
}
```

### 경로 + 쿼리 + 본문 조합

```python
@app.put("/users/{user_id}")
def update_user(
    user_id: int,            # 경로 매개변수
    notify: bool = False,    # 쿼리 매개변수
    user: UserCreate         # 요청 본문
):
    return {
        "user_id": user_id,
        "notify": notify,
        "data": user
    }
```

**FastAPI는 자동으로 구분:**
```
- 함수 매개변수가 경로에 있으면 → 경로 매개변수
- Pydantic 모델이면 → 요청 본문
- 그 외 → 쿼리 매개변수
```

## 4. 응답 (Response)

### 기본 응답

```python
# dict 반환 → JSON으로 자동 변환
@app.get("/")
def read_root():
    return {"message": "Hello"}
# → {"message": "Hello"}

# list 반환
@app.get("/items")
def get_items():
    return [1, 2, 3]
# → [1, 2, 3]
```

### 응답 모델 (Response Model)

응답 데이터의 형식을 명시적으로 정의합니다.

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # DB에서 가져온 데이터 (민감 정보 포함)
    user_from_db = {
        "id": user_id,
        "name": "홍길동",
        "email": "hong@example.com",
        "password": "hashed_password"  # 민감 정보!
    }
    return user_from_db
# 응답: {"id": 1, "name": "홍길동", "email": "hong@example.com"}
# password는 응답 모델에 없으므로 제외됨!
```

**response_model의 장점:**
```
┌─────────────────────────────────────────────────────────────┐
│  response_model 장점                                        │
├─────────────────────────────────────────────────────────────┤
│  1. 민감한 데이터 자동 필터링 (비밀번호 등)                   │
│  2. 응답 형식 문서화 (Swagger UI)                           │
│  3. 응답 데이터 검증                                        │
│  4. 일관된 API 응답 보장                                    │
└─────────────────────────────────────────────────────────────┘
```

### HTTP 상태 코드

```python
from fastapi import FastAPI, status

app = FastAPI()

# 성공적인 생성 (201 Created)
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(name: str):
    return {"name": name}

# 콘텐츠 없음 (204 No Content)
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    return None
```

**주요 상태 코드:**
```
┌─────────┬───────────────────────────────────────────────────┐
│  코드   │  의미                                             │
├─────────┼───────────────────────────────────────────────────┤
│  200    │  OK - 성공                                        │
│  201    │  Created - 생성 성공                              │
│  204    │  No Content - 성공 (응답 본문 없음)               │
│  400    │  Bad Request - 잘못된 요청                        │
│  401    │  Unauthorized - 인증 필요                         │
│  403    │  Forbidden - 권한 없음                            │
│  404    │  Not Found - 찾을 수 없음                         │
│  422    │  Unprocessable Entity - 검증 실패                 │
│  500    │  Internal Server Error - 서버 오류                │
└─────────┴───────────────────────────────────────────────────┘
```

## 5. 의존성 주입 (Dependency Injection)

FastAPI의 가장 강력한 기능 중 하나입니다.

### 기본 개념

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# 의존성 함수
def get_database():
    """데이터베이스 연결을 제공하는 함수"""
    db = Database()
    try:
        yield db
    finally:
        db.close()

# 의존성 사용
@app.get("/users")
def get_users(db = Depends(get_database)):
    #          ↑ get_database()의 반환값이 db에 주입됨
    return db.query("SELECT * FROM users")
```

**Depends() 동작:**
```
┌─────────────────────────────────────────────────────────────┐
│  @app.get("/users")                                         │
│  def get_users(db = Depends(get_database)):                 │
│       │                    │                                │
│       │                    └─ get_database 함수 실행        │
│       │                                                     │
│       └─ 그 결과(db)를 매개변수로 받음                       │
│                                                             │
│  실행 순서:                                                  │
│  1. 요청이 들어옴                                           │
│  2. get_database() 실행 → db 생성                           │
│  3. get_users(db) 실행                                      │
│  4. get_database()의 finally 블록 실행 → db.close()         │
└─────────────────────────────────────────────────────────────┘
```

### 이 프로젝트에서의 의존성

```python
# app/database.py
def get_db():
    """데이터베이스 세션 제공"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/dependencies/auth.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 반환"""
    # 토큰 검증 및 사용자 조회
    ...

# app/routers/auth.py
@router.get("/me")
def get_me(user: User = Depends(get_current_active_user)):
    #        ↑ 자동으로 인증 검사 + 사용자 조회
    return user
```

**의존성 체인:**
```
get_current_active_user
       │
       └─ Depends(get_current_user)
                   │
                   ├─ Depends(oauth2_scheme)  → 토큰 추출
                   │
                   └─ Depends(get_db)  → DB 세션
```

## 6. 라우터 (Router)

대규모 프로젝트에서 엔드포인트를 **모듈별로 분리**합니다.

### 기본 라우터 사용

```python
# app/routers/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_users():
    return [{"id": 1}]

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import users

app = FastAPI()

# 라우터 등록
app.include_router(
    users.router,
    prefix="/users",    # 경로 접두사
    tags=["Users"]      # Swagger UI 그룹
)
# 결과: /users/, /users/{user_id}
```

### 이 프로젝트의 라우터 구조

```python
# app/routers/__init__.py
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router

api_router = APIRouter()

# 각 라우터를 API 라우터에 포함
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(posts_router, prefix="/posts", tags=["Posts"])

# app/main.py
app.include_router(api_router, prefix="/api/v1")
```

**최종 URL 구조:**
```
/api/v1/auth/login       ← auth_router
/api/v1/auth/register
/api/v1/users/           ← users_router
/api/v1/users/{id}
/api/v1/posts/           ← posts_router
/api/v1/posts/{id}
```

## 7. 미들웨어 (Middleware)

모든 요청/응답을 **가로채서 처리**합니다.

### CORS 미들웨어

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 허용 출처
    allow_credentials=True,                   # 쿠키 허용
    allow_methods=["*"],                      # 모든 HTTP 메서드
    allow_headers=["*"],                      # 모든 헤더
)
```

**CORS란?**
```
┌─────────────────────────────────────────────────────────────┐
│  CORS (Cross-Origin Resource Sharing)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  브라우저는 보안상 다른 출처의 요청을 차단합니다.              │
│                                                             │
│  예: http://localhost:3000 (프론트엔드)                      │
│      → http://localhost:8000 (백엔드) 요청                   │
│                                                             │
│  출처가 다르면 (포트도 다르면) CORS 에러 발생!                │
│                                                             │
│  해결: 백엔드에서 프론트엔드 출처를 허용                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 이 프로젝트의 CORS 설정

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,    # .env에서 설정
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)

# app/config.py
cors_origins: str = '["http://localhost:3000","http://localhost:8080"]'
```

## 8. 예외 처리 (Exception Handling)

### HTTPException

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    return user
```

### 전역 예외 핸들러

```python
# app/main.py

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """요청 검증 에러 핸들러"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error["loc"],
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "입력값 검증 실패", "errors": errors}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류"}
    )
```

## 9. 자동 문서화

FastAPI는 **자동으로 API 문서를 생성**합니다.

### Swagger UI (Interactive)

```
http://localhost:8000/docs
```

- API 테스트 가능
- 요청/응답 예시
- 인증 테스트

### ReDoc

```
http://localhost:8000/redoc
```

- 읽기 전용 문서
- 깔끔한 디자인

### 문서화 개선

```python
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",                    # 짧은 설명
    description="새로운 사용자 계정을 생성합니다.",  # 상세 설명
    tags=["Users"],                         # 그룹
    responses={
        400: {"description": "잘못된 입력"},
        409: {"description": "이미 존재하는 사용자"}
    }
)
def create_user(user: UserCreate):
    """
    새로운 사용자를 생성합니다.

    - **email**: 유효한 이메일 주소
    - **username**: 3-50자의 사용자명
    - **password**: 8자 이상의 비밀번호
    """
    ...
```

**문서에 표시되는 정보:**
```
┌─────────────────────────────────────────────────────────────┐
│  POST /users                                                │
│  ─────────────────────────────────────────────              │
│  Summary: 사용자 생성                                        │
│                                                             │
│  Description:                                               │
│  새로운 사용자를 생성합니다.                                  │
│  - email: 유효한 이메일 주소                                 │
│  - username: 3-50자의 사용자명                              │
│  - password: 8자 이상의 비밀번호                            │
│                                                             │
│  Request Body:                                              │
│  {                                                          │
│    "email": "user@example.com",                             │
│    "username": "johndoe",                                   │
│    "password": "SecurePass123"                              │
│  }                                                          │
│                                                             │
│  Responses:                                                 │
│  201: 생성 성공                                             │
│  400: 잘못된 입력                                           │
│  409: 이미 존재하는 사용자                                   │
└─────────────────────────────────────────────────────────────┘
```

## 10. Lifespan 이벤트

애플리케이션 시작/종료 시 실행되는 코드입니다.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===================
    # 시작 시 (Startup)
    # ===================
    print("서버 시작!")
    init_db()  # 데이터베이스 초기화
    # 캐시 연결, 외부 서비스 연결 등

    yield  # 여기서 앱이 실행됨

    # ===================
    # 종료 시 (Shutdown)
    # ===================
    print("서버 종료!")
    # 연결 해제, 리소스 정리 등

app = FastAPI(lifespan=lifespan)
```

**실행 흐름:**
```
┌─────────────────────────────────────────────────────────────┐
│  1. uvicorn app.main:app 실행                               │
│          │                                                  │
│          ▼                                                  │
│  2. lifespan 시작 (yield 전)                                │
│     - 데이터베이스 초기화                                    │
│     - 캐시 연결                                             │
│          │                                                  │
│          ▼                                                  │
│  3. yield → 앱 실행 (요청 처리)                             │
│          │                                                  │
│          ▼                                                  │
│  4. Ctrl+C (종료 신호)                                      │
│          │                                                  │
│          ▼                                                  │
│  5. lifespan 종료 (yield 후)                                │
│     - 연결 해제                                             │
│     - 리소스 정리                                           │
└─────────────────────────────────────────────────────────────┘
```

## 요약

FastAPI 핵심 개념:

| 개념 | 설명 | 예시 |
|------|------|------|
| 경로 매개변수 | URL 경로의 변수 | `/users/{id}` |
| 쿼리 매개변수 | URL의 ?key=value | `/users?skip=0` |
| 요청 본문 | JSON 데이터 | `{"name": "..."}` |
| 의존성 주입 | 재사용 가능한 로직 | `Depends(get_db)` |
| 라우터 | 엔드포인트 그룹화 | `APIRouter()` |
| 미들웨어 | 요청/응답 처리 | CORS |
| 예외 처리 | 에러 응답 | `HTTPException` |
| 자동 문서화 | Swagger, ReDoc | `/docs`, `/redoc` |

## 다음 단계

다음 문서 [03-pydantic-schemas.md](./03-pydantic-schemas.md)에서는 Pydantic을 사용한 데이터 검증을 학습합니다.
