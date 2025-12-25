"""
Post Service
=============

게시글 관련 비즈니스 로직을 처리하는 서비스입니다.
"""

from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from app.models.post import Post, Comment, Category
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, CommentCreate
from app.utils.helpers import generate_slug


class PostService:
    """
    게시글 서비스 클래스

    게시글 CRUD, 댓글 관리 등의 비즈니스 로직을 처리합니다.
    """

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db

    # ===========================================
    # Category Methods
    # ===========================================

    def get_categories(self, include_inactive: bool = False) -> List[Category]:
        """
        카테고리 목록을 조회합니다.

        Args:
            include_inactive: 비활성 카테고리 포함 여부

        Returns:
            List[Category]: 카테고리 목록
        """
        query = self.db.query(Category)

        if not include_inactive:
            query = query.filter(Category.is_active == True)

        return query.order_by(Category.order).all()

    def create_category(self, name: str, slug: str, description: str = None) -> Category:
        """
        새 카테고리를 생성합니다.

        Args:
            name: 카테고리 이름
            slug: URL 슬러그
            description: 설명

        Returns:
            Category: 생성된 카테고리
        """
        # 슬러그 중복 확인
        if self.db.query(Category).filter(Category.slug == slug).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 슬러그입니다."
            )

        category = Category(
            name=name,
            slug=slug,
            description=description
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    # ===========================================
    # Post Methods
    # ===========================================

    def get_post(self, post_id: int) -> Optional[Post]:
        """
        ID로 게시글을 조회합니다.

        Args:
            post_id: 게시글 ID

        Returns:
            Optional[Post]: 게시글 또는 None
        """
        return self.db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category)
        ).filter(Post.id == post_id).first()

    def get_post_by_slug(self, slug: str) -> Optional[Post]:
        """
        슬러그로 게시글을 조회합니다.

        Args:
            slug: URL 슬러그

        Returns:
            Optional[Post]: 게시글 또는 None
        """
        return self.db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category)
        ).filter(Post.slug == slug).first()

    def get_posts(
        self,
        page: int = 1,
        size: int = 10,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        include_unpublished: bool = False
    ) -> Tuple[List[Post], int]:
        """
        게시글 목록을 조회합니다.

        Args:
            page: 페이지 번호
            size: 페이지당 항목 수
            category_id: 카테고리 필터
            search: 검색어
            include_unpublished: 미공개 글 포함 여부

        Returns:
            Tuple[List[Post], int]: (게시글 목록, 전체 개수)
        """
        query = self.db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category)
        )

        # 필터 적용
        if not include_unpublished:
            query = query.filter(Post.is_published == True)

        if category_id:
            query = query.filter(Post.category_id == category_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Post.title.ilike(search_pattern)) |
                (Post.content.ilike(search_pattern))
            )

        # 전체 개수
        total = query.count()

        # 정렬 및 페이지네이션
        posts = query.order_by(
            desc(Post.is_pinned),
            desc(Post.created_at)
        ).offset((page - 1) * size).limit(size).all()

        return posts, total

    def create_post(self, post_data: PostCreate, author_id: int) -> Post:
        """
        새 게시글을 생성합니다.

        Args:
            post_data: 게시글 데이터
            author_id: 작성자 ID

        Returns:
            Post: 생성된 게시글
        """
        # 임시 ID로 슬러그 생성 (나중에 업데이트)
        temp_slug = generate_slug(post_data.title)

        post = Post(
            title=post_data.title,
            content=post_data.content,
            slug=temp_slug,
            author_id=author_id,
            category_id=post_data.category_id,
            is_published=post_data.is_published
        )

        self.db.add(post)
        self.db.flush()  # ID 생성

        # 실제 슬러그로 업데이트 (ID 포함)
        post.slug = generate_slug(post_data.title, post.id)

        self.db.commit()
        self.db.refresh(post)

        return post

    def update_post(
        self,
        post_id: int,
        post_data: PostUpdate,
        user: User
    ) -> Post:
        """
        게시글을 수정합니다.

        Args:
            post_id: 게시글 ID
            post_data: 수정할 데이터
            user: 요청한 사용자

        Returns:
            Post: 수정된 게시글

        Raises:
            HTTPException: 권한이 없거나 게시글이 없는 경우
        """
        post = self.get_post(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )

        # 권한 확인 (작성자 또는 관리자)
        if post.author_id != user.id and not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="수정 권한이 없습니다."
            )

        # 필드 업데이트
        if post_data.title is not None:
            post.title = post_data.title
            post.slug = generate_slug(post_data.title, post.id)

        if post_data.content is not None:
            post.content = post_data.content

        if post_data.category_id is not None:
            post.category_id = post_data.category_id

        if post_data.is_published is not None:
            post.is_published = post_data.is_published

        if post_data.is_pinned is not None:
            post.is_pinned = post_data.is_pinned

        self.db.commit()
        self.db.refresh(post)

        return post

    def delete_post(self, post_id: int, user: User) -> bool:
        """
        게시글을 삭제합니다.

        Args:
            post_id: 게시글 ID
            user: 요청한 사용자

        Returns:
            bool: 성공 여부
        """
        post = self.get_post(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )

        # 권한 확인
        if post.author_id != user.id and not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="삭제 권한이 없습니다."
            )

        self.db.delete(post)
        self.db.commit()

        return True

    def increment_view_count(self, post_id: int) -> None:
        """
        게시글 조회수를 증가시킵니다.

        Args:
            post_id: 게시글 ID
        """
        self.db.query(Post).filter(Post.id == post_id).update(
            {Post.view_count: Post.view_count + 1}
        )
        self.db.commit()

    # ===========================================
    # Comment Methods
    # ===========================================

    def get_comments(self, post_id: int) -> List[Comment]:
        """
        게시글의 댓글 목록을 조회합니다.

        Args:
            post_id: 게시글 ID

        Returns:
            List[Comment]: 댓글 목록 (대댓글 구조 포함)
        """
        return self.db.query(Comment).options(
            joinedload(Comment.author)
        ).filter(
            Comment.post_id == post_id,
            Comment.parent_id == None,  # 최상위 댓글만
            Comment.is_active == True
        ).order_by(Comment.created_at).all()

    def create_comment(
        self,
        post_id: int,
        comment_data: CommentCreate,
        author_id: int
    ) -> Comment:
        """
        댓글을 생성합니다.

        Args:
            post_id: 게시글 ID
            comment_data: 댓글 데이터
            author_id: 작성자 ID

        Returns:
            Comment: 생성된 댓글
        """
        # 게시글 확인
        post = self.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )

        # 대댓글인 경우 부모 댓글 확인
        if comment_data.parent_id:
            parent = self.db.query(Comment).filter(
                Comment.id == comment_data.parent_id,
                Comment.post_id == post_id
            ).first()

            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="부모 댓글을 찾을 수 없습니다."
                )

        comment = Comment(
            content=comment_data.content,
            post_id=post_id,
            author_id=author_id,
            parent_id=comment_data.parent_id
        )

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def delete_comment(self, comment_id: int, user: User) -> bool:
        """
        댓글을 삭제합니다 (소프트 삭제).

        Args:
            comment_id: 댓글 ID
            user: 요청한 사용자

        Returns:
            bool: 성공 여부
        """
        comment = self.db.query(Comment).filter(
            Comment.id == comment_id
        ).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없습니다."
            )

        if comment.author_id != user.id and not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="삭제 권한이 없습니다."
            )

        # 소프트 삭제
        comment.is_active = False
        comment.content = "삭제된 댓글입니다."
        self.db.commit()

        return True

    def get_comment_count(self, post_id: int) -> int:
        """
        게시글의 댓글 수를 반환합니다.

        Args:
            post_id: 게시글 ID

        Returns:
            int: 댓글 수
        """
        return self.db.query(func.count(Comment.id)).filter(
            Comment.post_id == post_id,
            Comment.is_active == True
        ).scalar()
