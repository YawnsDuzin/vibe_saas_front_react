# 프로젝트 구조

## 개요

이 문서에서는 FastAPI 프로젝트의 **폴더 구조와 각 파일의 역할**을 상세히 설명합니다. 이 구조를 이해하면 코드를 어디에 작성해야 하는지 명확해집니다.

## 1. 전체 폴더 구조

```
FastAPI_Tutorial/
│
├── app/                          # 📦 메인 애플리케이션
│   ├── __init__.py               #    패키지 초기화
│   ├── main.py                   #    🚀 앱 진입점
│   ├── config.py                 #    ⚙️ 환경 설정
│   ├── database.py               #    🗄️ DB 연결
│   │
│   ├── models/                   #    📊 DB 모델 (테이블)
│   │   ├── __init__.py
│   │   ├── user.py               #       사용자 모델
│   │   ├── post.py               #       게시글/댓글 모델
│   │   ├── theme.py              #       테마 설정 모델
│   │   └── menu.py               #       메뉴 모델
│   │
│   ├── schemas/                  #    📋 Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── user.py               #       사용자 스키마
│   │   ├── auth.py               #       인증 스키마
│   │   ├── post.py               #       게시글 스키마
│   │   ├── theme.py              #       테마 스키마
│   │   └── menu.py               #       메뉴 스키마
│   │
│   ├── routers/                  #    🛣️ API 엔드포인트
│   │   ├── __init__.py           #       라우터 통합
│   │   ├── auth.py               #       인증 라우터
│   │   ├── users.py              #       사용자 라우터
│   │   ├── posts.py              #       게시글 라우터
│   │   ├── dashboard.py          #       대시보드 라우터
│   │   ├── theme.py              #       테마 라우터
│   │   └── menu.py               #       메뉴 라우터
│   │
│   ├── services/                 #    💼 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth.py               #       인증 서비스
│   │   ├── user.py               #       사용자 서비스
│   │   └── post.py               #       게시글 서비스
│   │
│   ├── dependencies/             #    🔌 의존성 함수
│   │   ├── __init__.py
│   │   └── auth.py               #       인증 의존성
│   │
│   └── utils/                    #    🔧 유틸리티
│       ├── __init__.py
│       ├── security.py           #       보안 함수
│       └── helpers.py            #       헬퍼 함수
│
├── tests/                        # 🧪 테스트
│   ├── __init__.py
│   ├── conftest.py               #    테스트 설정
│   ├── test_auth.py              #    인증 테스트
│   └── test_users.py             #    사용자 테스트
│
├── data/                         # 📁 데이터 (SQLite 등)
│   └── app.db
│
├── .env                          # 🔐 환경 변수
├── .env.example                  # 📝 환경 변수 예시
├── requirements.txt              # 📦 패키지 목록
├── alembic.ini                   # 🔄 마이그레이션 설정
└── README.md                     # 📖 프로젝트 설명
```

## 2. 레이어 아키텍처

이 프로젝트는 **계층형 아키텍처**를 따릅니다.

```
┌─────────────────────────────────────────────────────────────┐
│                     계층형 아키텍처                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   클라이언트 (브라우저, 앱)                                  │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────────────────┐              │
│   │          Routers (라우터)                │   API 계층   │
│   │   HTTP 요청 받기, 응답 반환              │              │
│   └────────────────────┬────────────────────┘              │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────┐              │
│   │         Services (서비스)                │  비즈니스    │
│   │   비즈니스 로직, 데이터 처리             │   계층      │
│   └────────────────────┬────────────────────┘              │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────┐              │
│   │          Models (모델)                   │  데이터     │
│   │   데이터베이스 테이블 정의               │   계층      │
│   └────────────────────┬────────────────────┘              │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────┐              │
│   │         Database (데이터베이스)          │  저장소     │
│   └─────────────────────────────────────────┘              │
│                                                             │
│   ┌─────────────────────────────────────────┐              │
│   │       Dependencies (의존성)              │  횡단 관심사│
│   │   인증, 권한, DB 세션 등                 │              │
│   └─────────────────────────────────────────┘              │
│                                                             │
│   ┌─────────────────────────────────────────┐              │
│   │         Schemas (스키마)                 │  DTO       │
│   │   요청/응답 데이터 검증                  │              │
│   └─────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 3. 각 계층 상세 설명

### 3.1 main.py - 앱 진입점

```python
# app/main.py

"""
FastAPI 애플리케이션의 진입점

역할:
1. FastAPI 앱 인스턴스 생성
2. 미들웨어 등록 (CORS 등)
3. 라우터 연결
4. 예외 핸들러 등록
5. 수명 주기 이벤트 관리
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import api_router

# 수명 주기 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # 시작 시 DB 초기화
    yield
    # 종료 시 정리 작업

# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS 미들웨어
app.add_middleware(CORSMiddleware, ...)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    ...
```

### 3.2 config.py - 환경 설정

```python
# app/config.py

"""
환경 변수 및 설정 관리

역할:
1. .env 파일에서 설정 로드
2. 타입 안전한 설정 접근
3. 설정 값 캐싱
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 앱 설정
    app_name: str = "FastAPI Boilerplate"
    debug: bool = False

    # DB 설정
    db_type: str = "sqlite"
    db_host: str = "localhost"
    ...

    # JWT 설정
    jwt_secret_key: str
    access_token_expire_minutes: int = 30
    ...

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 3.3 database.py - 데이터베이스

```python
# app/database.py

"""
데이터베이스 연결 관리

역할:
1. SQLAlchemy 엔진 생성
2. 세션 팩토리 생성
3. 세션 의존성 제공 (get_db)
4. 테이블 초기화 (init_db)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3.4 models/ - 데이터베이스 모델

```python
# app/models/user.py

"""
SQLAlchemy ORM 모델

역할:
1. DB 테이블 구조 정의
2. 관계(relationship) 설정
3. 테이블 동작 정의
"""

from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))

    # 관계
    posts = relationship("Post", back_populates="author")
```

### 3.5 schemas/ - Pydantic 스키마

```python
# app/schemas/user.py

"""
Pydantic 스키마 (DTO - Data Transfer Object)

역할:
1. 요청 데이터 검증
2. 응답 데이터 형식 정의
3. API 문서 자동 생성
"""

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    """사용자 응답"""
    id: int
    email: EmailStr
    username: str

    model_config = {"from_attributes": True}
```

### 3.6 routers/ - API 엔드포인트

```python
# app/routers/auth.py

"""
API 라우터

역할:
1. HTTP 엔드포인트 정의
2. 요청 받기 / 응답 반환
3. 의존성 주입
4. 스키마 검증 적용
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth import AuthService
from app.schemas.auth import LoginRequest, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    return service.login(request.username, request.password)
```

### 3.7 services/ - 비즈니스 로직

```python
# app/services/auth.py

"""
비즈니스 로직 서비스

역할:
1. 실제 비즈니스 로직 처리
2. 데이터베이스 조작
3. 외부 서비스 연동
4. 에러 처리
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, username: str, password: str) -> Token:
        # 1. 사용자 찾기
        user = self.db.query(User).filter(...).first()

        # 2. 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            raise HTTPException(...)

        # 3. 토큰 생성
        token = create_access_token(...)

        return Token(access_token=token)
```

### 3.8 dependencies/ - 의존성 함수

```python
# app/dependencies/auth.py

"""
FastAPI 의존성

역할:
1. 인증/인가 처리
2. 공통 로직 재사용
3. 요청 전처리
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 반환"""
    # 토큰 검증 및 사용자 조회
    ...

async def get_current_admin_user(
    user: User = Depends(get_current_user)
) -> User:
    """관리자 권한 확인"""
    if user.role != "admin":
        raise HTTPException(403, "권한 없음")
    return user
```

### 3.9 utils/ - 유틸리티

```python
# app/utils/security.py

"""
유틸리티 함수

역할:
1. 비밀번호 해싱
2. JWT 토큰 생성/검증
3. 기타 공통 함수
"""

from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"])

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY)
```

## 4. 요청 처리 흐름 예시

### 로그인 요청 처리

```
┌─────────────────────────────────────────────────────────────┐
│  POST /api/v1/auth/login                                    │
│  {"username": "john", "password": "pass123"}                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  1. main.py                                                 │
│     app.include_router(auth_router, prefix="/api/v1/auth")  │
│     → /login 경로로 라우팅                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. schemas/auth.py                                         │
│     LoginRequest 스키마로 요청 데이터 검증                   │
│     - username: str (필수)                                  │
│     - password: str (필수)                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. routers/auth.py                                         │
│     @router.post("/login")                                  │
│     def login(request: LoginRequest, db: Session):          │
│         service = AuthService(db)                           │
│         return service.login(...)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. dependencies (get_db)                                   │
│     db = SessionLocal()  ← 세션 생성                         │
│     yield db                                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. services/auth.py                                        │
│     AuthService.login():                                    │
│     - db.query(User).filter(...).first()                    │
│     - verify_password(...)                                  │
│     - create_access_token(...)                              │
│     return Token(access_token=...)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 응답                                                    │
│     {"access_token": "eyJ...", "token_type": "bearer"}      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  7. dependencies (get_db) finally                           │
│     db.close()  ← 세션 정리                                  │
└─────────────────────────────────────────────────────────────┘
```

## 5. 라우터 통합 구조

### routers/__init__.py

```python
# app/routers/__init__.py

"""
모든 라우터를 통합하는 파일

역할:
1. 개별 라우터 import
2. prefix와 tags 설정
3. 하나의 api_router로 통합
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router
from .dashboard import router as dashboard_router
from .theme import router as theme_router
from .menu import router as menu_router

# 통합 라우터 생성
api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)
api_router.include_router(
    posts_router,
    prefix="/posts",
    tags=["Posts"]
)
# ...
```

### main.py에서 등록

```python
# app/main.py

from app.routers import api_router

app.include_router(api_router, prefix="/api/v1")
```

### 최종 URL 구조

```
/api/v1/
├── /auth/
│   ├── POST /register     회원가입
│   ├── POST /login        로그인
│   ├── POST /refresh      토큰 갱신
│   └── GET  /me           내 정보
│
├── /users/
│   ├── GET  /             사용자 목록
│   ├── GET  /{id}         사용자 상세
│   ├── PUT  /{id}         사용자 수정
│   └── DELETE /{id}       사용자 삭제
│
├── /posts/
│   ├── GET  /             게시글 목록
│   ├── POST /             게시글 작성
│   ├── GET  /{id}         게시글 상세
│   ├── PUT  /{id}         게시글 수정
│   ├── DELETE /{id}       게시글 삭제
│   └── /{id}/comments/    댓글 관련
│
├── /dashboard/
│   └── GET  /stats        통계
│
├── /theme/
│   ├── GET  /             테마 조회
│   └── PUT  /             테마 변경
│
└── /menu/
    └── GET  /             메뉴 목록
```

## 6. 파일 명명 규칙

```
┌─────────────────────────────────────────────────────────────┐
│  파일 명명 규칙                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  폴더명         소문자 + 언더스코어 (snake_case)             │
│  예: models/, routers/, services/                           │
│                                                             │
│  파일명         소문자 + 언더스코어                          │
│  예: user.py, auth.py, post.py                              │
│                                                             │
│  클래스명       PascalCase                                  │
│  예: User, UserCreate, AuthService                          │
│                                                             │
│  함수명         소문자 + 언더스코어                          │
│  예: get_user, create_post, get_password_hash               │
│                                                             │
│  변수명         소문자 + 언더스코어                          │
│  예: user_id, access_token, db_session                      │
│                                                             │
│  상수명         대문자 + 언더스코어                          │
│  예: SECRET_KEY, MAX_RETRY, DEFAULT_PAGE_SIZE               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7. 새 기능 추가 시 작업 순서

새로운 기능(예: "좋아요" 기능)을 추가할 때:

```
1️⃣  models/like.py        모델 정의 (테이블)
    - Like 클래스 정의
    - 관계 설정

2️⃣  schemas/like.py       스키마 정의 (요청/응답)
    - LikeCreate
    - LikeResponse

3️⃣  services/like.py      서비스 정의 (비즈니스 로직)
    - LikeService 클래스
    - toggle_like(), get_like_count()

4️⃣  routers/like.py       라우터 정의 (엔드포인트)
    - POST /posts/{id}/like
    - GET /posts/{id}/likes

5️⃣  routers/__init__.py   라우터 등록
    - api_router.include_router(like_router)

6️⃣  tests/test_like.py    테스트 작성
```

## 요약

| 폴더/파일 | 역할 | 의존 방향 |
|----------|------|----------|
| main.py | 앱 진입점 | routers ← |
| config.py | 환경 설정 | 모든 곳에서 사용 |
| database.py | DB 연결 | models, services |
| models/ | DB 테이블 | database |
| schemas/ | 데이터 검증 | (독립적) |
| routers/ | API 엔드포인트 | services, schemas |
| services/ | 비즈니스 로직 | models |
| dependencies/ | 공통 의존성 | services, database |
| utils/ | 유틸리티 | (독립적) |

## 다음 단계

다음 문서 [07-routers.md](./07-routers.md)에서는 라우터(API 엔드포인트)를 상세히 학습합니다.
