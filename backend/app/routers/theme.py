"""
Theme Router
=============

테마 설정 API 엔드포인트입니다.

엔드포인트:
- GET /: 내 테마 설정 조회
- PUT /: 테마 설정 수정
- GET /available: 사용 가능한 테마 목록
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.theme import UserTheme
from app.schemas.theme import ThemeResponse, ThemeUpdate, AvailableThemesResponse
from app.dependencies.auth import get_current_active_user

router = APIRouter()


@router.get(
    "/available",
    response_model=AvailableThemesResponse,
    summary="사용 가능한 테마",
    description="사용 가능한 테마 목록을 조회합니다."
)
def get_available_themes():
    """
    사용 가능한 테마 목록 조회

    시스템에서 지원하는 테마 목록과 기본 테마를 반환합니다.
    이 엔드포인트는 인증 없이 접근할 수 있습니다.

    Returns:
        - themes: 사용 가능한 테마 목록
        - default_theme: 기본 테마
    """
    return AvailableThemesResponse(
        themes=settings.available_themes_list,
        default_theme=settings.default_theme
    )


@router.get(
    "/",
    response_model=ThemeResponse,
    summary="내 테마 설정",
    description="현재 사용자의 테마 설정을 조회합니다."
)
def get_my_theme(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    내 테마 설정 조회

    현재 로그인한 사용자의 테마 설정을 반환합니다.
    테마 설정이 없는 경우 기본 테마로 새로 생성합니다.

    Returns:
        테마 설정 정보
    """
    theme = db.query(UserTheme).filter(
        UserTheme.user_id == current_user.id
    ).first()

    # 테마 설정이 없으면 생성
    if not theme:
        theme = UserTheme(
            user_id=current_user.id,
            theme_name=settings.default_theme
        )
        db.add(theme)
        db.commit()
        db.refresh(theme)

    return theme


@router.put(
    "/",
    response_model=ThemeResponse,
    summary="테마 설정 수정",
    description="테마 설정을 수정합니다."
)
def update_my_theme(
    theme_data: ThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    테마 설정 수정

    현재 사용자의 테마 설정을 수정합니다.

    - **theme_name**: 테마 이름 (light, dark, blue, green)
    - **sidebar_collapsed**: 사이드바 접힘 상태
    - **custom_settings**: 기타 커스텀 설정 (JSON)

    Returns:
        수정된 테마 설정
    """
    theme = db.query(UserTheme).filter(
        UserTheme.user_id == current_user.id
    ).first()

    # 테마 설정이 없으면 생성
    if not theme:
        theme = UserTheme(
            user_id=current_user.id,
            theme_name=settings.default_theme
        )
        db.add(theme)
        db.commit()
        db.refresh(theme)

    # 테마 이름 유효성 검사
    if theme_data.theme_name:
        if theme_data.theme_name not in settings.available_themes_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 테마입니다. 사용 가능: {settings.available_themes_list}"
            )
        theme.theme_name = theme_data.theme_name

    # 기타 필드 업데이트
    if theme_data.sidebar_collapsed is not None:
        theme.sidebar_collapsed = theme_data.sidebar_collapsed

    if theme_data.custom_settings is not None:
        # 기존 설정과 병합
        current_settings = theme.custom_settings or {}
        current_settings.update(theme_data.custom_settings)
        theme.custom_settings = current_settings

    db.commit()
    db.refresh(theme)

    return theme
