# JWT 인증 시스템

## 개요

이 프로젝트는 **JWT(JSON Web Token)** 기반 인증을 사용합니다. JWT는 사용자 정보를 안전하게 전달하는 표준 방식입니다.

## 1. JWT란?

### 기본 개념

```
┌─────────────────────────────────────────────────────────────┐
│                       JWT 구조                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.                      │ ← Header
│  eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.            │ ← Payload
│  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c               │ ← Signature
│                                                             │
│  세 부분이 점(.)으로 구분됨                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**각 부분 설명:**
```
Header (헤더):
{
  "alg": "HS256",    ← 서명 알고리즘
  "typ": "JWT"       ← 토큰 타입
}

Payload (페이로드):
{
  "sub": "123",      ← 사용자 ID (subject)
  "username": "john",
  "exp": 1609459200  ← 만료 시간
}

Signature (서명):
HMACSHA256(
  base64(header) + "." + base64(payload),
  secret_key
)
```

### JWT vs 세션

```
┌────────────────────────────────────────────────────────────┐
│  세션 기반 인증                 JWT 기반 인증               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  [클라이언트] ──로그인──→ [서버]                            │
│  [클라이언트] ←──세션ID── [서버]  [클라이언트] ←──JWT── [서버]│
│                                                            │
│  세션 저장소 필요              토큰에 정보 포함             │
│  (Redis, DB 등)               서버 저장소 불필요           │
│                                                            │
│  요청마다 세션 조회            토큰 자체 검증               │
│  서버 부하 증가                서버 부하 감소               │
│                                                            │
│  스케일링 어려움               스케일링 쉬움                │
│  (세션 공유 필요)              (상태 없음)                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## 2. 인증 흐름

### 로그인 → 토큰 발급

```
┌─────────────────────────────────────────────────────────────┐
│                       로그인 흐름                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 클라이언트 → 서버                                        │
│     POST /api/v1/auth/login                                 │
│     {"username": "john", "password": "pass123"}             │
│                                                             │
│  2. 서버: 사용자 인증                                        │
│     - 이메일/사용자명으로 사용자 조회                        │
│     - 비밀번호 검증 (bcrypt)                                │
│                                                             │
│  3. 서버: 토큰 생성                                         │
│     - Access Token (30분)                                   │
│     - Refresh Token (7일)                                   │
│                                                             │
│  4. 서버 → 클라이언트                                       │
│     {                                                       │
│       "access_token": "eyJhbG...",                          │
│       "refresh_token": "eyJhbG...",                         │
│       "token_type": "bearer"                                │
│     }                                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### API 요청 (인증 필요)

```
┌─────────────────────────────────────────────────────────────┐
│                       API 요청 흐름                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 클라이언트 → 서버                                        │
│     GET /api/v1/users/me                                    │
│     Headers:                                                │
│       Authorization: Bearer eyJhbGciOiJIUzI1NiIs...         │
│                                                             │
│  2. 서버: 토큰 검증                                         │
│     - 서명 확인 (위변조 검사)                               │
│     - 만료 시간 확인                                        │
│     - 토큰 타입 확인 (access)                               │
│                                                             │
│  3. 서버: 사용자 조회                                       │
│     - 토큰의 user_id로 DB 조회                              │
│     - 활성 상태 확인                                        │
│                                                             │
│  4. 서버 → 클라이언트                                       │
│     {"id": 1, "username": "john", ...}                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 토큰 갱신

```
┌─────────────────────────────────────────────────────────────┐
│                       토큰 갱신 흐름                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Access Token 만료됨 (401 Unauthorized)                     │
│                                                             │
│  1. 클라이언트 → 서버                                        │
│     POST /api/v1/auth/refresh                               │
│     {"refresh_token": "eyJhbG..."}                          │
│                                                             │
│  2. 서버: 리프레시 토큰 검증                                │
│     - 서명 및 만료 확인                                     │
│     - 토큰 타입 확인 (refresh)                              │
│     - 사용자 상태 확인                                      │
│                                                             │
│  3. 서버: 새 토큰 발급                                      │
│     - 새 Access Token                                       │
│     - 새 Refresh Token (선택)                               │
│                                                             │
│  4. 서버 → 클라이언트                                       │
│     {"access_token": "새토큰...", ...}                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 3. 이 프로젝트의 인증 구현

### 토큰 생성 (utils/security.py)

```python
# app/utils/security.py

from datetime import datetime, timedelta
from jose import jwt
from app.config import settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, username 등)
        expires_delta: 만료 시간 (기본: settings 값)

    Returns:
        JWT 문자열
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes  # 30분
        )

    # 페이로드에 추가 정보
    to_encode.update({
        "exp": expire,      # 만료 시간
        "type": "access"    # 토큰 타입
    })

    # JWT 인코딩
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm  # HS256
    )

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    리프레시 토큰 생성

    액세스 토큰보다 긴 만료 시간 (7일)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days  # 7일
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

### 토큰 검증 (utils/security.py)

```python
def decode_token(token: str) -> dict | None:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 문자열

    Returns:
        디코딩된 페이로드 또는 None (실패 시)
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        # 만료, 서명 오류 등
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    토큰 타입 검증

    Args:
        token: JWT 토큰
        expected_type: 예상 타입 ("access" 또는 "refresh")

    Returns:
        타입 일치 여부
    """
    payload = decode_token(token)
    if payload is None:
        return False
    return payload.get("type") == expected_type
```

### 로그인 서비스 (services/auth.py)

```python
# app/services/auth.py

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, username: str, password: str) -> Token:
        """
        로그인 처리

        1. 사용자 인증
        2. 토큰 생성
        3. 로그인 기록
        """
        # 1. 사용자 인증
        user = self.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="이메일/사용자명 또는 비밀번호가 올바르지 않습니다."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail="비활성화된 계정입니다."
            )

        # 2. 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        self.db.commit()

        # 3. 토큰 생성
        token_data = {
            "sub": str(user.id),       # 사용자 ID (문자열)
            "username": user.username,
            "email": user.email,
            "role": user.role.value    # "admin", "user" 등
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def authenticate_user(self, username: str, password: str) -> User | None:
        """
        사용자 인증

        이메일 또는 사용자명으로 로그인 가능
        """
        # 이메일 또는 사용자명으로 찾기
        user = self.db.query(User).filter(
            (User.email == username) | (User.username == username)
        ).first()

        if not user:
            return None

        # 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            return None

        return user
```

### 인증 의존성 (dependencies/auth.py)

```python
# app/dependencies/auth.py

from fastapi.security import OAuth2PasswordBearer

# 토큰 추출 스킴
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 반환

    Authorization 헤더에서 토큰을 추출하고,
    검증 후 사용자를 반환합니다.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 토큰 디코딩
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # 토큰 타입 확인 (access만 허용)
    if payload.get("type") != "access":
        raise credentials_exception

    # 사용자 ID 추출
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user
```

## 4. 토큰 페이로드 구조

### 이 프로젝트의 토큰 페이로드

```python
# Access Token 페이로드
{
    "sub": "123",              # 사용자 ID (subject)
    "username": "john",
    "email": "john@example.com",
    "role": "user",            # 사용자 역할
    "exp": 1704067200,         # 만료 시간 (Unix timestamp)
    "type": "access"           # 토큰 타입
}

# Refresh Token 페이로드
{
    "sub": "123",
    "username": "john",
    "email": "john@example.com",
    "role": "user",
    "exp": 1704672000,         # 7일 후
    "type": "refresh"
}
```

### 표준 클레임 (Claims)

```
┌────────────┬───────────────────────────────────────────────┐
│  클레임    │  설명                                         │
├────────────┼───────────────────────────────────────────────┤
│  sub       │  Subject - 주체 (사용자 ID)                   │
│  exp       │  Expiration - 만료 시간                       │
│  iat       │  Issued At - 발급 시간                        │
│  nbf       │  Not Before - 사용 시작 시간                  │
│  iss       │  Issuer - 발급자                              │
│  aud       │  Audience - 대상                              │
│  jti       │  JWT ID - 토큰 고유 ID                        │
└────────────┴───────────────────────────────────────────────┘
```

## 5. 역할 기반 접근 제어 (RBAC)

### 사용자 역할

```python
# app/models/user.py

class UserRole(str, enum.Enum):
    """사용자 역할"""
    ADMIN = "admin"          # 관리자: 모든 권한
    MODERATOR = "moderator"  # 운영자: 콘텐츠 관리
    USER = "user"            # 일반 사용자: 기본 권한
```

### 역할별 권한

```
┌─────────────────────────────────────────────────────────────┐
│                    역할별 권한                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ADMIN (관리자)                                             │
│  ├── 모든 사용자 관리 (CRUD)                                │
│  ├── 모든 게시글 관리                                       │
│  ├── 카테고리 관리                                          │
│  └── 시스템 설정                                            │
│                                                             │
│  MODERATOR (운영자)                                         │
│  ├── 게시글 수정/삭제 (모든 사용자)                         │
│  ├── 댓글 관리                                              │
│  └── 게시글 고정/숨김                                       │
│                                                             │
│  USER (일반 사용자)                                         │
│  ├── 본인 프로필 수정                                       │
│  ├── 게시글 작성                                            │
│  ├── 본인 게시글 수정/삭제                                  │
│  └── 댓글 작성                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 역할 검사 의존성

```python
# 관리자 전용
async def get_current_admin_user(
    user: User = Depends(get_current_active_user)
) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "관리자만 접근 가능합니다.")
    return user

# 동적 역할 검사
def require_role(roles: list):
    async def checker(user: User = Depends(get_current_active_user)):
        if user.role not in roles:
            raise HTTPException(403, "권한이 없습니다.")
        return user
    return checker

# 사용
@router.delete("/users/{id}")
def delete_user(
    admin: User = Depends(get_current_admin_user)  # 관리자만
):
    ...

@router.put("/posts/{id}/pin")
def pin_post(
    user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    ...
```

## 6. 클라이언트 사용

### 로그인

```javascript
// 로그인 요청
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password123'
  })
});

const { access_token, refresh_token } = await response.json();

// 토큰 저장
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### API 호출

```javascript
// 인증이 필요한 API 호출
const token = localStorage.getItem('access_token');

const response = await fetch('/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 토큰 갱신

```javascript
// 401 에러 시 토큰 갱신
async function refreshTokens() {
  const refresh_token = localStorage.getItem('refresh_token');

  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });

  if (response.ok) {
    const { access_token, refresh_token: new_refresh } = await response.json();
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', new_refresh);
    return true;
  }

  // 갱신 실패 → 로그아웃
  localStorage.clear();
  window.location.href = '/login';
  return false;
}
```

## 7. 보안 고려사항

```
┌─────────────────────────────────────────────────────────────┐
│                    보안 체크리스트                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ 시크릿 키를 환경 변수로 관리                            │
│     - .env 파일에 저장                                      │
│     - 프로덕션에서 강력한 키 사용                           │
│                                                             │
│  ✅ 토큰 만료 시간 적절히 설정                              │
│     - Access: 30분                                         │
│     - Refresh: 7일                                          │
│                                                             │
│  ✅ HTTPS 사용                                              │
│     - 토큰 탈취 방지                                        │
│                                                             │
│  ✅ 토큰 타입 검증                                          │
│     - access/refresh 구분                                   │
│     - refresh로 API 호출 방지                               │
│                                                             │
│  ✅ 비밀번호 해싱                                           │
│     - bcrypt 사용                                           │
│     - 평문 저장 금지                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 요약

| 구성 요소 | 역할 | 위치 |
|----------|------|------|
| create_access_token | 액세스 토큰 생성 | utils/security.py |
| create_refresh_token | 리프레시 토큰 생성 | utils/security.py |
| decode_token | 토큰 검증/디코딩 | utils/security.py |
| AuthService.login | 로그인 처리 | services/auth.py |
| get_current_user | 인증 의존성 | dependencies/auth.py |

## 다음 단계

다음 문서 [11-security.md](./11-security.md)에서는 비밀번호 해싱과 보안 유틸리티를 학습합니다.
