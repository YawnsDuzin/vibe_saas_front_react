"""
Theme Schemas
==============

테마 설정 관련 Pydantic 스키마입니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ThemeBase(BaseModel):
    """테마 기본 스키마"""
    theme_name: str = Field(
        default="light",
        description="테마 이름",
        example="dark"
    )
    sidebar_collapsed: bool = Field(
        default=False,
        description="사이드바 접힘 상태"
    )


class ThemeCreate(ThemeBase):
    """테마 생성 스키마"""
    custom_settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="커스텀 설정"
    )


class ThemeUpdate(BaseModel):
    """
    테마 수정 스키마

    모든 필드가 선택적입니다.
    """
    theme_name: Optional[str] = Field(None, description="테마 이름")
    sidebar_collapsed: Optional[bool] = Field(None, description="사이드바 접힘 상태")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="커스텀 설정")


class ThemeResponse(ThemeBase):
    """테마 응답 스키마"""
    id: int = Field(..., description="테마 설정 ID")
    user_id: int = Field(..., description="사용자 ID")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="커스텀 설정")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 1,
                "theme_name": "dark",
                "sidebar_collapsed": False,
                "custom_settings": {
                    "font_size": "medium",
                    "language": "ko"
                },
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00"
            }
        }
    }


class AvailableThemesResponse(BaseModel):
    """사용 가능한 테마 목록 응답"""
    themes: list[str] = Field(..., description="사용 가능한 테마 목록")
    default_theme: str = Field(..., description="기본 테마")

    model_config = {
        "json_schema_extra": {
            "example": {
                "themes": ["light", "dark", "blue", "green"],
                "default_theme": "light"
            }
        }
    }
