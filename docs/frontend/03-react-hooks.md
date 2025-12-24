# React Hooks 상세 가이드

## Hooks란?

Hooks는 React 16.8에서 도입된 기능으로, **함수형 컴포넌트에서 상태(state)와 React의 다양한 기능을 사용**할 수 있게 해주는 특별한 함수입니다.

### Hooks의 규칙

```
┌─────────────────────────────────────────────────────────────┐
│                    Hooks 사용 규칙                           │
├─────────────────────────────────────────────────────────────┤
│  1. 최상위에서만 호출: 조건문, 반복문, 중첩 함수 안에서 X    │
│  2. React 함수 안에서만: 일반 JS 함수에서 X                 │
│  3. use로 시작: 모든 Hook은 use로 시작                      │
└─────────────────────────────────────────────────────────────┘
```

```jsx
// ❌ 잘못된 사용
function Component() {
  if (condition) {
    const [value, setValue] = useState(0);  // 조건문 안에서 X
  }

  for (let i = 0; i < 3; i++) {
    useEffect(() => {});  // 반복문 안에서 X
  }
}

// ✅ 올바른 사용
function Component() {
  const [value, setValue] = useState(0);  // 최상위에서 호출

  useEffect(() => {
    // 조건 로직은 Hook 안에서
    if (condition) {
      // ...
    }
  }, [condition]);
}
```

---

## 1. useState - 상태 관리

가장 기본적인 Hook으로, **컴포넌트의 상태를 선언하고 업데이트**합니다.

### 기본 사용법

```jsx
import { useState } from "react";

function Counter() {
  // const [현재값, 업데이트함수] = useState(초기값);
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>카운트: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
      <button onClick={() => setCount(count - 1)}>-1</button>
      <button onClick={() => setCount(0)}>초기화</button>
    </div>
  );
}
```

### 다양한 타입의 상태

```tsx
// 숫자
const [count, setCount] = useState(0);

// 문자열
const [name, setName] = useState("");

// 불린
const [isOpen, setIsOpen] = useState(false);

// 배열
const [items, setItems] = useState<string[]>([]);

// 객체
const [user, setUser] = useState<User | null>(null);

// TypeScript에서 타입 지정
const [value, setValue] = useState<number | null>(null);
```

### 상태 업데이트 패턴

```jsx
// 1. 직접 새 값 설정
setCount(10);

// 2. 이전 값을 기반으로 업데이트 (권장)
setCount(prev => prev + 1);  // 이전 값 + 1

// 3. 객체 상태 업데이트 (전개 연산자 사용)
setUser(prev => ({ ...prev, name: "새이름" }));

// 4. 배열에 추가
setItems(prev => [...prev, "새 아이템"]);

// 5. 배열에서 제거
setItems(prev => prev.filter(item => item !== "제거할 아이템"));
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/posts/page.tsx
export default function PostsPage() {
  // 여러 상태 관리
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // 검색어 입력 처리
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
      <input
        value={searchQuery}
        onChange={handleSearch}
        placeholder="검색..."
      />
      {/* ... */}
    </div>
  );
}
```

---

## 2. useEffect - 부수 효과 처리

컴포넌트의 **렌더링 이후에 실행되는 로직**을 처리합니다. API 호출, 이벤트 리스너 등록, 타이머 설정 등에 사용됩니다.

### 기본 사용법

```jsx
import { useEffect } from "react";

function Component() {
  // 매 렌더링마다 실행
  useEffect(() => {
    console.log("렌더링됨");
  });

  // 마운트 시에만 실행 (한 번)
  useEffect(() => {
    console.log("컴포넌트가 화면에 나타남");
  }, []);  // 빈 배열

  // 특정 값이 변할 때만 실행
  useEffect(() => {
    console.log(`count가 ${count}로 변경됨`);
  }, [count]);  // count를 의존성 배열에 추가
}
```

### 의존성 배열 (Dependency Array)

```jsx
// 1. 의존성 배열 없음: 매 렌더링마다 실행
useEffect(() => {
  // ...
});

// 2. 빈 배열: 마운트 시 한 번만 실행
useEffect(() => {
  // API 호출, 초기화 등
}, []);

// 3. 값 지정: 해당 값이 변경될 때만 실행
useEffect(() => {
  // userId가 변경될 때마다 사용자 정보 다시 불러오기
  fetchUser(userId);
}, [userId]);

// 4. 여러 값: 하나라도 변경되면 실행
useEffect(() => {
  // page 또는 search가 변경될 때마다 실행
  fetchPosts(page, search);
}, [page, search]);
```

### 클린업 함수

컴포넌트가 언마운트되거나 effect가 다시 실행되기 전에 **정리(cleanup)** 작업을 수행합니다.

```jsx
useEffect(() => {
  // 타이머 설정
  const timer = setInterval(() => {
    console.log("tick");
  }, 1000);

  // 클린업: 타이머 정리
  return () => {
    clearInterval(timer);
  };
}, []);

useEffect(() => {
  // 이벤트 리스너 등록
  window.addEventListener("resize", handleResize);

  // 클린업: 이벤트 리스너 제거
  return () => {
    window.removeEventListener("resize", handleResize);
  };
}, []);
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/dashboard/page.tsx
export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 마운트 시 데이터 로드
  useEffect(() => {
    const loadStats = async () => {
      try {
        setIsLoading(true);
        const data = await dashboardApi.getStats();
        setStats(data);
      } catch (error) {
        console.error("대시보드 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);  // 빈 배열 = 마운트 시 한 번만

  // ...
}

// frontend/src/app/(main)/posts/page.tsx
export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  // 페이지나 검색어가 변경될 때마다 게시글 다시 로드
  useEffect(() => {
    const loadPosts = async () => {
      try {
        const response = await postsApi.getList({
          page: currentPage,
          search: searchQuery,
        });
        setPosts(response.items);
      } catch (error) {
        console.error("게시글 로드 실패:", error);
      }
    };

    loadPosts();
  }, [currentPage, searchQuery]);  // 의존성 배열

  // ...
}

// frontend/src/components/layout/MainLayout.tsx
// 테마 적용
useEffect(() => {
  const root = window.document.documentElement;
  root.classList.remove("light", "dark");

  if (theme === "system") {
    const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    root.classList.add(systemTheme);
  } else {
    root.classList.add(theme);
  }
}, [theme]);  // theme가 변경될 때마다 실행
```

---

## 3. useCallback - 함수 메모이제이션

함수를 **메모이제이션(캐싱)**하여 불필요한 재생성을 방지합니다.

### 언제 사용하나요?

```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // ❌ 매 렌더링마다 새 함수 생성
  const handleClick = () => {
    console.log("클릭");
  };

  // ✅ 의존성이 변경될 때만 새 함수 생성
  const handleClick = useCallback(() => {
    console.log("클릭");
  }, []);

  return <Child onClick={handleClick} />;
}
```

### 사용 예시

```tsx
const Parent = () => {
  const [items, setItems] = useState<string[]>([]);

  // 의존성: setItems (실제로는 변경되지 않음)
  const addItem = useCallback((item: string) => {
    setItems(prev => [...prev, item]);
  }, []);

  // 의존성: 특정 값
  const searchItems = useCallback((query: string) => {
    return items.filter(item => item.includes(query));
  }, [items]);  // items가 변경되면 함수 재생성

  return <Child onAdd={addItem} onSearch={searchItems} />;
};
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/MainLayout.tsx
const MainLayout = ({ children }: MainLayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // 사이드바 토글 함수 메모이제이션
  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);

  return (
    <div>
      <Header onMenuToggle={toggleSidebar} />
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
    </div>
  );
};
```

---

## 4. useMemo - 값 메모이제이션

**계산 비용이 높은 값**을 메모이제이션하여 불필요한 재계산을 방지합니다.

### 기본 사용법

```jsx
import { useMemo } from "react";

function ExpensiveComponent({ items }) {
  // ❌ 매 렌더링마다 계산
  const total = items.reduce((sum, item) => sum + item.price, 0);

  // ✅ items가 변경될 때만 계산
  const total = useMemo(() => {
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);

  return <div>총액: {total}</div>;
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/Sidebar.tsx
const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const { user } = useAuthStore();

  // 권한에 따른 메뉴 필터링 (계산 비용 있음)
  const filteredMenuItems = useMemo(() => {
    return menuItems.filter(item => {
      if (!item.roles) return true;
      return item.roles.includes(user?.role as UserRole);
    });
  }, [user?.role]);  // role이 변경될 때만 재계산

  return (
    <nav>
      {filteredMenuItems.map(item => (
        <MenuItem key={item.href} item={item} />
      ))}
    </nav>
  );
};
```

---

## 5. useRef - 참조 저장

**렌더링을 트리거하지 않고 값을 저장**하거나, **DOM 요소에 직접 접근**할 때 사용합니다.

### DOM 접근

```jsx
import { useRef } from "react";

function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();  // DOM 요소에 직접 접근
  };

  return (
    <div>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>입력창 포커스</button>
    </div>
  );
}
```

### 값 저장 (렌더링 없이)

```jsx
function Timer() {
  const [count, setCount] = useState(0);
  const timerRef = useRef<number | null>(null);  // 타이머 ID 저장

  const start = () => {
    timerRef.current = setInterval(() => {
      setCount(prev => prev + 1);
    }, 1000);
  };

  const stop = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };

  return (
    <div>
      <p>카운트: {count}</p>
      <button onClick={start}>시작</button>
      <button onClick={stop}>정지</button>
    </div>
  );
}
```

### 프로젝트 예시

```tsx
// 검색 입력창에 자동 포커스
const SearchInput = () => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();  // 마운트 시 포커스
  }, []);

  return <input ref={inputRef} placeholder="검색..." />;
};
```

---

## 6. useRouter (Next.js)

Next.js에서 **프로그래밍 방식으로 페이지 이동**을 처리합니다.

```tsx
"use client";
import { useRouter } from "next/navigation";

function LoginButton() {
  const router = useRouter();

  const handleLogin = async () => {
    await login();
    router.push("/dashboard");  // 대시보드로 이동
  };

  const handleBack = () => {
    router.back();  // 이전 페이지로
  };

  const handleRefresh = () => {
    router.refresh();  // 현재 페이지 새로고침
  };

  return (
    <button onClick={handleLogin}>로그인</button>
  );
}
```

### 프로젝트 예시

```tsx
// frontend/src/app/(auth)/login/page.tsx
export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuthStore();

  // 이미 로그인되어 있으면 대시보드로 리다이렉트
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.username, data.password);
      router.push("/dashboard");  // 로그인 성공 후 이동
    } catch (error) {
      toast.error("로그인 실패");
    }
  };

  // ...
}

// frontend/src/app/(auth)/register/page.tsx
const onSubmit = async (data: RegisterFormData) => {
  try {
    await authApi.register(data);
    toast.success("회원가입 완료");
    setTimeout(() => {
      router.push("/login");  // 2초 후 로그인 페이지로
    }, 2000);
  } catch (error) {
    toast.error("회원가입 실패");
  }
};
```

---

## 7. usePathname (Next.js)

현재 URL 경로를 가져옵니다.

```tsx
"use client";
import { usePathname } from "next/navigation";

function NavLink({ href, children }) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <a
      href={href}
      className={isActive ? "text-blue-500 font-bold" : "text-gray-500"}
    >
      {children}
    </a>
  );
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/Sidebar.tsx
export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const pathname = usePathname();  // 현재 경로

  return (
    <nav>
      {menuItems.map(item => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md",
            pathname === item.href  // 현재 경로면 활성화 스타일
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:bg-accent"
          )}
        >
          <item.icon className="h-4 w-4" />
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
};
```

---

## 8. useForm (React Hook Form)

폼 상태 관리를 위한 외부 라이브러리 Hook입니다.

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// 1. 스키마 정의 (Zod)
const loginSchema = z.object({
  username: z.string().min(1, "사용자명을 입력하세요"),
  password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다"),
});

// 2. 타입 추론
type LoginFormData = z.infer<typeof loginSchema>;

// 3. 컴포넌트에서 사용
function LoginForm() {
  const {
    register,      // 입력 필드 등록
    handleSubmit,  // 폼 제출 핸들러
    formState: { errors, isSubmitting },  // 폼 상태
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),  // Zod 검증 연결
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    console.log(data);  // { username: "...", password: "..." }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("username")} />
      {errors.username && <span>{errors.username.message}</span>}

      <input type="password" {...register("password")} />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "처리 중..." : "로그인"}
      </button>
    </form>
  );
}
```

### 프로젝트 예시

```tsx
// frontend/src/app/(auth)/login/page.tsx
const loginSchema = z.object({
  username: z.string().min(1, "사용자명 또는 이메일을 입력하세요"),
  password: z.string().min(1, "비밀번호를 입력하세요"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login, isLoading } = useAuthStore();
  const router = useRouter();

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

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.username, data.password);
      toast.success("로그인 성공");
      router.push("/dashboard");
    } catch {
      toast.error("로그인 실패");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="username">사용자명 또는 이메일</Label>
        <Input id="username" {...register("username")} />
        {errors.username && (
          <p className="text-destructive">{errors.username.message}</p>
        )}
      </div>
      {/* ... */}
    </form>
  );
}
```

---

## 9. Custom Hooks - 커스텀 훅

**로직을 재사용**하기 위해 직접 만드는 Hook입니다.

### 작성 규칙

1. 함수 이름은 `use`로 시작
2. 다른 Hook을 내부에서 사용 가능
3. 값이나 함수를 반환

### 예시: useToggle

```tsx
// hooks/useToggle.ts
import { useState, useCallback } from "react";

function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return { value, toggle, setTrue, setFalse };
}

// 사용
function Modal() {
  const { value: isOpen, toggle, setFalse: close } = useToggle(false);

  return (
    <div>
      <button onClick={toggle}>모달 토글</button>
      {isOpen && (
        <div className="modal">
          <p>모달 내용</p>
          <button onClick={close}>닫기</button>
        </div>
      )}
    </div>
  );
}
```

### 예시: useLocalStorage

```tsx
// hooks/useLocalStorage.ts
import { useState, useEffect } from "react";

function useLocalStorage<T>(key: string, initialValue: T) {
  // 초기값 로드
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // 값 변경 시 저장
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    } catch (error) {
      console.error(error);
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue] as const;
}

// 사용
function Settings() {
  const [theme, setTheme] = useLocalStorage("theme", "light");
  // theme는 localStorage에 자동 저장됨
}
```

---

## Hooks 사용 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                    컴포넌트 렌더링 흐름                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. useState 초기화                                          │
│     const [state, setState] = useState(initialValue)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. useMemo, useCallback 계산                               │
│     메모이제이션된 값/함수 준비                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. JSX 렌더링                                               │
│     return <div>...</div>                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. useEffect 실행                                          │
│     렌더링 완료 후 side effects 실행                         │
└─────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┴──────────────────┐
           ▼                                      ▼
┌──────────────────────┐              ┌──────────────────────┐
│  상태 변경 발생      │              │  의존성 변경         │
│  setState(newValue)  │              │  dependency 변경     │
└──────────────────────┘              └──────────────────────┘
           │                                      │
           └──────────────────┬──────────────────┘
                              │
                              ▼
                     [ 다시 렌더링 ]
```

---

## 요약

| Hook | 용도 | 주요 사용처 |
|------|------|------------|
| `useState` | 상태 관리 | 입력값, 로딩 상태, 목록 데이터 |
| `useEffect` | 부수 효과 | API 호출, 이벤트 리스너, 타이머 |
| `useCallback` | 함수 메모이제이션 | 이벤트 핸들러, 자식에게 전달되는 함수 |
| `useMemo` | 값 메모이제이션 | 비용 높은 계산, 필터링된 목록 |
| `useRef` | 참조 저장 | DOM 접근, 타이머 ID, 이전 값 |
| `useRouter` | 페이지 이동 | 로그인 후 리다이렉트, 폼 제출 후 이동 |
| `usePathname` | 현재 경로 | 네비게이션 활성화 표시 |
| `useForm` | 폼 관리 | 로그인, 회원가입, 게시글 작성 |

## 다음 단계

다음 문서 [04-nextjs-fundamentals.md](./04-nextjs-fundamentals.md)에서 Next.js의 기초 개념을 학습합니다.
