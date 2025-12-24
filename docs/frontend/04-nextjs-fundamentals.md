# Next.js 기초 개념

## Next.js란?

Next.js는 React를 기반으로 한 **풀스택 웹 프레임워크**입니다. React만으로는 클라이언트 사이드 렌더링(CSR)만 가능하지만, Next.js를 사용하면 서버 사이드 렌더링(SSR), 정적 사이트 생성(SSG) 등 다양한 렌더링 방식을 사용할 수 있습니다.

### React vs Next.js

```
┌─────────────────────────────────────────────────────────────┐
│                    React vs Next.js                          │
├───────────────────────────┬─────────────────────────────────┤
│         React             │           Next.js               │
├───────────────────────────┼─────────────────────────────────┤
│  UI 라이브러리            │  풀스택 프레임워크              │
│  CSR (Client Side)        │  CSR + SSR + SSG 지원           │
│  라우팅 직접 설정         │  파일 기반 자동 라우팅          │
│  별도 서버 필요           │  내장 서버 제공                 │
│  SEO 불리                 │  SEO 최적화                     │
│  설정 필요                │  Zero Config                    │
└───────────────────────────┴─────────────────────────────────┘
```

### Next.js의 주요 기능

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 핵심 기능                         │
├─────────────────────────────────────────────────────────────┤
│  ✅ 파일 기반 라우팅: 폴더 구조 = URL 구조                  │
│  ✅ 서버 컴포넌트: 서버에서 렌더링, 번들 크기 감소          │
│  ✅ 클라이언트 컴포넌트: 브라우저에서 인터랙션 처리         │
│  ✅ 레이아웃 시스템: 페이지 간 공통 UI 공유                 │
│  ✅ 데이터 페칭: 서버에서 직접 데이터 가져오기              │
│  ✅ 미들웨어: 요청 전처리 (인증 등)                         │
│  ✅ API 라우트: 백엔드 API 구축 가능                        │
│  ✅ 이미지 최적화: 자동 이미지 최적화                       │
│  ✅ 폰트 최적화: Google Fonts 자동 최적화                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 렌더링 방식 이해

### CSR (Client Side Rendering)

브라우저에서 JavaScript로 페이지를 그립니다.

```
┌─────────────┐    빈 HTML    ┌─────────────┐
│   서버      │ ───────────▶ │   브라우저   │
└─────────────┘               └─────────────┘
                                    │
                              JS 다운로드
                                    │
                                    ▼
                              React 실행
                                    │
                                    ▼
                              페이지 표시
```

- 장점: 페이지 전환 빠름
- 단점: 초기 로딩 느림, SEO 불리

### SSR (Server Side Rendering)

서버에서 완성된 HTML을 만들어 보냅니다.

```
┌─────────────┐  완성된 HTML  ┌─────────────┐
│   서버      │ ───────────▶ │   브라우저   │
│  (렌더링)   │               │  (표시)      │
└─────────────┘               └─────────────┘
```

- 장점: 초기 로딩 빠름, SEO 유리
- 단점: 서버 부하

### Next.js의 접근법

Next.js는 두 방식을 **적절히 조합**합니다:
- 서버 컴포넌트: SSR 사용 (데이터 페칭, 정적 UI)
- 클라이언트 컴포넌트: CSR 사용 (인터랙션)

---

## 2. 서버 컴포넌트 vs 클라이언트 컴포넌트

### 서버 컴포넌트 (기본)

```tsx
// 기본적으로 모든 컴포넌트는 서버 컴포넌트
// "use client" 지시어가 없으면 서버 컴포넌트

// app/users/page.tsx
async function UsersPage() {
  // 서버에서 직접 데이터 fetch 가능
  const users = await fetch('https://api.example.com/users')
    .then(res => res.json());

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

export default UsersPage;
```

**서버 컴포넌트 특징:**
- `async/await` 직접 사용 가능
- 데이터베이스, 파일 시스템 접근 가능
- 브라우저 API 사용 불가 (window, document 등)
- useState, useEffect 등 Hook 사용 불가
- 이벤트 핸들러 (onClick 등) 사용 불가

### 클라이언트 컴포넌트

```tsx
// "use client" 지시어로 클라이언트 컴포넌트 선언
"use client";

import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);  // Hook 사용 가능

  return (
    <div>
      <p>카운트: {count}</p>
      <button onClick={() => setCount(count + 1)}>  {/* 이벤트 핸들러 */}
        +1
      </button>
    </div>
  );
}

export default Counter;
```

**클라이언트 컴포넌트 특징:**
- `"use client"` 지시어 필수
- useState, useEffect 등 Hook 사용 가능
- 이벤트 핸들러 사용 가능
- 브라우저 API 사용 가능

### 언제 무엇을 사용할까?

```
┌─────────────────────────────────────────────────────────────┐
│              서버 컴포넌트 vs 클라이언트 컴포넌트            │
├────────────────────────────┬────────────────────────────────┤
│     서버 컴포넌트          │      클라이언트 컴포넌트       │
├────────────────────────────┼────────────────────────────────┤
│  데이터 페칭               │  onClick, onChange 등 이벤트   │
│  민감한 정보 접근          │  useState, useEffect Hook      │
│  백엔드 리소스 접근        │  브라우저 API (localStorage)   │
│  정적 UI 렌더링            │  사용자 인터랙션               │
│  무거운 의존성 사용        │  상태 관리 라이브러리          │
└────────────────────────────┴────────────────────────────────┘
```

### 프로젝트 예시

```tsx
// frontend/src/app/(auth)/login/page.tsx
"use client";  // 클라이언트 컴포넌트 (폼 인터랙션 필요)

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

export default function LoginPage() {
  const router = useRouter();
  const { register, handleSubmit } = useForm();
  // useState, useRouter 등 Hook 사용
  // onClick, onSubmit 등 이벤트 핸들러 사용
}

// frontend/src/components/layout/Header.tsx
"use client";  // 클라이언트 컴포넌트 (테마 토글, 드롭다운 등)

// frontend/src/components/layout/Sidebar.tsx
"use client";  // 클라이언트 컴포넌트 (현재 경로 표시, 메뉴 접기)
```

---

## 3. 프로젝트 구조

### App Router 구조

Next.js 13부터 도입된 App Router는 `app` 폴더를 사용합니다.

```
frontend/
├── src/
│   └── app/                    # App Router 루트
│       ├── layout.tsx          # 루트 레이아웃 (필수)
│       ├── page.tsx            # 홈페이지 (/)
│       ├── globals.css         # 전역 스타일
│       │
│       ├── (auth)/             # 라우트 그룹 (URL에 미포함)
│       │   ├── layout.tsx      # 인증 페이지 레이아웃
│       │   ├── login/
│       │   │   └── page.tsx    # /login
│       │   └── register/
│       │       └── page.tsx    # /register
│       │
│       └── (main)/             # 라우트 그룹
│           ├── layout.tsx      # 메인 페이지 레이아웃
│           ├── dashboard/
│           │   └── page.tsx    # /dashboard
│           ├── posts/
│           │   ├── page.tsx    # /posts
│           │   ├── new/
│           │   │   └── page.tsx # /posts/new
│           │   └── [id]/
│           │       └── page.tsx # /posts/1, /posts/2, ...
│           ├── users/
│           │   └── page.tsx    # /users
│           └── settings/
│               └── page.tsx    # /settings
```

### 특수 파일들

| 파일명 | 역할 |
|--------|------|
| `layout.tsx` | 레이아웃 (여러 페이지에서 공유) |
| `page.tsx` | 페이지 컴포넌트 (URL로 접근 가능) |
| `loading.tsx` | 로딩 UI |
| `error.tsx` | 에러 UI |
| `not-found.tsx` | 404 페이지 |

---

## 4. 레이아웃 시스템

레이아웃은 **여러 페이지에서 공유하는 UI**입니다.

### 루트 레이아웃

```tsx
// app/layout.tsx - 모든 페이지에 적용
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        {children}  {/* 각 페이지가 여기에 렌더링 */}
      </body>
    </html>
  );
}
```

### 중첩 레이아웃

```tsx
// app/(main)/layout.tsx - 메인 페이지들에만 적용
import { MainLayout } from "@/components/layout";

export default function MainPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MainLayout>
      {children}  {/* 각 메인 페이지가 여기에 */}
    </MainLayout>
  );
}
```

### 레이아웃 중첩 구조

```
RootLayout (app/layout.tsx)
    │
    ├── (auth) Layout → LoginPage, RegisterPage
    │
    └── (main) Layout → MainLayout
            │
            ├── DashboardPage
            ├── PostsPage
            ├── UsersPage
            └── SettingsPage
```

### 프로젝트 예시

```tsx
// frontend/src/app/layout.tsx (루트 레이아웃)
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

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
        <Toaster />  {/* 토스트 알림 */}
      </body>
    </html>
  );
}

// frontend/src/app/(main)/layout.tsx (메인 레이아웃)
import { MainLayout } from "@/components/layout";

export default function MainPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MainLayout>{children}</MainLayout>;
}
```

---

## 5. 라우트 그룹

괄호 `()`로 감싸면 **URL에 영향을 주지 않는** 폴더를 만들 수 있습니다.

```
app/
├── (auth)/           # URL: /login, /register (auth 제외)
│   ├── login/
│   └── register/
│
├── (main)/           # URL: /dashboard, /posts (main 제외)
│   ├── dashboard/
│   └── posts/
│
└── (marketing)/      # URL: /about, /contact (marketing 제외)
    ├── about/
    └── contact/
```

### 라우트 그룹의 용도

1. **레이아웃 분리**: 인증 페이지와 메인 페이지에 다른 레이아웃 적용
2. **코드 조직화**: 관련 페이지들을 그룹으로 묶기

### 프로젝트 예시

```
app/
├── (auth)/               # 인증 관련 페이지 그룹
│   ├── layout.tsx        # 간단한 레이아웃 (인증 페이지용)
│   ├── login/page.tsx    # /login
│   └── register/page.tsx # /register
│
└── (main)/               # 메인 애플리케이션 그룹
    ├── layout.tsx        # MainLayout 적용 (사이드바, 헤더)
    ├── dashboard/page.tsx  # /dashboard
    ├── posts/page.tsx      # /posts
    ├── users/page.tsx      # /users
    └── settings/page.tsx   # /settings
```

---

## 6. 동적 라우팅

URL의 일부가 **변수**인 경우 대괄호 `[]`를 사용합니다.

### 기본 동적 라우트

```
app/
└── posts/
    └── [id]/
        └── page.tsx    # /posts/1, /posts/2, /posts/abc
```

```tsx
// app/posts/[id]/page.tsx
interface PageProps {
  params: Promise<{ id: string }>;  // Next.js 15에서 Promise로 변경
}

export default async function PostPage({ params }: PageProps) {
  const { id } = await params;  // params 대기

  return <div>게시글 ID: {id}</div>;
}
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/posts/[id]/page.tsx
"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";

export default function PostDetailPage() {
  const params = useParams();
  const id = params.id as string;  // URL에서 id 추출

  const [post, setPost] = useState<Post | null>(null);

  useEffect(() => {
    const loadPost = async () => {
      const data = await postsApi.getById(Number(id));
      setPost(data);
    };
    loadPost();
  }, [id]);

  if (!post) return <div>로딩 중...</div>;

  return (
    <div>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </div>
  );
}
```

---

## 7. 네비게이션

### Link 컴포넌트

클라이언트 사이드 네비게이션을 위한 컴포넌트입니다.

```tsx
import Link from "next/link";

function Navigation() {
  return (
    <nav>
      <Link href="/">홈</Link>
      <Link href="/about">소개</Link>
      <Link href="/posts">게시글</Link>
      <Link href="/posts/1">첫 번째 게시글</Link>

      {/* 동적 경로 */}
      <Link href={`/posts/${postId}`}>게시글 보기</Link>
    </nav>
  );
}
```

### useRouter

프로그래밍 방식의 네비게이션입니다.

```tsx
"use client";

import { useRouter } from "next/navigation";

function LoginForm() {
  const router = useRouter();

  const handleSubmit = async () => {
    await login();
    router.push("/dashboard");  // 페이지 이동
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/Sidebar.tsx
import Link from "next/link";
import { usePathname } from "next/navigation";

export const Sidebar = () => {
  const pathname = usePathname();  // 현재 경로

  return (
    <nav>
      {menuItems.map(item => (
        <Link
          key={item.href}
          href={item.href}
          className={pathname === item.href ? "active" : ""}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
};

// frontend/src/app/(auth)/login/page.tsx
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const onSubmit = async (data) => {
    await login(data);
    router.push("/dashboard");  // 로그인 성공 후 이동
  };
}
```

---

## 8. 미들웨어

**모든 요청 전에 실행**되는 코드입니다. 인증 확인, 리다이렉트 등에 사용됩니다.

```tsx
// middleware.ts (프로젝트 루트에 위치)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token");

  // 보호된 경로에 토큰 없이 접근하면 로그인으로 리다이렉트
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

// 미들웨어가 적용될 경로 설정
export const config = {
  matcher: ["/dashboard/:path*", "/posts/:path*"],
};
```

### 프로젝트 예시

```tsx
// frontend/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/posts", "/users", "/settings"];
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token");

  // 보호된 경로에 토큰 없이 접근
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 이미 로그인된 상태에서 인증 페이지 접근
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));
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

---

## 9. 환경 변수

### 환경 변수 설정

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=my-secret-key
```

### 접두사 규칙

```
┌─────────────────────────────────────────────────────────────┐
│                    환경 변수 접두사                          │
├────────────────────────────┬────────────────────────────────┤
│  NEXT_PUBLIC_xxx           │  클라이언트에서 접근 가능      │
│  (접두사 없음)             │  서버에서만 접근 가능          │
└────────────────────────────┴────────────────────────────────┘
```

### 사용 예시

```tsx
// 클라이언트에서 사용 가능
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// 서버에서만 사용 가능 (클라이언트에서 접근 불가)
const secretKey = process.env.SECRET_KEY;
```

### 프로젝트 예시

```tsx
// frontend/src/lib/api/client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// API 호출 시 사용
const response = await fetch(`${API_URL}/posts`);
```

---

## 요약

| 개념 | 설명 |
|------|------|
| **서버 컴포넌트** | 서버에서 렌더링, async/await 사용 가능, Hook 불가 |
| **클라이언트 컴포넌트** | "use client" 선언, Hook/이벤트 사용 가능 |
| **App Router** | app 폴더 기반 라우팅 시스템 |
| **layout.tsx** | 여러 페이지에서 공유하는 레이아웃 |
| **page.tsx** | URL로 접근 가능한 페이지 |
| **라우트 그룹 ()** | URL에 영향 없이 폴더 그룹화 |
| **동적 라우트 []** | URL 파라미터 처리 (/posts/[id]) |
| **Link** | 클라이언트 사이드 네비게이션 |
| **useRouter** | 프로그래밍 방식 네비게이션 |
| **middleware.ts** | 요청 전처리 (인증 등) |

## 다음 단계

다음 문서 [05-nextjs-app-router.md](./05-nextjs-app-router.md)에서 App Router를 더 자세히 학습합니다.
