# 스타일링 가이드 - Tailwind CSS

## 개요

이 프로젝트는 **Tailwind CSS**를 사용하여 스타일링합니다. Tailwind CSS는 유틸리티 우선(Utility-First) CSS 프레임워크로, 미리 정의된 클래스를 조합하여 스타일을 적용합니다.

---

## 1. Tailwind CSS 기초

### 기존 CSS vs Tailwind CSS

```html
<!-- 기존 CSS -->
<style>
  .card {
    padding: 16px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
</style>
<div class="card">내용</div>

<!-- Tailwind CSS -->
<div class="p-4 bg-white rounded-lg shadow">내용</div>
```

### 클래스 네이밍 규칙

```
{속성}-{값}

예:
p-4       → padding: 1rem (16px)
bg-white  → background-color: white
rounded-lg → border-radius: 0.5rem
shadow    → box-shadow: 0 1px 3px rgba(0,0,0,0.1)
```

---

## 2. 자주 사용하는 클래스

### 레이아웃

```tsx
// Flexbox
<div className="flex">           // display: flex
<div className="flex-col">       // flex-direction: column
<div className="items-center">   // align-items: center
<div className="justify-between"> // justify-content: space-between
<div className="gap-4">          // gap: 1rem

// Grid
<div className="grid grid-cols-3"> // 3열 그리드
<div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4"> // 반응형

// 크기
<div className="w-full">         // width: 100%
<div className="h-screen">       // height: 100vh
<div className="min-h-screen">   // min-height: 100vh
<div className="max-w-md">       // max-width: 28rem
```

### 간격 (Spacing)

```tsx
// Padding (내부 여백)
<div className="p-4">     // padding: 1rem (모든 방향)
<div className="px-4">    // padding-left/right: 1rem
<div className="py-2">    // padding-top/bottom: 0.5rem
<div className="pt-4">    // padding-top: 1rem
<div className="pb-4">    // padding-bottom: 1rem

// Margin (외부 여백)
<div className="m-4">     // margin: 1rem
<div className="mx-auto"> // margin-left/right: auto (중앙 정렬)
<div className="mt-4">    // margin-top: 1rem
<div className="mb-6">    // margin-bottom: 1.5rem

// 간격 값
// 0 = 0px, 1 = 0.25rem (4px), 2 = 0.5rem (8px), 4 = 1rem (16px), 6 = 1.5rem, 8 = 2rem
```

### 색상

```tsx
// 배경색
<div className="bg-white">
<div className="bg-gray-100">
<div className="bg-blue-500">
<div className="bg-primary">      // 테마 색상

// 텍스트 색상
<p className="text-black">
<p className="text-gray-500">
<p className="text-blue-600">
<p className="text-primary">

// 투명도
<div className="bg-black/50">     // 50% 투명도
<div className="bg-background/95"> // 95% 투명도

// 테마 색상 (프로젝트)
bg-background     // 배경색
bg-foreground     // 전경색
bg-primary        // 주요 색상
bg-secondary      // 보조 색상
bg-accent         // 강조 색상
bg-muted          // 흐린 색상
bg-destructive    // 위험/삭제 색상
```

### 텍스트

```tsx
// 크기
<p className="text-xs">     // 0.75rem
<p className="text-sm">     // 0.875rem
<p className="text-base">   // 1rem
<p className="text-lg">     // 1.125rem
<p className="text-xl">     // 1.25rem
<p className="text-2xl">    // 1.5rem
<p className="text-3xl">    // 1.875rem

// 굵기
<p className="font-normal"> // 400
<p className="font-medium"> // 500
<p className="font-semibold"> // 600
<p className="font-bold">   // 700

// 정렬
<p className="text-left">
<p className="text-center">
<p className="text-right">
```

### 테두리

```tsx
// 테두리
<div className="border">          // border: 1px solid
<div className="border-2">        // border: 2px solid
<div className="border-gray-200"> // border-color

// 둥근 모서리
<div className="rounded">         // border-radius: 0.25rem
<div className="rounded-md">      // border-radius: 0.375rem
<div className="rounded-lg">      // border-radius: 0.5rem
<div className="rounded-full">    // border-radius: 9999px (원형)
```

### 그림자

```tsx
<div className="shadow">          // 작은 그림자
<div className="shadow-md">       // 중간 그림자
<div className="shadow-lg">       // 큰 그림자
<div className="shadow-xl">       // 매우 큰 그림자
```

---

## 3. 반응형 디자인

### 브레이크포인트

```
sm:  640px 이상   (스마트폰 가로)
md:  768px 이상   (태블릿)
lg:  1024px 이상  (데스크톱)
xl:  1280px 이상  (큰 데스크톱)
2xl: 1536px 이상  (매우 큰 화면)
```

### 사용법

```tsx
// 모바일 우선 (Mobile First)
<div className="
  w-full          // 기본: 전체 너비
  md:w-1/2        // 768px 이상: 50%
  lg:w-1/3        // 1024px 이상: 33%
">

// 숨기기/표시
<div className="hidden md:block">  // 768px 미만에서 숨김
<div className="block md:hidden">  // 768px 이상에서 숨김

// 그리드 열 수
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  // 기본: 1열, 768px+: 2열, 1024px+: 4열
```

### 프로젝트 예시

```tsx
// src/components/layout/Sidebar.tsx
// 데스크톱에서만 표시
<aside className="hidden md:flex md:flex-col md:w-64 md:fixed">
  {/* 사이드바 내용 */}
</aside>

// 모바일에서만 표시 (Sheet)
<Sheet open={isOpen} onOpenChange={onClose}>
  <SheetContent side="left" className="w-64 md:hidden">
    {/* 모바일 메뉴 */}
  </SheetContent>
</Sheet>
```

---

## 4. 상태 변형 (State Variants)

### 호버, 포커스, 활성화

```tsx
// 호버
<button className="bg-blue-500 hover:bg-blue-600">
  마우스 올리면 색상 변경
</button>

// 포커스
<input className="border focus:border-blue-500 focus:ring-2">

// 활성화 (클릭 중)
<button className="bg-blue-500 active:bg-blue-700">

// 비활성화
<button className="disabled:opacity-50 disabled:cursor-not-allowed" disabled>
```

### 다크 모드

```tsx
// 다크 모드에서 다른 스타일
<div className="bg-white dark:bg-gray-900">
<p className="text-gray-900 dark:text-gray-100">
```

### 조합

```tsx
// 여러 상태 조합
<button className="
  bg-primary
  hover:bg-primary/90
  focus:ring-2
  focus:ring-primary
  disabled:opacity-50
  dark:bg-primary-dark
">
```

---

## 5. 프로젝트 테마 설정

### globals.css 구조

```css
/* src/app/globals.css */
@import "tailwindcss";      /* Tailwind 기본 스타일 */
@import "tw-animate-css";   /* 애니메이션 */

/* 테마 변수 정의 */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ... */
}

/* 라이트 모드 색상 */
:root {
  --background: oklch(1 0 0);           /* 흰색 */
  --foreground: oklch(0.145 0 0);       /* 거의 검정 */
  --primary: oklch(0.205 0 0);          /* 주요 색상 */
  --secondary: oklch(0.97 0 0);
  --muted: oklch(0.97 0 0);
  --accent: oklch(0.97 0 0);
  --destructive: oklch(0.577 0.245 27.325);  /* 빨간색 */
  /* ... */
}

/* 다크 모드 색상 */
.dark {
  --background: oklch(0.145 0 0);       /* 거의 검정 */
  --foreground: oklch(0.985 0 0);       /* 거의 흰색 */
  --primary: oklch(0.985 0 0);
  /* ... */
}

/* 기본 스타일 */
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### 테마 색상 사용

```tsx
// 테마 색상 클래스
<div className="bg-background">      // 배경색 (라이트: 흰색, 다크: 검정)
<div className="text-foreground">    // 텍스트 (라이트: 검정, 다크: 흰색)
<div className="bg-primary">         // 주요 색상
<div className="text-primary">
<div className="bg-secondary">       // 보조 색상
<div className="bg-muted">           // 흐린 배경
<div className="text-muted-foreground"> // 흐린 텍스트
<div className="bg-accent">          // 강조 배경 (호버 등)
<div className="bg-destructive">     // 위험/삭제 버튼
<div className="text-destructive">   // 에러 메시지
```

---

## 6. cn() 유틸리티 함수

### 정의

```tsx
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 기능

1. **clsx**: 조건부 클래스 결합
2. **tailwind-merge**: 충돌하는 Tailwind 클래스 해결

### 사용 예시

```tsx
import { cn } from "@/lib/utils";

// 조건부 클래스
<div className={cn(
  "base-class",
  isActive && "active-class",
  isDisabled && "disabled-class"
)}>

// Tailwind 클래스 충돌 해결
cn("px-4", "px-6")  // → "px-6" (나중 값 우선)

// 컴포넌트에서 className prop 병합
interface ButtonProps {
  className?: string;
}

const Button = ({ className, ...props }: ButtonProps) => {
  return (
    <button
      className={cn(
        "px-4 py-2 bg-primary text-white rounded",  // 기본 스타일
        className  // 외부에서 전달된 추가 스타일
      )}
      {...props}
    />
  );
};

// 사용
<Button className="mt-4">저장</Button>  // mt-4가 추가됨
```

### 프로젝트 예시

```tsx
// src/components/layout/Sidebar.tsx
<Link
  href={item.href}
  className={cn(
    // 기본 스타일
    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
    // 조건부 스타일 (현재 경로면 활성화)
    pathname === item.href
      ? "bg-accent text-accent-foreground"
      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
  )}
>
```

---

## 7. shadcn/ui 컴포넌트 스타일

### variants 패턴

```tsx
// src/components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  // 기본 스타일
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// 사용
<Button variant="destructive" size="sm">삭제</Button>
```

---

## 8. 자주 사용하는 패턴

### 카드 레이아웃

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <Card key={item.id} className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle>{item.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{item.description}</p>
      </CardContent>
    </Card>
  ))}
</div>
```

### 중앙 정렬 컨테이너

```tsx
// 화면 중앙에 카드 배치 (로그인 페이지)
<div className="flex min-h-screen items-center justify-center bg-background">
  <Card className="w-full max-w-md">
    {/* 내용 */}
  </Card>
</div>
```

### 사이드바 + 콘텐츠 레이아웃

```tsx
<div className="flex min-h-screen">
  {/* 사이드바 */}
  <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 border-r">
    {/* 사이드바 내용 */}
  </aside>

  {/* 메인 콘텐츠 */}
  <div className="flex-1 md:ml-64">
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
      {/* 헤더 */}
    </header>
    <main className="p-6">
      {/* 페이지 콘텐츠 */}
    </main>
  </div>
</div>
```

### 폼 레이아웃

```tsx
<form className="space-y-4">
  <div className="space-y-2">
    <Label htmlFor="email">이메일</Label>
    <Input id="email" type="email" placeholder="email@example.com" />
    <p className="text-sm text-destructive">에러 메시지</p>
  </div>

  <div className="space-y-2">
    <Label htmlFor="password">비밀번호</Label>
    <Input id="password" type="password" />
  </div>

  <Button type="submit" className="w-full">
    제출
  </Button>
</form>
```

---

## 9. 유용한 클래스 조합

```tsx
// 로딩 스피너
<div className="animate-spin h-8 w-8 border-4 border-primary rounded-full border-t-transparent" />

// 줄임표 (말줄임)
<p className="truncate">긴 텍스트가 잘립니다...</p>

// 여러 줄 말줄임
<p className="line-clamp-2">2줄까지만 표시하고 잘립니다...</p>

// 스크롤 가능 영역
<div className="overflow-y-auto max-h-96">
  {/* 긴 내용 */}
</div>

// 고정 헤더 (스크롤해도 상단 고정)
<header className="sticky top-0 z-40 bg-background/95 backdrop-blur">

// 전체 화면 오버레이
<div className="fixed inset-0 bg-black/50 z-50">

// 뱃지
<span className="inline-flex items-center rounded-full bg-primary px-2 py-1 text-xs font-medium text-primary-foreground">
  New
</span>
```

---

## 요약

| 개념 | 설명 |
|------|------|
| 유틸리티 클래스 | `p-4`, `bg-white` 등 미리 정의된 클래스 |
| 반응형 | `md:`, `lg:` 접두사로 브레이크포인트 지정 |
| 상태 변형 | `hover:`, `focus:`, `dark:` 접두사 |
| 테마 색상 | `bg-primary`, `text-muted-foreground` 등 |
| cn() | 조건부 클래스 결합 + 충돌 해결 |
| variants | shadcn/ui의 variant 패턴 |

## 다음 단계

다음 문서 [12-forms-validation.md](./12-forms-validation.md)에서 폼과 검증을 학습합니다.
