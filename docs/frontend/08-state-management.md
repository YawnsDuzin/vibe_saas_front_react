# 상태 관리 - Zustand

## 상태 관리란?

**상태(State)**는 애플리케이션의 데이터입니다. 예를 들어:
- 로그인한 사용자 정보
- 현재 선택된 테마
- 장바구니 아이템 목록
- 폼 입력 값

### 왜 상태 관리가 필요할까?

```
문제: 여러 컴포넌트에서 같은 데이터 필요

                ┌─────────────┐
                │   Header    │ ← user.name 필요
                └─────────────┘
                       ↑
                ┌─────────────┐
                │   Sidebar   │ ← user.role 필요
                └─────────────┘
                       ↑
                ┌─────────────┐
                │   Profile   │ ← user 전체 필요
                └─────────────┘

Props로만 전달하면 → "Props Drilling" 문제 발생
                     (중간 컴포넌트들이 불필요하게 props 전달)
```

**해결책: 전역 상태 관리**
```
                ┌─────────────────────────────┐
                │        Zustand Store        │
                │    { user, login, logout }  │
                └─────────────────────────────┘
                      ↓       ↓       ↓
              ┌───────┴───┐ ┌─┴─────┐ ┌┴──────────┐
              │  Header   │ │Sidebar│ │  Profile  │
              └───────────┘ └───────┘ └───────────┘
              (직접 접근)   (직접 접근)  (직접 접근)
```

---

## Zustand 소개

Zustand(독일어로 "상태")는 React용 **경량 상태 관리 라이브러리**입니다.

### Zustand vs 다른 라이브러리

```
┌─────────────────────────────────────────────────────────────┐
│                    상태 관리 라이브러리 비교                 │
├────────────────┬────────────┬───────────┬───────────────────┤
│                │   Redux    │  Zustand  │  Context API      │
├────────────────┼────────────┼───────────┼───────────────────┤
│  번들 크기     │    큼      │   작음    │  React 내장       │
│  보일러플레이트│    많음    │   적음    │  중간             │
│  학습 곡선     │    높음    │   낮음    │  낮음             │
│  DevTools      │    O       │   O       │  제한적           │
│  성능          │    좋음    │   좋음    │  리렌더링 이슈    │
└────────────────┴────────────┴───────────┴───────────────────┘
```

---

## 1. Zustand 기본 사용법

### Store 생성

```tsx
// stores/counterStore.ts
import { create } from "zustand";

// 1. 상태 타입 정의
interface CounterState {
  count: number;           // 상태 값
  increment: () => void;   // 액션 함수
  decrement: () => void;
  reset: () => void;
}

// 2. Store 생성
export const useCounterStore = create<CounterState>((set) => ({
  // 초기 상태
  count: 0,

  // 액션 (상태 업데이트 함수)
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
```

### 컴포넌트에서 사용

```tsx
// components/Counter.tsx
"use client";

import { useCounterStore } from "@/stores/counterStore";

export const Counter = () => {
  // 전체 상태 가져오기
  const { count, increment, decrement, reset } = useCounterStore();

  // 또는 필요한 것만 선택
  // const count = useCounterStore((state) => state.count);
  // const increment = useCounterStore((state) => state.increment);

  return (
    <div>
      <p>카운트: {count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={decrement}>-1</button>
      <button onClick={reset}>초기화</button>
    </div>
  );
};
```

---

## 2. authStore - 인증 상태 관리

프로젝트의 인증 상태를 관리하는 Store입니다.

### 전체 코드

```tsx
// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authApi, setTokens, clearTokens } from "@/lib/api";
import type { User } from "@/types";

// 상태 타입 정의
interface AuthState {
  user: User | null;           // 현재 로그인한 사용자
  isAuthenticated: boolean;    // 인증 여부
  isLoading: boolean;          // 로딩 상태
  error: string | null;        // 에러 메시지

  // 액션
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

// Store 생성
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // 초기 상태
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // 로그인
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          // 1. 로그인 API 호출
          const tokens = await authApi.login(username, password);
          // 2. 토큰 저장 (쿠키)
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
        clearTokens();  // 토큰 삭제
        set({ user: null, isAuthenticated: false });
      },

      // 사용자 정보 조회 (토큰으로)
      fetchUser: async () => {
        set({ isLoading: true });
        try {
          const user = await authApi.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      // 에러 초기화
      clearError: () => set({ error: null }),
    }),
    {
      name: "auth-storage",  // localStorage 키
      partialize: (state) => ({
        // 저장할 상태만 선택
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### 각 부분 설명

#### 1. 타입 정의

```tsx
interface AuthState {
  // 상태 (데이터)
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // 액션 (함수)
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}
```

#### 2. set 함수로 상태 업데이트

```tsx
// 방법 1: 객체 직접 전달
set({ isLoading: true });

// 방법 2: 이전 상태 기반 업데이트
set((state) => ({ count: state.count + 1 }));

// 여러 값 동시 업데이트
set({ user, isAuthenticated: true, isLoading: false });
```

#### 3. persist 미들웨어

```tsx
persist(
  (set) => ({ /* store 정의 */ }),
  {
    name: "auth-storage",  // localStorage 키
    partialize: (state) => ({
      // 저장할 상태만 선택 (isLoading, error는 저장 안함)
      user: state.user,
      isAuthenticated: state.isAuthenticated,
    }),
  }
)
```

**효과:**
- 페이지 새로고침해도 로그인 상태 유지
- localStorage에 `auth-storage` 키로 저장

### 사용 예시

```tsx
// 로그인 페이지
"use client";

import { useAuthStore } from "@/stores/authStore";

export default function LoginPage() {
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleLogin = async (data) => {
    try {
      await login(data.username, data.password);
      router.push("/dashboard");
    } catch {
      // 에러는 store에서 처리됨
    }
  };

  return (
    <form onSubmit={handleSubmit(handleLogin)}>
      {error && <p className="text-red-500">{error}</p>}
      <button disabled={isLoading}>
        {isLoading ? "로그인 중..." : "로그인"}
      </button>
    </form>
  );
}

// 헤더 컴포넌트
import { useAuthStore } from "@/stores/authStore";

export const Header = () => {
  const { user, logout } = useAuthStore();

  return (
    <header>
      <span>안녕하세요, {user?.username}님!</span>
      <button onClick={logout}>로그아웃</button>
    </header>
  );
};

// 사이드바 컴포넌트
import { useAuthStore } from "@/stores/authStore";

export const Sidebar = () => {
  const user = useAuthStore((state) => state.user);
  // user?.role로 권한 체크
};
```

---

## 3. themeStore - 테마 상태 관리

```tsx
// src/stores/themeStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "light" | "dark" | "system";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "system",  // 기본값: 시스템 설정 따름
      setTheme: (theme: Theme) => set({ theme }),
    }),
    {
      name: "theme-storage",  // localStorage 키
    }
  )
);
```

### 사용 예시

```tsx
// 테마 토글 버튼
"use client";

import { useThemeStore } from "@/stores/themeStore";
import { Sun, Moon } from "lucide-react";

export const ThemeToggle = () => {
  const { theme, setTheme } = useThemeStore();

  return (
    <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      {theme === "dark" ? <Sun /> : <Moon />}
    </button>
  );
};

// 레이아웃에서 테마 적용
"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/stores/themeStore";

export const MainLayout = ({ children }) => {
  const { theme } = useThemeStore();

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  return <div>{children}</div>;
};
```

---

## 4. Zustand 패턴들

### 선택적 구독 (성능 최적화)

```tsx
// ❌ 전체 상태 구독 (불필요한 리렌더링)
const { user, login, logout, isLoading } = useAuthStore();

// ✅ 필요한 것만 구독 (최적화)
const user = useAuthStore((state) => state.user);
const login = useAuthStore((state) => state.login);

// ✅ shallow 비교로 여러 값 선택
import { useShallow } from "zustand/react/shallow";

const { user, isLoading } = useAuthStore(
  useShallow((state) => ({
    user: state.user,
    isLoading: state.isLoading,
  }))
);
```

### 비동기 액션

```tsx
const useStore = create((set) => ({
  data: null,
  isLoading: false,
  error: null,

  fetchData: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch("/api/data");
      const data = await response.json();
      set({ data, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },
}));
```

### get으로 현재 상태 읽기

```tsx
const useStore = create((set, get) => ({
  items: [],

  addItem: (item) => {
    const currentItems = get().items;  // 현재 상태 읽기
    set({ items: [...currentItems, item] });
  },

  removeItem: (id) => {
    const currentItems = get().items;
    set({ items: currentItems.filter(item => item.id !== id) });
  },
}));
```

### Store 외부에서 상태 접근

```tsx
// 컴포넌트 외부 (유틸리티 함수 등)에서
const currentUser = useAuthStore.getState().user;
const logout = useAuthStore.getState().logout;

// 상태 변경 구독
const unsubscribe = useAuthStore.subscribe((state) => {
  console.log("상태 변경:", state);
});
```

---

## 5. 상태 관리 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                      로그인 흐름                             │
└─────────────────────────────────────────────────────────────┘

  사용자 입력          Store              API              UI
      │                  │                 │                │
      │ 폼 제출          │                 │                │
      ├─────────────────▶│                 │                │
      │                  │ set(isLoading)  │                │
      │                  ├─────────────────┼───────────────▶│ 로딩 표시
      │                  │                 │                │
      │                  │ login API ──────▶                │
      │                  │                 │                │
      │                  │ ◀────── tokens  │                │
      │                  │                 │                │
      │                  │ setTokens       │                │
      │                  │ (쿠키 저장)     │                │
      │                  │                 │                │
      │                  │ fetchUser ──────▶                │
      │                  │                 │                │
      │                  │ ◀────── user    │                │
      │                  │                 │                │
      │                  │ set(user,       │                │
      │                  │   isAuth=true)  │                │
      │                  ├─────────────────┼───────────────▶│ UI 업데이트
      │                  │                 │                │
      │                  │ persist         │                │
      │                  │ (localStorage)  │                │
```

---

## 6. Store 구조 권장 패턴

```tsx
// stores/exampleStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

// 1. 타입 정의
interface ExampleState {
  // 상태
  items: Item[];
  selectedId: number | null;
  isLoading: boolean;
  error: string | null;

  // 액션
  fetchItems: () => Promise<void>;
  selectItem: (id: number) => void;
  addItem: (item: Item) => void;
  removeItem: (id: number) => void;
  clearError: () => void;
}

// 2. Store 생성
export const useExampleStore = create<ExampleState>()(
  persist(
    (set, get) => ({
      // 초기 상태
      items: [],
      selectedId: null,
      isLoading: false,
      error: null,

      // 비동기 액션
      fetchItems: async () => {
        set({ isLoading: true, error: null });
        try {
          const items = await api.getItems();
          set({ items, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "에러 발생",
            isLoading: false
          });
        }
      },

      // 동기 액션
      selectItem: (id) => set({ selectedId: id }),

      addItem: (item) => {
        const items = get().items;
        set({ items: [...items, item] });
      },

      removeItem: (id) => {
        const items = get().items;
        set({ items: items.filter(i => i.id !== id) });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "example-storage",
      partialize: (state) => ({
        items: state.items,
        selectedId: state.selectedId,
      }),
    }
  )
);
```

---

## 요약

| 개념 | 설명 |
|------|------|
| Store | 상태와 액션을 담는 저장소 |
| `create` | Store 생성 함수 |
| `set` | 상태 업데이트 함수 |
| `get` | 현재 상태 읽기 함수 |
| `persist` | localStorage 지속성 미들웨어 |
| 선택적 구독 | 성능 최적화를 위한 부분 구독 |

## 다음 단계

다음 문서 [09-api-integration.md](./09-api-integration.md)에서 API 연동 방법을 학습합니다.
