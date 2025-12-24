# 컴포넌트 상세 분석

## 개요

이 문서에서는 프로젝트의 주요 컴포넌트들을 상세히 분석합니다. 각 컴포넌트의 역할, Props, 상태, 그리고 동작 방식을 설명합니다.

---

## 1. 레이아웃 컴포넌트

### MainLayout - 메인 레이아웃

**파일 위치:** `src/components/layout/MainLayout.tsx`

```tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const router = useRouter();
  const { isAuthenticated, isLoading, fetchUser } = useAuthStore();
  const { theme } = useThemeStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // 마운트 시 사용자 정보 로드
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // 인증 확인
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

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

  // 로딩 중 표시
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin h-8 w-8 border-4 border-primary rounded-full border-t-transparent" />
      </div>
    );
  }

  // 비인증 상태
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col md:ml-64">
        <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
```

**핵심 기능:**
| 기능 | 설명 |
|------|------|
| 인증 확인 | 로그인 안 되어 있으면 /login으로 리다이렉트 |
| 테마 적용 | 라이트/다크/시스템 테마 적용 |
| 사이드바 토글 | 모바일에서 사이드바 열기/닫기 |
| 레이아웃 구성 | 사이드바 + 헤더 + 메인 콘텐츠 |

**컴포넌트 구조:**
```
MainLayout
├── Sidebar (왼쪽, 고정)
└── div.flex-1 (오른쪽)
    ├── Header (상단)
    └── main (콘텐츠 영역)
        └── {children}
```

---

### Header - 헤더 컴포넌트

**파일 위치:** `src/components/layout/Header.tsx`

```tsx
"use client";

import { Menu, Sun, Moon, LogOut, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { useRouter } from "next/navigation";

interface HeaderProps {
  onMenuToggle: () => void;
}

export const Header = ({ onMenuToggle }: HeaderProps) => {
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
      <div className="flex h-14 items-center justify-between px-4">
        {/* 모바일 메뉴 버튼 */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuToggle}
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex-1" />

        <div className="flex items-center gap-2">
          {/* 테마 토글 */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* 사용자 드롭다운 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    {user?.username?.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end">
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user?.username}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push("/settings")}>
                <Settings className="mr-2 h-4 w-4" />
                설정
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                로그아웃
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
```

**Props:**
| Prop | 타입 | 설명 |
|------|------|------|
| `onMenuToggle` | `() => void` | 모바일 메뉴 토글 함수 |

**핵심 기능:**
- 모바일 메뉴 버튼 (md 이하에서만 표시)
- 테마 토글 (라이트 ↔ 다크)
- 사용자 드롭다운 메뉴 (설정, 로그아웃)

---

### Sidebar - 사이드바 컴포넌트

**파일 위치:** `src/components/layout/Sidebar.tsx`

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, FileText, Users, Settings, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { useAuthStore } from "@/stores/authStore";
import { UserRole } from "@/types";

// 메뉴 아이템 정의
const menuItems = [
  { href: "/dashboard", label: "대시보드", icon: Home },
  { href: "/posts", label: "게시글", icon: FileText },
  { href: "/users", label: "사용자 관리", icon: Users, roles: ["admin", "moderator"] },
  { href: "/settings", label: "설정", icon: Settings },
];

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const pathname = usePathname();
  const { user } = useAuthStore();

  // 권한에 따른 메뉴 필터링
  const filteredMenuItems = menuItems.filter(item => {
    if (!item.roles) return true;
    return item.roles.includes(user?.role as UserRole);
  });

  // 메뉴 링크 렌더링
  const renderNavLinks = () => (
    <nav className="space-y-1 px-2">
      {filteredMenuItems.map(item => (
        <Link
          key={item.href}
          href={item.href}
          onClick={onClose}  // 모바일에서 클릭 시 닫기
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
            pathname === item.href
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          )}
        >
          <item.icon className="h-4 w-4" />
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );

  return (
    <>
      {/* 데스크톱 사이드바 */}
      <aside className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 border-r bg-background">
        <div className="flex h-14 items-center border-b px-4">
          <span className="text-lg font-semibold">FastAPI Tutorial</span>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          {renderNavLinks()}
        </div>
      </aside>

      {/* 모바일 사이드바 (Sheet) */}
      <Sheet open={isOpen} onOpenChange={onClose}>
        <SheetContent side="left" className="w-64 p-0">
          <div className="flex h-14 items-center justify-between border-b px-4">
            <span className="text-lg font-semibold">FastAPI Tutorial</span>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="py-4">{renderNavLinks()}</div>
        </SheetContent>
      </Sheet>
    </>
  );
};
```

**Props:**
| Prop | 타입 | 설명 |
|------|------|------|
| `isOpen` | `boolean` | 모바일에서 사이드바 열림 상태 |
| `onClose` | `() => void` | 사이드바 닫기 함수 (선택적) |

**핵심 기능:**
- 데스크톱: 고정된 왼쪽 사이드바
- 모바일: Sheet 컴포넌트로 슬라이드 메뉴
- 권한 기반 메뉴 필터링 (roles 속성)
- 현재 경로 활성화 표시

---

## 2. UI 컴포넌트 (shadcn/ui)

### Button - 버튼

```tsx
// 사용 예시
import { Button } from "@/components/ui/button";

// 기본 버튼
<Button>클릭</Button>

// 변형 (variant)
<Button variant="default">기본</Button>
<Button variant="destructive">삭제</Button>
<Button variant="outline">외곽선</Button>
<Button variant="secondary">보조</Button>
<Button variant="ghost">고스트</Button>
<Button variant="link">링크</Button>

// 크기 (size)
<Button size="default">기본</Button>
<Button size="sm">작게</Button>
<Button size="lg">크게</Button>
<Button size="icon">아이콘</Button>

// 로딩 상태
<Button disabled={isLoading}>
  {isLoading ? "처리 중..." : "제출"}
</Button>
```

### Card - 카드

```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>카드 제목</CardTitle>
    <CardDescription>카드 설명</CardDescription>
  </CardHeader>
  <CardContent>
    <p>카드 내용</p>
  </CardContent>
  <CardFooter>
    <Button>액션</Button>
  </CardFooter>
</Card>
```

### Input - 입력 필드

```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

<div className="space-y-2">
  <Label htmlFor="email">이메일</Label>
  <Input
    id="email"
    type="email"
    placeholder="example@email.com"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
  />
</div>

// React Hook Form과 함께
<Input {...register("email")} />
```

### Dialog - 모달 다이얼로그

```tsx
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";

const [open, setOpen] = useState(false);

<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>다이얼로그 열기</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>제목</DialogTitle>
      <DialogDescription>설명</DialogDescription>
    </DialogHeader>
    <div className="py-4">내용</div>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">취소</Button>
      </DialogClose>
      <Button onClick={handleConfirm}>확인</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Tabs - 탭

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

<Tabs defaultValue="profile">
  <TabsList>
    <TabsTrigger value="profile">프로필</TabsTrigger>
    <TabsTrigger value="password">비밀번호</TabsTrigger>
    <TabsTrigger value="theme">테마</TabsTrigger>
  </TabsList>
  <TabsContent value="profile">
    프로필 설정 내용
  </TabsContent>
  <TabsContent value="password">
    비밀번호 변경 내용
  </TabsContent>
  <TabsContent value="theme">
    테마 설정 내용
  </TabsContent>
</Tabs>
```

### DropdownMenu - 드롭다운 메뉴

```tsx
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost">메뉴 열기</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={() => console.log("항목 1")}>
      항목 1
    </DropdownMenuItem>
    <DropdownMenuItem onClick={() => console.log("항목 2")}>
      항목 2
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-destructive">
      삭제
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## 3. 페이지 컴포넌트

### DashboardPage - 대시보드

**파일 위치:** `src/app/(main)/dashboard/page.tsx`

```tsx
"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Users, FileText, MessageSquare, Activity } from "lucide-react";
import { dashboardApi } from "@/lib/api";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await dashboardApi.getStats();
        setStats(data);
      } catch (error) {
        console.error("대시보드 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadStats();
  }, []);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">대시보드</h1>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="전체 사용자"
          value={stats?.total_users ?? 0}
          icon={Users}
        />
        <StatCard
          title="전체 게시글"
          value={stats?.total_posts ?? 0}
          icon={FileText}
        />
        <StatCard
          title="전체 댓글"
          value={stats?.total_comments ?? 0}
          icon={MessageSquare}
        />
        <StatCard
          title="활성도"
          value="--"
          icon={Activity}
        />
      </div>

      {/* 최근 활동 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentUsers users={stats?.recent_users ?? []} />
        <RecentPosts posts={stats?.recent_posts ?? []} />
      </div>
    </div>
  );
}

// 통계 카드 컴포넌트
const StatCard = ({ title, value, icon: Icon }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
    </CardContent>
  </Card>
);
```

**핵심 기능:**
- API에서 통계 데이터 로드
- 통계 카드 그리드 표시
- 최근 사용자/게시글 목록

---

### LoginPage - 로그인 페이지

**파일 위치:** `src/app/(auth)/login/page.tsx`

```tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import Link from "next/link";

// 폼 스키마
const loginSchema = z.object({
  username: z.string().min(1, "사용자명 또는 이메일을 입력하세요"),
  password: z.string().min(1, "비밀번호를 입력하세요"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, isAuthenticated, error, clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
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
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold">로그인</CardTitle>
        <CardDescription>계정에 로그인하세요</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">사용자명 또는 이메일</Label>
            <Input
              id="username"
              {...register("username")}
              placeholder="사용자명 또는 이메일"
            />
            {errors.username && (
              <p className="text-sm text-destructive">{errors.username.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              type="password"
              {...register("password")}
              placeholder="비밀번호"
            />
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "로그인 중..." : "로그인"}
          </Button>
        </form>
      </CardContent>
      <CardFooter className="flex justify-center">
        <p className="text-sm text-muted-foreground">
          계정이 없으신가요?{" "}
          <Link href="/register" className="text-primary hover:underline">
            회원가입
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
```

**핵심 기능:**
- React Hook Form + Zod 검증
- Zustand store와 연동
- 토스트 알림
- 조건부 리다이렉트

---

## 4. 컴포넌트 계층 구조

```
App
├── RootLayout
│   └── Toaster (전역 토스트)
│
├── (auth) Layout
│   ├── LoginPage
│   │   ├── Card
│   │   │   ├── CardHeader
│   │   │   ├── CardContent
│   │   │   │   └── form
│   │   │   │       ├── Input (username)
│   │   │   │       ├── Input (password)
│   │   │   │       └── Button (submit)
│   │   │   └── CardFooter
│   │   └── Link (to register)
│   │
│   └── RegisterPage
│       └── (유사한 구조)
│
└── (main) Layout
    └── MainLayout
        ├── Sidebar
        │   └── nav
        │       └── Link (반복)
        │
        ├── Header
        │   ├── Button (menu toggle)
        │   ├── Button (theme toggle)
        │   └── DropdownMenu (user)
        │
        └── {children}
            ├── DashboardPage
            │   ├── StatCard (x4)
            │   ├── RecentUsers
            │   └── RecentPosts
            │
            ├── PostsPage
            │   ├── Input (search)
            │   ├── Button (new post)
            │   └── Card (반복)
            │
            └── ...
```

---

## 요약

| 컴포넌트 | 위치 | 역할 |
|----------|------|------|
| MainLayout | layout/ | 메인 페이지 레이아웃 |
| Header | layout/ | 헤더 (테마, 사용자 메뉴) |
| Sidebar | layout/ | 네비게이션 사이드바 |
| Button | ui/ | 버튼 |
| Card | ui/ | 카드 컨테이너 |
| Input | ui/ | 입력 필드 |
| Dialog | ui/ | 모달 다이얼로그 |
| Tabs | ui/ | 탭 |
| DropdownMenu | ui/ | 드롭다운 메뉴 |

## 다음 단계

다음 문서 [08-state-management.md](./08-state-management.md)에서 Zustand를 이용한 상태 관리를 학습합니다.
