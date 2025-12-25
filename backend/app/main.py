"""
FastAPI Main Application
=========================

FastAPI 보일러플레이트 메인 애플리케이션입니다.

Features:
- 다중 데이터베이스 지원 (PostgreSQL, MySQL, MariaDB, SQLite)
- JWT 인증
- 게시판
- 대시보드
- 테마 설정
- 메뉴 관리
- 파일 업로드 (다중 스토리지 지원)

Usage:
    uvicorn app.main:app --reload

Swagger UI:
    http://localhost:8000/docs

ReDoc:
    http://localhost:8000/redoc
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 수명 주기 관리

    시작 시:
    - 데이터베이스 테이블 생성

    종료 시:
    - 리소스 정리
    """
    # Startup
    print(f"🚀 {settings.app_name} v{settings.app_version} 시작...")
    print(f"📦 데이터베이스: {settings.db_type}")
    print(f"🔧 디버그 모드: {settings.debug}")

    # 데이터베이스 초기화
    init_db()
    print("✅ 데이터베이스 테이블 생성 완료")

    yield

    # Shutdown
    print("👋 애플리케이션 종료...")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.app_name,
    description="""
## FastAPI 보일러플레이트

이 API는 다음 기능을 제공합니다:

### 🔐 인증
- 회원가입 / 로그인
- JWT 토큰 기반 인증
- 토큰 갱신

### 👤 사용자 관리
- 프로필 조회 / 수정
- 관리자용 사용자 관리

### 📝 게시판
- 게시글 CRUD
- 댓글 시스템
- 카테고리 분류

### 📊 대시보드
- 통계 정보
- 최근 활동

### 🎨 테마
- 테마 설정 관리

### 📋 메뉴
- 동적 메뉴 구조

### 📁 파일 업로드
- 다중 스토리지 지원 (Local, Supabase, Cloudflare R2, AWS S3)
- 파일 관리 API
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS 미들웨어 설정
# allow_origins=["*"]와 allow_credentials=True는 함께 사용할 수 없으므로
# allow_origin_regex를 사용하여 모든 origin을 동적으로 허용
if settings.cors_origins_list == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r".*",  # 모든 origin 허용 (정규식)
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
    )


# ===========================================
# Exception Handlers
# ===========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    요청 검증 에러 핸들러

    Pydantic 검증 실패 시 사용자 친화적인 메시지를 반환합니다.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "입력값 검증에 실패했습니다.",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    전역 예외 핸들러

    처리되지 않은 예외를 잡아서 적절한 응답을 반환합니다.
    """
    # 디버그 모드에서는 상세 정보 표시
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 내부 오류가 발생했습니다."}
    )


# ===========================================
# API Routes
# ===========================================

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 로컬 스토리지 사용 시 정적 파일 서빙
storage_type = os.getenv("STORAGE_TYPE", "local")
if storage_type == "local":
    upload_dir = Path(os.getenv("STORAGE_LOCAL_DIR", "uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_url = os.getenv("STORAGE_LOCAL_URL", "/uploads")
    app.mount(upload_url, StaticFiles(directory=str(upload_dir)), name="uploads")


# ===========================================
# Root Endpoints
# ===========================================

@app.get("/", tags=["Root"])
async def root():
    """
    루트 엔드포인트

    API 정보를 반환합니다.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트

    서비스 상태를 확인합니다.
    """
    return {
        "status": "healthy",
        "database": settings.db_type
    }


# ===========================================
# Development Entry Point
# ===========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
