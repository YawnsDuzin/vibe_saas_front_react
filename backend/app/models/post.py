"""
Post & Comment Models
======================

게시판 기능을 위한 모델입니다.

Features:
- 게시글 CRUD
- 카테고리 분류
- 댓글 시스템
- 조회수 추적
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """
    게시글 카테고리 모델

    Attributes:
        id (int): 기본 키
        name (str): 카테고리 이름
        slug (str): URL용 슬러그
        description (str): 설명
        order (int): 정렬 순서
        is_active (bool): 활성화 여부
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    posts = relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"


class Post(Base):
    """
    게시글 모델

    Attributes:
        id (int): 기본 키
        title (str): 제목
        content (str): 내용
        slug (str): URL용 슬러그
        author_id (int): 작성자 FK
        category_id (int): 카테고리 FK
        view_count (int): 조회수
        is_published (bool): 공개 여부
        is_pinned (bool): 상단 고정 여부
        created_at (datetime): 작성 일시
        updated_at (datetime): 수정 일시
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)

    # 외래 키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # 메타데이터
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title[:30]}...')>"


class Comment(Base):
    """
    댓글 모델

    Attributes:
        id (int): 기본 키
        content (str): 댓글 내용
        author_id (int): 작성자 FK
        post_id (int): 게시글 FK
        parent_id (int): 부모 댓글 FK (대댓글용)
        is_active (bool): 활성화 여부
        created_at (datetime): 작성 일시
        updated_at (datetime): 수정 일시
    """

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    # 외래 키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # 상태
    is_active = Column(Boolean, default=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, post_id={self.post_id})>"
