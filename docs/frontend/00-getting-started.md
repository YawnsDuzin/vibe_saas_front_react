# Frontend 문서 시작하기

## 문서 개요

이 문서 시리즈는 FastAPI Tutorial 프로젝트의 Frontend 부분을 상세히 설명합니다. Next.js와 React를 전혀 모르는 분도 이해할 수 있도록 기초부터 차근차근 설명합니다.

## 문서 구성

| 번호 | 문서명 | 설명 |
|------|--------|------|
| 00 | getting-started.md | 현재 문서 - 전체 개요 및 학습 가이드 |
| 01 | javascript-basics.md | React 이해를 위한 JavaScript 기초 |
| 02 | react-fundamentals.md | React 핵심 개념 |
| 03 | react-hooks.md | React Hooks 상세 설명 |
| 04 | nextjs-fundamentals.md | Next.js 기초 개념 |
| 05 | nextjs-app-router.md | Next.js App Router 상세 |
| 06 | project-structure.md | 프로젝트 구조 분석 |
| 07 | components-detail.md | 컴포넌트 상세 분석 |
| 08 | state-management.md | 상태 관리 (Zustand) |
| 09 | api-integration.md | API 연동 |
| 10 | authentication.md | 인증 시스템 |
| 11 | styling.md | 스타일링 (Tailwind CSS) |
| 12 | forms-validation.md | 폼과 검증 |

## 학습 순서

### 1단계: 기초 개념 (01-05)
JavaScript, React, Next.js의 기본 개념을 학습합니다. 프로그래밍 경험이 있다면 01번은 빠르게 읽고 넘어가도 됩니다.

### 2단계: 프로젝트 이해 (06-07)
실제 프로젝트의 구조와 컴포넌트를 분석합니다. 코드를 직접 보면서 앞서 배운 개념이 어떻게 적용되는지 확인합니다.

### 3단계: 기능 구현 (08-12)
상태 관리, API 연동, 인증, 스타일링 등 실제 기능 구현 방법을 학습합니다.

## 프로젝트 기술 스택

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend 기술 스택                        │
├─────────────────────────────────────────────────────────────┤
│  프레임워크    │ Next.js 16.1.1 (App Router)                 │
│  UI 라이브러리 │ React 19.2.3                               │
│  언어         │ TypeScript 5                                │
│  상태 관리    │ Zustand                                     │
│  폼 관리      │ React Hook Form + Zod                       │
│  스타일링     │ Tailwind CSS v4 + shadcn/ui                 │
│  아이콘       │ Lucide React                                │
│  테마         │ next-themes                                 │
│  토스트 알림  │ Sonner                                      │
│  쿠키 관리    │ js-cookie                                   │
└─────────────────────────────────────────────────────────────┘
```

## 개발 환경 설정

### 필수 소프트웨어
- Node.js 18.x 이상
- npm 또는 yarn 패키지 매니저
- 코드 에디터 (VS Code 권장)

### 프로젝트 실행

```bash
# 1. frontend 폴더로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. 개발 서버 실행
npm run dev
```

개발 서버가 실행되면 `http://localhost:3000`에서 애플리케이션을 확인할 수 있습니다.

### 환경 변수 설정

`frontend/.env.local` 파일을 생성하고 다음 내용을 추가합니다:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 프로젝트 기능 개요

이 프로젝트는 **관리자 대시보드** 형태의 웹 애플리케이션입니다.

### 주요 기능

```
┌─────────────────────────────────────────────────────────────┐
│                      주요 기능                               │
├─────────────────────────────────────────────────────────────┤
│  ✅ 사용자 인증 (로그인/회원가입/로그아웃)                    │
│  ✅ JWT 토큰 기반 인증 (Access + Refresh Token)             │
│  ✅ 대시보드 (통계 및 최근 활동)                             │
│  ✅ 게시글 CRUD (작성/조회/수정/삭제)                        │
│  ✅ 댓글 시스템 (작성/삭제)                                  │
│  ✅ 사용자 관리 (관리자 전용)                                │
│  ✅ 프로필 설정 (정보 수정/비밀번호 변경)                     │
│  ✅ 테마 설정 (라이트/다크/시스템)                           │
│  ✅ 반응형 디자인 (모바일/태블릿/데스크톱)                    │
│  ✅ 역할 기반 접근 제어 (Admin/Moderator/User)              │
└─────────────────────────────────────────────────────────────┘
```

### 페이지 구성

| 경로 | 페이지 | 접근 권한 |
|------|--------|----------|
| `/login` | 로그인 | 비로그인 사용자 |
| `/register` | 회원가입 | 비로그인 사용자 |
| `/dashboard` | 대시보드 | 로그인 필요 |
| `/posts` | 게시글 목록 | 로그인 필요 |
| `/posts/new` | 게시글 작성 | 로그인 필요 |
| `/posts/[id]` | 게시글 상세 | 로그인 필요 |
| `/users` | 사용자 관리 | Admin/Moderator |
| `/settings` | 설정 | 로그인 필요 |

## 폴더 구조 미리보기

```
frontend/
├── public/                    # 정적 파일
├── src/
│   ├── app/                   # Next.js App Router (페이지)
│   │   ├── (auth)/           # 인증 페이지 그룹
│   │   │   ├── login/        # 로그인 페이지
│   │   │   └── register/     # 회원가입 페이지
│   │   ├── (main)/           # 메인 페이지 그룹
│   │   │   ├── dashboard/    # 대시보드
│   │   │   ├── posts/        # 게시글
│   │   │   ├── users/        # 사용자 관리
│   │   │   └── settings/     # 설정
│   │   ├── layout.tsx        # 루트 레이아웃
│   │   └── globals.css       # 전역 스타일
│   ├── components/            # 재사용 컴포넌트
│   │   ├── layout/           # 레이아웃 컴포넌트
│   │   └── ui/               # UI 컴포넌트 (shadcn)
│   ├── lib/                   # 유틸리티 및 API
│   │   ├── api/              # API 클라이언트
│   │   └── utils.ts          # 유틸리티 함수
│   ├── stores/               # 상태 관리 (Zustand)
│   └── types/                # TypeScript 타입
├── middleware.ts              # Next.js 미들웨어 (인증)
├── package.json              # 프로젝트 설정
└── tsconfig.json             # TypeScript 설정
```

## 다음 단계

다음 문서 [01-javascript-basics.md](./01-javascript-basics.md)에서 React를 이해하기 위한 JavaScript 기초 개념을 학습합니다.

## 용어 사전

| 용어 | 설명 |
|------|------|
| **컴포넌트 (Component)** | 재사용 가능한 UI 조각. 버튼, 카드, 폼 등 |
| **상태 (State)** | 시간에 따라 변하는 데이터. 사용자 정보, 입력값 등 |
| **프롭스 (Props)** | 부모 컴포넌트가 자식에게 전달하는 데이터 |
| **훅 (Hook)** | React의 상태와 기능을 사용할 수 있게 해주는 함수 |
| **라우팅 (Routing)** | URL에 따라 다른 페이지를 보여주는 것 |
| **렌더링 (Rendering)** | 데이터를 화면에 표시하는 것 |
| **API** | 서버와 통신하기 위한 인터페이스 |
| **JWT** | JSON Web Token, 인증에 사용되는 토큰 |
