"""
Authentication Tests
=====================

인증 관련 API 테스트입니다.
"""

import pytest
from fastapi import status


class TestRegister:
    """회원가입 테스트"""

    def test_register_success(self, client):
        """정상 회원가입"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPass123",
                "full_name": "New User"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """중복 이메일 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # 이미 존재
                "username": "anotheruser",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "이미 등록된 이메일" in response.json()["detail"]

    def test_register_duplicate_username(self, client, test_user):
        """중복 사용자명 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "another@example.com",
                "username": "testuser",  # 이미 존재
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "이미 사용 중인 사용자명" in response.json()["detail"]

    def test_register_weak_password(self, client):
        """약한 비밀번호 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "weak"  # 너무 짧고 대문자/숫자 없음
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_username(self, client):
        """유효하지 않은 사용자명 회원가입 실패"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "123user",  # 숫자로 시작
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """로그인 테스트"""

    def test_login_with_email(self, client, test_user):
        """이메일로 로그인"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_username(self, client, test_user):
        """사용자명으로 로그인"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, test_user):
        """잘못된 비밀번호 로그인 실패"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "WrongPassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자 로그인 실패"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """토큰 갱신 테스트"""

    def test_refresh_token_success(self, client, test_user):
        """토큰 갱신 성공"""
        # 먼저 로그인
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # 토큰 갱신
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_with_invalid_token(self, client):
        """유효하지 않은 토큰으로 갱신 실패"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMe:
    """내 정보 조회 테스트"""

    def test_get_me_success(self, client, auth_headers):
        """내 정보 조회 성공"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_me_unauthorized(self, client):
        """인증 없이 내 정보 조회 실패"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
