"""
Users Router
=============

사용자 관리 API 엔드포인트입니다.

엔드포인트:
- GET /: 사용자 목록 (관리자)
- GET /{user_id}: 사용자 상세
- PUT /{user_id}: 사용자 수정
- DELETE /{user_id}: 사용자 삭제 (관리자)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService
from app.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="사용자 목록 조회",
    description="모든 사용자 목록을 조회합니다. (관리자 전용)"
)
def get_users(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=100, description="최대 조회 수"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 목록 조회 (관리자 전용)

    모든 사용자의 목록을 페이지네이션하여 반환합니다.

    - **skip**: 건너뛸 레코드 수 (기본값: 0)
    - **limit**: 최대 조회 수 (기본값: 100, 최대: 100)
    - **is_active**: True면 활성 사용자만, False면 비활성 사용자만

    Returns:
        사용자 목록
    """
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit, is_active=is_active)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 상세 조회",
    description="특정 사용자의 정보를 조회합니다."
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자 상세 조회

    특정 사용자의 상세 정보를 조회합니다.
    본인 또는 관리자만 조회할 수 있습니다.

    - **user_id**: 조회할 사용자 ID

    Returns:
        사용자 정보
    """
    # 본인 또는 관리자만 조회 가능
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
    summary="사용자 정보 수정",
    description="사용자 정보를 수정합니다."
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자 정보 수정

    사용자 정보를 수정합니다.
    본인만 수정할 수 있습니다 (관리자 제외).

    - **user_id**: 수정할 사용자 ID
    - **email**: 새 이메일 (선택)
    - **username**: 새 사용자명 (선택)
    - **full_name**: 새 이름 (선택)
    - **password**: 새 비밀번호 (선택)

    Returns:
        수정된 사용자 정보
    """
    # 본인만 수정 가능
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 수정할 권한이 없습니다."
        )

    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    description="사용자를 삭제합니다. (관리자 전용)"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 삭제 (관리자 전용)

    사용자 계정을 완전히 삭제합니다.
    관련된 게시글, 댓글 등도 함께 삭제됩니다.

    - **user_id**: 삭제할 사용자 ID

    주의: 이 작업은 되돌릴 수 없습니다.
    """
    # 자기 자신은 삭제 불가
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 삭제할 수 없습니다."
        )

    user_service = UserService(db)
    user_service.delete_user(user_id)


@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="사용자 비활성화",
    description="사용자 계정을 비활성화합니다."
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    사용자 비활성화

    사용자 계정을 비활성화합니다 (Soft Delete).
    본인 또는 관리자가 수행할 수 있습니다.

    - **user_id**: 비활성화할 사용자 ID

    Returns:
        비활성화된 사용자 정보
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다."
        )

    user_service = UserService(db)
    return user_service.deactivate_user(user_id)
