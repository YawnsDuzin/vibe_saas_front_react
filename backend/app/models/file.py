"""
File Model
===========

파일 업로드 정보를 저장하는 모델입니다.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base


class File(Base):
    """업로드된 파일 모델"""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    # 파일 정보
    filename = Column(String(255), nullable=False, comment="원본 파일명")
    storage_key = Column(String(500), nullable=False, unique=True, comment="스토리지 키/경로")
    content_type = Column(String(100), nullable=False, comment="MIME 타입")
    size = Column(BigInteger, nullable=False, comment="파일 크기 (bytes)")
    url = Column(String(1000), nullable=False, comment="접근 URL")

    # 스토리지 정보
    storage_type = Column(String(50), nullable=False, comment="스토리지 타입")
    folder = Column(String(255), default="", comment="저장 폴더")

    # 메타데이터
    alt_text = Column(String(255), nullable=True, comment="대체 텍스트")
    description = Column(String(500), nullable=True, comment="설명")

    # 관계
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploader = relationship("User", backref="uploaded_files")
    post_files = relationship("PostFile", back_populates="file", cascade="all, delete-orphan")

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<File {self.filename}>"

    @property
    def extension(self) -> str:
        """파일 확장자를 반환합니다."""
        if "." in self.filename:
            return self.filename.rsplit(".", 1)[-1].lower()
        return ""

    @property
    def is_image(self) -> bool:
        """이미지 파일 여부를 반환합니다."""
        return self.content_type.startswith("image/")

    @property
    def size_formatted(self) -> str:
        """포맷된 파일 크기를 반환합니다."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"
