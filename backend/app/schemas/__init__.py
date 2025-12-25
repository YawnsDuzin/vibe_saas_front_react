"""
Pydantic Schemas
=================

API 요청/응답을 검증하고 직렬화하는 Pydantic 스키마 패키지입니다.

포함된 스키마:
- User: 사용자 관련 스키마
- Post: 게시글 관련 스키마
- Comment: 댓글 관련 스키마
- Theme: 테마 설정 스키마
- Menu: 메뉴 구조 스키마
- Auth: 인증 관련 스키마
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    CategoryCreate,
    CategoryResponse,
    CommentCreate,
    CommentResponse,
)
from app.schemas.theme import (
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse,
)
from app.schemas.menu import (
    MenuCreate,
    MenuUpdate,
    MenuResponse,
)
from app.schemas.auth import (
    Token,
    TokenData,
    LoginRequest,
    RefreshTokenRequest,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Post
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostListResponse",
    "CategoryCreate",
    "CategoryResponse",
    "CommentCreate",
    "CommentResponse",
    # Theme
    "ThemeCreate",
    "ThemeUpdate",
    "ThemeResponse",
    # Menu
    "MenuCreate",
    "MenuUpdate",
    "MenuResponse",
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
]
