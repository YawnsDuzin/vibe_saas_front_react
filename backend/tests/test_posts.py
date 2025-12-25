"""
Posts Tests
============

게시판 관련 API 테스트입니다.
"""

import pytest
from fastapi import status

from app.models.post import Post, Category


class TestPosts:
    """게시글 테스트"""

    def test_create_post(self, client, auth_headers):
        """게시글 작성"""
        response = client.post(
            "/api/v1/posts/",
            json={
                "title": "테스트 게시글",
                "content": "테스트 내용입니다."
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "테스트 게시글"
        assert data["content"] == "테스트 내용입니다."
        assert "id" in data
        assert "slug" in data

    def test_create_post_unauthorized(self, client):
        """인증 없이 게시글 작성 실패"""
        response = client.post(
            "/api/v1/posts/",
            json={
                "title": "테스트 게시글",
                "content": "테스트 내용입니다."
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_posts(self, client, auth_headers, db_session, test_user):
        """게시글 목록 조회"""
        # 게시글 생성
        post = Post(
            title="테스트 게시글",
            content="테스트 내용",
            slug="test-post-1",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.get("/api/v1/posts/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) >= 1

    def test_get_post_detail(self, client, db_session, test_user):
        """게시글 상세 조회"""
        post = Post(
            title="테스트 게시글",
            content="테스트 내용",
            slug="test-post-detail",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.get(f"/api/v1/posts/{post.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "테스트 게시글"
        assert data["view_count"] >= 1  # 조회수 증가 확인

    def test_get_post_not_found(self, client):
        """존재하지 않는 게시글 조회"""
        response = client.get("/api/v1/posts/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_post(self, client, auth_headers, db_session, test_user):
        """게시글 수정"""
        post = Post(
            title="원래 제목",
            content="원래 내용",
            slug="original-post",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.put(
            f"/api/v1/posts/{post.id}",
            json={
                "title": "수정된 제목",
                "content": "수정된 내용"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "수정된 제목"
        assert data["content"] == "수정된 내용"

    def test_delete_post(self, client, auth_headers, db_session, test_user):
        """게시글 삭제"""
        post = Post(
            title="삭제할 게시글",
            content="삭제될 내용",
            slug="delete-post",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.delete(
            f"/api/v1/posts/{post.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 삭제 확인
        deleted = db_session.query(Post).filter(Post.id == post.id).first()
        assert deleted is None

    def test_search_posts(self, client, db_session, test_user):
        """게시글 검색"""
        post = Post(
            title="FastAPI 튜토리얼",
            content="FastAPI 학습 내용",
            slug="fastapi-tutorial",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.get("/api/v1/posts/?search=FastAPI")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1


class TestComments:
    """댓글 테스트"""

    def test_create_comment(self, client, auth_headers, db_session, test_user):
        """댓글 작성"""
        post = Post(
            title="테스트 게시글",
            content="테스트 내용",
            slug="comment-test-post",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.post(
            f"/api/v1/posts/{post.id}/comments",
            json={"content": "테스트 댓글입니다."},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "테스트 댓글입니다."

    def test_get_comments(self, client, db_session, test_user):
        """댓글 목록 조회"""
        post = Post(
            title="테스트 게시글",
            content="테스트 내용",
            slug="get-comments-post",
            author_id=test_user.id,
            is_published=True
        )
        db_session.add(post)
        db_session.commit()

        response = client.get(f"/api/v1/posts/{post.id}/comments")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)


class TestCategories:
    """카테고리 테스트"""

    def test_get_categories(self, client, db_session):
        """카테고리 목록 조회"""
        category = Category(
            name="공지사항",
            slug="notices",
            description="공지사항 카테고리"
        )
        db_session.add(category)
        db_session.commit()

        response = client.get("/api/v1/posts/categories")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_create_category_admin_only(self, client, auth_headers):
        """일반 사용자 카테고리 생성 실패"""
        response = client.post(
            "/api/v1/posts/categories",
            json={
                "name": "새 카테고리",
                "slug": "new-category"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_category_by_admin(self, client, admin_headers):
        """관리자 카테고리 생성"""
        response = client.post(
            "/api/v1/posts/categories",
            json={
                "name": "관리자 카테고리",
                "slug": "admin-category",
                "description": "관리자가 만든 카테고리"
            },
            headers=admin_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "관리자 카테고리"
