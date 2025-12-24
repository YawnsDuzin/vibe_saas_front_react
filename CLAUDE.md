# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI boilerplate project with JWT authentication, role-based access control, and multi-database support. Korean language is used for UI messages and documentation.

## Development Commands

```bash
# Run development server
uvicorn app.main:app --reload

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

## Environment Setup

1. Copy `.env.example` to `.env`
2. Configure database type via `DB_TYPE` (postgresql, mysql, mariadb, sqlite)
3. Set `JWT_SECRET_KEY` and `SECRET_KEY` for production

## Architecture

### Layer Structure

```
Request → Router → Service → Model/DB
                ↘ Dependency (auth) ↗
```

- **Routers** (`app/routers/`): HTTP endpoints, request/response handling
- **Services** (`app/services/`): Business logic, database operations
- **Dependencies** (`app/dependencies/`): Reusable injection dependencies (auth, db session)
- **Models** (`app/models/`): SQLAlchemy ORM models
- **Schemas** (`app/schemas/`): Pydantic validation schemas

### Authentication Flow

JWT tokens with access/refresh pattern:
- `get_current_user`: Validates JWT, returns User
- `get_current_active_user`: Adds active status check
- `get_current_admin_user`: Adds admin role check
- `require_role([roles])`: Factory for custom role requirements

### Database

- Multi-DB support configured via `DB_TYPE` environment variable
- Session dependency: `db: Session = Depends(get_db)`
- Dev uses `init_db()` for auto table creation; production should use Alembic migrations

### API Structure

All API routes under `/api/v1/`:
- `/auth` - Login, register, token refresh
- `/users` - User management
- `/posts` - Posts and comments CRUD
- `/dashboard` - Statistics
- `/theme` - User theme settings
- `/menu` - Dynamic menu structure

### User Roles

`UserRole` enum: `ADMIN`, `MODERATOR`, `USER`

### Testing

Tests use in-memory SQLite with dependency override. Fixtures in `tests/conftest.py`:
- `db_session` - Fresh DB session per test (tables created/dropped per test)
- `client` - TestClient instance (depends on db_session)
- `test_user` / `admin_user` - Pre-created users with known credentials
- `user_token` / `admin_token` - JWT access tokens
- `auth_headers` / `admin_headers` - Ready-to-use auth headers

Test user credentials: `testuser` / `TestPass123`
Admin user credentials: `adminuser` / `AdminPass123`
