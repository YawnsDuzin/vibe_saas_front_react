# 보안 유틸리티

## 개요

이 문서에서는 **비밀번호 해싱**과 **JWT 토큰 관리** 등 보안 관련 유틸리티 함수들을 설명합니다.

## 1. 비밀번호 보안

### 왜 해싱이 필요한가?

```
┌─────────────────────────────────────────────────────────────┐
│                    비밀번호 저장 방식                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ❌ 잘못된 방식: 평문 저장                                   │
│  ──────────────────────────────                             │
│  DB: password = "mypassword123"                             │
│                                                             │
│  → DB가 해킹되면 모든 비밀번호 노출                          │
│  → 같은 비밀번호를 다른 사이트에서도 사용할 수 있음          │
│                                                             │
│                                                             │
│  ✅ 올바른 방식: 해싱 저장                                   │
│  ──────────────────────────────                             │
│  DB: hashed_password = "$2b$12$LQv3c1yqBw..."               │
│                                                             │
│  → 해시는 원본으로 되돌릴 수 없음 (단방향)                   │
│  → 같은 비밀번호도 다른 해시값 (salt 사용)                   │
│  → 무차별 대입 공격 어려움                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### bcrypt 알고리즘

```python
# bcrypt의 특징
#
# 1. Salt 자동 생성
#    - 같은 비밀번호도 매번 다른 해시
#    - Rainbow Table 공격 방지
#
# 2. 느린 해싱 (의도적)
#    - 비용 요소(cost factor)로 속도 조절
#    - 무차별 대입 공격 방어
#
# 3. 해시 형식
#    $2b$12$LQv3c1yqBwEHGZoR5xtKYOx7gXz8Jz5Q.KpW6dRxX5K0Y5K0Y5K0Y
#    ├─┤├─┤├───────────────────────────────────────────────────┤
#    알고  비용     salt (22자) + hash (31자)
#    리즘  요소

```

### 이 프로젝트의 비밀번호 함수

```python
# app/utils/security.py

from passlib.context import CryptContext

# bcrypt 설정
pwd_context = CryptContext(
    schemes=["bcrypt"],  # bcrypt 알고리즘 사용
    deprecated="auto"    # 구식 알고리즘 자동 감지
)


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시합니다.

    Args:
        password: 원본 비밀번호 (예: "MyP@ssword123")

    Returns:
        해시된 비밀번호 (예: "$2b$12$...")

    Example:
        >>> hashed = get_password_hash("password123")
        >>> print(hashed)
        '$2b$12$LQv3c1yqBwEHGZoR5xtKYO...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호를 검증합니다.

    입력된 비밀번호가 저장된 해시와 일치하는지 확인합니다.

    Args:
        plain_password: 사용자가 입력한 비밀번호
        hashed_password: DB에 저장된 해시

    Returns:
        일치 여부 (True/False)

    Example:
        >>> hashed = get_password_hash("password123")
        >>> verify_password("password123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
```

### 사용 예시

```python
# 회원가입 시
def create_user(user_data: UserCreate, db: Session):
    hashed_password = get_password_hash(user_data.password)

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password  # 해시된 비밀번호 저장
    )
    db.add(user)
    db.commit()
    return user


# 로그인 시
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    # 비밀번호 검증
    if not verify_password(password, user.hashed_password):
        return None

    return user
```

## 2. JWT 토큰 관리

### JWT 생성

```python
# app/utils/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from app.config import settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터
              {"sub": "user_id", "username": "john", ...}
        expires_delta: 만료 시간 (기본: 30분)

    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes  # 30
        )

    # 페이로드에 만료 시간과 타입 추가
    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    # JWT 인코딩
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm  # HS256
    )

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    리프레시 토큰 생성

    액세스 토큰보다 긴 만료 시간 (7일)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days  # 7
        )

    to_encode.update({
        "exp": expire,
        "type": "refresh"  # 리프레시 토큰 표시
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt
```

### JWT 검증

```python
def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 디코딩

    토큰을 검증하고 페이로드를 반환합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        디코딩된 페이로드 또는 None (실패 시)

    실패 케이스:
        - 토큰 만료
        - 서명 불일치
        - 형식 오류
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload

    except JWTError as e:
        # 만료, 서명 오류, 형식 오류 등
        print(f"[DEBUG] JWT 에러: {e}")
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    토큰 타입 검증

    Args:
        token: JWT 토큰
        expected_type: "access" 또는 "refresh"

    Returns:
        타입 일치 여부
    """
    payload = decode_token(token)
    if payload is None:
        return False
    return payload.get("type") == expected_type
```

## 3. 보안 설정 (config.py)

```python
# app/config.py

class Settings(BaseSettings):
    # JWT 설정
    jwt_secret_key: str = Field(
        default="change-this-secret-key-in-production",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # 일반 보안 설정
    secret_key: str = Field(
        default="change-this-secret-key",
        alias="SECRET_KEY"
    )
```

### 환경 변수 (.env)

```env
# 보안 키 (프로덕션에서는 강력한 랜덤 문자열 사용)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 강력한 시크릿 키 생성 방법
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 4. CORS 보안

### CORS란?

```
┌─────────────────────────────────────────────────────────────┐
│                    CORS (Cross-Origin Resource Sharing)     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  브라우저는 보안상 다른 출처의 요청을 기본적으로 차단합니다.   │
│                                                             │
│  출처 = 프로토콜 + 도메인 + 포트                             │
│                                                             │
│  같은 출처:                                                  │
│  http://localhost:3000 → http://localhost:3000  ✅          │
│                                                             │
│  다른 출처:                                                  │
│  http://localhost:3000 → http://localhost:8000  ❌          │
│  (포트가 다름)                                               │
│                                                             │
│  → 서버에서 CORS 헤더를 설정하여 허용                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### CORS 설정

```python
# app/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,

    # 허용할 출처 목록
    allow_origins=settings.cors_origins_list,
    # ["http://localhost:3000", "http://localhost:8080"]

    # 쿠키/인증 헤더 허용
    allow_credentials=True,

    # 허용할 HTTP 메서드
    allow_methods=["*"],  # 모든 메서드 (GET, POST, PUT, DELETE, ...)

    # 허용할 헤더
    allow_headers=["*"],  # 모든 헤더 (Authorization, Content-Type, ...)
)
```

### config.py의 CORS 설정

```python
# app/config.py

class Settings(BaseSettings):
    # CORS 설정 (JSON 문자열로 저장)
    cors_origins: str = Field(
        default='["http://localhost:3000","http://localhost:8080"]',
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        alias="CORS_ALLOW_CREDENTIALS"
    )
    cors_allow_methods: str = Field(
        default='["*"]',
        alias="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: str = Field(
        default='["*"]',
        alias="CORS_ALLOW_HEADERS"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """JSON 문자열 → 리스트 변환"""
        return json.loads(self.cors_origins)
```

## 5. 보안 Best Practices

### 환경 변수 관리

```
┌─────────────────────────────────────────────────────────────┐
│                    환경 변수 보안                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ DO:                                                     │
│  - .env 파일을 .gitignore에 추가                           │
│  - 프로덕션에서 강력한 시크릿 키 사용                       │
│  - 환경별로 다른 설정 사용                                  │
│  - 정기적으로 시크릿 키 교체                                │
│                                                             │
│  ❌ DON'T:                                                  │
│  - 코드에 시크릿 키 하드코딩                                │
│  - .env 파일을 Git에 커밋                                   │
│  - 개발용 키를 프로덕션에서 사용                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 비밀번호 정책

```python
# app/schemas/user.py

from pydantic import field_validator
import re

class UserCreate(BaseModel):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 강도 검증"""
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        if not re.search(r"[A-Z]", v):
            raise ValueError("대문자가 최소 1개 포함되어야 합니다.")

        if not re.search(r"[a-z]", v):
            raise ValueError("소문자가 최소 1개 포함되어야 합니다.")

        if not re.search(r"\d", v):
            raise ValueError("숫자가 최소 1개 포함되어야 합니다.")

        # 선택: 특수문자 요구
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        #     raise ValueError("특수문자가 최소 1개 포함되어야 합니다.")

        return v
```

### SQL Injection 방지

```python
# SQLAlchemy ORM을 사용하면 자동으로 방지됨

# ❌ 잘못된 방식: 문자열 조합
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ 올바른 방식: SQLAlchemy ORM (파라미터화)
user = db.query(User).filter(User.username == username).first()
```

### 입력 검증

```python
# Pydantic이 자동으로 처리

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    # 이메일 형식 검증
    email: EmailStr

    # 길이 제한
    username: str = Field(..., min_length=3, max_length=50)

    # 숫자 범위
    age: int = Field(..., ge=0, le=150)
```

## 6. 보안 체크리스트

```
┌─────────────────────────────────────────────────────────────┐
│                    보안 체크리스트                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  인증/인가                                                  │
│  □ 비밀번호 해싱 (bcrypt)                                   │
│  □ JWT 토큰 사용                                            │
│  □ 토큰 만료 시간 설정                                      │
│  □ 역할 기반 접근 제어 (RBAC)                               │
│                                                             │
│  데이터 보호                                                │
│  □ HTTPS 사용 (프로덕션)                                    │
│  □ 민감 데이터 응답에서 제외                                │
│  □ SQL Injection 방지 (ORM 사용)                            │
│  □ 입력 검증 (Pydantic)                                     │
│                                                             │
│  설정                                                       │
│  □ 시크릿 키 환경 변수 관리                                 │
│  □ CORS 적절히 설정                                         │
│  □ 디버그 모드 프로덕션에서 비활성화                         │
│  □ 에러 메시지에 민감 정보 제외                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 요약

| 함수 | 용도 | 라이브러리 |
|------|------|-----------|
| `get_password_hash()` | 비밀번호 해싱 | passlib (bcrypt) |
| `verify_password()` | 비밀번호 검증 | passlib (bcrypt) |
| `create_access_token()` | JWT 생성 | python-jose |
| `create_refresh_token()` | 리프레시 토큰 생성 | python-jose |
| `decode_token()` | JWT 검증 | python-jose |

## 다음 단계

다음 문서 [12-error-handling.md](./12-error-handling.md)에서는 에러 처리 방법을 학습합니다.
