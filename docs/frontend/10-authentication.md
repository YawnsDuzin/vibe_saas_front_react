# 인증 시스템 상세 가이드

## 개요

이 프로젝트는 **JWT (JSON Web Token)** 기반의 인증 시스템을 사용합니다. Access Token과 Refresh Token을 이용한 보안 인증 플로우를 구현합니다.

---

## 1. JWT 인증 이해하기

### JWT란?

JWT는 JSON 형식의 정보를 안전하게 전송하기 위한 토큰입니다.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

헤더.페이로드.서명
```

### Access Token vs Refresh Token

```
┌─────────────────────────────────────────────────────────────┐
│              Access Token vs Refresh Token                   │
├────────────────────────────┬────────────────────────────────┤
│       Access Token         │        Refresh Token           │
├────────────────────────────┼────────────────────────────────┤
│  짧은 수명 (15분~1시간)     │  긴 수명 (7일~30일)            │
│  API 요청에 사용           │  Access Token 갱신에만 사용    │
│  탈취 시 위험 기간 짧음     │  안전하게 저장 필요            │
│  매 요청마다 전송          │  갱신 시에만 전송              │
└────────────────────────────┴────────────────────────────────┘
```

### 인증 플로우

```
┌─────────────────────────────────────────────────────────────┐
│                      인증 플로우                             │
└─────────────────────────────────────────────────────────────┘

1. 로그인
   ┌────────┐        ┌────────┐
   │ Client │ ──────▶│ Server │
   └────────┘ 아이디  └────────┘
              비밀번호
                         │
                    인증 확인
                         │
   ┌────────┐        ┌───▼────┐
   │ Client │ ◀──────│ Server │
   └────────┘ Access └────────┘
              Refresh
              Token

2. API 요청
   ┌────────┐        ┌────────┐
   │ Client │ ──────▶│ Server │
   └────────┘ Access └────────┘
              Token      │
                    토큰 검증
                         │
   ┌────────┐        ┌───▼────┐
   │ Client │ ◀──────│ Server │
   └────────┘  응답   └────────┘

3. 토큰 만료 시
   ┌────────┐        ┌────────┐
   │ Client │ ──────▶│ Server │  ← 만료된 Access Token
   └────────┘        └────────┘
                         │
                    401 Unauthorized
                         │
   ┌────────┐        ┌───▼────┐
   │ Client │ ──────▶│ Server │  ← Refresh Token으로 갱신 요청
   └────────┘        └────────┘
                         │
                    새 Access Token 발급
                         │
   ┌────────┐        ┌───▼────┐
   │ Client │ ◀──────│ Server │
   └────────┘ 새 토큰 └────────┘
```

---

## 2. 프로젝트 인증 구현

### 토큰 저장 위치

```tsx
// src/lib/api/client.ts
import Cookies from "js-cookie";

// 토큰 저장
export const setTokens = (accessToken: string, refreshToken: string) => {
  Cookies.set("access_token", accessToken, { expires: 1 });    // 1일
  Cookies.set("refresh_token", refreshToken, { expires: 7 });  // 7일
};

// 토큰 조회
export const getAccessToken = (): string | undefined => {
  return Cookies.get("access_token");
};

export const getRefreshToken = (): string | undefined => {
  return Cookies.get("refresh_token");
};

// 토큰 삭제
export const clearTokens = () => {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
};
```

**왜 쿠키를 사용하나요?**

| 저장소 | 장점 | 단점 |
|--------|------|------|
| Cookie | 서버(미들웨어)에서 접근 가능, 만료 시간 설정 | XSS에 취약 (HttpOnly로 해결) |
| localStorage | 간편함 | 서버에서 접근 불가, XSS에 취약 |
| sessionStorage | 탭 닫으면 삭제 | 서버에서 접근 불가 |

---

## 3. 인증 관련 컴포넌트

### 로그인 페이지

```tsx
// src/app/(auth)/login/page.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/authStore";

// 검증 스키마
const loginSchema = z.object({
  username: z.string().min(1, "사용자명 또는 이메일을 입력하세요"),
  password: z.string().min(1, "비밀번호를 입력하세요"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, isAuthenticated, error, clearError } = useAuthStore();

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // 이미 로그인되어 있으면 대시보드로
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  // 에러 표시
  useEffect(() => {
    if (error) {
      toast.error(error);
      clearError();
    }
  }, [error, clearError]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.username, data.password);
      toast.success("로그인 성공!");
      router.push("/dashboard");
    } catch {
      // 에러는 store에서 처리
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>로그인</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="username">사용자명 또는 이메일</Label>
            <Input {...register("username")} />
            {errors.username && (
              <p className="text-destructive text-sm">{errors.username.message}</p>
            )}
          </div>
          <div>
            <Label htmlFor="password">비밀번호</Label>
            <Input type="password" {...register("password")} />
            {errors.password && (
              <p className="text-destructive text-sm">{errors.password.message}</p>
            )}
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "로그인 중..." : "로그인"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
```

### 회원가입 페이지

```tsx
// src/app/(auth)/register/page.tsx
"use client";

const registerSchema = z.object({
  email: z.string().email("올바른 이메일을 입력하세요"),
  username: z.string()
    .min(3, "3자 이상 입력하세요")
    .max(50, "50자 이하로 입력하세요")
    .regex(/^[a-zA-Z][a-zA-Z0-9_]*$/, "영문으로 시작, 영문/숫자/밑줄만 허용"),
  password: z.string()
    .min(8, "8자 이상 입력하세요")
    .regex(/[A-Z]/, "대문자를 포함해야 합니다")
    .regex(/[a-z]/, "소문자를 포함해야 합니다")
    .regex(/[0-9]/, "숫자를 포함해야 합니다"),
  confirmPassword: z.string(),
  full_name: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "비밀번호가 일치하지 않습니다",
  path: ["confirmPassword"],
});

export default function RegisterPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data) => {
    try {
      await authApi.register(data);
      toast.success("회원가입 완료! 로그인 페이지로 이동합니다.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "회원가입 실패");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* 폼 필드들 */}
    </form>
  );
}
```

---

## 4. authStore 상세

```tsx
// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authApi, setTokens, clearTokens } from "@/lib/api";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // 로그인
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          // 1. 로그인 API 호출 → 토큰 반환
          const tokens = await authApi.login(username, password);

          // 2. 토큰 쿠키에 저장
          setTokens(tokens.access_token, tokens.refresh_token);

          // 3. 사용자 정보 조회
          const user = await authApi.getCurrentUser();

          // 4. 상태 업데이트
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "로그인 실패",
            isLoading: false,
          });
          throw error;
        }
      },

      // 로그아웃
      logout: () => {
        clearTokens();
        set({ user: null, isAuthenticated: false });
      },

      // 저장된 토큰으로 사용자 정보 조회
      fetchUser: async () => {
        set({ isLoading: true });
        try {
          const user = await authApi.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

---

## 5. 미들웨어로 라우트 보호

```tsx
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// 인증이 필요한 경로
const protectedRoutes = ["/dashboard", "/posts", "/users", "/settings"];
// 로그인 상태에서 접근 불가한 경로
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token");

  // 보호된 경로에 토큰 없이 접근 → 로그인으로 리다이렉트
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );
  if (isProtectedRoute && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);  // 원래 경로 저장
    return NextResponse.redirect(loginUrl);
  }

  // 인증 페이지에 이미 로그인된 상태로 접근 → 대시보드로
  const isAuthRoute = authRoutes.some(route =>
    pathname.startsWith(route)
  );
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/posts/:path*",
    "/users/:path*",
    "/settings/:path*",
    "/login",
    "/register",
  ],
};
```

### 미들웨어 동작 흐름

```
요청: /dashboard
    │
    ▼
미들웨어 실행
    │
토큰 있음? ─── No ───▶ /login으로 리다이렉트
    │
   Yes
    │
    ▼
페이지 렌더링

────────────────────────────────────────

요청: /login
    │
    ▼
미들웨어 실행
    │
토큰 있음? ─── Yes ───▶ /dashboard로 리다이렉트
    │
    No
    │
    ▼
로그인 페이지 렌더링
```

---

## 6. 자동 토큰 갱신

```tsx
// src/lib/api/client.ts
export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();

  // 헤더에 토큰 추가
  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  // 401 에러: 토큰 만료
  if (response.status === 401) {
    const refreshToken = getRefreshToken();

    if (refreshToken) {
      try {
        // 토큰 갱신 요청
        const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const tokens = await refreshResponse.json();
          setTokens(tokens.access_token, tokens.refresh_token);

          // 원래 요청 재시도
          return fetchApi(endpoint, options);
        }
      } catch {
        // 갱신 실패 → 로그아웃
      }
    }

    // 토큰 없거나 갱신 실패 → 로그인 페이지로
    clearTokens();
    window.location.href = "/login";
  }

  if (!response.ok) {
    throw new ApiError(response.status, "API 요청 실패");
  }

  return response.json();
}
```

---

## 7. 권한 기반 접근 제어

### 역할 (Role) 정의

```tsx
// src/types/index.ts
export type UserRole = "admin" | "moderator" | "user";

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  // ...
}
```

### 메뉴 권한 필터링

```tsx
// src/components/layout/Sidebar.tsx
const menuItems = [
  { href: "/dashboard", label: "대시보드", icon: Home },
  { href: "/posts", label: "게시글", icon: FileText },
  { href: "/users", label: "사용자 관리", icon: Users, roles: ["admin", "moderator"] },
  { href: "/settings", label: "설정", icon: Settings },
];

export const Sidebar = () => {
  const { user } = useAuthStore();

  // 권한에 따른 메뉴 필터링
  const filteredMenuItems = menuItems.filter(item => {
    if (!item.roles) return true;  // roles 없으면 모두에게 표시
    return item.roles.includes(user?.role as UserRole);
  });

  return (
    <nav>
      {filteredMenuItems.map(item => (
        <Link key={item.href} href={item.href}>
          {item.label}
        </Link>
      ))}
    </nav>
  );
};
```

### 페이지 내 권한 체크

```tsx
// src/app/(main)/users/page.tsx
export default function UsersPage() {
  const { user } = useAuthStore();
  const router = useRouter();

  // 권한 체크
  useEffect(() => {
    if (user && !["admin", "moderator"].includes(user.role)) {
      toast.error("접근 권한이 없습니다");
      router.push("/dashboard");
    }
  }, [user, router]);

  if (!user || !["admin", "moderator"].includes(user.role)) {
    return null;
  }

  return <div>사용자 관리 페이지</div>;
}
```

---

## 8. 인증 상태 표시

### 헤더에서 사용자 정보 표시

```tsx
// src/components/layout/Header.tsx
export const Header = () => {
  const { user, logout } = useAuthStore();

  return (
    <header>
      <DropdownMenu>
        <DropdownMenuTrigger>
          <Avatar>
            <AvatarFallback>
              {user?.username?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <div className="px-2 py-1.5">
            <p className="font-medium">{user?.username}</p>
            <p className="text-muted-foreground text-sm">{user?.email}</p>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={logout}>
            로그아웃
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
};
```

---

## 9. 전체 인증 플로우 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    전체 인증 플로우                          │
└─────────────────────────────────────────────────────────────┘

[ 비로그인 상태 ]
        │
        │ /dashboard 접근
        ▼
┌───────────────┐
│  미들웨어     │ ─── 토큰 없음 ───▶ /login 리다이렉트
└───────────────┘
        │
        ▼
┌───────────────┐
│  로그인 폼    │
└───────────────┘
        │
        │ 제출
        ▼
┌───────────────┐
│  authStore    │
│  login()      │
└───────────────┘
        │
        │ API 호출
        ▼
┌───────────────┐      ┌───────────────┐
│  authApi      │ ───▶ │  FastAPI      │
│  login()      │ ◀─── │  /auth/login  │
└───────────────┘      └───────────────┘
        │
        │ 토큰 반환
        ▼
┌───────────────┐
│  setTokens()  │ ─── 쿠키에 저장
└───────────────┘
        │
        │ 사용자 정보 조회
        ▼
┌───────────────┐      ┌───────────────┐
│  authApi      │ ───▶ │  FastAPI      │
│  getCurrentUser│ ◀─── │  /users/me    │
└───────────────┘      └───────────────┘
        │
        │ 상태 업데이트
        ▼
┌───────────────┐
│  authStore    │ ─── user, isAuthenticated = true
│  persist      │ ─── localStorage에 저장
└───────────────┘
        │
        │ 리다이렉트
        ▼
┌───────────────┐
│  /dashboard   │
└───────────────┘
```

---

## 요약

| 개념 | 설명 |
|------|------|
| JWT | JSON Web Token, 인증에 사용되는 토큰 |
| Access Token | API 요청에 사용, 짧은 수명 |
| Refresh Token | Access Token 갱신용, 긴 수명 |
| 쿠키 저장 | js-cookie로 토큰 저장/관리 |
| 미들웨어 | 라우트 보호, 리다이렉트 처리 |
| authStore | Zustand로 인증 상태 관리 |
| 자동 갱신 | 401 에러 시 자동으로 토큰 갱신 |

## 다음 단계

다음 문서 [11-styling.md](./11-styling.md)에서 Tailwind CSS 스타일링을 학습합니다.
