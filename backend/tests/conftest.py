"""
Test Configuration
===================

pytest fixture 및 테스트 설정입니다.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

# 테스트용 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    """테스트용 데이터베이스 세션을 제공합니다."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 의존성 오버라이드
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    각 테스트 함수마다 새로운 데이터베이스 세션을 제공합니다.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    테스트용 FastAPI 클라이언트를 제공합니다.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    """
    테스트용 일반 사용자를 생성합니다.
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db_session) -> User:
    """
    테스트용 관리자 사용자를 생성합니다.
    """
    user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def user_token(client, test_user):
    """
    테스트 사용자의 인증 토큰을 반환합니다.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """
    관리자의 인증 토큰을 반환합니다.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "adminuser",
            "password": "AdminPass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(user_token):
    """
    일반 사용자 인증 헤더를 반환합니다.
    """
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    """
    관리자 인증 헤더를 반환합니다.
    """
    return {"Authorization": f"Bearer {admin_token}"}
