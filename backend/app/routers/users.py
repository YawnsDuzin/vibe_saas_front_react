"""
Users Router
=============

사용자 개인 정보 API 엔드포인트입니다.

엔드포인트:
- GET /me: 내 정보 조회
- PUT /me: 내 정보 수정
- POST /me/deactivate: 내 계정 비활성화
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService
from app.dependencies.auth import get_current_active_user

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다."
)
def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    내 정보 조회

    현재 로그인한 사용자의 정보를 반환합니다.

    Returns:
        현재 사용자 정보
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="내 정보 수정",
    description="현재 로그인한 사용자의 정보를 수정합니다."
)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    내 정보 수정

    현재 로그인한 사용자의 정보를 수정합니다.

    - **email**: 새 이메일 (선택)
    - **username**: 새 사용자명 (선택)
    - **full_name**: 새 이름 (선택)
    - **password**: 새 비밀번호 (선택)

    Returns:
        수정된 사용자 정보
    """
    user_service = UserService(db)
    return user_service.update_user(current_user.id, user_data)


@router.post(
    "/me/deactivate",
    response_model=UserResponse,
    summary="내 계정 비활성화",
    description="현재 로그인한 사용자의 계정을 비활성화합니다."
)
def deactivate_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    내 계정 비활성화

    현재 로그인한 사용자의 계정을 비활성화합니다 (Soft Delete).
    비활성화 후에는 로그인이 불가능합니다.

    Returns:
        비활성화된 사용자 정보
    """
    user_service = UserService(db)
    return user_service.deactivate_user(current_user.id)


# 기존 API 호환성을 위한 엔드포인트 (deprecated)
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 상세 조회 (deprecated)",
    description="특정 사용자의 정보를 조회합니다. /users/me 사용을 권장합니다.",
    deprecated=True
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자 상세 조회 (deprecated)

    본인 정보만 조회 가능합니다.
    /users/me 엔드포인트 사용을 권장합니다.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 조회할 권한이 없습니다."
        )

    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 수정 (deprecated)",
    description="사용자 정보를 수정합니다. /users/me 사용을 권장합니다.",
    deprecated=True
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자 정보 수정 (deprecated)

    본인 정보만 수정 가능합니다.
    /users/me 엔드포인트 사용을 권장합니다.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 수정할 권한이 없습니다."
        )

    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)
