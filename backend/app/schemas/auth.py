"""
Authentication Schemas
=======================

인증 관련 Pydantic 스키마입니다.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """
    토큰 응답 스키마

    로그인 성공 시 반환되는 JWT 토큰 정보입니다.
    """
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    """
    토큰 페이로드 스키마

    JWT 토큰에서 디코딩된 데이터입니다.
    """
    user_id: Optional[int] = Field(None, description="사용자 ID")
    username: Optional[str] = Field(None, description="사용자명")
    email: Optional[str] = Field(None, description="이메일")
    role: Optional[str] = Field(None, description="사용자 역할")


class LoginRequest(BaseModel):
    """
    로그인 요청 스키마

    이메일 또는 사용자명으로 로그인할 수 있습니다.
    """
    username: str = Field(
        ...,
        description="이메일 또는 사용자명",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="비밀번호",
        example="password123"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "user@example.com",
                "password": "SecureP@ss123"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """
    토큰 갱신 요청 스키마

    리프레시 토큰을 사용하여 새 액세스 토큰을 발급받습니다.
    """
    refresh_token: str = Field(
        ...,
        description="리프레시 토큰",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )


class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청 스키마"""
    current_password: str = Field(
        ...,
        min_length=1,
        description="현재 비밀번호"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="새 비밀번호"
    )


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""
    email: EmailStr = Field(
        ...,
        description="가입된 이메일",
        example="user@example.com"
    )
