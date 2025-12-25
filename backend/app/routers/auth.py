"""
Authentication Router
======================

인증 관련 API 엔드포인트입니다.

엔드포인트:
- POST /register: 회원가입
- POST /login: 로그인
- POST /refresh: 토큰 갱신
- GET /me: 현재 사용자 정보
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, RefreshTokenRequest
from app.services.user import UserService
from app.services.auth import AuthService
from app.dependencies.auth import get_current_active_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다."
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    회원가입

    새로운 사용자 계정을 생성합니다.

    - **email**: 유효한 이메일 주소 (중복 불가)
    - **username**: 사용자명 (3-50자, 영문 시작, 중복 불가)
    - **password**: 비밀번호 (8자 이상, 대/소문자/숫자 포함)
    - **full_name**: 실제 이름 (선택)

    Returns:
        생성된 사용자 정보
    """
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="로그인",
    description="이메일/사용자명과 비밀번호로 로그인합니다."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    로그인

    이메일 또는 사용자명과 비밀번호로 인증하고 토큰을 발급받습니다.

    OAuth2 표준 양식을 사용합니다:
    - **username**: 이메일 또는 사용자명
    - **password**: 비밀번호

    Returns:
        access_token과 refresh_token
    """
    auth_service = AuthService(db)
    return auth_service.login(form_data.username, form_data.password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="토큰 갱신",
    description="리프레시 토큰으로 새 액세스 토큰을 발급받습니다."
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    토큰 갱신

    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.
    리프레시 토큰도 함께 갱신됩니다.

    - **refresh_token**: 유효한 리프레시 토큰

    Returns:
        새로운 access_token과 refresh_token
    """
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(request.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다."
)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    내 정보 조회

    현재 인증된 사용자의 정보를 반환합니다.
    Authorization 헤더에 유효한 Bearer 토큰이 필요합니다.

    Returns:
        현재 사용자 정보
    """
    return current_user
