"""
Dependencies
=============

FastAPI의 Depends() 시스템에 사용되는 종속성들입니다.

이 패키지는 다음을 제공합니다:
- 인증/인가 종속성
- 공통 쿼리 파라미터
- 데이터베이스 세션
"""

from app.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_optional_current_user,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_optional_current_user",
]
