"""
Menu Router
============

메뉴 구조 API 엔드포인트입니다.

엔드포인트:
- GET /: 메뉴 트리 조회
- POST /: 메뉴 생성 (관리자)
- PUT /{menu_id}: 메뉴 수정 (관리자)
- DELETE /{menu_id}: 메뉴 삭제 (관리자)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse
from app.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user,
    get_optional_current_user
)

router = APIRouter()


def get_menu_tree(
    db: Session,
    user: Optional[User] = None
) -> List[MenuResponse]:
    """
    메뉴 트리를 구성합니다.

    사용자의 역할에 따라 접근 가능한 메뉴만 반환합니다.
    """
    # 최상위 메뉴만 조회
    menus = db.query(Menu).filter(
        Menu.parent_id == None,
        Menu.is_active == True
    ).order_by(Menu.order).all()

    result = []
    for menu in menus:
        # 역할 기반 필터링
        if menu.required_role:
            if not user:
                continue
            if menu.required_role == "admin" and user.role != UserRole.ADMIN:
                continue
            if menu.required_role == "moderator" and user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
                continue

        menu_dict = build_menu_dict(menu, user)
        result.append(menu_dict)

    return result


def build_menu_dict(menu: Menu, user: Optional[User] = None) -> dict:
    """
    메뉴를 딕셔너리로 변환합니다 (재귀).
    """
    children = []
    for child in sorted(menu.children, key=lambda x: x.order):
        if not child.is_active:
            continue

        # 역할 기반 필터링
        if child.required_role:
            if not user:
                continue
            if child.required_role == "admin" and user.role != UserRole.ADMIN:
                continue
            if child.required_role == "moderator" and user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
                continue

        children.append(build_menu_dict(child, user))

    return {
        "id": menu.id,
        "name": menu.name,
        "url": menu.url,
        "icon": menu.icon,
        "parent_id": menu.parent_id,
        "order": menu.order,
        "is_active": menu.is_active,
        "required_role": menu.required_role,
        "created_at": menu.created_at,
        "children": children
    }


@router.get(
    "/",
    response_model=MenuTreeResponse,
    summary="메뉴 트리 조회",
    description="전체 메뉴 구조를 트리 형태로 조회합니다."
)
def get_menus(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    메뉴 트리 조회

    사용자의 역할에 따라 접근 가능한 메뉴를 트리 구조로 반환합니다.
    로그인하지 않은 경우 공개 메뉴만 반환됩니다.

    Returns:
        계층적 메뉴 트리
    """
    menu_tree = get_menu_tree(db, current_user)
    return MenuTreeResponse(menus=menu_tree)


@router.post(
    "/",
    response_model=MenuResponse,
    status_code=status.HTTP_201_CREATED,
    summary="메뉴 생성",
    description="새로운 메뉴를 생성합니다. (관리자 전용)"
)
def create_menu(
    menu_data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    메뉴 생성 (관리자 전용)

    새로운 메뉴 항목을 생성합니다.
    하위 메뉴인 경우 parent_id를 지정합니다.

    - **name**: 메뉴 이름
    - **url**: 메뉴 URL
    - **icon**: 아이콘 클래스 (선택)
    - **parent_id**: 부모 메뉴 ID (선택)
    - **order**: 정렬 순서
    - **required_role**: 필요 역할 (선택)

    Returns:
        생성된 메뉴
    """
    # 부모 메뉴 확인
    if menu_data.parent_id:
        parent = db.query(Menu).filter(Menu.id == menu_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="부모 메뉴를 찾을 수 없습니다."
            )

    menu = Menu(
        name=menu_data.name,
        url=menu_data.url,
        icon=menu_data.icon,
        parent_id=menu_data.parent_id,
        order=menu_data.order,
        required_role=menu_data.required_role
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)

    return build_menu_dict(menu)


@router.put(
    "/{menu_id}",
    response_model=MenuResponse,
    summary="메뉴 수정",
    description="메뉴를 수정합니다. (관리자 전용)"
)
def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    메뉴 수정 (관리자 전용)

    기존 메뉴를 수정합니다.

    - **menu_id**: 수정할 메뉴 ID
    - **name**: 새 이름 (선택)
    - **url**: 새 URL (선택)
    - **icon**: 새 아이콘 (선택)
    - **parent_id**: 새 부모 (선택)
    - **order**: 새 순서 (선택)
    - **is_active**: 활성화 여부 (선택)
    - **required_role**: 필요 역할 (선택)

    Returns:
        수정된 메뉴
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메뉴를 찾을 수 없습니다."
        )

    # 부모 메뉴 변경 시 확인
    if menu_data.parent_id is not None:
        if menu_data.parent_id == menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자기 자신을 부모로 지정할 수 없습니다."
            )
        if menu_data.parent_id != 0:  # 0은 최상위로 이동
            parent = db.query(Menu).filter(Menu.id == menu_data.parent_id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="부모 메뉴를 찾을 수 없습니다."
                )
            menu.parent_id = menu_data.parent_id
        else:
            menu.parent_id = None

    # 필드 업데이트
    if menu_data.name is not None:
        menu.name = menu_data.name
    if menu_data.url is not None:
        menu.url = menu_data.url
    if menu_data.icon is not None:
        menu.icon = menu_data.icon
    if menu_data.order is not None:
        menu.order = menu_data.order
    if menu_data.is_active is not None:
        menu.is_active = menu_data.is_active
    if menu_data.required_role is not None:
        menu.required_role = menu_data.required_role if menu_data.required_role else None

    db.commit()
    db.refresh(menu)

    return build_menu_dict(menu)


@router.delete(
    "/{menu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="메뉴 삭제",
    description="메뉴를 삭제합니다. (관리자 전용)"
)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    메뉴 삭제 (관리자 전용)

    메뉴를 삭제합니다.
    하위 메뉴가 있는 경우에도 함께 삭제됩니다.

    - **menu_id**: 삭제할 메뉴 ID
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메뉴를 찾을 수 없습니다."
        )

    db.delete(menu)
    db.commit()


@router.post(
    "/init-default",
    response_model=MenuTreeResponse,
    summary="기본 메뉴 초기화",
    description="기본 메뉴 구조를 생성합니다. (관리자 전용)"
)
def init_default_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    기본 메뉴 초기화 (관리자 전용)

    기본 메뉴 구조를 생성합니다.
    이미 메뉴가 있는 경우 추가됩니다.

    Returns:
        생성된 메뉴 트리
    """
    default_menus = [
        {"name": "대시보드", "url": "/dashboard", "icon": "fa-dashboard", "order": 0},
        {"name": "게시판", "url": "/posts", "icon": "fa-list", "order": 1},
        {"name": "내 정보", "url": "/profile", "icon": "fa-user", "order": 2},
        {"name": "설정", "url": "/settings", "icon": "fa-cog", "order": 3},
        {"name": "관리자", "url": "/admin", "icon": "fa-shield", "order": 4, "required_role": "admin"},
    ]

    admin_submenus = [
        {"name": "사용자 관리", "url": "/admin/users", "icon": "fa-users", "order": 0},
        {"name": "게시글 관리", "url": "/admin/posts", "icon": "fa-file", "order": 1},
        {"name": "메뉴 관리", "url": "/admin/menus", "icon": "fa-bars", "order": 2},
    ]

    # 기본 메뉴 생성
    admin_menu = None
    for menu_data in default_menus:
        menu = Menu(**menu_data)
        db.add(menu)
        db.flush()
        if menu_data["name"] == "관리자":
            admin_menu = menu

    # 관리자 하위 메뉴 생성
    if admin_menu:
        for submenu_data in admin_submenus:
            submenu = Menu(
                **submenu_data,
                parent_id=admin_menu.id,
                required_role="admin"
            )
            db.add(submenu)

    db.commit()

    # 생성된 메뉴 트리 반환
    menu_tree = get_menu_tree(db, current_user)
    return MenuTreeResponse(menus=menu_tree)
