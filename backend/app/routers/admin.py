"""
Admin Router
=============

관리자 전용 API 엔드포인트입니다.

엔드포인트:
- GET /users: 사용자 목록 (관리자)
- GET /users/{user_id}: 사용자 상세 (관리자)
- PUT /users/{user_id}: 사용자 수정 (관리자)
- DELETE /users/{user_id}: 사용자 삭제 (관리자)
- POST /users/{user_id}/toggle-active: 사용자 활성/비활성 토글 (관리자)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PaginatedUserResponse
from app.services.user import UserService
from app.dependencies.auth import get_current_admin_user

router = APIRouter()


# ===========================================
# Admin Users Endpoints
# ===========================================

@router.get(
    "/users",
    response_model=PaginatedUserResponse,
    summary="사용자 목록 조회",
    description="모든 사용자 목록을 조회합니다. (관리자 전용)"
)
def get_users(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    search: Optional[str] = Query(None, description="검색어 (이름, 이메일)"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 목록 조회 (관리자 전용)

    모든 사용자의 목록을 페이지네이션하여 반환합니다.

    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    - **search**: 검색어 (사용자명, 이메일로 검색)
    - **is_active**: True면 활성 사용자만, False면 비활성 사용자만

    Returns:
        페이지네이션된 사용자 목록
    """
    user_service = UserService(db)
    skip = (page - 1) * size

    users = user_service.get_users(skip=skip, limit=size, is_active=is_active, search=search)
    total = user_service.get_users_count(is_active=is_active, search=search)

    return PaginatedUserResponse(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size  # 올림 나눗셈
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="사용자 상세 조회",
    description="특정 사용자의 정보를 조회합니다. (관리자 전용)"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 상세 조회 (관리자 전용)

    특정 사용자의 상세 정보를 조회합니다.

    - **user_id**: 조회할 사용자 ID

    Returns:
        사용자 정보
    """
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="사용자 정보 수정",
    description="사용자 정보를 수정합니다. (관리자 전용)"
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 정보 수정 (관리자 전용)

    관리자가 사용자 정보를 수정합니다.

    - **user_id**: 수정할 사용자 ID
    - **email**: 새 이메일 (선택)
    - **username**: 새 사용자명 (선택)
    - **full_name**: 새 이름 (선택)
    - **is_active**: 활성 상태 (선택)
    - **role**: 역할 (선택)

    Returns:
        수정된 사용자 정보
    """
    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)


@router.delete(
    "/users/{user_id}",
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
    "/users/{user_id}/toggle-active",
    response_model=UserResponse,
    summary="사용자 활성/비활성 토글",
    description="사용자 계정의 활성 상태를 토글합니다. (관리자 전용)"
)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    사용자 활성/비활성 토글 (관리자 전용)

    사용자 계정의 활성 상태를 반전시킵니다.

    - **user_id**: 토글할 사용자 ID

    Returns:
        수정된 사용자 정보
    """
    # 자기 자신은 비활성화 불가
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신의 상태는 변경할 수 없습니다."
        )

    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    if user.is_active:
        return user_service.deactivate_user(user_id)
    else:
        return user_service.activate_user(user_id)
