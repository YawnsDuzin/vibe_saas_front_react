# FastAPI Boilerplate

FastAPI 백엔드와 Next.js 프론트엔드를 사용한 풀스택 보일러플레이트 프로젝트입니다.

## 주요 기능

### 백엔드 (FastAPI)
- 🔐 **인증 시스템**: JWT 기반 회원가입/로그인 (Access/Refresh Token)
- 👤 **사용자 관리**: 역할 기반 권한 관리 (Admin, Moderator, User)
- 📝 **게시판**: 게시글 CRUD, 댓글, 카테고리
- 📊 **대시보드**: 통계 및 최근 활동
- 🎨 **테마 설정**: 사용자별 테마 커스터마이징
- 📋 **동적 메뉴**: 역할 기반 메뉴 구조
- 🗄️ **다중 DB 지원**: PostgreSQL, MySQL, MariaDB, SQLite

### 프론트엔드 (Next.js)
- ⚛️ **React 19 + Next.js 16**: 최신 App Router 사용
- 🎨 **Tailwind CSS + shadcn/ui**: 현대적인 UI 컴포넌트
- 📦 **Zustand**: 경량 상태 관리
- 📝 **React Hook Form + Zod**: 폼 유효성 검증
- 🌓 **다크/라이트 테마**: next-themes 기반 테마 지원

## 빠른 시작

### 백엔드

```bash
# 저장소 클론
git clone <repository-url>
cd vibe_saas_front_react

# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 백엔드 서버 실행
uvicorn app.main:app --reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

### 프론트엔드

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

서버 실행 후:
- **백엔드**: http://localhost:8000
- **프론트엔드**: http://localhost:3000

## API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 자세한 문서

- [설치 가이드](docs/01_installation.md)
- [환경 설정](docs/02_configuration.md)
- [사용 가이드](docs/03_usage.md)
- [API 레퍼런스](docs/04_api_reference.md)
- [수정 및 확장 가이드](docs/05_customization.md)

### 백엔드 튜토리얼

- [시작하기](docs/backend/00-getting-started.md)
- [Python 기초](docs/backend/01-python-basics.md)
- [FastAPI 기본](docs/backend/02-fastapi-fundamentals.md)
- [Pydantic 스키마](docs/backend/03-pydantic-schemas.md)
- [SQLAlchemy 모델](docs/backend/04-sqlalchemy-models.md)
- [데이터베이스](docs/backend/05-database.md)
- [프로젝트 구조](docs/backend/06-project-structure.md)
- [라우터](docs/backend/07-routers.md)
- [서비스](docs/backend/08-services.md)
- [의존성](docs/backend/09-dependencies.md)
- [인증](docs/backend/10-authentication.md)
- [보안](docs/backend/11-security.md)
- [에러 처리](docs/backend/12-error-handling.md)

### 프론트엔드 튜토리얼

- [시작하기](docs/frontend/00-getting-started.md)
- [JavaScript 기초](docs/frontend/01-javascript-basics.md)
- [React 기본](docs/frontend/02-react-fundamentals.md)
- [React Hooks](docs/frontend/03-react-hooks.md)
- [Next.js 기본](docs/frontend/04-nextjs-fundamentals.md)
- [Next.js App Router](docs/frontend/05-nextjs-app-router.md)
- [프로젝트 구조](docs/frontend/06-project-structure.md)
- [컴포넌트 상세](docs/frontend/07-components-detail.md)
- [상태 관리](docs/frontend/08-state-management.md)
- [API 통합](docs/frontend/09-api-integration.md)
- [인증](docs/frontend/10-authentication.md)
- [스타일링](docs/frontend/11-styling.md)
- [폼 및 유효성 검사](docs/frontend/12-forms-validation.md)

## 프로젝트 구조

```
vibe_saas_front_react/
├── backend/                  # FastAPI 백엔드
│   ├── app/                  # 애플리케이션 코드
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI 애플리케이션
│   │   ├── config.py         # 설정 관리
│   │   ├── database.py       # DB 연결
│   │   ├── models/           # SQLAlchemy 모델
│   │   ├── schemas/          # Pydantic 스키마
│   │   ├── routers/          # API 라우터
│   │   ├── services/         # 비즈니스 로직
│   │   ├── dependencies/     # 종속성 (인증 등)
│   │   └── utils/            # 유틸리티
│   ├── tests/                # 백엔드 테스트
│   ├── alembic/              # DB 마이그레이션
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/              # App Router 페이지
│   │   │   ├── (auth)/       # 인증 페이지 (로그인, 회원가입)
│   │   │   └── (main)/       # 메인 페이지 (대시보드, 게시글 등)
│   │   ├── components/       # 재사용 컴포넌트
│   │   │   ├── layout/       # 레이아웃 (Header, Sidebar, MainLayout)
│   │   │   └── ui/           # UI 컴포넌트 (shadcn/ui)
│   │   ├── lib/              # 유틸리티 및 API 클라이언트
│   │   ├── stores/           # Zustand 상태 관리
│   │   └── types/            # TypeScript 타입 정의
│   ├── package.json
│   └── tsconfig.json
├── docs/                     # 문서
│   ├── backend/              # 백엔드 튜토리얼
│   └── frontend/             # 프론트엔드 튜토리얼
└── README.md
```

## 라이선스

MIT License
