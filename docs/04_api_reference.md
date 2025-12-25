# API 레퍼런스

이 문서는 모든 API 엔드포인트의 상세 명세를 제공합니다.

## API 개요

- **Base URL**: `/api/v1`
- **인증**: Bearer Token (JWT)
- **Content-Type**: `application/json`

---

## 인증 API

### POST /auth/register

새 사용자를 등록합니다.

**Request Body:**
```json
{
    "email": "string (required)",
    "username": "string (required, 3-50자)",
    "password": "string (required, 8자 이상)",
    "full_name": "string (optional)"
}
```

**Response (201):**
```json
{
    "id": "integer",
    "email": "string",
    "username": "string",
    "full_name": "string | null",
    "role": "string",
    "is_active": "boolean",
    "is_verified": "boolean",
    "created_at": "datetime",
    "last_login": "datetime | null"
}
```

**Errors:**
- 400: 이메일/사용자명 중복
- 422: 검증 실패

---

### POST /auth/login

로그인하여 토큰을 발급받습니다.

**Request Body (form-data):**
```
username: string (이메일 또는 사용자명)
password: string
```

**Response (200):**
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
}
```

**Errors:**
- 401: 인증 실패
- 400: 비활성화된 계정

---

### POST /auth/refresh

토큰을 갱신합니다.

**Request Body:**
```json
{
    "refresh_token": "string"
}
```

**Response (200):**
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
}
```

---

### GET /auth/me

현재 사용자 정보를 조회합니다.

**Headers:** `Authorization: Bearer {token}`

**Response (200):** UserResponse

---

## 사용자 API

### GET /users/

사용자 목록을 조회합니다. (관리자 전용)

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `is_active`: boolean (optional)

**Response (200):** UserResponse[]

---

### GET /users/{user_id}

특정 사용자를 조회합니다.

**Response (200):** UserResponse

---

### PUT /users/{user_id}

사용자 정보를 수정합니다.

**Request Body:**
```json
{
    "email": "string (optional)",
    "username": "string (optional)",
    "full_name": "string (optional)",
    "password": "string (optional)"
}
```

---

### DELETE /users/{user_id}

사용자를 삭제합니다. (관리자 전용)

**Response (204):** No Content

---

## 게시판 API

### GET /posts/

게시글 목록을 조회합니다.

**Query Parameters:**
- `page`: integer (default: 1)
- `size`: integer (default: 10, max: 50)
- `category_id`: integer (optional)
- `search`: string (optional)

**Response (200):**
```json
{
    "items": "PostResponse[]",
    "total": "integer",
    "page": "integer",
    "size": "integer",
    "pages": "integer"
}
```

---

### POST /posts/

게시글을 작성합니다.

**Request Body:**
```json
{
    "title": "string (1-200자)",
    "content": "string",
    "category_id": "integer (optional)",
    "is_published": "boolean (default: true)"
}
```

**Response (201):** PostResponse

---

### GET /posts/{post_id}

게시글 상세를 조회합니다.

**Response (200):** PostResponse

---

### PUT /posts/{post_id}

게시글을 수정합니다.

**Request Body:**
```json
{
    "title": "string (optional)",
    "content": "string (optional)",
    "category_id": "integer (optional)",
    "is_published": "boolean (optional)",
    "is_pinned": "boolean (optional)"
}
```

---

### DELETE /posts/{post_id}

게시글을 삭제합니다.

**Response (204):** No Content

---

### GET /posts/categories

카테고리 목록을 조회합니다.

**Response (200):** CategoryResponse[]

---

### POST /posts/categories

카테고리를 생성합니다. (관리자 전용)

**Request Body:**
```json
{
    "name": "string",
    "slug": "string",
    "description": "string (optional)",
    "order": "integer (default: 0)"
}
```

---

### GET /posts/{post_id}/comments

게시글의 댓글을 조회합니다.

**Response (200):** CommentResponse[]

---

### POST /posts/{post_id}/comments

댓글을 작성합니다.

**Request Body:**
```json
{
    "content": "string (1-1000자)",
    "parent_id": "integer (optional, 대댓글)"
}
```

---

### DELETE /posts/comments/{comment_id}

댓글을 삭제합니다.

**Response (204):** No Content

---

## 대시보드 API

### GET /dashboard/

사용자 대시보드 통계를 조회합니다.

**Response (200):**
```json
{
    "total_posts": "integer",
    "total_users": "integer",
    "total_comments": "integer",
    "posts_today": "integer",
    "users_today": "integer",
    "my_posts": "integer",
    "my_comments": "integer"
}
```

---

### GET /dashboard/admin

관리자 대시보드를 조회합니다. (관리자 전용)

**Response (200):** AdminDashboardStats

---

### GET /dashboard/recent-posts

최근 게시글을 조회합니다.

**Query Parameters:**
- `limit`: integer (default: 5)

---

### GET /dashboard/recent-users

최근 가입자를 조회합니다. (관리자 전용)

---

## 테마 API

### GET /theme/available

사용 가능한 테마를 조회합니다.

**Response (200):**
```json
{
    "themes": ["light", "dark", "blue", "green"],
    "default_theme": "light"
}
```

---

### GET /theme/

내 테마 설정을 조회합니다.

**Response (200):** ThemeResponse

---

### PUT /theme/

테마 설정을 수정합니다.

**Request Body:**
```json
{
    "theme_name": "string (optional)",
    "sidebar_collapsed": "boolean (optional)",
    "custom_settings": "object (optional)"
}
```

---

## 메뉴 API

### GET /menu/

메뉴 트리를 조회합니다.

**Response (200):**
```json
{
    "menus": "MenuResponse[]"
}
```

---

### POST /menu/

메뉴를 생성합니다. (관리자 전용)

**Request Body:**
```json
{
    "name": "string",
    "url": "string (optional)",
    "icon": "string (optional)",
    "parent_id": "integer (optional)",
    "order": "integer (default: 0)",
    "required_role": "string (optional)"
}
```

---

### PUT /menu/{menu_id}

메뉴를 수정합니다. (관리자 전용)

---

### DELETE /menu/{menu_id}

메뉴를 삭제합니다. (관리자 전용)

---

### POST /menu/init-default

기본 메뉴를 초기화합니다. (관리자 전용)

---

## 파일 API

### GET /files/storage-info

스토리지 정보를 조회합니다.

**Response (200):**
```json
{
    "storage_type": "local",
    "max_file_size": 10485760,
    "allowed_types": ["image/jpeg", "image/png", "image/gif", "application/pdf"],
    "allowed_extensions": ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]
}
```

---

### POST /files/upload

파일을 업로드합니다.

**Request (multipart/form-data):**
- `file`: File (required)
- `folder`: string (optional)
- `alt_text`: string (optional)
- `description`: string (optional)

**Response (201):**
```json
{
    "id": "integer",
    "filename": "string",
    "url": "string",
    "content_type": "string",
    "size": "integer",
    "size_formatted": "string"
}
```

---

### POST /files/upload-multiple

여러 파일을 업로드합니다.

**Request (multipart/form-data):**
- `files`: File[] (required)
- `folder`: string (optional)

**Response (201):** FileUploadResponse[]

---

### GET /files/

현재 사용자의 파일 목록을 조회합니다.

**Query Parameters:**
- `page`: integer (default: 1)
- `size`: integer (default: 20)
- `content_type`: string (optional, 예: "image/")
- `folder`: string (optional)

**Response (200):**
```json
{
    "items": "FileResponse[]",
    "total": "integer",
    "page": "integer",
    "size": "integer",
    "pages": "integer"
}
```

---

### GET /files/{file_id}

파일 상세 정보를 조회합니다.

**Response (200):** FileResponse

---

### PATCH /files/{file_id}

파일 메타데이터를 수정합니다.

**Request Body:**
```json
{
    "alt_text": "string (optional)",
    "description": "string (optional)"
}
```

---

### DELETE /files/{file_id}

파일을 삭제합니다.

**Response (204):** No Content

---

### GET /files/admin/all

모든 파일을 조회합니다. (관리자 전용)

**Query Parameters:**
- `page`: integer (default: 1)
- `size`: integer (default: 20)
- `content_type`: string (optional)
- `uploader_id`: integer (optional)

**Response (200):** FileListResponse

---

## 에러 응답 형식

모든 에러는 다음 형식으로 반환됩니다:

```json
{
    "detail": "에러 메시지"
}
```

검증 에러 (422):
```json
{
    "detail": "입력값 검증에 실패했습니다.",
    "errors": [
        {
            "field": "body -> email",
            "message": "value is not a valid email address",
            "type": "value_error.email"
        }
    ]
}
```

---

## 스키마 정의

### UserResponse

```json
{
    "id": "integer",
    "email": "string",
    "username": "string",
    "full_name": "string | null",
    "role": "admin | moderator | user",
    "is_active": "boolean",
    "is_verified": "boolean",
    "created_at": "datetime",
    "last_login": "datetime | null"
}
```

### PostResponse

```json
{
    "id": "integer",
    "title": "string",
    "content": "string",
    "slug": "string",
    "view_count": "integer",
    "is_published": "boolean",
    "is_pinned": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime | null",
    "author": "AuthorInfo",
    "category": "CategoryResponse | null",
    "comment_count": "integer"
}
```

### CommentResponse

```json
{
    "id": "integer",
    "content": "string",
    "author": "AuthorInfo",
    "post_id": "integer",
    "parent_id": "integer | null",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime | null",
    "replies": "CommentResponse[]"
}
```

### FileResponse

```json
{
    "id": "integer",
    "filename": "string",
    "storage_key": "string",
    "content_type": "string",
    "size": "integer",
    "url": "string",
    "storage_type": "string",
    "folder": "string",
    "alt_text": "string | null",
    "description": "string | null",
    "uploader_id": "integer",
    "created_at": "datetime",
    "updated_at": "datetime",
    "extension": "string",
    "is_image": "boolean",
    "size_formatted": "string"
}
```

### FileListResponse

```json
{
    "items": "FileResponse[]",
    "total": "integer",
    "page": "integer",
    "size": "integer",
    "pages": "integer"
}
```

### StorageInfoResponse

```json
{
    "storage_type": "string",
    "max_file_size": "integer",
    "allowed_types": "string[]",
    "allowed_extensions": "string[]"
}
```
