"""
관리자 계정 생성 스크립트

사용법:
    cd backend
    python scripts/create_admin.py
"""

import sys
import os

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def create_admin():
    """관리자 계정 생성"""
    # DB 초기화
    init_db()

    db = SessionLocal()

    try:
        # 기본 관리자 정보
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "Admin123!"  # 변경 권장

        # 이미 존재하는지 확인
        existing = db.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()

        if existing:
            if existing.role == UserRole.ADMIN:
                print(f"✅ 관리자 계정이 이미 존재합니다: {existing.username}")
            else:
                # 기존 계정을 관리자로 업그레이드
                existing.role = UserRole.ADMIN
                db.commit()
                print(f"✅ 기존 계정을 관리자로 업그레이드했습니다: {existing.username}")
            return

        # 새 관리자 생성
        admin = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name="관리자",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )

        db.add(admin)
        db.commit()

        print("=" * 50)
        print("✅ 관리자 계정이 생성되었습니다!")
        print("=" * 50)
        print(f"  아이디: {admin_username}")
        print(f"  이메일: {admin_email}")
        print(f"  비밀번호: {admin_password}")
        print("=" * 50)
        print("⚠️  보안을 위해 비밀번호를 변경하세요!")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
