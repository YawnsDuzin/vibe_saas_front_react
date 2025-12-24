# API 라우터 (Routers)

## 개요

라우터는 **API 엔드포인트를 정의**하는 계층입니다. HTTP 요청을 받아서 적절한 서비스를 호출하고 응답을 반환합니다.

## 1. 라우터 기본 개념

### APIRouter란?

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    return [{"id": 1, "name": "Alice"}]
```

**APIRouter vs FastAPI:**
```
┌─────────────────────────────────────────────────────────────┐
│  FastAPI (app)           APIRouter (router)                 │
├─────────────────────────────────────────────────────────────┤
│  - 메인 애플리케이션     - 기능별 라우터                    │
│  - 미들웨어 등록         - 엔드포인트 정의                  │
│  - 앱 설정               - 모듈화된 경로 관리               │
│  - 수명 주기 관리        - 재사용 가능                      │
│                                                             │
│  app = FastAPI()         router = APIRouter()               │
│  @app.get("/")           @router.get("/users")              │
│                                                             │
│  app.include_router(router)  ← 라우터를 앱에 등록           │
└─────────────────────────────────────────────────────────────┘
```

## 2. 라우터 정의 방법

### 기본 CRUD 라우터

```python
# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


# ===========================
# GET - 목록 조회
# ===========================
@router.get(
    "/",
    response_model=List[UserResponse],
    summary="사용자 목록 조회",
    description="모든 사용자의 목록을 반환합니다."
)
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    사용자 목록을 페이징하여 조회합니다.

    - **skip**: 건너뛸 항목 수 (기본 0)
    - **limit**: 반환할 최대 항목 수 (기본 10)
    """
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)


# ===========================
# GET - 단일 조회
# ===========================
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 상세 조회"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 상세 정보를 조회합니다.

    - **user_id**: 조회할 사용자 ID
    """
    service = UserService(db)
    user = service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


# ===========================
# POST - 생성
# ===========================
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성"
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 사용자를 생성합니다.

    - **email**: 이메일 주소 (중복 불가)
    - **username**: 사용자명 (중복 불가)
    - **password**: 비밀번호 (최소 8자)
    """
    service = UserService(db)
    return service.create_user(user_data)


# ===========================
# PUT - 전체 수정
# ===========================
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 수정"
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    사용자 정보를 수정합니다.
    """
    service = UserService(db)
    user = service.update_user(user_id, user_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


# ===========================
# DELETE - 삭제
# ===========================
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    사용자를 삭제합니다.
    """
    service = UserService(db)
    success = service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return None
```

## 3. 이 프로젝트의 라우터

### 인증 라우터 (auth.py)

```python
# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, RefreshTokenRequest
from app.services.user import UserService
from app.services.auth import AuthService
from app.dependencies.auth import get_current_active_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    새 사용자 계정을 생성합니다.

    - **email**: 유효한 이메일 주소 (중복 불가)
    - **username**: 3-50자 사용자명 (중복 불가)
    - **password**: 8자 이상, 대/소문자/숫자 포함
    """
    user_service = UserService(db)
    return user_service.create_user(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="로그인"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    로그인하여 JWT 토큰을 발급받습니다.

    OAuth2 표준 양식을 사용합니다:
    - **username**: 이메일 또는 사용자명
    - **password**: 비밀번호
    """
    auth_service = AuthService(db)
    return auth_service.login(form_data.username, form_data.password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="토큰 갱신"
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    리프레시 토큰으로 새 액세스 토큰을 발급받습니다.
    """
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(request.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회"
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    현재 로그인한 사용자의 정보를 조회합니다.

    Authorization 헤더에 Bearer 토큰이 필요합니다.
    """
    return current_user
```

### 게시글 라우터 (posts.py)

```python
# app/routers/posts.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post import PostService
from app.dependencies.auth import get_current_active_user, get_optional_current_user

router = APIRouter()


@router.get("/", response_model=List[PostResponse])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    is_published: bool = True,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    게시글 목록을 조회합니다.

    - **skip**: 건너뛸 항목 수
    - **limit**: 최대 조회 수 (1-100)
    - **category_id**: 카테고리 필터 (선택)
    - **is_published**: 공개 게시글만 조회 (기본 True)
    """
    service = PostService(db)
    return service.get_posts(
        skip=skip,
        limit=limit,
        category_id=category_id,
        is_published=is_published
    )


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 로그인 필수
):
    """
    새 게시글을 작성합니다.

    로그인이 필요합니다.
    """
    service = PostService(db)
    return service.create_post(post_data, author_id=current_user.id)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    게시글 상세 정보를 조회합니다.
    """
    service = PostService(db)
    post = service.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    service.increment_view_count(post_id)

    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글을 수정합니다.

    본인이 작성한 게시글만 수정할 수 있습니다.
    """
    service = PostService(db)
    post = service.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 권한 확인
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    return service.update_post(post_id, post_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글을 삭제합니다.
    """
    service = PostService(db)
    post = service.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    service.delete_post(post_id)
    return None
```

## 4. 라우터 옵션 상세

### 데코레이터 옵션

```python
@router.post(
    "/users",                              # 경로
    response_model=UserResponse,           # 응답 모델
    status_code=status.HTTP_201_CREATED,   # 상태 코드
    summary="사용자 생성",                  # 짧은 설명
    description="새 사용자를 생성합니다.",   # 상세 설명
    tags=["Users"],                        # 태그 (그룹)
    deprecated=False,                      # 비권장 표시
    response_description="생성된 사용자",   # 응답 설명
    responses={                            # 추가 응답 문서
        400: {"description": "잘못된 요청"},
        409: {"description": "중복된 사용자"}
    }
)
def create_user(...):
    ...
```

**옵션 설명:**
```
┌─────────────────────┬────────────────────────────────────────┐
│  옵션               │  설명                                  │
├─────────────────────┼────────────────────────────────────────┤
│  response_model     │  응답 데이터 형식 (Pydantic 모델)      │
│  status_code        │  성공 시 HTTP 상태 코드                │
│  summary            │  API 제목 (Swagger에 표시)             │
│  description        │  API 상세 설명                         │
│  tags               │  API 그룹 (Swagger 그룹화)             │
│  deprecated         │  비권장 API 표시                       │
│  responses          │  추가 응답 코드 문서화                 │
│  include_in_schema  │  Swagger에 표시 여부                   │
└─────────────────────┴────────────────────────────────────────┘
```

### 경로 매개변수

```python
# 기본 경로 매개변수
@router.get("/users/{user_id}")
def get_user(user_id: int):  # int로 자동 변환 및 검증
    ...

# Path를 사용한 상세 설정
from fastapi import Path

@router.get("/users/{user_id}")
def get_user(
    user_id: int = Path(
        ...,                    # 필수
        title="사용자 ID",
        description="조회할 사용자의 고유 ID",
        ge=1,                   # >= 1
        example=123
    )
):
    ...

# 여러 경로 매개변수
@router.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    ...
```

### 쿼리 매개변수

```python
from fastapi import Query
from typing import Optional, List

@router.get("/posts")
def get_posts(
    # 기본값이 있는 쿼리
    skip: int = 0,
    limit: int = 10,

    # Query로 상세 설정
    q: str = Query(
        None,                       # 기본값 (선택적)
        min_length=1,               # 최소 길이
        max_length=100,             # 최대 길이
        description="검색어"
    ),

    # 리스트 쿼리 (?tags=a&tags=b)
    tags: List[str] = Query([]),

    # 필수 쿼리
    category: str = Query(..., description="필수 카테고리")
):
    ...
```

### 요청 본문

```python
from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: Optional[int] = None

@router.post("/posts")
def create_post(post: PostCreate):  # 자동으로 JSON → Pydantic
    ...

# 여러 본문
@router.put("/posts/{post_id}")
def update_post(
    post_id: int,              # 경로
    post: PostUpdate,          # 본문 1
    metadata: PostMetadata     # 본문 2 (자동으로 묶임)
):
    ...
```

## 5. 응답 처리

### 다양한 응답 형식

```python
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

# JSON 응답 (기본)
@router.get("/data")
def get_data():
    return {"key": "value"}

# 커스텀 JSON 응답
@router.get("/custom")
def custom_response():
    return JSONResponse(
        status_code=200,
        content={"message": "Custom"},
        headers={"X-Custom-Header": "value"}
    )

# HTML 응답
@router.get("/html", response_class=HTMLResponse)
def get_html():
    return "<h1>Hello</h1>"

# 파일 응답
@router.get("/file")
def get_file():
    return FileResponse("path/to/file.pdf")
```

### 응답 모델

```python
# 단일 모델
@router.get("/user", response_model=UserResponse)
def get_user():
    return user

# 리스트
@router.get("/users", response_model=List[UserResponse])
def get_users():
    return users

# 필드 제외
@router.get(
    "/user",
    response_model=UserResponse,
    response_model_exclude={"password"}  # password 제외
)

# 필드 포함
@router.get(
    "/user",
    response_model=UserResponse,
    response_model_include={"id", "email"}  # id, email만
)

# None 제외
@router.get(
    "/user",
    response_model=UserResponse,
    response_model_exclude_none=True  # None 값 제외
)
```

## 6. 라우터 통합

### routers/__init__.py

```python
# app/routers/__init__.py

from fastapi import APIRouter

# 개별 라우터 import
from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router
from .dashboard import router as dashboard_router
from .theme import router as theme_router
from .menu import router as menu_router

# 통합 라우터
api_router = APIRouter()

# 라우터 등록
api_router.include_router(
    auth_router,
    prefix="/auth",       # /api/v1/auth/*
    tags=["Auth"]         # Swagger 그룹
)

api_router.include_router(
    users_router,
    prefix="/users",      # /api/v1/users/*
    tags=["Users"]
)

api_router.include_router(
    posts_router,
    prefix="/posts",      # /api/v1/posts/*
    tags=["Posts"]
)

api_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

api_router.include_router(
    theme_router,
    prefix="/theme",
    tags=["Theme"]
)

api_router.include_router(
    menu_router,
    prefix="/menu",
    tags=["Menu"]
)
```

### main.py에서 등록

```python
# app/main.py

from app.routers import api_router

app.include_router(
    api_router,
    prefix="/api/v1"  # 모든 라우터에 /api/v1 접두사
)
```

## 7. 권한 별 엔드포인트

### 인증 불필요

```python
@router.get("/public")
def public_endpoint():
    """누구나 접근 가능"""
    return {"message": "Public"}
```

### 로그인 필요

```python
@router.get("/protected")
def protected_endpoint(
    user: User = Depends(get_current_active_user)
):
    """로그인한 사용자만 접근"""
    return {"user": user.username}
```

### 관리자 전용

```python
@router.delete("/admin-only")
def admin_only_endpoint(
    admin: User = Depends(get_current_admin_user)
):
    """관리자만 접근"""
    return {"message": "Admin action"}
```

### 특정 역할 필요

```python
@router.post("/moderator-action")
def moderator_action(
    user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    """관리자 또는 운영자만 접근"""
    return {"message": "Moderator action"}
```

## 8. 중첩 라우터

### 댓글 라우터 (게시글 하위)

```python
# app/routers/posts.py

# 게시글의 댓글 목록
@router.get("/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id == post_id).all()

# 댓글 작성
@router.post("/{post_id}/comments")
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    ...
```

**URL 구조:**
```
POST /api/v1/posts              게시글 작성
GET  /api/v1/posts/{id}         게시글 조회
GET  /api/v1/posts/{id}/comments    댓글 목록
POST /api/v1/posts/{id}/comments    댓글 작성
```

## 요약

| 데코레이터 | HTTP 메서드 | 용도 |
|-----------|------------|------|
| `@router.get` | GET | 조회 |
| `@router.post` | POST | 생성 |
| `@router.put` | PUT | 전체 수정 |
| `@router.patch` | PATCH | 부분 수정 |
| `@router.delete` | DELETE | 삭제 |

## 다음 단계

다음 문서 [08-services.md](./08-services.md)에서는 서비스 계층(비즈니스 로직)을 학습합니다.
