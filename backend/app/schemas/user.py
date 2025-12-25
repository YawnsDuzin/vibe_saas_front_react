"""
User Schemas
=============

사용자 관련 Pydantic 스키마입니다.

스키마는 다음 목적으로 사용됩니다:
- 요청 데이터 검증
- 응답 데이터 직렬화
- API 문서 자동 생성
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """
    사용자 기본 스키마

    모든 사용자 스키마의 기반이 되는 공통 필드를 정의합니다.
    """
    email: EmailStr = Field(..., description="사용자 이메일", example="user@example.com")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="사용자명 (3-50자)",
        example="johndoe"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="실제 이름",
        example="John Doe"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        사용자명 유효성 검사

        - 영문, 숫자, 언더스코어만 허용
        - 숫자로 시작할 수 없음
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError(
                "사용자명은 영문으로 시작하고 영문, 숫자, 언더스코어만 포함할 수 있습니다."
            )
        return v


class UserCreate(UserBase):
    """
    사용자 생성 스키마

    회원가입 시 필요한 데이터를 정의합니다.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="비밀번호 (최소 8자)",
        example="SecureP@ss123"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        비밀번호 강도 검증

        - 최소 8자
        - 대문자, 소문자, 숫자 각각 1개 이상 포함
        """
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("비밀번호에 대문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호에 소문자가 최소 1개 포함되어야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호에 숫자가 최소 1개 포함되어야 합니다.")
        return v


class UserUpdate(BaseModel):
    """
    사용자 정보 수정 스키마

    부분 업데이트를 지원합니다 (PATCH).
    모든 필드가 선택적입니다.
    """
    email: Optional[EmailStr] = Field(None, description="이메일")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="사용자명")
    full_name: Optional[str] = Field(None, max_length=100, description="실제 이름")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="새 비밀번호")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("사용자명은 영문으로 시작해야 합니다.")
        return v


class UserResponse(BaseModel):
    """
    사용자 응답 스키마

    API 응답에서 반환되는 사용자 정보입니다.
    비밀번호 같은 민감한 정보는 제외됩니다.
    """
    id: int = Field(..., description="사용자 ID")
    email: EmailStr = Field(..., description="이메일")
    username: str = Field(..., description="사용자명")
    full_name: Optional[str] = Field(None, description="실제 이름")
    role: str = Field(..., description="사용자 역할")
    is_active: bool = Field(..., description="계정 활성화 상태")
    is_verified: bool = Field(..., description="이메일 인증 여부")
    created_at: datetime = Field(..., description="가입 일시")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인")

    model_config = {
        "from_attributes": True,  # ORM 모드 활성화
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-15T12:30:00"
            }
        }
    }


class UserInDB(UserResponse):
    """
    데이터베이스 사용자 스키마

    내부적으로 사용되며, 해시된 비밀번호를 포함합니다.
    API 응답으로 직접 반환하지 않습니다.
    """
    hashed_password: str = Field(..., description="해시된 비밀번호")
