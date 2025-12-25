"""
User Service
=============

사용자 관련 비즈니스 로직을 처리하는 서비스입니다.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.theme import UserTheme
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash


class UserService:
    """
    사용자 서비스 클래스

    사용자 생성, 조회, 수정, 삭제 등의 비즈니스 로직을 처리합니다.
    """

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """
        ID로 사용자를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 사용자 또는 None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자를 조회합니다.

        Args:
            email: 사용자 이메일

        Returns:
            Optional[User]: 사용자 또는 None
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자를 조회합니다.

        Args:
            username: 사용자명

        Returns:
            Optional[User]: 사용자 또는 None
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        사용자 목록을 조회합니다.

        Args:
            skip: 건너뛸 레코드 수
            limit: 최대 조회 수
            is_active: 활성 상태 필터

        Returns:
            List[User]: 사용자 목록
        """
        query = self.db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreate) -> User:
        """
        새 사용자를 생성합니다.

        이메일과 사용자명의 중복을 확인하고,
        비밀번호를 해시하여 저장합니다.

        Args:
            user_data: 사용자 생성 데이터

        Returns:
            User: 생성된 사용자

        Raises:
            HTTPException: 이메일 또는 사용자명이 이미 존재하는 경우
        """
        # 이메일 중복 확인
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )

        # 사용자명 중복 확인
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다."
            )

        # 사용자 생성
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=UserRole.USER,
            is_active=True,
            is_verified=False
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # 기본 테마 설정 생성
        theme = UserTheme(user_id=user.id, theme_name="light")
        self.db.add(theme)
        self.db.commit()

        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        사용자 정보를 수정합니다.

        Args:
            user_id: 수정할 사용자 ID
            user_data: 수정할 데이터

        Returns:
            User: 수정된 사용자

        Raises:
            HTTPException: 사용자를 찾을 수 없는 경우
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        # 이메일 변경 시 중복 확인
        if user_data.email and user_data.email != user.email:
            if self.get_user_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 등록된 이메일입니다."
                )
            user.email = user_data.email

        # 사용자명 변경 시 중복 확인
        if user_data.username and user_data.username != user.username:
            if self.get_user_by_username(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용 중인 사용자명입니다."
                )
            user.username = user_data.username

        # 기타 필드 업데이트
        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: int) -> bool:
        """
        사용자를 삭제합니다.

        실제 삭제 대신 비활성화(soft delete)를 권장합니다.

        Args:
            user_id: 삭제할 사용자 ID

        Returns:
            bool: 성공 여부

        Raises:
            HTTPException: 사용자를 찾을 수 없는 경우
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        self.db.delete(user)
        self.db.commit()

        return True

    def deactivate_user(self, user_id: int) -> User:
        """
        사용자 계정을 비활성화합니다 (Soft Delete).

        Args:
            user_id: 비활성화할 사용자 ID

        Returns:
            User: 비활성화된 사용자
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)

        return user

    def update_last_login(self, user: User) -> None:
        """
        마지막 로그인 시간을 업데이트합니다.

        Args:
            user: 사용자 객체
        """
        user.last_login = datetime.utcnow()
        self.db.commit()
