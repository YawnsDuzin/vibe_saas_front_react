"""
Authentication Service
=======================

인증 관련 비즈니스 로직을 처리하는 서비스입니다.
"""

from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import Token, TokenData
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)


class AuthService:
    """
    인증 서비스 클래스

    로그인, 토큰 갱신, 비밀번호 검증 등의 인증 로직을 처리합니다.
    """

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db

    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        사용자를 인증합니다.

        이메일 또는 사용자명으로 사용자를 찾고,
        비밀번호를 검증합니다.

        Args:
            username: 이메일 또는 사용자명
            password: 비밀번호

        Returns:
            Optional[User]: 인증된 사용자 또는 None
        """
        # 이메일 또는 사용자명으로 사용자 찾기
        user = self.db.query(User).filter(
            (User.email == username) | (User.username == username)
        ).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def login(self, username: str, password: str) -> Token:
        """
        로그인을 수행하고 토큰을 발급합니다.

        Args:
            username: 이메일 또는 사용자명
            password: 비밀번호

        Returns:
            Token: 액세스 토큰과 리프레시 토큰

        Raises:
            HTTPException: 인증 실패 시 401 에러
        """
        user = self.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일/사용자명 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 계정입니다. 관리자에게 문의하세요."
            )

        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        self.db.commit()

        # 토큰 생성 (sub는 반드시 문자열이어야 함)
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def refresh_tokens(self, refresh_token: str) -> Token:
        """
        리프레시 토큰을 사용하여 새 토큰을 발급합니다.

        Args:
            refresh_token: 리프레시 토큰

        Returns:
            Token: 새로운 액세스 토큰과 리프레시 토큰

        Raises:
            HTTPException: 토큰이 유효하지 않은 경우 401 에러
        """
        # 토큰 타입 확인
        if not verify_token_type(refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 토큰 디코딩
        payload = decode_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었거나 유효하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 사용자 확인
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 계정입니다."
            )

        # 새 토큰 생성 (sub는 반드시 문자열이어야 함)
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    def get_token_data(self, token: str) -> Optional[TokenData]:
        """
        토큰에서 사용자 정보를 추출합니다.

        Args:
            token: JWT 토큰

        Returns:
            Optional[TokenData]: 토큰 데이터 또는 None
        """
        payload = decode_token(token)
        if payload is None:
            return None

        return TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            role=payload.get("role")
        )
