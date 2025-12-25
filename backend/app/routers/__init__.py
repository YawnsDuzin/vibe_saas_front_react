"""
API Routers
============

FastAPI 라우터들을 정의하는 패키지입니다.

각 라우터는 특정 기능 영역을 담당합니다:
- auth: 인증 (로그인, 회원가입, 토큰 갱신)
- users: 사용자 관리
- posts: 게시글 및 댓글
- dashboard: 대시보드 통계
- theme: 테마 설정
- menu: 메뉴 구조
"""

from fastapi import APIRouter

from app.routers import auth, users, posts, dashboard, theme, menu

# 메인 API 라우터
api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["인증"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["사용자"]
)

api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["게시판"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["대시보드"]
)

api_router.include_router(
    theme.router,
    prefix="/theme",
    tags=["테마"]
)

api_router.include_router(
    menu.router,
    prefix="/menu",
    tags=["메뉴"]
)
