# Next.js App Router 상세 가이드

## App Router 개요

App Router는 Next.js 13에서 도입된 새로운 라우팅 시스템입니다. `app` 폴더를 사용하며, 이전의 Pages Router(`pages` 폴더)보다 더 강력한 기능을 제공합니다.

### Pages Router vs App Router

```
┌─────────────────────────────────────────────────────────────┐
│              Pages Router vs App Router                      │
├────────────────────────────┬────────────────────────────────┤
│      Pages Router          │         App Router             │
│      (pages 폴더)          │         (app 폴더)             │
├────────────────────────────┼────────────────────────────────┤
│  모든 컴포넌트가 클라이언트│  서버 컴포넌트가 기본          │
│  _app.js로 전역 레이아웃   │  layout.tsx로 중첩 레이아웃    │
│  getServerSideProps 등     │  async 컴포넌트에서 직접 fetch │
│  파일 = 페이지             │  page.tsx = 페이지             │
│  라우트 그룹 없음          │  () 라우트 그룹 지원           │
└────────────────────────────┴────────────────────────────────┘
```

---

## 1. 폴더/파일 컨벤션

### 특수 파일 이름

```
app/
├── layout.tsx      # 레이아웃 (필수 - 루트에 하나)
├── page.tsx        # 페이지 (URL로 접근 가능)
├── loading.tsx     # 로딩 UI
├── error.tsx       # 에러 UI
├── not-found.tsx   # 404 페이지
├── template.tsx    # 템플릿 (레이아웃과 비슷, 매번 리마운트)
├── default.tsx     # 병렬 라우트 기본값
├── route.ts        # API 라우트
└── middleware.ts   # 미들웨어 (루트에만)
```

### 폴더 = 라우트

```
app/
├── page.tsx                    # /
├── about/
│   └── page.tsx                # /about
├── posts/
│   ├── page.tsx                # /posts
│   ├── new/
│   │   └── page.tsx            # /posts/new
│   └── [id]/
│       └── page.tsx            # /posts/1, /posts/2, ...
└── users/
    └── [userId]/
        └── settings/
            └── page.tsx        # /users/1/settings
```

---

## 2. layout.tsx 상세

### 기본 구조

```tsx
// app/layout.tsx (루트 레이아웃 - 필수)
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <header>공통 헤더</header>
        <main>{children}</main>
        <footer>공통 푸터</footer>
      </body>
    </html>
  );
}
```

### 중첩 레이아웃

```tsx
// app/(main)/layout.tsx
export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex">
      <Sidebar />          {/* 메인 페이지들의 공통 사이드바 */}
      <div className="flex-1">
        {children}         {/* 각 페이지 내용 */}
      </div>
    </div>
  );
}

// app/(main)/dashboard/page.tsx
export default function DashboardPage() {
  return <h1>대시보드</h1>;
}

// 결과: 사이드바 + 대시보드 내용이 함께 표시
```

### 레이아웃 중첩 흐름

```
RootLayout (html, body)
    │
    └── MainLayout (사이드바, 헤더)
            │
            └── DashboardPage (대시보드 내용)
```

### 프로젝트 예시

```tsx
// frontend/src/app/layout.tsx (루트 레이아웃)
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

// 폰트 설정
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// 메타데이터 설정
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
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
```

---

## 3. page.tsx 상세

### 기본 페이지

```tsx
// app/about/page.tsx
export default function AboutPage() {
  return (
    <div>
      <h1>소개 페이지</h1>
      <p>이 페이지는 /about URL로 접근할 수 있습니다.</p>
    </div>
  );
}
```

### 서버 컴포넌트에서 데이터 페칭

```tsx
// app/posts/page.tsx (서버 컴포넌트)
async function getPosts() {
  const res = await fetch("https://api.example.com/posts");
  return res.json();
}

export default async function PostsPage() {
  const posts = await getPosts();  // 서버에서 데이터 fetch

  return (
    <div>
      <h1>게시글 목록</h1>
      <ul>
        {posts.map((post: any) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

### 클라이언트 컴포넌트 페이지

```tsx
// app/posts/page.tsx (클라이언트 컴포넌트)
"use client";

import { useState, useEffect } from "react";

export default function PostsPage() {
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/api/posts")
      .then((res) => res.json())
      .then((data) => {
        setPosts(data);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) return <div>로딩 중...</div>;

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

---

## 4. 동적 라우트 상세

### 기본 동적 라우트 [param]

```tsx
// app/posts/[id]/page.tsx
// URL: /posts/1, /posts/2, /posts/abc

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function PostPage({ params }: PageProps) {
  const { id } = await params;

  return <div>게시글 ID: {id}</div>;
}
```

### 클라이언트 컴포넌트에서 동적 라우트

```tsx
// app/posts/[id]/page.tsx
"use client";

import { useParams } from "next/navigation";

export default function PostPage() {
  const params = useParams();
  const id = params.id as string;

  return <div>게시글 ID: {id}</div>;
}
```

### Catch-all 라우트 [...param]

```tsx
// app/docs/[...slug]/page.tsx
// URL: /docs/a, /docs/a/b, /docs/a/b/c

interface PageProps {
  params: Promise<{ slug: string[] }>;
}

export default async function DocsPage({ params }: PageProps) {
  const { slug } = await params;
  // /docs/a/b/c → slug = ["a", "b", "c"]

  return <div>경로: {slug.join("/")}</div>;
}
```

### Optional Catch-all [[...param]]

```tsx
// app/shop/[[...categories]]/page.tsx
// URL: /shop, /shop/a, /shop/a/b

interface PageProps {
  params: Promise<{ categories?: string[] }>;
}

export default async function ShopPage({ params }: PageProps) {
  const { categories } = await params;
  // /shop → categories = undefined
  // /shop/a/b → categories = ["a", "b"]

  return <div>{categories ? categories.join("/") : "전체 상품"}</div>;
}
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/posts/[id]/page.tsx
"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { postsApi } from "@/lib/api";

export default function PostDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [postData, commentsData] = await Promise.all([
          postsApi.getById(Number(id)),
          postsApi.getComments(Number(id)),
        ]);
        setPost(postData);
        setComments(commentsData);
      } catch (error) {
        console.error("로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [id]);

  if (isLoading) return <div>로딩 중...</div>;
  if (!post) return <div>게시글을 찾을 수 없습니다.</div>;

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
      <section>
        <h2>댓글 ({comments.length})</h2>
        {/* 댓글 목록 */}
      </section>
    </article>
  );
}
```

---

## 5. 라우트 그룹 ()

괄호로 감싼 폴더는 **URL에 영향을 주지 않습니다**.

### 사용 목적

1. **레이아웃 분리**: 다른 레이아웃을 적용할 그룹 분리
2. **코드 조직화**: 관련 라우트를 논리적으로 그룹화

### 예시

```
app/
├── (marketing)/          # URL에 "marketing" 포함 안됨
│   ├── layout.tsx        # 마케팅 페이지 레이아웃
│   ├── about/page.tsx    # /about
│   └── contact/page.tsx  # /contact
│
├── (shop)/               # URL에 "shop" 포함 안됨
│   ├── layout.tsx        # 쇼핑몰 레이아웃
│   ├── products/page.tsx # /products
│   └── cart/page.tsx     # /cart
│
└── (auth)/               # URL에 "auth" 포함 안됨
    ├── layout.tsx        # 인증 페이지 레이아웃
    ├── login/page.tsx    # /login
    └── register/page.tsx # /register
```

### 프로젝트 적용

```
app/
├── (auth)/                     # 인증 페이지 그룹
│   ├── layout.tsx              # 간단한 레이아웃 (중앙 정렬 카드)
│   ├── login/page.tsx          # /login
│   └── register/page.tsx       # /register
│
└── (main)/                     # 메인 애플리케이션 그룹
    ├── layout.tsx              # MainLayout (사이드바 + 헤더)
    ├── dashboard/page.tsx      # /dashboard
    ├── posts/
    │   ├── page.tsx            # /posts
    │   ├── new/page.tsx        # /posts/new
    │   └── [id]/page.tsx       # /posts/1, /posts/2, ...
    ├── users/page.tsx          # /users
    └── settings/page.tsx       # /settings
```

### 그룹별 레이아웃

```tsx
// frontend/src/app/(auth)/layout.tsx
"use client";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      {/* 인증 페이지는 중앙에 카드 형태로 표시 */}
      {children}
    </div>
  );
}

// frontend/src/app/(main)/layout.tsx
import { MainLayout } from "@/components/layout";

export default function MainPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MainLayout>{children}</MainLayout>;
  // 메인 페이지는 사이드바 + 헤더와 함께 표시
}
```

---

## 6. loading.tsx

페이지가 로딩되는 동안 표시할 UI입니다.

```tsx
// app/posts/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin h-8 w-8 border-4 border-primary rounded-full border-t-transparent" />
    </div>
  );
}
```

### 동작 원리

```
1. /posts 페이지 요청
2. loading.tsx 즉시 표시
3. page.tsx 로딩 완료
4. page.tsx로 교체
```

---

## 7. error.tsx

에러 발생 시 표시할 UI입니다.

```tsx
// app/posts/error.tsx
"use client";  // 에러 컴포넌트는 클라이언트 컴포넌트여야 함

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">오류가 발생했습니다</h2>
      <p className="text-muted-foreground mb-4">{error.message}</p>
      <button
        onClick={reset}  // 다시 시도
        className="px-4 py-2 bg-primary text-white rounded"
      >
        다시 시도
      </button>
    </div>
  );
}
```

---

## 8. not-found.tsx

404 에러 페이지입니다.

```tsx
// app/not-found.tsx
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-6xl font-bold mb-4">404</h1>
      <h2 className="text-2xl mb-4">페이지를 찾을 수 없습니다</h2>
      <Link
        href="/"
        className="px-4 py-2 bg-primary text-white rounded"
      >
        홈으로 돌아가기
      </Link>
    </div>
  );
}
```

### 프로그래밍 방식으로 404 트리거

```tsx
import { notFound } from "next/navigation";

export default async function PostPage({ params }) {
  const post = await getPost(params.id);

  if (!post) {
    notFound();  // not-found.tsx가 표시됨
  }

  return <div>{post.title}</div>;
}
```

---

## 9. 메타데이터

### 정적 메타데이터

```tsx
// app/layout.tsx 또는 page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "내 웹사이트",
  description: "웹사이트 설명",
  keywords: ["키워드1", "키워드2"],
  openGraph: {
    title: "내 웹사이트",
    description: "웹사이트 설명",
    images: ["/og-image.png"],
  },
};
```

### 동적 메타데이터

```tsx
// app/posts/[id]/page.tsx
import type { Metadata } from "next";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const post = await getPost(id);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [post.image],
    },
  };
}

export default async function PostPage({ params }: Props) {
  // ...
}
```

---

## 10. 전체 페이지 흐름

### 요청 처리 순서

```
1. 사용자가 /posts/1 요청
          │
          ▼
2. middleware.ts 실행 (인증 확인 등)
          │
          ▼
3. 레이아웃 렌더링 (RootLayout → MainLayout)
          │
          ▼
4. loading.tsx 표시 (있으면)
          │
          ▼
5. page.tsx 렌더링
          │
    ┌─────┴─────┐
    ▼           ▼
 성공        에러 발생
    │           │
    ▼           ▼
 페이지      error.tsx
 표시        표시
```

### 프로젝트 전체 구조

```
frontend/src/app/
├── layout.tsx              # 루트 레이아웃
├── page.tsx                # 홈 (/ → /dashboard 리다이렉트)
├── globals.css             # 전역 스타일
│
├── (auth)/                 # 인증 그룹
│   ├── layout.tsx          # 인증 레이아웃
│   ├── login/
│   │   └── page.tsx        # 로그인 페이지
│   └── register/
│       └── page.tsx        # 회원가입 페이지
│
└── (main)/                 # 메인 그룹
    ├── layout.tsx          # 메인 레이아웃
    ├── dashboard/
    │   └── page.tsx        # 대시보드
    ├── posts/
    │   ├── page.tsx        # 게시글 목록
    │   ├── new/
    │   │   └── page.tsx    # 새 게시글
    │   └── [id]/
    │       └── page.tsx    # 게시글 상세
    ├── users/
    │   └── page.tsx        # 사용자 관리
    └── settings/
        └── page.tsx        # 설정
```

---

## 요약

| 파일/폴더 | 역할 |
|-----------|------|
| `layout.tsx` | 공유 레이아웃, 중첩 가능 |
| `page.tsx` | URL로 접근 가능한 페이지 |
| `loading.tsx` | 로딩 중 UI |
| `error.tsx` | 에러 발생 시 UI |
| `not-found.tsx` | 404 페이지 |
| `[param]` | 동적 라우트 |
| `[...param]` | Catch-all 라우트 |
| `(group)` | URL에 영향 없는 라우트 그룹 |

## 다음 단계

다음 문서 [06-project-structure.md](./06-project-structure.md)에서 실제 프로젝트 구조를 상세히 분석합니다.
