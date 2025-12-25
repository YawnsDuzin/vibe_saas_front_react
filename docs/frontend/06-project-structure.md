# 프로젝트 구조 상세 분석

## 전체 폴더 구조

```
frontend/
├── public/                          # 정적 파일 (이미지, 폰트 등)
│
├── src/                             # 소스 코드
│   ├── app/                         # Next.js App Router
│   │   ├── (auth)/                  # 인증 페이지 그룹
│   │   │   ├── layout.tsx           # 인증 레이아웃
│   │   │   ├── login/page.tsx       # 로그인 페이지
│   │   │   └── register/page.tsx    # 회원가입 페이지
│   │   ├── (main)/                  # 메인 페이지 그룹
│   │   │   ├── layout.tsx           # 메인 레이아웃
│   │   │   ├── dashboard/page.tsx   # 대시보드
│   │   │   ├── posts/               # 게시글
│   │   │   │   ├── page.tsx         # 목록
│   │   │   │   ├── new/page.tsx     # 작성
│   │   │   │   └── [id]/page.tsx    # 상세
│   │   │   ├── users/page.tsx       # 사용자 관리
│   │   │   └── settings/page.tsx    # 설정
│   │   ├── layout.tsx               # 루트 레이아웃
│   │   ├── page.tsx                 # 홈페이지
│   │   └── globals.css              # 전역 스타일
│   │
│   ├── components/                  # 재사용 컴포넌트
│   │   ├── layout/                  # 레이아웃 컴포넌트
│   │   │   ├── MainLayout.tsx       # 메인 레이아웃
│   │   │   ├── Header.tsx           # 헤더
│   │   │   ├── Sidebar.tsx          # 사이드바
│   │   │   └── index.ts             # 내보내기
│   │   └── ui/                      # UI 컴포넌트 (shadcn/ui)
│   │
│   ├── stores/                      # 상태 관리 (Zustand)
│   │   ├── authStore.ts             # 인증 상태
│   │   └── themeStore.ts            # 테마 상태
│   │
│   └── types/                       # TypeScript 타입
│       └── index.ts                 # 타입 정의
│
├── middleware.ts                    # Next.js 미들웨어
├── package.json                     # 프로젝트 설정
├── tsconfig.json                    # TypeScript 설정
├── next.config.ts                   # Next.js 설정
└── .env.local                       # 환경 변수 (선택)
```

---

## 1. app/ 폴더 상세

### 루트 파일들

```
app/
├── layout.tsx      # 모든 페이지에 적용되는 루트 레이아웃
├── page.tsx        # 홈페이지 (/)
└── globals.css     # 전역 CSS 스타일
```

#### layout.tsx - 루트 레이아웃

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

// 폰트 설정 - Geist 폰트 사용
const geistSans = Geist({
  variable: "--font-geist-sans",  // CSS 변수로 등록
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// 페이지 메타데이터
export const metadata: Metadata = {
  title: "FastAPI Tutorial",
  description: "FastAPI Tutorial with Next.js",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Toaster position="top-right" />  {/* 토스트 알림 */}
      </body>
    </html>
  );
}
```

**핵심 포인트:**
- `Geist` 폰트를 CSS 변수로 등록
- `Toaster` 컴포넌트로 전역 토스트 알림 제공
- `suppressHydrationWarning`: 서버/클라이언트 불일치 경고 방지 (테마 때문)

#### page.tsx - 홈페이지

```tsx
// src/app/page.tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");  // 바로 대시보드로 리다이렉트
}
```

---

### (auth) 라우트 그룹

인증 관련 페이지들을 그룹화합니다. URL에 `auth`는 포함되지 않습니다.

```
(auth)/
├── layout.tsx        # 인증 페이지 레이아웃
├── login/
│   └── page.tsx      # /login
└── register/
    └── page.tsx      # /register
```

#### (auth)/layout.tsx

```tsx
// src/app/(auth)/layout.tsx
"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/stores/themeStore";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useThemeStore();

  // 테마 적용
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches ? "dark" : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      {children}  {/* 로그인/회원가입 카드 */}
    </div>
  );
}
```

**레이아웃 특징:**
- 화면 중앙에 콘텐츠 배치 (`items-center justify-center`)
- 테마 적용 로직 포함

---

### (main) 라우트 그룹

메인 애플리케이션 페이지들입니다.

```
(main)/
├── layout.tsx           # MainLayout 적용
├── dashboard/
│   └── page.tsx         # /dashboard
├── posts/
│   ├── page.tsx         # /posts
│   ├── new/
│   │   └── page.tsx     # /posts/new
│   └── [id]/
│       └── page.tsx     # /posts/1, /posts/2, ...
├── users/
│   └── page.tsx         # /users
└── settings/
    └── page.tsx         # /settings
```

#### (main)/layout.tsx

```tsx
// src/app/(main)/layout.tsx
import { MainLayout } from "@/components/layout";

export default function MainPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MainLayout>{children}</MainLayout>;
}
```

**레이아웃 구조:**
```
MainLayout
├── Sidebar (왼쪽)
└── 콘텐츠 영역 (오른쪽)
    ├── Header (상단)
    └── {children} (메인 콘텐츠)
```

---

## 2. components/ 폴더 상세

### layout/ - 레이아웃 컴포넌트

```
components/layout/
├── MainLayout.tsx    # 메인 레이아웃
├── Header.tsx        # 헤더
├── Sidebar.tsx       # 사이드바
└── index.ts          # 내보내기
```

#### index.ts - 모듈 내보내기

```tsx
// src/components/layout/index.ts
export { MainLayout } from "./MainLayout";
export { Header } from "./Header";
export { Sidebar } from "./Sidebar";
```

**사용 예시:**
```tsx
// 개별 import 대신
import { MainLayout, Header, Sidebar } from "@/components/layout";
```

### ui/ - UI 컴포넌트 (shadcn/ui)

```
components/ui/
├── avatar.tsx        # 아바타 (사용자 프로필 이미지)
├── badge.tsx         # 배지 (라벨, 태그)
├── button.tsx        # 버튼
├── card.tsx          # 카드
├── dialog.tsx        # 모달 다이얼로그
├── dropdown-menu.tsx # 드롭다운 메뉴
├── form.tsx          # 폼 관련 컴포넌트
├── input.tsx         # 입력 필드
├── label.tsx         # 레이블
├── separator.tsx     # 구분선
├── sheet.tsx         # 사이드 패널 (모바일 메뉴)
├── sonner.tsx        # 토스트 알림
├── table.tsx         # 테이블
└── tabs.tsx          # 탭
```

**shadcn/ui 특징:**
- 복사하여 사용하는 컴포넌트 (node_modules에 없음)
- Radix UI 기반 (접근성 보장)
- Tailwind CSS로 스타일링
- 커스터마이징 가능

---

## 3. stores/ 폴더 상세

Zustand를 사용한 전역 상태 관리입니다.

```
stores/
├── authStore.ts     # 인증 상태 (사용자 정보, 로그인/로그아웃)
└── themeStore.ts    # 테마 상태 (라이트/다크/시스템)
```

### authStore.ts - 인증 상태 관리

```tsx
// src/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await authApi.login({ username, password });
          const user = await authApi.getCurrentUser(tokens.access_token);
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : '로그인에 실패했습니다.';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        clearTokens();
        set({ user: null, isAuthenticated: false, error: null });
      },

      fetchUser: async () => { /* ... */ },
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

**핵심 포인트:**
- `persist` 미들웨어로 localStorage에 상태 유지
- `partialize`로 저장할 상태만 선택

### themeStore.ts - 테마 상태 관리

```tsx
// src/stores/themeStore.ts
interface ThemeState {
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;
}
```

---

## 4. types/ 폴더 상세

TypeScript 타입 정의입니다. 모든 타입이 `src/types/index.ts`에 정의되어 있습니다.

```tsx
// src/types/index.ts

// ===== 사용자 타입 =====
export type UserRole = 'admin' | 'moderator' | 'user';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}

// ===== 인증 타입 =====
export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ===== 게시글 타입 =====
export interface AuthorInfo {
  id: number;
  username: string;
  full_name: string | null;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  slug: string;
  view_count: number;
  is_published: boolean;
  is_pinned: boolean;
  created_at: string;
  updated_at: string | null;
  author: AuthorInfo;
  category: Category | null;
  comment_count: number;
}

export interface PostListResponse {
  items: Post[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// ===== 댓글 타입 =====
export interface Comment {
  id: number;
  content: string;
  author: AuthorInfo;
  post_id: number;
  parent_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  replies: Comment[];
}

// ===== 대시보드 타입 =====
export interface DashboardStats {
  total_users: number;
  total_posts: number;
  total_comments: number;
  recent_users: User[];
  recent_posts: Post[];
}
```

---

## 5. 루트 파일들

### middleware.ts

```tsx
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/posts", "/users", "/settings"];
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token");

  // 보호된 경로에 토큰 없이 접근
  if (protectedRoutes.some(route => pathname.startsWith(route)) && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 인증 페이지에 이미 로그인된 상태로 접근
  if (authRoutes.some(route => pathname.startsWith(route)) && token) {
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

### package.json 주요 의존성

```json
{
  "dependencies": {
    "next": "16.1.1",           // Next.js 프레임워크
    "react": "19.2.3",          // React 라이브러리
    "zustand": "^5.0.9",        // 상태 관리
    "react-hook-form": "^7.69.0", // 폼 관리
    "zod": "^4.2.1",            // 스키마 검증
    "@hookform/resolvers": "^5.2.2", // RHF + Zod 연결
    "js-cookie": "^3.0.5",      // 쿠키 관리
    "lucide-react": "^0.562.0", // 아이콘
    "sonner": "^2.0.7",         // 토스트 알림
    "clsx": "^2.1.1",           // 조건부 클래스
    "tailwind-merge": "^3.4.0", // Tailwind 클래스 병합

    // Radix UI (shadcn/ui 기반)
    "@radix-ui/react-avatar": "...",
    "@radix-ui/react-dialog": "...",
    "@radix-ui/react-dropdown-menu": "...",
    "@radix-ui/react-label": "...",
    "@radix-ui/react-separator": "...",
    "@radix-ui/react-slot": "...",
    "@radix-ui/react-tabs": "..."
  }
}
```

---

## 6. Import 경로 별칭 (@/)

### tsconfig.json 설정

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 사용 예시

```tsx
// 상대 경로 대신
import { Button } from "../../../components/ui/button";

// @ 별칭 사용
import { Button } from "@/components/ui/button";

// 예시
import { MainLayout } from "@/components/layout";
import { useAuthStore } from "@/stores/authStore";
import { User, Post } from "@/types";
```

---

## 7. 데이터 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 인터페이스                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    페이지 (pages)                    │   │
│  │  DashboardPage, PostsPage, UsersPage, SettingsPage  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                    상태 읽기/수정                            │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    상태 관리 (stores)                │   │
│  │         authStore, themeStore                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                      HTTP 요청                               │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    FastAPI 백엔드                    │   │
│  │            http://localhost:8000/api/v1             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 요약

| 폴더/파일 | 역할 | 주요 내용 |
|-----------|------|----------|
| `app/` | 페이지 및 라우팅 | 레이아웃, 페이지 컴포넌트 |
| `components/` | 재사용 컴포넌트 | 레이아웃, UI 컴포넌트 |
| `stores/` | 상태 관리 | Zustand 스토어 (auth, theme) |
| `types/` | 타입 정의 | TypeScript 인터페이스 |
| `middleware.ts` | 요청 전처리 | 인증 확인, 리다이렉트 |

## 다음 단계

다음 문서 [07-components-detail.md](./07-components-detail.md)에서 각 컴포넌트를 상세히 분석합니다.
