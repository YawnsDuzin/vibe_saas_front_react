"""
Post & Comment Schemas
=======================

게시글 및 댓글 관련 Pydantic 스키마입니다.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ===========================================
# Category Schemas
# ===========================================

class CategoryBase(BaseModel):
    """카테고리 기본 스키마"""
    name: str = Field(..., max_length=50, description="카테고리 이름", example="공지사항")
    slug: str = Field(..., max_length=50, description="URL용 슬러그", example="notices")
    description: Optional[str] = Field(None, max_length=255, description="설명")
    order: int = Field(default=0, description="정렬 순서")


class CategoryCreate(CategoryBase):
    """카테고리 생성 스키마"""
    pass


class CategoryResponse(CategoryBase):
    """카테고리 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================
# Post Schemas
# ===========================================

class PostBase(BaseModel):
    """게시글 기본 스키마"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="게시글 제목",
        example="FastAPI 시작하기"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="게시글 내용",
        example="FastAPI는 현대적인 Python 웹 프레임워크입니다."
    )
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    is_published: bool = Field(default=True, description="공개 여부")


class PostCreate(PostBase):
    """
    게시글 생성 스키마

    author_id는 인증된 사용자에서 자동으로 설정됩니다.
    """
    pass


class PostUpdate(BaseModel):
    """
    게시글 수정 스키마

    부분 업데이트를 지원합니다.
    """
    title: Optional[str] = Field(None, max_length=200, description="제목")
    content: Optional[str] = Field(None, description="내용")
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    is_published: Optional[bool] = Field(None, description="공개 여부")
    is_pinned: Optional[bool] = Field(None, description="상단 고정")


class AuthorInfo(BaseModel):
    """작성자 요약 정보"""
    id: int
    username: str
    full_name: Optional[str] = None

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    """
    게시글 상세 응답 스키마

    단일 게시글 조회 시 사용됩니다.
    """
    id: int = Field(..., description="게시글 ID")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    slug: str = Field(..., description="URL 슬러그")
    view_count: int = Field(..., description="조회수")
    is_published: bool = Field(..., description="공개 여부")
    is_pinned: bool = Field(..., description="상단 고정")
    created_at: datetime = Field(..., description="작성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    author: AuthorInfo = Field(..., description="작성자 정보")
    category: Optional[CategoryResponse] = Field(None, description="카테고리")
    comment_count: int = Field(default=0, description="댓글 수")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "FastAPI 시작하기",
                "content": "FastAPI는 현대적인 Python 웹 프레임워크입니다.",
                "slug": "fastapi-시작하기-1",
                "view_count": 100,
                "is_published": True,
                "is_pinned": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "author": {
                    "id": 1,
                    "username": "admin",
                    "full_name": "Admin User"
                },
                "category": {
                    "id": 1,
                    "name": "공지사항",
                    "slug": "notices"
                },
                "comment_count": 5
            }
        }
    }


class PostListResponse(BaseModel):
    """
    게시글 목록 응답 스키마

    페이지네이션 정보와 함께 게시글 목록을 반환합니다.
    """
    items: List[PostResponse] = Field(..., description="게시글 목록")
    total: int = Field(..., description="전체 게시글 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지당 항목 수")
    pages: int = Field(..., description="전체 페이지 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 10,
                "pages": 10
            }
        }
    }


# ===========================================
# Comment Schemas
# ===========================================

class CommentBase(BaseModel):
    """댓글 기본 스키마"""
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="댓글 내용",
        example="좋은 글 감사합니다!"
    )


class CommentCreate(CommentBase):
    """
    댓글 생성 스키마

    대댓글인 경우 parent_id를 지정합니다.
    """
    parent_id: Optional[int] = Field(None, description="부모 댓글 ID (대댓글인 경우)")


class CommentUpdate(BaseModel):
    """댓글 수정 스키마"""
    content: str = Field(..., min_length=1, max_length=1000, description="댓글 내용")


class CommentResponse(BaseModel):
    """
    댓글 응답 스키마

    대댓글은 replies 필드에 포함됩니다.
    """
    id: int = Field(..., description="댓글 ID")
    content: str = Field(..., description="내용")
    author: AuthorInfo = Field(..., description="작성자")
    post_id: int = Field(..., description="게시글 ID")
    parent_id: Optional[int] = Field(None, description="부모 댓글 ID")
    is_active: bool = Field(..., description="활성화 상태")
    created_at: datetime = Field(..., description="작성 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")
    replies: List["CommentResponse"] = Field(default_factory=list, description="대댓글")

    model_config = {"from_attributes": True}


# 순환 참조 해결
CommentResponse.model_rebuild()
