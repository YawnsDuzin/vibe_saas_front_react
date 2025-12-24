# JavaScript 기초 - React를 위한 필수 개념

## 개요

React를 이해하기 위해 알아야 할 JavaScript의 핵심 개념들을 설명합니다. 이 문서에서 다루는 내용은 모두 프로젝트 코드에서 실제로 사용됩니다.

## 1. 변수 선언: const와 let

### const - 재할당 불가능한 변수

```javascript
const name = "홍길동";
// name = "김철수";  // 오류! const는 재할당 불가

const user = { name: "홍길동" };
user.name = "김철수";  // 가능! 객체의 속성 변경은 허용
```

### let - 재할당 가능한 변수

```javascript
let count = 0;
count = count + 1;  // 가능
```

### 프로젝트 예시

```typescript
// frontend/src/stores/authStore.ts
const useAuthStore = create<AuthState>()(...);  // 스토어는 한번 생성되면 변경 안됨

// frontend/src/app/(auth)/login/page.tsx
let errorMessage = "";  // 오류 메시지는 변경될 수 있음
```

**규칙**: 기본적으로 `const`를 사용하고, 값이 변해야 할 때만 `let`을 사용합니다.

---

## 2. 화살표 함수 (Arrow Function)

### 기본 문법

```javascript
// 전통적인 함수
function add(a, b) {
  return a + b;
}

// 화살표 함수 (동일한 기능)
const add = (a, b) => {
  return a + b;
};

// 한 줄일 때 중괄호와 return 생략 가능
const add = (a, b) => a + b;

// 매개변수가 하나일 때 괄호 생략 가능
const double = x => x * 2;
```

### 프로젝트 예시

```typescript
// frontend/src/components/layout/Header.tsx
const Header = () => {            // 컴포넌트 정의
  const handleLogout = () => {    // 이벤트 핸들러
    logout();
  };
  return <header>...</header>;
};

// frontend/src/lib/api/client.ts
export const getAccessToken = (): string | undefined => {
  return Cookies.get("access_token");
};
```

---

## 3. 템플릿 리터럴 (Template Literal)

백틱(`)을 사용하여 문자열 안에 변수를 삽입할 수 있습니다.

```javascript
const name = "홍길동";
const age = 25;

// 기존 방식
const message1 = "안녕하세요, " + name + "님. 나이는 " + age + "세입니다.";

// 템플릿 리터럴 (권장)
const message2 = `안녕하세요, ${name}님. 나이는 ${age}세입니다.`;
```

### 프로젝트 예시

```typescript
// frontend/src/lib/api/client.ts
const response = await fetch(`${API_URL}${endpoint}`, options);

// frontend/src/lib/api/posts.ts
export const postsApi = {
  getById: (id: number) => api.get<Post>(`/posts/${id}`),
  delete: (id: number) => api.delete<void>(`/posts/${id}`),
};
```

---

## 4. 구조 분해 할당 (Destructuring)

### 객체 구조 분해

```javascript
const user = {
  name: "홍길동",
  email: "hong@example.com",
  age: 25
};

// 기존 방식
const name = user.name;
const email = user.email;

// 구조 분해 할당
const { name, email, age } = user;

// 다른 이름으로 받기
const { name: userName } = user;  // userName = "홍길동"

// 기본값 설정
const { nickname = "익명" } = user;  // nickname = "익명" (없는 속성)
```

### 배열 구조 분해

```javascript
const numbers = [1, 2, 3];

// 기존 방식
const first = numbers[0];
const second = numbers[1];

// 구조 분해 할당
const [first, second, third] = numbers;

// 일부만 받기
const [a, , c] = numbers;  // a = 1, c = 3
```

### 프로젝트 예시

```typescript
// frontend/src/stores/authStore.ts - 객체 구조 분해
const { user, isAuthenticated, login, logout } = useAuthStore();

// React의 useState - 배열 구조 분해
const [isLoading, setIsLoading] = useState(false);
const [searchQuery, setSearchQuery] = useState("");

// 함수 매개변수에서 구조 분해
const Header = ({ onMenuToggle }: HeaderProps) => {
  // onMenuToggle 직접 사용
};
```

---

## 5. 전개 연산자 (Spread Operator)

### 배열 전개

```javascript
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];

// 배열 합치기
const combined = [...arr1, ...arr2];  // [1, 2, 3, 4, 5, 6]

// 배열 복사
const copy = [...arr1];  // [1, 2, 3]

// 요소 추가
const withNew = [...arr1, 4];  // [1, 2, 3, 4]
```

### 객체 전개

```javascript
const user = { name: "홍길동", age: 25 };

// 객체 복사
const copy = { ...user };

// 속성 추가/덮어쓰기
const updated = { ...user, age: 26, email: "hong@example.com" };
// { name: "홍길동", age: 26, email: "hong@example.com" }
```

### 프로젝트 예시

```typescript
// frontend/src/lib/api/client.ts
const options: RequestInit = {
  ...baseOptions,           // 기본 옵션 전개
  headers: {
    ...baseOptions.headers, // 기존 헤더 유지
    Authorization: `Bearer ${token}`,  // 새 헤더 추가
  },
};

// 상태 업데이트
set({ ...state, isLoading: true });
```

---

## 6. 옵셔널 체이닝 (Optional Chaining)

객체의 속성에 안전하게 접근하는 방법입니다. 중간에 `null` 또는 `undefined`가 있으면 오류 대신 `undefined`를 반환합니다.

```javascript
const user = {
  name: "홍길동",
  address: {
    city: "서울"
  }
};

// 기존 방식 (번거롭고 길다)
const city = user && user.address && user.address.city;

// 옵셔널 체이닝 (간결)
const city = user?.address?.city;  // "서울"

// address가 없는 경우
const user2 = { name: "김철수" };
const city2 = user2?.address?.city;  // undefined (오류 안남!)
```

### 프로젝트 예시

```typescript
// frontend/src/components/layout/Sidebar.tsx
const filteredMenuItems = menuItems.filter(item => {
  if (!item.roles) return true;  // roles가 없으면 모두에게 표시
  return item.roles.includes(user?.role as UserRole);  // user가 없을 수 있음
});

// frontend/src/app/(main)/posts/[id]/page.tsx
{post?.author?.username}  // post나 author가 없어도 오류 안남
```

---

## 7. Nullish Coalescing (??)

`null` 또는 `undefined`일 때만 기본값을 사용합니다.

```javascript
// ?? 연산자
const name = null ?? "익명";     // "익명"
const name2 = undefined ?? "익명"; // "익명"
const name3 = "" ?? "익명";      // "" (빈 문자열은 유효한 값)
const count = 0 ?? 10;          // 0 (0은 유효한 값)

// || 연산자와의 차이
const count2 = 0 || 10;         // 10 (0을 falsy로 취급)
```

### 프로젝트 예시

```typescript
// frontend/src/lib/api/posts.ts
const params = new URLSearchParams({
  page: (page ?? 1).toString(),        // page가 없으면 1
  size: (size ?? 10).toString(),       // size가 없으면 10
});
```

---

## 8. 배열 메서드

### map - 변환

배열의 각 요소를 변환하여 새 배열을 만듭니다.

```javascript
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);  // [2, 4, 6]

const users = [
  { name: "홍길동", age: 25 },
  { name: "김철수", age: 30 }
];
const names = users.map(user => user.name);  // ["홍길동", "김철수"]
```

### filter - 필터링

조건을 만족하는 요소만 추출합니다.

```javascript
const numbers = [1, 2, 3, 4, 5];
const evens = numbers.filter(n => n % 2 === 0);  // [2, 4]

const users = [
  { name: "홍길동", active: true },
  { name: "김철수", active: false }
];
const activeUsers = users.filter(user => user.active);
// [{ name: "홍길동", active: true }]
```

### find - 검색

조건을 만족하는 첫 번째 요소를 반환합니다.

```javascript
const users = [
  { id: 1, name: "홍길동" },
  { id: 2, name: "김철수" }
];
const user = users.find(u => u.id === 1);  // { id: 1, name: "홍길동" }
```

### 프로젝트 예시

```typescript
// frontend/src/components/layout/Sidebar.tsx
// map으로 메뉴 아이템 렌더링
{filteredMenuItems.map((item) => (
  <Link key={item.href} href={item.href}>
    <item.icon className="h-4 w-4" />
    <span>{item.label}</span>
  </Link>
))}

// filter로 권한에 맞는 메뉴만 표시
const filteredMenuItems = menuItems.filter(item => {
  if (!item.roles) return true;
  return item.roles.includes(user?.role as UserRole);
});
```

---

## 9. async/await - 비동기 처리

### Promise와 async/await

```javascript
// Promise 방식
function fetchUser() {
  return fetch("/api/user")
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
}

// async/await 방식 (더 읽기 쉬움)
async function fetchUser() {
  try {
    const response = await fetch("/api/user");
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}
```

### 핵심 개념

- `async`: 함수가 비동기임을 선언
- `await`: Promise가 완료될 때까지 기다림
- `try/catch`: 오류 처리

### 프로젝트 예시

```typescript
// frontend/src/stores/authStore.ts
login: async (username: string, password: string) => {
  set({ isLoading: true, error: null });
  try {
    const tokens = await authApi.login(username, password);
    setTokens(tokens.access_token, tokens.refresh_token);
    const user = await authApi.getCurrentUser();
    set({ user, isAuthenticated: true, isLoading: false });
  } catch (error) {
    set({
      error: error instanceof Error ? error.message : "로그인 실패",
      isLoading: false,
    });
    throw error;
  }
},

// frontend/src/lib/api/client.ts
export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, options);
  if (!response.ok) {
    throw new ApiError(response.status, "API 요청 실패");
  }
  return response.json();
}
```

---

## 10. 모듈 시스템 (import/export)

### Named Export

```javascript
// utils.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export const PI = 3.14159;

// 사용하는 파일
import { add, subtract } from "./utils";
import { add as sum } from "./utils";  // 이름 변경
import * as utils from "./utils";      // 모두 가져오기
```

### Default Export

```javascript
// Button.js
const Button = () => <button>클릭</button>;
export default Button;

// 사용하는 파일
import Button from "./Button";          // 원하는 이름으로 가져오기
import MyButton from "./Button";        // 다른 이름도 가능
```

### 프로젝트 예시

```typescript
// frontend/src/lib/api/index.ts - Named Export
export { authApi } from "./auth";
export { postsApi } from "./posts";
export { usersApi } from "./users";
export { dashboardApi } from "./dashboard";

// frontend/src/components/layout/index.ts
export { MainLayout } from "./MainLayout";
export { Header } from "./Header";
export { Sidebar } from "./Sidebar";

// 사용 예시
import { authApi, postsApi } from "@/lib/api";
import { MainLayout, Header } from "@/components/layout";

// frontend/src/app/(auth)/login/page.tsx - Default Export
export default function LoginPage() { ... }
```

---

## 11. TypeScript 기초

이 프로젝트는 JavaScript의 확장인 TypeScript를 사용합니다.

### 타입 지정

```typescript
// 변수 타입
const name: string = "홍길동";
const age: number = 25;
const isActive: boolean = true;

// 함수 타입
function greet(name: string): string {
  return `안녕하세요, ${name}님!`;
}

// 화살표 함수 타입
const greet = (name: string): string => `안녕하세요, ${name}님!`;
```

### 인터페이스 (Interface)

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  age?: number;        // ? = 선택적 속성
}

const user: User = {
  id: 1,
  name: "홍길동",
  email: "hong@example.com"
};
```

### 타입 별칭 (Type Alias)

```typescript
type UserRole = "admin" | "moderator" | "user";

type LoginRequest = {
  username: string;
  password: string;
};
```

### 제네릭 (Generic)

```typescript
// T는 타입 매개변수
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

const num = first([1, 2, 3]);        // number
const str = first(["a", "b", "c"]);  // string
```

### 프로젝트 예시

```typescript
// frontend/src/types/index.ts
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

// frontend/src/lib/api/client.ts
export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // T 타입의 결과를 반환
}

// 사용 예시
const user = await fetchApi<User>("/users/me");  // User 타입 반환
const posts = await fetchApi<Post[]>("/posts");   // Post[] 타입 반환
```

---

## 요약

| 개념 | 설명 | 프로젝트에서 사용되는 곳 |
|------|------|------------------------|
| const/let | 변수 선언 | 모든 파일 |
| 화살표 함수 | 함수 정의 | 컴포넌트, 이벤트 핸들러 |
| 템플릿 리터럴 | 문자열 조합 | API URL, 메시지 |
| 구조 분해 | 값 추출 | useState, props, store |
| 전개 연산자 | 복사/합치기 | 상태 업데이트, API 옵션 |
| 옵셔널 체이닝 | 안전한 접근 | user?.name 등 |
| ?? 연산자 | 기본값 설정 | 매개변수 기본값 |
| map/filter | 배열 처리 | 목록 렌더링, 필터링 |
| async/await | 비동기 처리 | API 호출 |
| import/export | 모듈 | 파일 간 코드 공유 |
| TypeScript | 타입 안전성 | 모든 파일 |

## 다음 단계

다음 문서 [02-react-fundamentals.md](./02-react-fundamentals.md)에서 React의 핵심 개념을 학습합니다.
