"""
Post-File Association Model
============================

게시글과 파일의 다대다 관계를 정의하는 모델입니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class PostFile(Base):
    """
    게시글-파일 연결 모델

    게시글에 첨부된 파일들을 관리합니다.

    Attributes:
        id (int): 기본 키
        post_id (int): 게시글 FK
        file_id (int): 파일 FK
        display_order (int): 표시 순서
        created_at (datetime): 연결 일시
    """

    __tablename__ = "post_files"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    display_order = Column(Integer, default=0, comment="표시 순서")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 유니크 제약 조건: 같은 게시글에 같은 파일은 한 번만 첨부 가능
    __table_args__ = (
        UniqueConstraint('post_id', 'file_id', name='uq_post_file'),
    )

    # 관계 설정
    post = relationship("Post", back_populates="post_files")
    file = relationship("File", back_populates="post_files")

    def __repr__(self) -> str:
        return f"<PostFile(post_id={self.post_id}, file_id={self.file_id})>"
