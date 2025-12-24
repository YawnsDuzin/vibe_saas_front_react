# API 연동 가이드

## 개요

이 문서에서는 프론트엔드에서 FastAPI 백엔드와 통신하는 방법을 설명합니다. API 클라이언트 구조, HTTP 요청 방법, 에러 처리 등을 다룹니다.

---

## 1. API 클라이언트 구조

### 폴더 구조

```
src/lib/api/
├── client.ts       # 공통 API 클라이언트 (fetch 래퍼)
├── auth.ts         # 인증 API
├── posts.ts        # 게시글 API
├── users.ts        # 사용자 API
├── dashboard.ts    # 대시보드 API
└── index.ts        # 내보내기
```

---

## 2. client.ts - 공통 API 클라이언트

### 전체 코드

```tsx
// src/lib/api/client.ts
import Cookies from "js-cookie";

// API 기본 URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ─────────────────────────────────────────────
// 토큰 관리 함수
// ─────────────────────────────────────────────

// Access Token 가져오기
export const getAccessToken = (): string | undefined => {
  return Cookies.get("access_token");
};

// Refresh Token 가져오기
export const getRefreshToken = (): string | undefined => {
  return Cookies.get("refresh_token");
};

// 토큰 저장 (쿠키)
export const setTokens = (accessToken: string, refreshToken: string) => {
  Cookies.set("access_token", accessToken, { expires: 1 });    // 1일
  Cookies.set("refresh_token", refreshToken, { expires: 7 });  // 7일
};

// 토큰 삭제
export const clearTokens = () => {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
};

// ─────────────────────────────────────────────
// 에러 클래스
// ─────────────────────────────────────────────

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.status = status;
    this.detail = detail || message;
  }
}

// ─────────────────────────────────────────────
// 공통 Fetch 함수
// ─────────────────────────────────────────────

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();

  // 기본 헤더
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // 토큰이 있으면 Authorization 헤더 추가
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  // API 요청
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // 401 에러: 토큰 만료 → 갱신 시도
  if (response.status === 401) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        // 토큰 갱신
        const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const tokens = await refreshResponse.json();
          setTokens(tokens.access_token, tokens.refresh_token);

          // 원래 요청 재시도
          (headers as Record<string, string>)["Authorization"] = `Bearer ${tokens.access_token}`;
          const retryResponse = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
          });

          if (!retryResponse.ok) {
            throw new ApiError(retryResponse.status, "API 요청 실패");
          }

          return retryResponse.json();
        }
      } catch {
        // 갱신 실패 → 로그아웃
        clearTokens();
        window.location.href = "/login";
      }
    } else {
      // Refresh Token 없음 → 로그인 페이지로
      clearTokens();
      window.location.href = "/login";
    }
  }

  // 에러 응답 처리
  if (!response.ok) {
    let errorDetail = "API 요청 실패";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorData.message || errorDetail;
    } catch {
      // JSON 파싱 실패 시 기본 메시지 사용
    }
    throw new ApiError(response.status, errorDetail);
  }

  // 성공 응답
  return response.json();
}

// ─────────────────────────────────────────────
// HTTP 메서드별 헬퍼 함수
// ─────────────────────────────────────────────

export const api = {
  get: <T>(endpoint: string) =>
    fetchApi<T>(endpoint, { method: "GET" }),

  post: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    fetchApi<T>(endpoint, { method: "DELETE" }),
};
```

### 핵심 기능 설명

#### 1. 토큰 관리

```tsx
// 쿠키에 토큰 저장/조회/삭제
setTokens(accessToken, refreshToken);  // 저장
const token = getAccessToken();        // 조회
clearTokens();                         // 삭제
```

**왜 쿠키를 사용하나요?**
- 미들웨어에서 접근 가능 (서버 사이드)
- 만료 시간 설정 가능
- 자동으로 요청에 포함 가능

#### 2. 자동 토큰 갱신

```
┌─────────────────────────────────────────────────────────────┐
│                    토큰 갱신 플로우                          │
└─────────────────────────────────────────────────────────────┘

    클라이언트              API 서버
        │                      │
        │ ── 요청 (만료된 토큰) ─▶
        │                      │
        │ ◀── 401 Unauthorized ──
        │                      │
        │ ── /auth/refresh ────▶  (refresh_token으로)
        │                      │
        │ ◀── 새 토큰 반환 ─────
        │                      │
        │ ── 원래 요청 재시도 ──▶  (새 access_token으로)
        │                      │
        │ ◀── 정상 응답 ────────
```

#### 3. 에러 처리

```tsx
class ApiError extends Error {
  status: number;   // HTTP 상태 코드 (401, 404, 500 등)
  detail: string;   // 에러 상세 메시지
}

// 사용
try {
  await api.get("/posts");
} catch (error) {
  if (error instanceof ApiError) {
    console.log(error.status);  // 404
    console.log(error.detail);  // "게시글을 찾을 수 없습니다"
  }
}
```

---

## 3. auth.ts - 인증 API

```tsx
// src/lib/api/auth.ts
import { api, setTokens, clearTokens } from "./client";
import type { User, Token, LoginRequest, RegisterRequest } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const authApi = {
  // 로그인 (OAuth2 형식: FormData)
  login: async (username: string, password: string): Promise<Token> => {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      body: formData,  // JSON이 아닌 FormData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "로그인 실패");
    }

    return response.json();
  },

  // 회원가입
  register: async (data: RegisterRequest): Promise<User> => {
    return api.post<User>("/auth/register", data);
  },

  // 현재 사용자 정보
  getCurrentUser: async (): Promise<User> => {
    return api.get<User>("/users/me");
  },

  // 토큰 갱신
  refreshToken: async (refreshToken: string): Promise<Token> => {
    return api.post<Token>("/auth/refresh", { refresh_token: refreshToken });
  },

  // 로그아웃
  logout: () => {
    clearTokens();
    window.location.href = "/login";
  },
};
```

**로그인 요청 형식:**
- OAuth2 표준을 따르므로 **FormData** 형식 사용
- `Content-Type: multipart/form-data` (자동 설정)

---

## 4. posts.ts - 게시글 API

```tsx
// src/lib/api/posts.ts
import { api } from "./client";
import type {
  Post,
  PostCreate,
  PostUpdate,
  PostListResponse,
  Comment,
  CommentCreate,
  PaginationParams,
} from "@/types";

export const postsApi = {
  // 게시글 목록 (페이지네이션, 검색)
  getList: async (params?: PaginationParams): Promise<PostListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.size) searchParams.append("size", params.size.toString());
    if (params?.search) searchParams.append("search", params.search);

    const query = searchParams.toString();
    return api.get<PostListResponse>(`/posts${query ? `?${query}` : ""}`);
  },

  // 게시글 상세
  getById: async (id: number): Promise<Post> => {
    return api.get<Post>(`/posts/${id}`);
  },

  // 게시글 작성
  create: async (data: PostCreate): Promise<Post> => {
    return api.post<Post>("/posts", data);
  },

  // 게시글 수정
  update: async (id: number, data: PostUpdate): Promise<Post> => {
    return api.put<Post>(`/posts/${id}`, data);
  },

  // 게시글 삭제
  delete: async (id: number): Promise<void> => {
    return api.delete<void>(`/posts/${id}`);
  },

  // ─── 댓글 API ───

  // 댓글 목록
  getComments: async (postId: number): Promise<Comment[]> => {
    return api.get<Comment[]>(`/posts/${postId}/comments`);
  },

  // 댓글 작성
  createComment: async (postId: number, data: CommentCreate): Promise<Comment> => {
    return api.post<Comment>(`/posts/${postId}/comments`, data);
  },

  // 댓글 삭제
  deleteComment: async (postId: number, commentId: number): Promise<void> => {
    return api.delete<void>(`/posts/${postId}/comments/${commentId}`);
  },
};
```

---

## 5. users.ts - 사용자 API

```tsx
// src/lib/api/users.ts
import { api } from "./client";
import type { User, UserUpdate, UserListResponse, PaginationParams } from "@/types";

export const usersApi = {
  // 사용자 목록 (관리자용)
  getList: async (params?: PaginationParams): Promise<UserListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.size) searchParams.append("size", params.size.toString());
    if (params?.search) searchParams.append("search", params.search);

    const query = searchParams.toString();
    return api.get<UserListResponse>(`/users${query ? `?${query}` : ""}`);
  },

  // 사용자 상세
  getById: async (id: number): Promise<User> => {
    return api.get<User>(`/users/${id}`);
  },

  // 사용자 정보 수정
  update: async (id: number, data: UserUpdate): Promise<User> => {
    return api.patch<User>(`/users/${id}`, data);
  },

  // 비밀번호 변경
  updatePassword: async (id: number, data: { current_password: string; new_password: string }): Promise<void> => {
    return api.patch<void>(`/users/${id}/password`, data);
  },

  // 사용자 삭제 (관리자용)
  delete: async (id: number): Promise<void> => {
    return api.delete<void>(`/users/${id}`);
  },

  // 사용자 활성화/비활성화 (관리자용)
  toggleActive: async (id: number, isActive: boolean): Promise<User> => {
    return api.patch<User>(`/users/${id}`, { is_active: isActive });
  },
};
```

---

## 6. dashboard.ts - 대시보드 API

```tsx
// src/lib/api/dashboard.ts
import { api } from "./client";
import type { DashboardStats, Post, User } from "@/types";

interface DashboardData extends DashboardStats {
  recent_users: User[];
  recent_posts: Post[];
}

export const dashboardApi = {
  // 대시보드 통계 + 최근 데이터
  getStats: async (): Promise<DashboardData> => {
    // 여러 API 병렬 호출
    const [stats, recentPosts] = await Promise.all([
      api.get<DashboardStats>("/dashboard"),
      api.get<Post[]>("/dashboard/recent-posts"),
    ]);

    return {
      ...stats,
      recent_posts: recentPosts,
    };
  },
};
```

---

## 7. 컴포넌트에서 API 사용

### 기본 패턴

```tsx
"use client";

import { useState, useEffect } from "react";
import { postsApi } from "@/lib/api";
import type { Post } from "@/types";

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 데이터 로드
  useEffect(() => {
    const loadPosts = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await postsApi.getList({ page: 1, size: 10 });
        setPosts(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "로드 실패");
      } finally {
        setIsLoading(false);
      }
    };

    loadPosts();
  }, []);

  // 로딩 중
  if (isLoading) return <div>로딩 중...</div>;

  // 에러
  if (error) return <div>에러: {error}</div>;

  // 정상 렌더링
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

### 페이지네이션 패턴

```tsx
export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  // 페이지 또는 검색어 변경 시 데이터 다시 로드
  useEffect(() => {
    const loadPosts = async () => {
      const response = await postsApi.getList({
        page: currentPage,
        size: 10,
        search: searchQuery,
      });
      setPosts(response.items);
      setTotalPages(response.pages);
    };
    loadPosts();
  }, [currentPage, searchQuery]);  // 의존성

  // 검색
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);  // 검색 시 첫 페이지로
  };

  // 페이지 변경
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div>
      <input value={searchQuery} onChange={handleSearch} placeholder="검색..." />

      <ul>
        {posts.map(post => <li key={post.id}>{post.title}</li>)}
      </ul>

      <div>
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i + 1}
            onClick={() => handlePageChange(i + 1)}
            className={currentPage === i + 1 ? "active" : ""}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}
```

### CRUD 패턴

```tsx
export default function PostDetailPage({ params }: { params: { id: string } }) {
  const [post, setPost] = useState<Post | null>(null);
  const router = useRouter();

  // Read
  useEffect(() => {
    postsApi.getById(Number(params.id)).then(setPost);
  }, [params.id]);

  // Update
  const handleUpdate = async (data: PostUpdate) => {
    try {
      const updated = await postsApi.update(Number(params.id), data);
      setPost(updated);
      toast.success("수정되었습니다");
    } catch {
      toast.error("수정 실패");
    }
  };

  // Delete
  const handleDelete = async () => {
    try {
      await postsApi.delete(Number(params.id));
      toast.success("삭제되었습니다");
      router.push("/posts");
    } catch {
      toast.error("삭제 실패");
    }
  };

  return (
    <div>
      <h1>{post?.title}</h1>
      <button onClick={handleDelete}>삭제</button>
    </div>
  );
}
```

---

## 8. API 엔드포인트 요약

### 인증 API

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/auth/login` | 로그인 (FormData) |
| POST | `/auth/register` | 회원가입 |
| POST | `/auth/refresh` | 토큰 갱신 |
| GET | `/users/me` | 현재 사용자 정보 |

### 게시글 API

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/posts` | 목록 (페이지네이션) |
| GET | `/posts/:id` | 상세 |
| POST | `/posts` | 작성 |
| PUT | `/posts/:id` | 수정 |
| DELETE | `/posts/:id` | 삭제 |

### 댓글 API

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/posts/:id/comments` | 댓글 목록 |
| POST | `/posts/:id/comments` | 댓글 작성 |
| DELETE | `/posts/:id/comments/:commentId` | 댓글 삭제 |

### 사용자 API

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/users` | 목록 (관리자) |
| GET | `/users/:id` | 상세 |
| PATCH | `/users/:id` | 수정 |
| DELETE | `/users/:id` | 삭제 (관리자) |

---

## 요약

| 개념 | 설명 |
|------|------|
| API 클라이언트 | fetch를 래핑한 공통 함수 |
| 토큰 관리 | 쿠키로 저장/조회/삭제 |
| 자동 갱신 | 401 에러 시 refresh token으로 갱신 |
| 에러 처리 | ApiError 클래스로 상태/메시지 관리 |
| HTTP 헬퍼 | api.get, api.post 등 간편 함수 |

## 다음 단계

다음 문서 [10-authentication.md](./10-authentication.md)에서 인증 시스템을 상세히 학습합니다.
