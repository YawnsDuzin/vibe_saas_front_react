# 사용 가이드

이 문서에서는 API 사용 방법을 단계별로 설명합니다.

## 목차

1. [시작하기](#시작하기)
2. [인증](#인증)
3. [사용자 관리](#사용자-관리)
4. [게시판](#게시판)
5. [대시보드](#대시보드)
6. [테마 설정](#테마-설정)
7. [메뉴 관리](#메뉴-관리)

---

## 시작하기

### API 기본 URL

```
http://localhost:8000/api/v1
```

### API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 헬스 체크

```bash
curl http://localhost:8000/health
```

응답:
```json
{
    "status": "healthy",
    "database": "postgresql"
}
```

---

## 인증

### 회원가입

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123",
    "full_name": "홍길동"
  }'
```

응답:
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "myuser",
    "full_name": "홍길동",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00"
}
```

### 로그인

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"
```

응답:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

### 토큰 사용

모든 인증이 필요한 API 호출에 토큰을 포함합니다:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 토큰 갱신

액세스 토큰이 만료되면 리프레시 토큰으로 새 토큰을 발급받습니다:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

---

## 사용자 관리

### 내 정보 조회

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {token}"
```

### 내 정보 수정

```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "김철수",
    "email": "newemail@example.com"
  }'
```

### 비밀번호 변경

```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePass456"
  }'
```

### 사용자 목록 조회 (관리자)

```bash
curl "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer {admin_token}"
```

---

## 게시판

### 게시글 목록 조회

```bash
# 기본 조회
curl http://localhost:8000/api/v1/posts/

# 페이지네이션
curl "http://localhost:8000/api/v1/posts/?page=1&size=10"

# 검색
curl "http://localhost:8000/api/v1/posts/?search=FastAPI"

# 카테고리 필터
curl "http://localhost:8000/api/v1/posts/?category_id=1"
```

응답:
```json
{
    "items": [
        {
            "id": 1,
            "title": "FastAPI 시작하기",
            "content": "FastAPI는...",
            "slug": "fastapi-시작하기-1",
            "view_count": 100,
            "author": {
                "id": 1,
                "username": "admin"
            },
            "created_at": "2024-01-01T00:00:00"
        }
    ],
    "total": 50,
    "page": 1,
    "size": 10,
    "pages": 5
}
```

### 게시글 작성

```bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "새 게시글",
    "content": "게시글 내용입니다.",
    "category_id": 1,
    "is_published": true
  }'
```

### 게시글 상세 조회

```bash
curl http://localhost:8000/api/v1/posts/1
```

### 게시글 수정

```bash
curl -X PUT http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "수정된 제목",
    "content": "수정된 내용"
  }'
```

### 게시글 삭제

```bash
curl -X DELETE http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer {token}"
```

### 댓글 작성

```bash
curl -X POST http://localhost:8000/api/v1/posts/1/comments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "좋은 글입니다!"
  }'
```

### 대댓글 작성

```bash
curl -X POST http://localhost:8000/api/v1/posts/1/comments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "감사합니다!",
    "parent_id": 1
  }'
```

### 댓글 목록 조회

```bash
curl http://localhost:8000/api/v1/posts/1/comments
```

---

## 대시보드

대시보드는 사용자 역할에 따라 다른 정보를 표시합니다.

### 권한별 표시 정보

| 정보 | 관리자 | 일반 사용자 |
|------|--------|-------------|
| 전체 사용자 수 | O | X |
| 전체 게시글 수 | O | O |
| 전체 댓글 수 | O | X |
| 오늘 가입자 수 | O | X |
| 오늘 게시글 수 | X | O |
| 내 게시글 수 | X | O |
| 내 댓글 수 | X | O |
| 최근 가입 사용자 | O | X |
| 최근 게시글 | O | O |

### 통계 조회

```bash
curl http://localhost:8000/api/v1/dashboard/ \
  -H "Authorization: Bearer {token}"
```

응답:
```json
{
    "total_posts": 150,
    "total_users": 50,
    "total_comments": 320,
    "posts_today": 5,
    "users_today": 2,
    "my_posts": 10,
    "my_comments": 25
}
```

### 관리자 통계 (관리자)

```bash
curl http://localhost:8000/api/v1/dashboard/admin \
  -H "Authorization: Bearer {admin_token}"
```

### 최근 게시글

```bash
curl "http://localhost:8000/api/v1/dashboard/recent-posts?limit=5" \
  -H "Authorization: Bearer {token}"
```

### 최근 가입자 (관리자)

```bash
curl "http://localhost:8000/api/v1/dashboard/recent-users?limit=5" \
  -H "Authorization: Bearer {admin_token}"
```

---

## 테마 설정

### 사용 가능한 테마 조회

```bash
curl http://localhost:8000/api/v1/theme/available
```

응답:
```json
{
    "themes": ["light", "dark", "blue", "green"],
    "default_theme": "light"
}
```

### 내 테마 설정 조회

```bash
curl http://localhost:8000/api/v1/theme/ \
  -H "Authorization: Bearer {token}"
```

### 테마 설정 변경

```bash
curl -X PUT http://localhost:8000/api/v1/theme/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "theme_name": "dark",
    "sidebar_collapsed": true,
    "custom_settings": {
        "font_size": "large",
        "language": "ko"
    }
  }'
```

---

## 메뉴 관리

### 메뉴 트리 조회

```bash
# 비로그인 (공개 메뉴만)
curl http://localhost:8000/api/v1/menu/

# 로그인 (역할에 따른 메뉴)
curl http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {token}"
```

응답:
```json
{
    "menus": [
        {
            "id": 1,
            "name": "대시보드",
            "url": "/dashboard",
            "icon": "fa-dashboard",
            "children": []
        },
        {
            "id": 2,
            "name": "게시판",
            "url": "/posts",
            "icon": "fa-list",
            "children": [
                {
                    "id": 3,
                    "name": "공지사항",
                    "url": "/posts/notices"
                }
            ]
        }
    ]
}
```

### 기본 메뉴 초기화 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/init-default \
  -H "Authorization: Bearer {admin_token}"
```

### 메뉴 생성 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "새 메뉴",
    "url": "/new-menu",
    "icon": "fa-star",
    "order": 5
  }'
```

### 하위 메뉴 생성 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "하위 메뉴",
    "url": "/parent/child",
    "parent_id": 1,
    "order": 0
  }'
```

### 메뉴 수정 (관리자)

```bash
curl -X PUT http://localhost:8000/api/v1/menu/1 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "수정된 메뉴",
    "is_active": false
  }'
```

### 메뉴 삭제 (관리자)

```bash
curl -X DELETE http://localhost:8000/api/v1/menu/1 \
  -H "Authorization: Bearer {admin_token}"
```

---

## HTTP 상태 코드

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성됨 |
| 204 | 삭제됨 (내용 없음) |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 찾을 수 없음 |
| 422 | 검증 실패 |
| 500 | 서버 오류 |

---

## 다음 단계

- [API 레퍼런스](04_api_reference.md): 전체 API 상세 문서
- [수정 및 확장](05_customization.md): 커스터마이징 가이드
