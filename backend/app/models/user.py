"""
User Model
===========

사용자 정보를 저장하는 모델입니다.

Features:
- 이메일 기반 인증
- 비밀번호 해싱
- 역할(Role) 기반 권한 관리
- 계정 활성화/비활성화
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """사용자 역할 정의"""
    ADMIN = "admin"          # 관리자
    MODERATOR = "moderator"  # 운영자
    USER = "user"            # 일반 사용자


class User(Base):
    """
    사용자 모델

    Attributes:
        id (int): 기본 키
        email (str): 이메일 (유니크)
        username (str): 사용자명 (유니크)
        hashed_password (str): 해시된 비밀번호
        full_name (str): 실제 이름
        role (UserRole): 사용자 역할
        is_active (bool): 계정 활성화 여부
        is_verified (bool): 이메일 인증 여부
        created_at (datetime): 생성 일시
        updated_at (datetime): 수정 일시
        last_login (datetime): 마지막 로그인 일시
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # 역할 및 권한
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    # 계정 상태
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 관계 설정
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    theme = relationship("UserTheme", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @property
    def is_admin(self) -> bool:
        """관리자 여부 확인"""
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """운영자 이상 권한 확인"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
