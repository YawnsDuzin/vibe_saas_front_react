# 프로젝트 구조 상세 분석

## 전체 폴더 구조

```
frontend/
├── public/                          # 정적 파일 (이미지, 폰트 등)
│
├── src/                             # 소스 코드
│   ├── app/                         # Next.js App Router
│   │   ├── (auth)/                  # 인증 페이지 그룹
│   │   ├── (main)/                  # 메인 페이지 그룹
│   │   ├── layout.tsx               # 루트 레이아웃
│   │   ├── page.tsx                 # 홈페이지
│   │   └── globals.css              # 전역 스타일
│   │
│   ├── components/                  # 재사용 컴포넌트
│   │   ├── layout/                  # 레이아웃 컴포넌트
│   │   └── ui/                      # UI 컴포넌트 (shadcn)
│   │
│   ├── lib/                         # 유틸리티 및 라이브러리
│   │   ├── api/                     # API 클라이언트
│   │   └── utils.ts                 # 유틸리티 함수
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
├── tailwind.config.ts               # Tailwind CSS 설정
└── .env.local                       # 환경 변수
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

## 3. lib/ 폴더 상세

### api/ - API 클라이언트

```
lib/api/
├── client.ts        # 공통 API 클라이언트
├── auth.ts          # 인증 API
├── posts.ts         # 게시글 API
├── users.ts         # 사용자 API
├── dashboard.ts     # 대시보드 API
└── index.ts         # 내보내기
```

#### index.ts - API 모듈 내보내기

```tsx
// src/lib/api/index.ts
export { authApi } from "./auth";
export { postsApi } from "./posts";
export { usersApi } from "./users";
export { dashboardApi } from "./dashboard";
export { ApiError, getAccessToken, setTokens, clearTokens } from "./client";
```

**사용 예시:**
```tsx
import { authApi, postsApi } from "@/lib/api";

await authApi.login(username, password);
const posts = await postsApi.getList({ page: 1 });
```

### utils.ts - 유틸리티 함수

```tsx
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Tailwind CSS 클래스 병합 유틸리티
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**사용 예시:**
```tsx
// 조건부 클래스 적용
<div className={cn(
  "base-class",
  isActive && "active-class",
  variant === "primary" && "primary-class"
)}>
```

---

## 4. stores/ 폴더 상세

Zustand를 사용한 전역 상태 관리입니다.

```
stores/
├── authStore.ts     # 인증 상태 (사용자 정보, 로그인/로그아웃)
└── themeStore.ts    # 테마 상태 (라이트/다크/시스템)
```

### authStore.ts 구조

```tsx
interface AuthState {
  user: User | null;           // 현재 사용자
  isAuthenticated: boolean;    // 인증 여부
  isLoading: boolean;          // 로딩 상태
  error: string | null;        // 에러 메시지

  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}
```

### themeStore.ts 구조

```tsx
interface ThemeState {
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;
}
```

---

## 5. types/ 폴더 상세

TypeScript 타입 정의입니다.

```tsx
// src/types/index.ts

// 사용자
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export type UserRole = "admin" | "moderator" | "user";

// 게시글
export interface Post {
  id: number;
  title: string;
  content: string;
  slug: string;
  view_count: number;
  is_published: boolean;
  is_pinned: boolean;
  author: User;
  category?: Category;
  created_at: string;
  updated_at: string;
}

// 댓글
export interface Comment {
  id: number;
  content: string;
  author: User;
  parent_id?: number;
  created_at: string;
  updated_at: string;
}

// 인증
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// 페이지네이션
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
```

---

## 6. 루트 파일들

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

## 7. Import 경로 별칭 (@/)

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
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";
import { User, Post } from "@/types";
```

---

## 8. 데이터 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 인터페이스                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    페이지 (pages)                    │   │
│  │  DashboardPage, PostsPage, UsersPage, SettingsPage  │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                    상태 읽기/수정                           │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    상태 관리 (stores)                │   │
│  │         authStore, themeStore                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                      API 호출                               │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    API 클라이언트 (lib/api)          │   │
│  │    authApi, postsApi, usersApi, dashboardApi        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                      HTTP 요청                              │
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
| `lib/` | 유틸리티 | API 클라이언트, 헬퍼 함수 |
| `stores/` | 상태 관리 | Zustand 스토어 |
| `types/` | 타입 정의 | TypeScript 인터페이스 |
| `middleware.ts` | 요청 전처리 | 인증 확인, 리다이렉트 |

## 다음 단계

다음 문서 [07-components-detail.md](./07-components-detail.md)에서 각 컴포넌트를 상세히 분석합니다.
