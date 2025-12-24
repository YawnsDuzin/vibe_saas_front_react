# 폼과 검증 가이드

## 개요

이 프로젝트는 **React Hook Form**과 **Zod**를 사용하여 폼을 관리하고 검증합니다. 이 조합은 타입 안전성과 우수한 개발자 경험을 제공합니다.

---

## 1. 왜 React Hook Form + Zod인가?

### 기존 방식의 문제점

```tsx
// ❌ useState로 직접 관리 (비효율적)
function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!username) newErrors.username = "필수입니다";
    if (!password) newErrors.password = "필수입니다";
    if (password.length < 8) newErrors.password = "8자 이상";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);
    // ...
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={username} onChange={e => setUsername(e.target.value)} />
      {errors.username && <span>{errors.username}</span>}
      <input value={password} onChange={e => setPassword(e.target.value)} />
      {errors.password && <span>{errors.password}</span>}
      <button disabled={isSubmitting}>제출</button>
    </form>
  );
}
```

### React Hook Form + Zod 방식

```tsx
// ✅ 깔끔하고 타입 안전
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  username: z.string().min(1, "필수입니다"),
  password: z.string().min(8, "8자 이상"),
});

type FormData = z.infer<typeof schema>;  // 타입 자동 추론

function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    // data는 이미 검증됨, 타입 안전
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("username")} />
      {errors.username && <span>{errors.username.message}</span>}
      <input {...register("password")} />
      {errors.password && <span>{errors.password.message}</span>}
      <button disabled={isSubmitting}>제출</button>
    </form>
  );
}
```

---

## 2. Zod 스키마 정의

### 기본 타입

```tsx
import { z } from "zod";

// 문자열
z.string()                     // 기본 문자열
z.string().min(1, "필수")       // 최소 1자
z.string().max(100, "최대 100자")
z.string().email("이메일 형식 오류")
z.string().url("URL 형식 오류")

// 숫자
z.number()
z.number().min(0, "0 이상")
z.number().max(100, "100 이하")
z.number().positive("양수만")
z.number().int("정수만")

// 불린
z.boolean()

// 열거형
z.enum(["admin", "user", "guest"])

// 선택적 필드
z.string().optional()          // string | undefined
z.string().nullable()          // string | null
```

### 객체 스키마

```tsx
const userSchema = z.object({
  email: z.string().email("올바른 이메일을 입력하세요"),
  username: z.string()
    .min(3, "3자 이상 입력하세요")
    .max(50, "50자 이하로 입력하세요"),
  age: z.number().min(0).max(150).optional(),
});

// 타입 추론
type User = z.infer<typeof userSchema>;
// { email: string; username: string; age?: number }
```

### 정규식 검증

```tsx
const usernameSchema = z.string()
  .min(3, "3자 이상")
  .max(50, "50자 이하")
  .regex(
    /^[a-zA-Z][a-zA-Z0-9_]*$/,
    "영문으로 시작, 영문/숫자/밑줄만 허용"
  );

const passwordSchema = z.string()
  .min(8, "8자 이상 입력하세요")
  .regex(/[A-Z]/, "대문자를 포함해야 합니다")
  .regex(/[a-z]/, "소문자를 포함해야 합니다")
  .regex(/[0-9]/, "숫자를 포함해야 합니다");
```

### 조건부 검증 (refine)

```tsx
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: "비밀번호가 일치하지 않습니다",
    path: ["confirmPassword"],  // 에러 표시 위치
  }
);
```

---

## 3. React Hook Form 사용법

### 기본 사용

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const {
    register,       // 입력 필드 등록
    handleSubmit,   // 폼 제출 핸들러
    formState: {
      errors,       // 검증 에러
      isSubmitting, // 제출 중 여부
      isValid,      // 유효성 여부
      isDirty,      // 수정됨 여부
    },
    reset,          // 폼 초기화
    setValue,       // 값 직접 설정
    watch,          // 값 실시간 감시
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: FormData) => {
    console.log(data);  // { email: "...", password: "..." }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email")} />
      <input type="password" {...register("password")} />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "처리 중..." : "제출"}
      </button>
    </form>
  );
}
```

### register 함수

```tsx
// register는 입력 필드에 필요한 props를 반환
const { register } = useForm();

<input {...register("email")} />

// 위 코드는 아래와 동일
<input
  name="email"
  onChange={...}
  onBlur={...}
  ref={...}
/>
```

### 에러 표시

```tsx
const { register, formState: { errors } } = useForm();

<div>
  <label htmlFor="email">이메일</label>
  <input id="email" {...register("email")} />
  {errors.email && (
    <p className="text-sm text-destructive">
      {errors.email.message}
    </p>
  )}
</div>
```

### 값 감시 (watch)

```tsx
const { watch, register } = useForm();

// 특정 필드 감시
const email = watch("email");

// 모든 필드 감시
const allValues = watch();

// 사용 예: 비밀번호 강도 표시
const password = watch("password", "");
const strength = calculateStrength(password);

return (
  <div>
    <input {...register("password")} />
    <div>비밀번호 강도: {strength}</div>
  </div>
);
```

### 값 직접 설정 (setValue)

```tsx
const { setValue, register } = useForm();

// 외부 데이터로 폼 채우기
useEffect(() => {
  if (userData) {
    setValue("email", userData.email);
    setValue("username", userData.username);
  }
}, [userData, setValue]);
```

### 폼 초기화 (reset)

```tsx
const { reset, handleSubmit } = useForm();

const onSubmit = async (data) => {
  await saveData(data);
  reset();  // 폼 초기화
};

// 특정 값으로 초기화
reset({
  email: "new@email.com",
  password: "",
});
```

---

## 4. 프로젝트 폼 예시

### 로그인 폼

```tsx
// src/app/(auth)/login/page.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// 1. 스키마 정의
const loginSchema = z.object({
  username: z.string().min(1, "사용자명 또는 이메일을 입력하세요"),
  password: z.string().min(1, "비밀번호를 입력하세요"),
});

// 2. 타입 추론
type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();

  // 3. useForm 설정
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

  // 4. 제출 핸들러
  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.username, data.password);
      toast.success("로그인 성공!");
      router.push("/dashboard");
    } catch (error) {
      toast.error("로그인 실패");
    }
  };

  // 5. 렌더링
  return (
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
  );
}
```

### 회원가입 폼 (복잡한 검증)

```tsx
// src/app/(auth)/register/page.tsx
"use client";

const registerSchema = z.object({
  email: z.string()
    .min(1, "이메일을 입력하세요")
    .email("올바른 이메일 형식이 아닙니다"),

  username: z.string()
    .min(3, "3자 이상 입력하세요")
    .max(50, "50자 이하로 입력하세요")
    .regex(
      /^[a-zA-Z][a-zA-Z0-9_]*$/,
      "영문으로 시작하고, 영문/숫자/밑줄만 사용 가능합니다"
    ),

  password: z.string()
    .min(8, "8자 이상 입력하세요")
    .regex(/[A-Z]/, "대문자를 포함해야 합니다")
    .regex(/[a-z]/, "소문자를 포함해야 합니다")
    .regex(/[0-9]/, "숫자를 포함해야 합니다"),

  confirmPassword: z.string()
    .min(1, "비밀번호 확인을 입력하세요"),

  full_name: z.string().optional(),
})
// 비밀번호 일치 검증
.refine(
  (data) => data.password === data.confirmPassword,
  {
    message: "비밀번호가 일치하지 않습니다",
    path: ["confirmPassword"],
  }
);

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      username: "",
      password: "",
      confirmPassword: "",
      full_name: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      // confirmPassword는 API에 보내지 않음
      const { confirmPassword, ...registerData } = data;
      await authApi.register(registerData);
      toast.success("회원가입 완료!");
      setTimeout(() => router.push("/login"), 2000);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "회원가입 실패");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* 각 필드 렌더링 */}
    </form>
  );
}
```

### 게시글 작성 폼

```tsx
// src/app/(main)/posts/new/page.tsx
"use client";

const postSchema = z.object({
  title: z.string()
    .min(1, "제목을 입력하세요")
    .max(200, "200자 이하로 입력하세요"),
  content: z.string()
    .min(1, "내용을 입력하세요"),
  is_published: z.boolean().default(true),
});

type PostFormData = z.infer<typeof postSchema>;

export default function NewPostPage() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
    defaultValues: {
      title: "",
      content: "",
      is_published: true,
    },
  });

  const onSubmit = async (data: PostFormData) => {
    try {
      const post = await postsApi.create(data);
      toast.success("게시글이 작성되었습니다");
      router.push(`/posts/${post.id}`);
    } catch (error) {
      toast.error("게시글 작성 실패");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">제목</Label>
        <Input
          id="title"
          {...register("title")}
          placeholder="게시글 제목"
        />
        {errors.title && (
          <p className="text-sm text-destructive">{errors.title.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="content">내용</Label>
        <Textarea
          id="content"
          {...register("content")}
          placeholder="게시글 내용을 입력하세요"
          rows={10}
        />
        {errors.content && (
          <p className="text-sm text-destructive">{errors.content.message}</p>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_published"
          {...register("is_published")}
          className="h-4 w-4"
        />
        <Label htmlFor="is_published">공개</Label>
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "작성 중..." : "게시글 작성"}
      </Button>
    </form>
  );
}
```

---

## 5. 고급 패턴

### 동적 필드

```tsx
// 동적으로 필드 추가/제거
import { useFieldArray } from "react-hook-form";

const schema = z.object({
  tags: z.array(z.string().min(1)).min(1, "태그를 1개 이상 입력하세요"),
});

function TagsForm() {
  const { control, register, handleSubmit } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { tags: [""] },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "tags",
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {fields.map((field, index) => (
        <div key={field.id}>
          <input {...register(`tags.${index}`)} />
          <button type="button" onClick={() => remove(index)}>삭제</button>
        </div>
      ))}
      <button type="button" onClick={() => append("")}>태그 추가</button>
      <button type="submit">저장</button>
    </form>
  );
}
```

### 폼 모드

```tsx
const { register, handleSubmit, formState } = useForm({
  mode: "onChange",      // 입력할 때마다 검증
  // mode: "onBlur",     // 포커스 벗어날 때 검증
  // mode: "onSubmit",   // 제출할 때만 검증 (기본값)
  // mode: "onTouched",  // 처음 포커스 벗어난 후 입력마다 검증
  // mode: "all",        // 모든 이벤트에서 검증
});
```

### 에러 메시지 컴포넌트화

```tsx
// components/FormError.tsx
interface FormErrorProps {
  error?: { message?: string };
}

export const FormError = ({ error }: FormErrorProps) => {
  if (!error?.message) return null;
  return (
    <p className="text-sm text-destructive mt-1">
      {error.message}
    </p>
  );
};

// 사용
<Input {...register("email")} />
<FormError error={errors.email} />
```

---

## 6. 검증 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                      폼 검증 흐름                            │
└─────────────────────────────────────────────────────────────┘

1. 사용자 입력
      │
      ▼
2. register가 onChange 감지
      │
      ▼
3. mode에 따라 검증 실행
      │
      ▼
4. zodResolver가 Zod 스키마로 검증
      │
   ┌──┴──┐
   ▼     ▼
 성공   실패
   │     │
   │     ▼
   │   errors 상태 업데이트
   │     │
   │     ▼
   │   에러 메시지 표시
   │
   ▼
5. handleSubmit 호출 (폼 제출)
      │
      ▼
6. 모든 필드 검증
      │
   ┌──┴──┐
   ▼     ▼
 성공   실패
   │     │
   │     ▼
   │   onSubmit 호출 안됨
   │   에러 표시
   │
   ▼
7. onSubmit 호출 (검증된 데이터 전달)
      │
      ▼
8. API 요청
```

---

## 요약

| 개념 | 설명 |
|------|------|
| Zod | 스키마 기반 검증 라이브러리 |
| zodResolver | React Hook Form + Zod 연결 |
| register | 입력 필드 등록 함수 |
| handleSubmit | 폼 제출 핸들러 (검증 포함) |
| errors | 검증 에러 객체 |
| isSubmitting | 제출 중 상태 |
| watch | 값 실시간 감시 |
| setValue | 값 직접 설정 |
| reset | 폼 초기화 |

## 문서 완료

이것으로 Frontend 문서 시리즈가 완료되었습니다. 처음부터 순서대로 학습하시면 Next.js와 React를 이해하고 이 프로젝트의 코드를 파악하는 데 도움이 될 것입니다.

### 문서 목록

1. [00-getting-started.md](./00-getting-started.md) - 시작하기
2. [01-javascript-basics.md](./01-javascript-basics.md) - JavaScript 기초
3. [02-react-fundamentals.md](./02-react-fundamentals.md) - React 기초
4. [03-react-hooks.md](./03-react-hooks.md) - React Hooks
5. [04-nextjs-fundamentals.md](./04-nextjs-fundamentals.md) - Next.js 기초
6. [05-nextjs-app-router.md](./05-nextjs-app-router.md) - App Router
7. [06-project-structure.md](./06-project-structure.md) - 프로젝트 구조
8. [07-components-detail.md](./07-components-detail.md) - 컴포넌트 상세
9. [08-state-management.md](./08-state-management.md) - 상태 관리
10. [09-api-integration.md](./09-api-integration.md) - API 연동
11. [10-authentication.md](./10-authentication.md) - 인증 시스템
12. [11-styling.md](./11-styling.md) - 스타일링
13. [12-forms-validation.md](./12-forms-validation.md) - 폼과 검증 (현재)
