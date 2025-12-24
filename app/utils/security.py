"""
Security Utilities
===================

보안 관련 유틸리티 함수들입니다.

기능:
- 비밀번호 해싱 및 검증
- JWT 토큰 생성 및 검증
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# 비밀번호 해싱 컨텍스트
# bcrypt 알고리즘 사용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시합니다.

    bcrypt 알고리즘을 사용하여 비밀번호를 안전하게 해시합니다.

    Args:
        password: 원본 비밀번호

    Returns:
        str: 해시된 비밀번호

    Example:
        ```python
        hashed = get_password_hash("mypassword123")
        # '$2b$12$...'
        ```
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호를 검증합니다.

    입력된 비밀번호가 해시된 비밀번호와 일치하는지 확인합니다.

    Args:
        plain_password: 검증할 원본 비밀번호
        hashed_password: 저장된 해시 비밀번호

    Returns:
        bool: 일치 여부

    Example:
        ```python
        is_valid = verify_password("mypassword123", hashed)
        # True
        ```
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰을 생성합니다.

    JWT 형식의 액세스 토큰을 생성합니다.
    기본 만료 시간은 설정 파일에서 가져옵니다.

    Args:
        data: 토큰에 포함할 데이터 (user_id, username 등)
        expires_delta: 만료 시간 (기본값: 설정 파일의 값)

    Returns:
        str: 인코딩된 JWT 토큰

    Example:
        ```python
        token = create_access_token(
            data={"sub": user.id, "username": user.username}
        )
        # 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        ```
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    리프레시 토큰을 생성합니다.

    액세스 토큰보다 긴 만료 시간을 가지며,
    액세스 토큰 갱신에 사용됩니다.

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (기본값: 7일)

    Returns:
        str: 인코딩된 JWT 리프레시 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰을 디코딩합니다.

    토큰이 유효하면 페이로드를 반환하고,
    만료되었거나 유효하지 않으면 None을 반환합니다.

    Args:
        token: 디코딩할 JWT 토큰

    Returns:
        Optional[Dict]: 디코딩된 페이로드 또는 None

    Example:
        ```python
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")
        ```
    """
    try:
        print(f"[DEBUG decode_token] Using secret: {settings.jwt_secret_key[:10]}...")
        print(f"[DEBUG decode_token] Using algorithm: {settings.jwt_algorithm}")
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        print(f"[DEBUG decode_token] JWTError: {e}")
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    토큰 타입을 검증합니다.

    Args:
        token: 검증할 토큰
        expected_type: 예상 타입 ("access" 또는 "refresh")

    Returns:
        bool: 타입 일치 여부
    """
    payload = decode_token(token)
    if payload is None:
        return False
    return payload.get("type") == expected_type
