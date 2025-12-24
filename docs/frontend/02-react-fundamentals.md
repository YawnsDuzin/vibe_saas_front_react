# React 기초 개념

## React란?

React는 Facebook(현 Meta)에서 만든 **UI(사용자 인터페이스) 라이브러리**입니다. 웹 페이지의 화면을 구성하는 컴포넌트를 만들고 관리하는 데 특화되어 있습니다.

### React의 특징

```
┌─────────────────────────────────────────────────────────────┐
│                    React의 핵심 특징                         │
├─────────────────────────────────────────────────────────────┤
│  1. 컴포넌트 기반: UI를 재사용 가능한 조각으로 나눔          │
│  2. 선언적 UI: "어떻게" 보다 "무엇을" 보여줄지 선언          │
│  3. 단방향 데이터 흐름: 부모 → 자식으로 데이터 전달          │
│  4. Virtual DOM: 효율적인 화면 업데이트                      │
│  5. JSX: JavaScript 안에서 HTML처럼 작성                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. JSX (JavaScript XML)

JSX는 JavaScript 안에서 HTML과 비슷한 문법으로 UI를 작성할 수 있게 해줍니다.

### 기본 문법

```jsx
// HTML처럼 보이지만 JavaScript입니다
const element = <h1>안녕하세요!</h1>;

// 여러 줄일 때는 괄호로 감싸기
const element = (
  <div>
    <h1>제목</h1>
    <p>내용</p>
  </div>
);
```

### JSX vs HTML 차이점

```jsx
// 1. class 대신 className
<div className="container">  // HTML: class="container"

// 2. for 대신 htmlFor
<label htmlFor="email">     // HTML: for="email"

// 3. 스타일은 객체로
<div style={{ color: "red", fontSize: "16px" }}>
// HTML: style="color: red; font-size: 16px"

// 4. 모든 태그는 닫아야 함
<input type="text" />       // HTML: <input type="text">
<img src="..." />           // HTML: <img src="...">

// 5. 이벤트는 camelCase
<button onClick={handleClick}>  // HTML: onclick="handleClick()"
```

### JavaScript 표현식 삽입 - 중괄호 {}

```jsx
const name = "홍길동";
const isLoggedIn = true;

// 변수 삽입
<h1>안녕하세요, {name}님!</h1>

// 계산식
<p>1 + 1 = {1 + 1}</p>

// 조건부 렌더링 (삼항 연산자)
<p>{isLoggedIn ? "환영합니다!" : "로그인해주세요"}</p>

// 조건부 렌더링 (&& 연산자)
{isLoggedIn && <button>로그아웃</button>}
```

### 프로젝트 예시

```tsx
// frontend/src/app/(auth)/login/page.tsx
<Card className="w-full max-w-md">
  <CardHeader className="space-y-1 text-center">
    <CardTitle className="text-2xl font-bold">로그인</CardTitle>
    <CardDescription>
      계정에 로그인하세요
    </CardDescription>
  </CardHeader>
  <CardContent>
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* JavaScript 변수/함수를 {}로 삽입 */}
      <Input {...register("username")} />
      {errors.username && (
        <p className="text-destructive">{errors.username.message}</p>
      )}
    </form>
  </CardContent>
</Card>
```

---

## 2. 컴포넌트 (Component)

컴포넌트는 **재사용 가능한 UI 조각**입니다. 버튼, 카드, 헤더, 폼 등을 컴포넌트로 만들어 여러 곳에서 사용할 수 있습니다.

### 함수형 컴포넌트

```jsx
// 가장 기본적인 컴포넌트
function Greeting() {
  return <h1>안녕하세요!</h1>;
}

// 화살표 함수로도 가능 (권장)
const Greeting = () => {
  return <h1>안녕하세요!</h1>;
};

// 한 줄이면 return 생략
const Greeting = () => <h1>안녕하세요!</h1>;
```

### 컴포넌트 사용

```jsx
// 컴포넌트는 HTML 태그처럼 사용
function App() {
  return (
    <div>
      <Greeting />        {/* 첫 글자 대문자! */}
      <Greeting />        {/* 여러 번 재사용 가능 */}
      <button>클릭</button>  {/* 소문자는 HTML 태그 */}
    </div>
  );
}
```

### 컴포넌트 파일 구조

```
// 하나의 파일에 하나의 컴포넌트 (권장)
// src/components/Greeting.tsx

export const Greeting = () => {
  return <h1>안녕하세요!</h1>;
};

// 또는 default export
export default function Greeting() {
  return <h1>안녕하세요!</h1>;
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/Header.tsx
export const Header = ({ onMenuToggle }: HeaderProps) => {
  // 헤더 컴포넌트
  return (
    <header className="sticky top-0 z-40 ...">
      <div className="flex h-14 items-center ...">
        {/* 모바일 메뉴 버튼 */}
        <Button variant="ghost" size="icon" onClick={onMenuToggle}>
          <Menu className="h-5 w-5" />
        </Button>
        {/* ... */}
      </div>
    </header>
  );
};

// frontend/src/components/layout/MainLayout.tsx
// Header 컴포넌트 사용
export const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="flex min-h-screen">
      <Sidebar isOpen={sidebarOpen} />
      <div className="flex-1">
        <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
        <main>{children}</main>
      </div>
    </div>
  );
};
```

---

## 3. Props (속성)

Props는 **부모 컴포넌트가 자식 컴포넌트에 전달하는 데이터**입니다.

### Props 전달과 받기

```jsx
// 부모 컴포넌트
function App() {
  return (
    <div>
      <Greeting name="홍길동" age={25} />  {/* props 전달 */}
      <Greeting name="김철수" age={30} />
    </div>
  );
}

// 자식 컴포넌트 - props 받기 (방법 1)
function Greeting(props) {
  return <h1>안녕하세요, {props.name}님! ({props.age}세)</h1>;
}

// 자식 컴포넌트 - 구조 분해 (방법 2, 권장)
function Greeting({ name, age }) {
  return <h1>안녕하세요, {name}님! ({age}세)</h1>;
}
```

### TypeScript에서 Props 타입 정의

```tsx
// 타입 정의
interface GreetingProps {
  name: string;
  age: number;
  email?: string;  // 선택적 prop
}

// 컴포넌트에 타입 적용
const Greeting = ({ name, age, email }: GreetingProps) => {
  return (
    <div>
      <h1>안녕하세요, {name}님!</h1>
      <p>나이: {age}세</p>
      {email && <p>이메일: {email}</p>}
    </div>
  );
};
```

### 다양한 Props 타입

```tsx
interface ComponentProps {
  // 기본 타입
  title: string;
  count: number;
  isActive: boolean;

  // 배열
  items: string[];

  // 객체
  user: { name: string; age: number };

  // 함수 (이벤트 핸들러)
  onClick: () => void;
  onSubmit: (data: FormData) => void;

  // 자식 컴포넌트 (children)
  children: React.ReactNode;
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/Sidebar.tsx
interface SidebarProps {
  isOpen: boolean;      // 열림/닫힘 상태
  onClose?: () => void; // 닫기 핸들러 (선택적)
}

export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  // props 사용
  return (
    <aside className={isOpen ? "flex" : "hidden"}>
      {/* ... */}
    </aside>
  );
};

// 사용하는 곳 (MainLayout)
<Sidebar
  isOpen={sidebarOpen}
  onClose={() => setSidebarOpen(false)}
/>
```

---

## 4. children Props

`children`은 **컴포넌트 태그 사이의 내용**을 전달하는 특별한 prop입니다.

```jsx
// Wrapper 컴포넌트 정의
const Card = ({ children }) => {
  return <div className="border rounded p-4">{children}</div>;
};

// 사용
function App() {
  return (
    <Card>
      <h2>카드 제목</h2>      {/* 이 내용이 children으로 전달 */}
      <p>카드 내용입니다</p>
    </Card>
  );
}
```

### 프로젝트 예시

```tsx
// frontend/src/components/layout/MainLayout.tsx
interface MainLayoutProps {
  children: React.ReactNode;  // children 타입
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="flex min-h-screen">
      <Sidebar isOpen={sidebarOpen} />
      <div className="flex-1 flex flex-col">
        <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 p-6">
          {children}  {/* 각 페이지 내용이 여기에 들어감 */}
        </main>
      </div>
    </div>
  );
};

// frontend/src/app/(main)/layout.tsx - 사용
export default function MainPagesLayout({ children }: { children: React.ReactNode }) {
  return <MainLayout>{children}</MainLayout>;
}
```

---

## 5. 조건부 렌더링

특정 조건에 따라 다른 UI를 보여주는 방법입니다.

### 삼항 연산자

```jsx
// condition ? true일 때 : false일 때
const Greeting = ({ isLoggedIn, name }) => {
  return (
    <div>
      {isLoggedIn ? (
        <h1>환영합니다, {name}님!</h1>
      ) : (
        <h1>로그인해주세요</h1>
      )}
    </div>
  );
};
```

### && 연산자

```jsx
// 조건이 true일 때만 렌더링
const Greeting = ({ isLoggedIn, name }) => {
  return (
    <div>
      {isLoggedIn && <h1>환영합니다, {name}님!</h1>}
      {!isLoggedIn && <button>로그인</button>}
    </div>
  );
};
```

### 조기 반환 (Early Return)

```jsx
const UserProfile = ({ user, isLoading }) => {
  // 로딩 중이면 로딩 UI 반환
  if (isLoading) {
    return <div>로딩 중...</div>;
  }

  // 사용자가 없으면 안내 메시지
  if (!user) {
    return <div>사용자를 찾을 수 없습니다.</div>;
  }

  // 정상 상태
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
};
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/dashboard/page.tsx
export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  // 로딩 중 표시
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin h-8 w-8 border-4 ..."></div>
      </div>
    );
  }

  // 정상 렌더링
  return (
    <div className="space-y-6">
      <h1>대시보드</h1>
      {stats && (
        <div className="grid grid-cols-4">
          {/* 통계 카드 */}
        </div>
      )}
    </div>
  );
}

// frontend/src/components/layout/Sidebar.tsx
// 권한에 따른 메뉴 표시
const filteredMenuItems = menuItems.filter(item => {
  if (!item.roles) return true;  // 권한 제한 없으면 표시
  return item.roles.includes(user?.role as UserRole);  // 권한 확인
});
```

---

## 6. 리스트 렌더링 (map)

배열을 UI 목록으로 변환할 때 `map` 메서드를 사용합니다.

### 기본 사용법

```jsx
const fruits = ["사과", "바나나", "오렌지"];

const FruitList = () => {
  return (
    <ul>
      {fruits.map((fruit, index) => (
        <li key={index}>{fruit}</li>  // key 필수!
      ))}
    </ul>
  );
};
```

### key의 중요성

`key`는 React가 리스트 아이템을 구분하는 데 사용합니다. **고유한 값**이어야 합니다.

```jsx
const users = [
  { id: 1, name: "홍길동" },
  { id: 2, name: "김철수" },
];

const UserList = () => {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>  // id를 key로 사용 (권장)
      ))}
    </ul>
  );
};
```

### 프로젝트 예시

```tsx
// frontend/src/app/(main)/posts/page.tsx
// 게시글 목록 렌더링
{posts.map((post) => (
  <Card key={post.id}>  {/* 고유 id를 key로 사용 */}
    <CardHeader>
      <CardTitle>{post.title}</CardTitle>
    </CardHeader>
    <CardContent>
      <p>{post.content.substring(0, 100)}...</p>
    </CardContent>
    <CardFooter>
      <span>{post.author.username}</span>
      <span>{new Date(post.created_at).toLocaleDateString()}</span>
    </CardFooter>
  </Card>
))}

// frontend/src/components/layout/Sidebar.tsx
// 메뉴 아이템 렌더링
{filteredMenuItems.map((item) => (
  <Link
    key={item.href}  {/* href를 key로 사용 */}
    href={item.href}
    className={cn(
      "flex items-center gap-3 px-3 py-2 rounded-md",
      pathname === item.href && "bg-accent"  // 현재 경로면 활성화
    )}
  >
    <item.icon className="h-4 w-4" />
    <span>{item.label}</span>
  </Link>
))}
```

---

## 7. 이벤트 처리

사용자 동작(클릭, 입력 등)에 반응하는 방법입니다.

### 기본 이벤트 처리

```jsx
const Button = () => {
  // 이벤트 핸들러 함수
  const handleClick = () => {
    alert("클릭됨!");
  };

  return <button onClick={handleClick}>클릭하세요</button>;
};

// 인라인으로도 가능
<button onClick={() => alert("클릭됨!")}>클릭</button>
```

### 이벤트 객체

```jsx
const Input = () => {
  const handleChange = (event) => {
    console.log(event.target.value);  // 입력된 값
  };

  return <input type="text" onChange={handleChange} />;
};
```

### TypeScript에서 이벤트 타입

```tsx
const Form = () => {
  // 폼 제출 이벤트
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();  // 기본 동작 방지
    // 폼 처리 로직
  };

  // 입력 변경 이벤트
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  // 클릭 이벤트
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log("클릭됨");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
      <button onClick={handleClick}>제출</button>
    </form>
  );
};
```

### 주요 이벤트 종류

| 이벤트 | 설명 |
|--------|------|
| `onClick` | 클릭 |
| `onChange` | 값 변경 |
| `onSubmit` | 폼 제출 |
| `onFocus` / `onBlur` | 포커스 획득/상실 |
| `onKeyDown` / `onKeyUp` | 키보드 입력 |
| `onMouseEnter` / `onMouseLeave` | 마우스 오버/아웃 |

### 프로젝트 예시

```tsx
// frontend/src/app/(auth)/login/page.tsx
const onSubmit = async (data: LoginFormData) => {
  try {
    await login(data.username, data.password);
    toast.success("로그인 성공");
    router.push("/dashboard");
  } catch (error) {
    toast.error("로그인 실패");
  }
};

<form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
  <Input {...register("username")} />
  <Input type="password" {...register("password")} />
  <Button type="submit">로그인</Button>
</form>

// frontend/src/components/layout/Header.tsx
<Button variant="ghost" size="icon" onClick={onMenuToggle}>
  <Menu className="h-5 w-5" />
</Button>
```

---

## 8. 컴포넌트 구조도

프로젝트의 컴포넌트 관계를 시각화하면:

```
App
├── (auth) Layout
│   ├── LoginPage
│   └── RegisterPage
│
└── (main) Layout
    └── MainLayout
        ├── Sidebar
        │   └── MenuItem (반복)
        ├── Header
        │   ├── MenuToggle
        │   ├── ThemeToggle
        │   └── UserMenu
        └── {children}  ← 각 페이지가 여기에 렌더링
            ├── DashboardPage
            │   ├── StatCard (반복)
            │   └── RecentList
            ├── PostsPage
            │   └── PostCard (반복)
            ├── PostDetailPage
            │   └── CommentList
            ├── UsersPage
            │   └── UserTable
            └── SettingsPage
                └── Tabs
```

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| JSX | JS 안에서 HTML처럼 작성 | `<div className="box">` |
| 컴포넌트 | 재사용 가능한 UI 조각 | `const Button = () => <button>` |
| Props | 부모→자식 데이터 전달 | `<Card title="제목">` |
| children | 태그 사이 내용 | `<Card>{children}</Card>` |
| 조건부 렌더링 | 조건에 따른 UI | `{isLoading ? <Loader /> : <Content />}` |
| 리스트 렌더링 | 배열을 UI로 변환 | `{items.map(item => <Item key={item.id} />)}` |
| 이벤트 | 사용자 동작 처리 | `onClick={handleClick}` |

## 다음 단계

다음 문서 [03-react-hooks.md](./03-react-hooks.md)에서 React Hooks를 상세히 학습합니다.
