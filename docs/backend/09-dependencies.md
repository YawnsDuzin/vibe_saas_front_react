# 의존성 주입 (Dependency Injection)

## 개요

**의존성 주입(DI)**은 FastAPI의 핵심 기능 중 하나입니다. 코드를 재사용하고, 인증/권한 검사를 쉽게 적용할 수 있게 해줍니다.

## 1. 의존성 주입이란?

### 기본 개념

```python
# 의존성 = 함수가 실행되기 전에 필요한 것

from fastapi import Depends

# 의존성 함수
def get_database():
    return Database()

# 의존성 사용
@app.get("/users")
def get_users(db = Depends(get_database)):
    #          └─ get_database()의 반환값이 db에 주입됨
    return db.query("SELECT * FROM users")
```

**Depends() 동작 방식:**
```
┌─────────────────────────────────────────────────────────────┐
│  요청: GET /users                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. FastAPI가 get_users 함수 확인                           │
│                                                             │
│  2. Depends(get_database) 발견                              │
│     → get_database() 함수 실행                              │
│     → 반환값 저장                                           │
│                                                             │
│  3. get_users(db=반환값) 호출                               │
│                                                             │
│  4. 응답 반환                                               │
│                                                             │
│  5. 정리 작업 (finally 블록 등)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 의존성의 장점

```
┌─────────────────────────────────────────────────────────────┐
│  의존성 주입의 장점                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ 코드 재사용                                             │
│     - 한 번 작성, 여러 곳에서 사용                          │
│     - 예: get_db()를 모든 라우터에서 사용                   │
│                                                             │
│  ✅ 관심사 분리                                             │
│     - 인증 로직을 라우터에서 분리                           │
│     - 라우터는 비즈니스 로직에만 집중                       │
│                                                             │
│  ✅ 테스트 용이                                             │
│     - 의존성을 모킹(mocking)하여 테스트                     │
│     - 실제 DB 없이도 테스트 가능                            │
│                                                             │
│  ✅ 자동 정리                                               │
│     - yield 사용 시 자동 리소스 정리                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. 의존성 유형

### 함수 의존성

```python
# 가장 기본적인 의존성
def get_settings():
    return Settings()

@app.get("/config")
def read_config(settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

### Generator 의존성 (리소스 관리)

```python
def get_db():
    """세션 생성 → 사용 → 자동 정리"""
    db = SessionLocal()
    try:
        yield db        # 세션 제공
    finally:
        db.close()      # 요청 완료 후 정리

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Generator 동작:**
```
┌─────────────────────────────────────────────────────────────┐
│  요청 시작                                                  │
│      │                                                      │
│      ▼                                                      │
│  db = SessionLocal()   # 세션 생성                          │
│      │                                                      │
│      ▼                                                      │
│  yield db              # 라우터로 전달 (여기서 멈춤)         │
│      │                                                      │
│      ▼                                                      │
│  라우터 함수 실행      # db 사용                            │
│      │                                                      │
│      ▼                                                      │
│  요청 완료                                                  │
│      │                                                      │
│      ▼                                                      │
│  db.close()            # finally 블록 실행                  │
└─────────────────────────────────────────────────────────────┘
```

### 클래스 의존성

```python
class CommonQueryParams:
    """공통 쿼리 파라미터"""
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        q: str = None
    ):
        self.skip = skip
        self.limit = limit
        self.q = q

@app.get("/items")
def get_items(params: CommonQueryParams = Depends()):
    #                                     └─ Depends(CommonQueryParams)와 동일
    return {
        "skip": params.skip,
        "limit": params.limit,
        "query": params.q
    }
```

### 의존성 체인

```python
# 의존성이 다른 의존성을 사용할 수 있음

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),  # 의존성 1
    db: Session = Depends(get_db)          # 의존성 2
) -> User:
    # 토큰으로 사용자 조회
    ...

def get_current_admin_user(
    user: User = Depends(get_current_user)  # 의존성 3 (체인)
) -> User:
    if user.role != "admin":
        raise HTTPException(403)
    return user

# 최종 사용
@app.delete("/users/{id}")
def delete_user(
    admin: User = Depends(get_current_admin_user)
):
    # admin은 체인을 거쳐 검증된 관리자
    ...
```

**체인 시각화:**
```
get_current_admin_user
        │
        └─► Depends(get_current_user)
                    │
                    ├─► Depends(oauth2_scheme) → 토큰 추출
                    │
                    └─► Depends(get_db) → DB 세션
```

## 3. 이 프로젝트의 의존성

### 데이터베이스 세션 (database.py)

```python
# app/database.py

from sqlalchemy.orm import Session
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 제공

    매 요청마다 새 세션을 생성하고,
    요청 완료 후 자동으로 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 인증 의존성 (dependencies/auth.py)

```python
# app/dependencies/auth.py

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_token

# OAuth2 스킴 (토큰 추출)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 선택적 OAuth2 (토큰 없어도 됨)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # 토큰 없으면 None 반환
)


# ====================================
# 기본 인증 의존성
# ====================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 반환

    1. Authorization 헤더에서 토큰 추출
    2. 토큰 검증 및 디코딩
    3. 사용자 조회 및 반환
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 토큰 디코딩
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # 토큰 타입 확인
    if payload.get("type") != "access":
        raise credentials_exception

    # 사용자 ID 추출
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == int(user_id_str)).first()
    if user is None:
        raise credentials_exception

    return user


# ====================================
# 활성 사용자 확인
# ====================================

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    활성화된 사용자만 허용

    비활성화된 계정은 접근 거부
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다."
        )
    return current_user


# ====================================
# 관리자 전용
# ====================================

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    관리자만 허용
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다. 관리자만 접근할 수 있습니다."
        )
    return current_user


# ====================================
# 선택적 인증 (로그인 안해도 됨)
# ====================================

async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적 인증

    - 토큰이 있으면 사용자 반환
    - 토큰이 없으면 None 반환
    - 에러 발생하지 않음
    """
    if token is None:
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    if payload.get("type") != "access":
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    user = db.query(User).filter(User.id == int(user_id_str)).first()
    return user


# ====================================
# 역할 기반 접근 제어 (동적)
# ====================================

def require_role(required_roles: list):
    """
    특정 역할을 요구하는 의존성 팩토리

    Args:
        required_roles: 허용되는 역할 목록

    Returns:
        의존성 함수

    Example:
        @router.get("/admin")
        def admin_only(user = Depends(require_role([UserRole.ADMIN]))):
            ...

        @router.get("/moderator")
        def mod_or_admin(user = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다."
            )
        return current_user

    return role_checker
```

## 4. 의존성 사용 예시

### 인증 필수 엔드포인트

```python
@router.get("/me")
def get_me(user: User = Depends(get_current_active_user)):
    """
    현재 로그인한 사용자 정보

    Authorization: Bearer <token> 헤더 필수
    """
    return user

@router.post("/posts")
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)  # 로그인 필수
):
    """로그인한 사용자만 게시글 작성 가능"""
    service = PostService(db)
    return service.create_post(post_data, author_id=user.id)
```

### 관리자 전용 엔드포인트

```python
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)  # 관리자 전용
):
    """관리자만 사용자 삭제 가능"""
    service = UserService(db)
    return service.delete_user(user_id)
```

### 선택적 인증

```python
@router.get("/posts")
def get_posts(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_current_user)
):
    """
    게시글 목록 조회

    - 비로그인: 공개 게시글만
    - 로그인: 본인 비공개 게시글도 포함
    """
    service = PostService(db)

    if user:
        # 로그인 사용자: 본인 글 포함
        return service.get_posts_for_user(user.id)
    else:
        # 비로그인: 공개글만
        return service.get_public_posts()
```

### 역할 기반 접근 제어

```python
from app.models.user import UserRole

# 관리자 또는 운영자
@router.put("/posts/{post_id}/pin")
def pin_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    """관리자 또는 운영자만 게시글 고정 가능"""
    ...

# 관리자만
@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    """관리자만 카테고리 삭제 가능"""
    ...
```

## 5. OAuth2PasswordBearer

### 동작 방식

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# tokenUrl: 토큰을 발급받는 엔드포인트
# Swagger UI에서 자동으로 로그인 폼 제공
```

**OAuth2PasswordBearer가 하는 일:**
```
┌─────────────────────────────────────────────────────────────┐
│  요청 헤더:                                                  │
│  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OAuth2PasswordBearer:                                      │
│  1. Authorization 헤더 확인                                 │
│  2. "Bearer " 접두사 제거                                   │
│  3. 토큰 문자열 반환 → "eyJhbGciOiJIUzI1NiIs..."            │
│                                                             │
│  토큰이 없으면:                                             │
│  - auto_error=True (기본): 401 에러                         │
│  - auto_error=False: None 반환                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 6. 의존성 테스트

### 의존성 오버라이드

```python
# tests/conftest.py

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.dependencies.auth import get_current_user

# 테스트용 DB 세션
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 테스트용 사용자
def override_get_current_user():
    return User(id=1, username="testuser", role=UserRole.USER)

# 의존성 오버라이드
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# 테스트
def test_get_me(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

## 7. 의존성 패턴 정리

```
┌─────────────────────────────────────────────────────────────┐
│                    의존성 패턴                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 리소스 관리 (DB 세션)                                   │
│     get_db() → yield db → finally: db.close()              │
│                                                             │
│  2. 인증 체인                                               │
│     oauth2_scheme → get_current_user → get_current_admin   │
│                                                             │
│  3. 팩토리 패턴 (동적 의존성)                               │
│     require_role([...]) → 의존성 함수 반환                  │
│                                                             │
│  4. 선택적 의존성                                           │
│     auto_error=False → None 반환 가능                       │
│                                                             │
│  5. 클래스 의존성                                           │
│     공통 파라미터 그룹화                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 요약

| 의존성 | 용도 | 위치 |
|--------|------|------|
| `get_db` | DB 세션 제공 | database.py |
| `get_current_user` | 인증된 사용자 | dependencies/auth.py |
| `get_current_active_user` | 활성 사용자 | dependencies/auth.py |
| `get_current_admin_user` | 관리자 | dependencies/auth.py |
| `get_optional_current_user` | 선택적 인증 | dependencies/auth.py |
| `require_role([...])` | 역할 기반 | dependencies/auth.py |

## 다음 단계

다음 문서 [10-authentication.md](./10-authentication.md)에서는 JWT 인증 시스템을 학습합니다.
