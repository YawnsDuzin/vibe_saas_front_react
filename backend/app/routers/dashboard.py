"""
Dashboard Router
=================

대시보드 API 엔드포인트입니다.

엔드포인트:
- GET /: 대시보드 통계
- GET /recent-posts: 최근 게시글
- GET /recent-users: 최근 가입자 (관리자)
"""

from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.post import Post, Comment
from app.schemas.post import PostResponse
from app.schemas.user import UserResponse
from app.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user
)

router = APIRouter()


class DashboardStats(BaseModel):
    """대시보드 통계 응답 스키마"""
    total_posts: int = Field(..., description="전체 게시글 수")
    total_users: int = Field(..., description="전체 사용자 수")
    total_comments: int = Field(..., description="전체 댓글 수")
    posts_today: int = Field(..., description="오늘 작성된 게시글")
    users_today: int = Field(..., description="오늘 가입한 사용자")
    my_posts: int = Field(..., description="내 게시글 수")
    my_comments: int = Field(..., description="내 댓글 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_posts": 150,
                "total_users": 50,
                "total_comments": 320,
                "posts_today": 5,
                "users_today": 2,
                "my_posts": 10,
                "my_comments": 25
            }
        }
    }


class AdminDashboardStats(DashboardStats):
    """관리자 대시보드 통계 응답 스키마"""
    active_users: int = Field(..., description="활성 사용자 수")
    inactive_users: int = Field(..., description="비활성 사용자 수")
    unpublished_posts: int = Field(..., description="미공개 게시글 수")


class RecentPostItem(BaseModel):
    """최근 게시글 항목"""
    id: int
    title: str
    author_username: str
    view_count: int
    comment_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get(
    "/",
    response_model=DashboardStats,
    summary="대시보드 통계",
    description="사용자 대시보드 통계 정보를 조회합니다."
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    대시보드 통계 조회

    현재 사용자를 위한 대시보드 통계를 반환합니다.

    Returns:
        - total_posts: 전체 공개 게시글 수
        - total_users: 전체 활성 사용자 수
        - total_comments: 전체 댓글 수
        - posts_today: 오늘 작성된 게시글 수
        - users_today: 오늘 가입한 사용자 수
        - my_posts: 내가 작성한 게시글 수
        - my_comments: 내가 작성한 댓글 수
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 전체 통계
    total_posts = db.query(func.count(Post.id)).filter(
        Post.is_published == True
    ).scalar()

    total_users = db.query(func.count(User.id)).filter(
        User.is_active == True
    ).scalar()

    total_comments = db.query(func.count(Comment.id)).filter(
        Comment.is_active == True
    ).scalar()

    # 오늘 통계
    posts_today = db.query(func.count(Post.id)).filter(
        Post.created_at >= today,
        Post.is_published == True
    ).scalar()

    users_today = db.query(func.count(User.id)).filter(
        User.created_at >= today
    ).scalar()

    # 내 통계
    my_posts = db.query(func.count(Post.id)).filter(
        Post.author_id == current_user.id
    ).scalar()

    my_comments = db.query(func.count(Comment.id)).filter(
        Comment.author_id == current_user.id,
        Comment.is_active == True
    ).scalar()

    return DashboardStats(
        total_posts=total_posts,
        total_users=total_users,
        total_comments=total_comments,
        posts_today=posts_today,
        users_today=users_today,
        my_posts=my_posts,
        my_comments=my_comments
    )


@router.get(
    "/admin",
    response_model=AdminDashboardStats,
    summary="관리자 대시보드",
    description="관리자용 상세 통계를 조회합니다. (관리자 전용)"
)
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    관리자 대시보드 통계 조회 (관리자 전용)

    일반 통계에 추가로 관리자용 상세 정보를 반환합니다.

    Returns:
        기본 통계 + 활성/비활성 사용자 수, 미공개 게시글 수
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 기본 통계
    total_posts = db.query(func.count(Post.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    total_comments = db.query(func.count(Comment.id)).scalar()

    posts_today = db.query(func.count(Post.id)).filter(
        Post.created_at >= today
    ).scalar()

    users_today = db.query(func.count(User.id)).filter(
        User.created_at >= today
    ).scalar()

    my_posts = db.query(func.count(Post.id)).filter(
        Post.author_id == current_user.id
    ).scalar()

    my_comments = db.query(func.count(Comment.id)).filter(
        Comment.author_id == current_user.id
    ).scalar()

    # 관리자 전용 통계
    active_users = db.query(func.count(User.id)).filter(
        User.is_active == True
    ).scalar()

    inactive_users = db.query(func.count(User.id)).filter(
        User.is_active == False
    ).scalar()

    unpublished_posts = db.query(func.count(Post.id)).filter(
        Post.is_published == False
    ).scalar()

    return AdminDashboardStats(
        total_posts=total_posts,
        total_users=total_users,
        total_comments=total_comments,
        posts_today=posts_today,
        users_today=users_today,
        my_posts=my_posts,
        my_comments=my_comments,
        active_users=active_users,
        inactive_users=inactive_users,
        unpublished_posts=unpublished_posts
    )


@router.get(
    "/recent-posts",
    response_model=List[RecentPostItem],
    summary="최근 게시글",
    description="최근 작성된 게시글 목록을 조회합니다."
)
def get_recent_posts(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    최근 게시글 조회

    최근 작성된 게시글 목록을 반환합니다.

    - **limit**: 조회할 개수 (기본값: 5)

    Returns:
        최근 게시글 목록
    """
    posts = db.query(Post).filter(
        Post.is_published == True
    ).order_by(Post.created_at.desc()).limit(limit).all()

    result = []
    for post in posts:
        comment_count = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post.id,
            Comment.is_active == True
        ).scalar()

        result.append(RecentPostItem(
            id=post.id,
            title=post.title,
            author_username=post.author.username,
            view_count=post.view_count,
            comment_count=comment_count,
            created_at=post.created_at
        ))

    return result


@router.get(
    "/recent-users",
    response_model=List[UserResponse],
    summary="최근 가입자",
    description="최근 가입한 사용자 목록을 조회합니다. (관리자 전용)"
)
def get_recent_users(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    최근 가입자 조회 (관리자 전용)

    최근 가입한 사용자 목록을 반환합니다.

    - **limit**: 조회할 개수 (기본값: 5)

    Returns:
        최근 가입자 목록
    """
    users = db.query(User).order_by(
        User.created_at.desc()
    ).limit(limit).all()

    return users
