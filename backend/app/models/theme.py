"""
Theme Model
============

사용자별 테마 설정을 저장하는 모델입니다.

Features:
- 테마 선택 (light, dark, blue, green 등)
- 사이드바 상태 기억
- 기타 UI 설정
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class UserTheme(Base):
    """
    사용자 테마 설정 모델

    Attributes:
        id (int): 기본 키
        user_id (int): 사용자 FK
        theme_name (str): 테마 이름
        sidebar_collapsed (bool): 사이드바 접힘 상태
        custom_settings (dict): 기타 커스텀 설정 (JSON)
        created_at (datetime): 생성 일시
        updated_at (datetime): 수정 일시
    """

    __tablename__ = "user_themes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 테마 설정
    theme_name = Column(String(50), default="light", nullable=False)
    sidebar_collapsed = Column(Boolean, default=False)

    # 확장 가능한 커스텀 설정 (JSON)
    custom_settings = Column(JSON, default=dict, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    user = relationship("User", back_populates="theme")

    def __repr__(self) -> str:
        return f"<UserTheme(id={self.id}, user_id={self.user_id}, theme='{self.theme_name}')>"

    def to_dict(self) -> dict:
        """테마 설정을 딕셔너리로 반환"""
        return {
            "theme_name": self.theme_name,
            "sidebar_collapsed": self.sidebar_collapsed,
            "custom_settings": self.custom_settings or {}
        }
