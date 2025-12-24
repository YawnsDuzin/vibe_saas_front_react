"""
Authentication Dependencies
============================

인증 관련 종속성 함수들입니다.

FastAPI의 Depends() 시스템을 활용하여
라우트에서 쉽게 인증을 적용할 수 있습니다.

Example:
    ```python
    @router.get("/me")
    def get_me(user: User = Depends(get_current_user)):
        return user
    ```
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_token

# OAuth2 스킴 정의
# tokenUrl은 토큰을 발급받는 엔드포인트를 지정합니다
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 선택적 OAuth2 (인증이 필수가 아닌 경우)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자를 반환합니다.

    JWT 토큰을 검증하고 해당 사용자를 데이터베이스에서 조회합니다.
    토큰이 유효하지 않거나 사용자를 찾을 수 없으면 401 에러를 발생시킵니다.

    Args:
        token: JWT 액세스 토큰
        db: 데이터베이스 세션

    Returns:
        User: 인증된 사용자 객체

    Raises:
        HTTPException: 인증 실패 시 401 에러

    Example:
        ```python
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return {"username": user.username}
        ```
    """
    print(f"[DEBUG] Received token: {token[:50] if token else 'None'}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 토큰 디코딩
    payload = decode_token(token)
    print(f"[DEBUG] Decoded payload: {payload}")
    if payload is None:
        print("[DEBUG] Token decode failed")
        raise credentials_exception

    # 토큰 타입 확인
    if payload.get("type") != "access":
        print(f"[DEBUG] Invalid token type: {payload.get('type')}")
        raise credentials_exception

    # 사용자 ID 추출 (sub는 문자열이므로 정수로 변환)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    user_id = int(user_id_str)

    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    활성화된 현재 사용자를 반환합니다.

    get_current_user에 추가로 계정 활성화 상태를 확인합니다.
    비활성화된 계정은 접근이 거부됩니다.

    Args:
        current_user: 인증된 사용자

    Returns:
        User: 활성화된 사용자

    Raises:
        HTTPException: 계정이 비활성화된 경우 400 에러

    Example:
        ```python
        @router.post("/posts")
        def create_post(
            post: PostCreate,
            user: User = Depends(get_current_active_user)
        ):
            # 활성 사용자만 글 작성 가능
            ...
        ```
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다."
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    관리자 권한을 가진 사용자를 반환합니다.

    관리자(ADMIN) 역할을 가진 사용자만 접근을 허용합니다.

    Args:
        current_user: 활성화된 인증 사용자

    Returns:
        User: 관리자 사용자

    Raises:
        HTTPException: 관리자가 아닌 경우 403 에러

    Example:
        ```python
        @router.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            admin: User = Depends(get_current_admin_user)
        ):
            # 관리자만 사용자 삭제 가능
            ...
        ```
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다. 관리자만 접근할 수 있습니다."
        )
    return current_user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적으로 현재 사용자를 반환합니다.

    인증이 필수가 아닌 엔드포인트에서 사용합니다.
    토큰이 없거나 유효하지 않으면 None을 반환합니다.

    Args:
        token: JWT 토큰 (선택)
        db: 데이터베이스 세션

    Returns:
        Optional[User]: 사용자 또는 None

    Example:
        ```python
        @router.get("/posts")
        def get_posts(user: Optional[User] = Depends(get_optional_current_user)):
            # 로그인하지 않아도 접근 가능
            # 로그인한 경우 user 객체가 제공됨
            ...
        ```
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


def require_role(required_roles: list):
    """
    특정 역할을 요구하는 종속성을 생성합니다.

    Args:
        required_roles: 허용되는 역할 목록

    Returns:
        종속성 함수

    Example:
        ```python
        @router.get("/admin")
        def admin_only(
            user: User = Depends(require_role([UserRole.ADMIN]))
        ):
            ...

        @router.get("/moderator")
        def moderator_or_admin(
            user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
        ):
            ...
        ```
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
