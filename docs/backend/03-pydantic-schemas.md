# Pydantic 스키마

## 개요

**Pydantic**은 Python에서 데이터 검증(validation)과 설정 관리를 위한 라이브러리입니다. FastAPI는 Pydantic을 사용하여 요청/응답 데이터를 자동으로 검증합니다.

## 1. Pydantic이란?

### 기본 개념

```python
from pydantic import BaseModel

# Pydantic 모델 정의
class User(BaseModel):
    name: str
    age: int
    email: str

# 올바른 데이터 → 성공
user = User(name="홍길동", age=25, email="hong@example.com")
print(user.name)  # "홍길동"

# 잘못된 데이터 → 에러 발생!
user = User(name="홍길동", age="스물다섯", email="hong@example.com")
# ValidationError: age는 정수여야 합니다
```

### Pydantic vs 일반 딕셔너리

```python
# 일반 딕셔너리: 검증 없음
user_dict = {
    "name": 123,           # 숫자도 가능 (문제!)
    "age": "스물다섯",      # 문자열도 가능 (문제!)
    "email": "invalid"     # 형식 검증 없음 (문제!)
}

# Pydantic: 자동 검증
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str              # 문자열만 허용
    age: int               # 정수만 허용
    email: EmailStr        # 이메일 형식만 허용

user = User(name="홍길동", age=25, email="hong@example.com")  # 성공
user = User(name=123, age="20", email="invalid")  # 에러!
```

**Pydantic의 장점:**
```
┌─────────────────────────────────────────────────────────────┐
│  Pydantic 장점                                              │
├─────────────────────────────────────────────────────────────┤
│  ✅ 자동 타입 검증     - 잘못된 타입 데이터 거부             │
│  ✅ 자동 타입 변환     - "25" → 25 자동 변환               │
│  ✅ IDE 자동완성      - 속성 자동완성 지원                  │
│  ✅ 직렬화/역직렬화   - JSON ↔ Python 객체 변환             │
│  ✅ API 문서 생성     - FastAPI Swagger 문서 자동 생성      │
└─────────────────────────────────────────────────────────────┘
```

## 2. 기본 모델 정의

### 필드 타입

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    # 기본 타입
    name: str                    # 문자열 (필수)
    age: int                     # 정수 (필수)
    height: float                # 실수 (필수)
    is_active: bool              # 불리언 (필수)

    # 선택적 필드 (None 허용)
    nickname: Optional[str] = None

    # 기본값 있는 필드
    role: str = "user"

    # 리스트 타입
    tags: List[str] = []

    # 날짜/시간
    created_at: datetime
```

### 필드 유효성 검사

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    # Field()로 상세 제약 설정
    username: str = Field(
        ...,                    # ... = 필수 필드
        min_length=3,           # 최소 3자
        max_length=50,          # 최대 50자
        description="사용자명"   # 설명 (문서용)
    )

    age: int = Field(
        ...,
        ge=0,                   # >= 0 (0 이상)
        le=150,                 # <= 150 (150 이하)
        description="나이"
    )

    email: str = Field(
        ...,
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',  # 정규식 패턴
        description="이메일"
    )

    # 커스텀 검증 로직
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """사용자명 검증"""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("영문으로 시작하고 영문/숫자/언더스코어만 허용")
        return v
```

**Field() 옵션:**
```
┌────────────────┬─────────────────────────────────────────┐
│  옵션          │  설명                                   │
├────────────────┼─────────────────────────────────────────┤
│  ...           │  필수 필드 (default 없음)               │
│  default       │  기본값                                 │
│  min_length    │  문자열 최소 길이                       │
│  max_length    │  문자열 최대 길이                       │
│  ge            │  숫자 >= (greater than or equal)        │
│  le            │  숫자 <= (less than or equal)           │
│  gt            │  숫자 > (greater than)                  │
│  lt            │  숫자 < (less than)                     │
│  pattern       │  정규식 패턴                            │
│  description   │  필드 설명 (문서용)                     │
│  example       │  예시 값 (문서용)                       │
└────────────────┴─────────────────────────────────────────┘
```

## 3. 이 프로젝트의 스키마

### 사용자 스키마 (app/schemas/user.py)

```python
# app/schemas/user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """
    사용자 기본 스키마 - 공통 필드 정의
    """
    email: EmailStr = Field(
        ...,
        description="사용자 이메일",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="사용자명 (3-50자)",
        example="johndoe"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="실제 이름"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """사용자명: 영문 시작, 영문/숫자/언더스코어만"""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError(
                "사용자명은 영문으로 시작하고 영문, 숫자, 언더스코어만 포함"
            )
        return v


class UserCreate(UserBase):
    """
    회원가입용 스키마 - UserBase + 비밀번호
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="비밀번호 (최소 8자)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 강도 검증"""
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상")
        if not re.search(r"[A-Z]", v):
            raise ValueError("대문자가 최소 1개 포함되어야 함")
        if not re.search(r"[a-z]", v):
            raise ValueError("소문자가 최소 1개 포함되어야 함")
        if not re.search(r"\d", v):
            raise ValueError("숫자가 최소 1개 포함되어야 함")
        return v


class UserResponse(BaseModel):
    """
    API 응답용 스키마 - 민감 정보 제외
    """
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # ORM 모드 활성화
    }
```

**스키마 상속 구조:**
```
┌─────────────────────────────────────────────────────────────┐
│                    스키마 상속 구조                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  UserBase (기본)                                            │
│  ├── email                                                  │
│  ├── username                                               │
│  └── full_name                                              │
│       │                                                     │
│       ├─── UserCreate (생성용)                              │
│       │    └── password  (추가)                             │
│       │                                                     │
│       └─── UserUpdate (수정용)                              │
│            └── 모든 필드 Optional                           │
│                                                             │
│  UserResponse (응답용) - 별도 정의                          │
│  ├── id, email, username, ...                               │
│  └── password 없음! (보안)                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 인증 스키마 (app/schemas/auth.py)

```python
# app/schemas/auth.py

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    토큰 응답 스키마 - 로그인 성공 시 반환
    """
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    """
    토큰 페이로드 스키마 - JWT에서 디코딩된 데이터
    """
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """
    로그인 요청 스키마
    """
    username: str = Field(
        ...,
        description="이메일 또는 사용자명",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="비밀번호"
    )


class RefreshTokenRequest(BaseModel):
    """
    토큰 갱신 요청 스키마
    """
    refresh_token: str = Field(
        ...,
        description="리프레시 토큰"
    )
```

## 4. 스키마 활용 패턴

### 요청 검증

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,  # ← Pydantic이 자동 검증
    db: Session = Depends(get_db)
):
    """
    요청 본문이 UserCreate 스키마와 일치하지 않으면
    FastAPI가 자동으로 422 에러를 반환합니다.
    """
    # 검증된 데이터 사용
    print(user_data.email)     # 유효한 이메일
    print(user_data.username)  # 검증된 사용자명
    print(user_data.password)  # 강도 검증된 비밀번호
    ...
```

**검증 실패 시 응답:**
```json
{
    "detail": [
        {
            "loc": ["body", "password"],
            "msg": "비밀번호는 최소 8자 이상이어야 합니다.",
            "type": "value_error"
        }
    ]
}
```

### 응답 필터링

```python
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    response_model=UserResponse를 설정하면
    응답에서 password 같은 민감한 필드가 자동으로 제외됩니다.
    """
    user = db.query(User).filter(User.id == user_id).first()

    # user에는 hashed_password가 있지만...
    return user  # UserResponse 필드만 응답에 포함됨
```

**응답 예시:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00",
    "last_login": null
}
// password나 hashed_password는 포함되지 않음!
```

### ORM 모드 (from_attributes)

SQLAlchemy 모델을 Pydantic 모델로 변환합니다.

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True  # ORM 모드 활성화
    }

# SQLAlchemy 모델 → Pydantic 모델 변환
user_orm = db.query(User).first()  # SQLAlchemy 객체
user_pydantic = UserResponse.model_validate(user_orm)

# 또는 FastAPI의 response_model에서 자동 변환
@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session):
    return db.query(User).first()  # 자동으로 UserResponse로 변환
```

**from_attributes 동작:**
```
┌─────────────────────────────────────────────────────────────┐
│  SQLAlchemy User 객체                                       │
│  ├── id = 1                                                 │
│  ├── username = "johndoe"                                   │
│  ├── email = "john@example.com"                             │
│  ├── hashed_password = "$2b$12$..."  ← 민감 정보            │
│  └── ...                                                    │
│                                                             │
│         ↓  response_model=UserResponse                      │
│                                                             │
│  UserResponse (Pydantic)                                    │
│  ├── id = 1                                                 │
│  ├── username = "johndoe"                                   │
│  ├── email = "john@example.com"                             │
│  └── (hashed_password 없음!)                                │
└─────────────────────────────────────────────────────────────┘
```

## 5. 고급 기능

### 중첩 모델 (Nested Models)

```python
from typing import List, Optional
from pydantic import BaseModel

class Comment(BaseModel):
    id: int
    content: str
    author: str

class Post(BaseModel):
    id: int
    title: str
    content: str
    comments: List[Comment] = []  # Comment 리스트

# 사용
post = Post(
    id=1,
    title="제목",
    content="내용",
    comments=[
        Comment(id=1, content="좋아요", author="Alice"),
        Comment(id=2, content="감사합니다", author="Bob")
    ]
)
```

### 커스텀 validator 종류

```python
from pydantic import BaseModel, field_validator, model_validator

class User(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str

    # 단일 필드 검증
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("3자 이상이어야 합니다")
        return v

    # 여러 필드를 함께 검증
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return self
```

### JSON 직렬화

```python
from pydantic import BaseModel
import json

class User(BaseModel):
    name: str
    age: int

user = User(name="홍길동", age=25)

# Pydantic → dict
user_dict = user.model_dump()
# {"name": "홍길동", "age": 25}

# Pydantic → JSON 문자열
user_json = user.model_dump_json()
# '{"name": "홍길동", "age": 25}'

# dict → Pydantic
user = User.model_validate({"name": "홍길동", "age": 25})

# JSON 문자열 → Pydantic
user = User.model_validate_json('{"name": "홍길동", "age": 25}')
```

### 특수 타입

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl

class User(BaseModel):
    # 이메일 형식 검증
    email: EmailStr  # "user@example.com"

    # URL 형식 검증
    website: Optional[HttpUrl] = None  # "https://example.com"

    # 날짜/시간 자동 파싱
    created_at: datetime  # "2024-01-01T00:00:00" → datetime 객체

    # 리스트 검증
    tags: List[str] = []

# 자동 변환
user = User(
    email="user@example.com",
    website="https://example.com",
    created_at="2024-01-01T12:00:00",  # 문자열 → datetime 자동 변환
    tags=["python", "fastapi"]
)

print(type(user.created_at))  # <class 'datetime.datetime'>
```

## 6. Pydantic Settings (환경 설정)

### 환경 변수 관리

```python
# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    환경 변수를 타입 안전하게 관리합니다.
    """

    # 환경 변수 매핑
    app_name: str = Field(default="MyApp", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")

    # 데이터베이스 설정
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="mydb", alias="DB_NAME")

    # JWT 설정
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # .env 파일에서 읽기
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 싱글톤 패턴으로 사용
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

**.env 파일:**
```env
APP_NAME=FastAPI 보일러플레이트
DEBUG=true
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fastapi_db
JWT_SECRET_KEY=my-super-secret-key
```

**사용:**
```python
from app.config import settings

print(settings.app_name)       # "FastAPI 보일러플레이트"
print(settings.debug)          # True
print(settings.jwt_secret_key) # "my-super-secret-key"
```

### 이 프로젝트의 Settings

```python
# app/config.py (프로젝트 실제 코드)

class Settings(BaseSettings):
    # 애플리케이션 설정
    app_name: str = Field(default="FastAPI Boilerplate", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    # 데이터베이스 설정 (다중 DB 지원)
    db_type: str = Field(default="postgresql", alias="DB_TYPE")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    db_name: str = Field(default="fastapi_db", alias="DB_NAME")

    # JWT 설정
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # CORS 설정 (JSON 문자열로 저장)
    cors_origins: str = Field(
        default='["http://localhost:3000"]',
        alias="CORS_ORIGINS"
    )

    @property
    def database_url(self) -> str:
        """DB 타입에 따른 연결 문자열 생성"""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_file}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        ...

    @property
    def cors_origins_list(self) -> List[str]:
        """JSON 문자열 → 리스트 변환"""
        return json.loads(self.cors_origins)
```

## 7. 스키마 설계 Best Practices

### 1. 용도별 스키마 분리

```python
# 생성용 (Create) - 필수 필드만
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# 수정용 (Update) - 모든 필드 선택적
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

# 응답용 (Response) - 민감 정보 제외
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    # password 없음!
```

### 2. 상속으로 중복 제거

```python
class UserBase(BaseModel):
    """공통 필드"""
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """생성용 = 공통 + 비밀번호"""
    password: str

class UserResponse(UserBase):
    """응답용 = 공통 + ID"""
    id: int

    model_config = {"from_attributes": True}
```

### 3. 문서화 (예시 포함)

```python
class UserCreate(BaseModel):
    email: EmailStr = Field(
        ...,
        description="사용자 이메일 주소",
        example="user@example.com"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecureP@ss123"
            }
        }
    }
```

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| BaseModel | 기본 모델 클래스 | `class User(BaseModel)` |
| Field() | 필드 제약 조건 | `Field(min_length=3)` |
| field_validator | 커스텀 검증 | `@field_validator("email")` |
| model_config | 모델 설정 | `from_attributes = True` |
| EmailStr | 이메일 타입 | `email: EmailStr` |
| BaseSettings | 환경 설정 | `class Settings(BaseSettings)` |

## 다음 단계

다음 문서 [04-sqlalchemy-models.md](./04-sqlalchemy-models.md)에서는 SQLAlchemy ORM 모델을 학습합니다.
