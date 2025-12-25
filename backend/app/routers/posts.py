"""
Posts Router
=============

게시판 API 엔드포인트입니다.

엔드포인트:
- GET /: 게시글 목록
- POST /: 게시글 작성
- GET /{post_id}: 게시글 상세
- PUT /{post_id}: 게시글 수정
- DELETE /{post_id}: 게시글 삭제
- GET /{post_id}/comments: 댓글 목록
- POST /{post_id}/comments: 댓글 작성
- DELETE /comments/{comment_id}: 댓글 삭제
"""

from typing import Optional, List
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    CommentCreate,
    CommentResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from app.services.post import PostService
from app.dependencies.auth import (
    get_current_active_user,
    get_optional_current_user,
    get_current_admin_user
)

router = APIRouter()


# ===========================================
# Category Endpoints
# ===========================================

@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="카테고리 목록",
    description="게시판 카테고리 목록을 조회합니다."
)
def get_categories(
    db: Session = Depends(get_db)
):
    """
    카테고리 목록 조회

    모든 활성 카테고리 목록을 반환합니다.

    Returns:
        카테고리 목록
    """
    post_service = PostService(db)
    return post_service.get_categories()


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="카테고리 생성",
    description="새로운 카테고리를 생성합니다. (관리자 전용)"
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    카테고리 생성 (관리자 전용)

    새로운 게시판 카테고리를 생성합니다.

    - **name**: 카테고리 이름
    - **slug**: URL용 슬러그 (고유)
    - **description**: 설명 (선택)

    Returns:
        생성된 카테고리
    """
    post_service = PostService(db)
    return post_service.create_category(
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description
    )


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="카테고리 수정",
    description="카테고리를 수정합니다. (관리자 전용)"
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    카테고리 수정 (관리자 전용)

    - **category_id**: 카테고리 ID
    - **name**: 새 이름 (선택)
    - **slug**: 새 슬러그 (선택)
    - **description**: 새 설명 (선택)
    - **order**: 정렬 순서 (선택)
    - **is_active**: 활성화 여부 (선택)

    Returns:
        수정된 카테고리
    """
    post_service = PostService(db)
    return post_service.update_category(
        category_id=category_id,
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description,
        order=category_data.order,
        is_active=category_data.is_active
    )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="카테고리 삭제",
    description="카테고리를 삭제합니다. (관리자 전용)"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    카테고리 삭제 (관리자 전용)

    카테고리를 삭제합니다.
    해당 카테고리에 속한 게시글들은 카테고리 없음으로 변경됩니다.

    - **category_id**: 삭제할 카테고리 ID
    """
    post_service = PostService(db)
    post_service.delete_category(category_id)


# ===========================================
# Post Endpoints
# ===========================================

@router.get(
    "/",
    response_model=PostListResponse,
    summary="게시글 목록",
    description="게시글 목록을 조회합니다."
)
def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    search: Optional[str] = Query(None, description="검색어"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    게시글 목록 조회

    페이지네이션된 게시글 목록을 반환합니다.
    검색 및 카테고리 필터링을 지원합니다.

    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지당 항목 수 (기본값: 10, 최대: 50)
    - **category_id**: 특정 카테고리만 필터링
    - **search**: 제목/내용 검색

    Returns:
        게시글 목록과 페이지네이션 정보
    """
    post_service = PostService(db)

    # 관리자는 미공개 글도 볼 수 있음
    include_unpublished = current_user and current_user.is_admin

    posts, total = post_service.get_posts(
        page=page,
        size=size,
        category_id=category_id,
        search=search,
        include_unpublished=include_unpublished
    )

    # 댓글 수 추가
    items = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "slug": post.slug,
            "view_count": post.view_count,
            "is_published": post.is_published,
            "is_pinned": post.is_pinned,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author": post.author,
            "category": post.category,
            "comment_count": post_service.get_comment_count(post.id)
        }
        items.append(post_dict)

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0
    )


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
    description="새로운 게시글을 작성합니다."
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 작성

    새로운 게시글을 작성합니다.
    로그인이 필요합니다.

    - **title**: 제목 (1-200자)
    - **content**: 내용
    - **category_id**: 카테고리 ID (선택)
    - **is_published**: 공개 여부 (기본값: true)

    Returns:
        생성된 게시글
    """
    post_service = PostService(db)
    post = post_service.create_post(post_data, current_user.id)

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "slug": post.slug,
        "view_count": post.view_count,
        "is_published": post.is_published,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": post.author,
        "category": post.category,
        "comment_count": 0
    }


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="게시글 상세",
    description="게시글 상세 정보를 조회합니다."
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    게시글 상세 조회

    특정 게시글의 상세 정보를 조회합니다.
    조회 시 조회수가 증가합니다.

    - **post_id**: 게시글 ID

    Returns:
        게시글 상세 정보
    """
    post_service = PostService(db)
    post = post_service.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 미공개 글은 작성자 또는 관리자만 조회 가능
    if not post.is_published:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )

    # 조회수 증가
    post_service.increment_view_count(post_id)

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "slug": post.slug,
        "view_count": post.view_count,
        "is_published": post.is_published,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": post.author,
        "category": post.category,
        "comment_count": post_service.get_comment_count(post_id)
    }


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="게시글 수정",
    description="게시글을 수정합니다."
)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 수정

    기존 게시글을 수정합니다.
    작성자 또는 관리자만 수정할 수 있습니다.

    - **post_id**: 게시글 ID
    - **title**: 새 제목 (선택)
    - **content**: 새 내용 (선택)
    - **category_id**: 새 카테고리 (선택)
    - **is_published**: 공개 여부 (선택)
    - **is_pinned**: 상단 고정 (선택, 관리자만)

    Returns:
        수정된 게시글
    """
    post_service = PostService(db)
    post = post_service.update_post(post_id, post_data, current_user)

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "slug": post.slug,
        "view_count": post.view_count,
        "is_published": post.is_published,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": post.author,
        "category": post.category,
        "comment_count": post_service.get_comment_count(post_id)
    }


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="게시글 삭제",
    description="게시글을 삭제합니다."
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 삭제

    게시글과 관련 댓글을 삭제합니다.
    작성자 또는 관리자만 삭제할 수 있습니다.

    - **post_id**: 삭제할 게시글 ID
    """
    post_service = PostService(db)
    post_service.delete_post(post_id, current_user)


# ===========================================
# Comment Endpoints
# ===========================================

@router.get(
    "/{post_id}/comments",
    response_model=List[CommentResponse],
    summary="댓글 목록",
    description="게시글의 댓글 목록을 조회합니다."
)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    댓글 목록 조회

    특정 게시글의 모든 댓글을 조회합니다.
    대댓글은 각 댓글의 replies 필드에 포함됩니다.

    - **post_id**: 게시글 ID

    Returns:
        댓글 목록 (대댓글 포함)
    """
    post_service = PostService(db)
    return post_service.get_comments(post_id)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 작성",
    description="게시글에 댓글을 작성합니다."
)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    댓글 작성

    게시글에 새 댓글을 작성합니다.
    대댓글은 parent_id를 지정합니다.

    - **post_id**: 게시글 ID
    - **content**: 댓글 내용
    - **parent_id**: 부모 댓글 ID (대댓글인 경우)

    Returns:
        생성된 댓글
    """
    post_service = PostService(db)
    return post_service.create_comment(post_id, comment_data, current_user.id)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="댓글 삭제",
    description="댓글을 삭제합니다."
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    댓글 삭제

    댓글을 삭제합니다 (소프트 삭제).
    작성자 또는 관리자만 삭제할 수 있습니다.

    - **comment_id**: 삭제할 댓글 ID
    """
    post_service = PostService(db)
    post_service.delete_comment(comment_id, current_user)
