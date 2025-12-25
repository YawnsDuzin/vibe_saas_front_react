# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack boilerplate project with FastAPI backend and Next.js frontend. Features JWT authentication, role-based access control, and multi-database support. Korean language is used for UI messages and documentation.

## Project Structure

```
project/
├── backend/          # FastAPI Backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/         # Next.js Frontend
│   └── src/
└── docs/             # Documentation
```

## Development Commands

### Backend (FastAPI)

```bash
# Change to backend directory
cd backend

# Run development server (localhost only)
uvicorn app.main:app --reload

# Run development server (allow external IP access)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Linting and formatting
black .
isort .
flake8

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Frontend (Next.js)

```bash
# Change to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (port 3000)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## Environment Setup

### Backend
1. Copy `backend/.env.example` to `backend/.env`
2. Configure database type via `DB_TYPE` (postgresql, mysql, mariadb, sqlite)
3. Set `JWT_SECRET_KEY` and `SECRET_KEY` for production
4. Configure file storage via `STORAGE_TYPE` (local, supabase, cloudflare, s3)

### Frontend
1. Create `frontend/.env.local` for environment variables (optional)
2. API URL is automatically detected based on browser's current host
3. Set `NEXT_PUBLIC_API_URL` only if you need to override the automatic detection

## Architecture

### Backend Layer Structure

```
Request → Router → Service → Model/DB
                ↘ Dependency (auth) ↗
```

- **Routers** (`backend/app/routers/`): HTTP endpoints, request/response handling
- **Services** (`backend/app/services/`): Business logic, database operations
- **Dependencies** (`backend/app/dependencies/`): Reusable injection dependencies (auth, db session)
- **Models** (`backend/app/models/`): SQLAlchemy ORM models
- **Schemas** (`backend/app/schemas/`): Pydantic validation schemas

### Frontend Structure

```
frontend/src/
├── app/              # Next.js App Router pages
│   ├── (auth)/       # Auth pages (login, register)
│   └── (main)/       # Main pages (dashboard, posts, users, settings)
├── components/       # Reusable components
│   ├── layout/       # MainLayout, Header, Sidebar
│   └── ui/           # shadcn/ui components
├── lib/              # Utilities and API client
├── stores/           # Zustand state management (authStore, themeStore)
└── types/            # TypeScript type definitions
```

- **Pages** (`app/`): Next.js App Router with route groups
- **Components** (`components/`): Layout and UI components (shadcn/ui based)
- **Stores** (`stores/`): Global state with Zustand (auth, theme)
- **API** (`lib/api/`): API client modules (authApi, postsApi, usersApi, dashboardApi, filesApi, menuApi, categoriesApi)
- **Utils** (`lib/utils.ts`): Tailwind class merge utility (`cn` function)

### Authentication Flow

JWT tokens with access/refresh pattern:

**Backend:**
- `get_current_user`: Validates JWT, returns User
- `get_current_active_user`: Adds active status check
- `get_current_admin_user`: Adds admin role check
- `require_role([roles])`: Factory for custom role requirements

**Frontend:**
- `authStore`: Zustand store for auth state (user, login, logout)
- `middleware.ts`: Route protection (redirects unauthenticated users)
- Tokens stored in cookies via `js-cookie`

### Database

- Multi-DB support configured via `DB_TYPE` environment variable
- Session dependency: `db: Session = Depends(get_db)`
- Dev uses `init_db()` for auto table creation; production should use Alembic migrations

### API Structure

All API routes under `/api/v1/`:
- `/auth` - Login, register, token refresh, current user
- `/users` - User management (admin only for list/delete)
- `/posts` - Posts and comments CRUD
- `/dashboard` - Statistics and recent activity
- `/theme` - User theme settings
- `/menu` - Dynamic menu structure
- `/files` - File upload and management (supports multiple storage backends)

### Frontend Routes

- `/login`, `/register` - Auth pages (redirect if authenticated)
- `/dashboard` - Main dashboard with stats (role-based display)
- `/posts`, `/posts/new`, `/posts/[id]`, `/posts/[id]/edit` - Post management
- `/files` - User file management (grid/list view, upload, edit, delete)
- `/settings` - User settings
- `/admin/users` - User management (admin only)
- `/admin/posts` - Post management for admin (admin only)
- `/admin/menus` - Menu management (admin only)
- `/admin/files` - File management for admin (admin only)

### User Roles

`UserRole` enum: `ADMIN`, `MODERATOR`, `USER`

### Testing

Tests use in-memory SQLite with dependency override. Fixtures in `backend/tests/conftest.py`:
- `db_session` - Fresh DB session per test (tables created/dropped per test)
- `client` - TestClient instance (depends on db_session)
- `test_user` / `admin_user` - Pre-created users with known credentials
- `user_token` / `admin_token` - JWT access tokens
- `auth_headers` / `admin_headers` - Ready-to-use auth headers

Test user credentials: `testuser` / `TestPass123`
Admin user credentials: `adminuser` / `AdminPass123`

### Frontend Tech Stack

- **Framework**: Next.js 16.1.1 with App Router
- **UI**: React 19, Tailwind CSS 4, shadcn/ui (Radix UI)
- **State**: Zustand 5 with persist middleware
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **Notifications**: Sonner (toast)
- **HTTP**: Native fetch with token management in `lib/api/client.ts`

### File Storage

Configurable storage backends via `STORAGE_TYPE` environment variable:
- `local` - Local file system storage (default, files stored in `uploads/` directory)
- `supabase` - Supabase Storage (requires `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET`)
- `cloudflare` - Cloudflare R2 (requires `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`)
- `s3` - AWS S3 (requires `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `AWS_REGION`)

Storage abstraction layer in `backend/app/storage/`:
- `base.py` - Abstract base class (`BaseStorage`)
- `local.py` - Local file system implementation
- `supabase.py` - Supabase storage implementation
- `cloudflare.py` - Cloudflare R2 implementation
- `s3.py` - AWS S3 implementation
- `factory.py` - Factory function for storage instantiation
