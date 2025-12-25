"""
Menu Schemas
=============

메뉴 구조 관련 Pydantic 스키마입니다.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    """메뉴 기본 스키마"""
    name: str = Field(
        ...,
        max_length=100,
        description="메뉴 이름",
        example="대시보드"
    )
    url: Optional[str] = Field(
        None,
        max_length=255,
        description="메뉴 URL",
        example="/dashboard"
    )
    icon: Optional[str] = Field(
        None,
        max_length=50,
        description="아이콘 클래스",
        example="fa-dashboard"
    )
    order: int = Field(
        default=0,
        description="정렬 순서"
    )
    required_role: Optional[str] = Field(
        None,
        description="필요한 최소 역할",
        example="admin"
    )


class MenuCreate(MenuBase):
    """메뉴 생성 스키마"""
    parent_id: Optional[int] = Field(
        None,
        description="부모 메뉴 ID"
    )


class MenuUpdate(BaseModel):
    """
    메뉴 수정 스키마

    모든 필드가 선택적입니다.
    """
    name: Optional[str] = Field(None, max_length=100, description="메뉴 이름")
    url: Optional[str] = Field(None, max_length=255, description="URL")
    icon: Optional[str] = Field(None, max_length=50, description="아이콘")
    parent_id: Optional[int] = Field(None, description="부모 메뉴 ID")
    order: Optional[int] = Field(None, description="정렬 순서")
    is_active: Optional[bool] = Field(None, description="활성화 여부")
    required_role: Optional[str] = Field(None, description="필요 역할")


class MenuResponse(MenuBase):
    """메뉴 응답 스키마"""
    id: int = Field(..., description="메뉴 ID")
    parent_id: Optional[int] = Field(None, description="부모 메뉴 ID")
    is_active: bool = Field(..., description="활성화 여부")
    created_at: datetime = Field(..., description="생성 일시")
    children: List["MenuResponse"] = Field(default_factory=list, description="하위 메뉴")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "대시보드",
                "url": "/dashboard",
                "icon": "fa-dashboard",
                "parent_id": None,
                "order": 0,
                "is_active": True,
                "required_role": None,
                "created_at": "2024-01-01T00:00:00",
                "children": []
            }
        }
    }


# 순환 참조 해결
MenuResponse.model_rebuild()


class MenuTreeResponse(BaseModel):
    """전체 메뉴 트리 응답"""
    menus: List[MenuResponse] = Field(..., description="최상위 메뉴 목록")

    model_config = {
        "json_schema_extra": {
            "example": {
                "menus": [
                    {
                        "id": 1,
                        "name": "대시보드",
                        "url": "/dashboard",
                        "icon": "fa-dashboard",
                        "children": []
                    },
                    {
                        "id": 2,
                        "name": "게시판",
                        "url": "/posts",
                        "icon": "fa-list",
                        "children": [
                            {
                                "id": 3,
                                "name": "공지사항",
                                "url": "/posts/notices",
                                "icon": "fa-bullhorn",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }
    }
