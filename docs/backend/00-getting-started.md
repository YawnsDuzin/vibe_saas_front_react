# FastAPI 백엔드 시작하기

## 개요

이 문서는 FastAPI를 사용한 백엔드 개발에 대해 **처음부터** 설명합니다. Python 웹 개발 경험이 없어도 이해할 수 있도록 상세하게 작성되었습니다.

## FastAPI란?

FastAPI는 Python으로 작성된 **현대적이고 빠른 웹 프레임워크**입니다.

### 주요 특징

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 특징                              │
├─────────────────────────────────────────────────────────────┤
│  🚀 빠른 성능      - Node.js, Go와 비슷한 속도              │
│  📝 자동 문서화    - Swagger UI, ReDoc 자동 생성            │
│  ✅ 타입 검증      - Pydantic을 이용한 자동 검증            │
│  🔧 쉬운 사용      - 직관적인 API 설계                      │
│  🔒 보안 내장      - OAuth2, JWT 지원                       │
└─────────────────────────────────────────────────────────────┘
```

### 다른 프레임워크와 비교

| 특징 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 성능 | 매우 빠름 | 보통 | 보통 |
| 학습 곡선 | 쉬움 | 쉬움 | 어려움 |
| 자동 문서화 | ✅ 내장 | ❌ 없음 | ❌ 없음 |
| 타입 힌트 | ✅ 필수 | ❌ 선택 | ❌ 선택 |
| 비동기 지원 | ✅ 내장 | ⚠️ 제한적 | ⚠️ 제한적 |

## 이 프로젝트의 기술 스택

### 핵심 라이브러리

```
┌────────────────────────────────────────────────────────────────┐
│                     기술 스택 구성                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  FastAPI          웹 프레임워크 (API 서버)                      │
│       │                                                        │
│       ├── Pydantic       데이터 검증 및 직렬화                  │
│       │                                                        │
│       ├── SQLAlchemy     데이터베이스 ORM                       │
│       │                                                        │
│       ├── python-jose    JWT 토큰 생성/검증                     │
│       │                                                        │
│       └── passlib        비밀번호 해싱 (bcrypt)                 │
│                                                                │
│  Uvicorn          ASGI 서버 (앱 실행)                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 라이브러리 역할 설명

#### 1. FastAPI
```python
# FastAPI는 웹 서버의 "뼈대"입니다
from fastapi import FastAPI

app = FastAPI()  # 애플리케이션 생성

@app.get("/")    # URL 경로 정의
def read_root():
    return {"message": "Hello"}  # JSON 응답 반환
```

#### 2. Pydantic
```python
# Pydantic은 데이터를 "검사"합니다
from pydantic import BaseModel

class User(BaseModel):
    name: str           # 문자열이어야 함
    age: int            # 정수여야 함
    email: str          # 필수 필드

# 잘못된 데이터가 오면 자동으로 에러 발생!
# {"name": "John", "age": "스물"}  → 에러: age는 숫자여야 합니다
```

#### 3. SQLAlchemy
```python
# SQLAlchemy는 데이터베이스와 "대화"합니다
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"  # 테이블 이름

    id = Column(Integer, primary_key=True)
    name = Column(String)

# Python 코드로 데이터베이스 조작
# user = User(name="John")
# db.add(user)
# db.commit()
```

#### 4. JWT (python-jose)
```python
# JWT는 사용자 인증을 위한 "신분증"입니다
from jose import jwt

# 토큰 생성 (로그인 시)
token = jwt.encode({"user_id": 123}, "secret_key")

# 토큰 검증 (API 호출 시)
data = jwt.decode(token, "secret_key")
# {"user_id": 123}
```

## 프로젝트 구조 미리보기

```
app/
├── main.py              # 🚀 앱 시작점 (FastAPI 앱 생성)
├── config.py            # ⚙️ 환경 설정 (DB 정보, 시크릿 키 등)
├── database.py          # 🗄️ 데이터베이스 연결 설정
│
├── models/              # 📦 데이터베이스 테이블 정의
│   ├── user.py          #    - 사용자 테이블
│   ├── post.py          #    - 게시글/댓글 테이블
│   └── ...
│
├── schemas/             # 📋 API 요청/응답 형식 정의
│   ├── user.py          #    - 사용자 관련 스키마
│   ├── auth.py          #    - 인증 관련 스키마
│   └── ...
│
├── routers/             # 🛣️ API 엔드포인트 (URL 경로)
│   ├── auth.py          #    - /auth/* 경로
│   ├── users.py         #    - /users/* 경로
│   └── ...
│
├── services/            # 💼 비즈니스 로직 (실제 처리)
│   ├── auth.py          #    - 로그인, 토큰 발급
│   ├── user.py          #    - 사용자 생성, 조회
│   └── ...
│
├── dependencies/        # 🔌 공통 의존성 (인증 확인 등)
│   └── auth.py          #    - 토큰 검증, 권한 확인
│
└── utils/               # 🔧 유틸리티 함수
    └── security.py      #    - 비밀번호 해싱, JWT 처리
```

## 요청 처리 흐름

사용자의 요청이 어떻게 처리되는지 이해하면 전체 구조를 파악하기 쉽습니다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          요청 처리 흐름                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   클라이언트                                                             │
│       │                                                                 │
│       │  POST /api/v1/auth/login                                        │
│       │  {"username": "john", "password": "1234"}                       │
│       ▼                                                                 │
│   ┌─────────────┐                                                       │
│   │   Router    │  ← 요청을 받아서 적절한 함수로 전달                     │
│   │  (auth.py)  │                                                       │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          │  유효성 검사 (Pydantic Schema)                                │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │   Service   │  ← 실제 비즈니스 로직 처리                              │
│   │  (auth.py)  │     - 사용자 조회                                      │
│   └──────┬──────┘     - 비밀번호 검증                                    │
│          │            - 토큰 생성                                        │
│          │                                                              │
│          │  데이터베이스 조작                                            │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │   Model     │  ← SQLAlchemy ORM                                     │
│   │  (user.py)  │     - 데이터베이스 테이블과 매핑                        │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          │  SQL 쿼리 실행                                               │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │  Database   │  ← 실제 데이터 저장소                                  │
│   │  (SQLite,   │     PostgreSQL, MySQL 등                              │
│   │   etc.)     │                                                       │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          │  응답 데이터                                                  │
│          ▼                                                              │
│   클라이언트                                                             │
│       {"access_token": "...", "refresh_token": "..."}                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 개발 환경 설정

### 1. 가상 환경 생성

```bash
# 프로젝트 폴더로 이동
cd FastAPI_Tutorial

# 가상 환경 생성 (처음 한 번만)
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

주요 패키지:
- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `sqlalchemy` - 데이터베이스 ORM
- `pydantic-settings` - 환경 설정 관리
- `python-jose` - JWT 토큰
- `passlib[bcrypt]` - 비밀번호 해싱

### 3. 환경 변수 설정

```bash
# .env.example을 복사해서 .env 파일 생성
cp .env.example .env

# .env 파일 수정
# DB_TYPE=sqlite          # 개발 시 SQLite 사용
# DEBUG=true              # 디버그 모드 활성화
# JWT_SECRET_KEY=your-secret-key-here
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (자동 재시작 활성화)
uvicorn app.main:app --reload

# 또는 특정 포트로 실행
uvicorn app.main:app --reload --port 8000
```

### 5. API 문서 확인

서버 실행 후 브라우저에서:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 이 프로젝트의 주요 기능

### 1. 인증 시스템 (Authentication)
```
/api/v1/auth/register  - 회원가입
/api/v1/auth/login     - 로그인 (토큰 발급)
/api/v1/auth/refresh   - 토큰 갱신
/api/v1/auth/me        - 내 정보 조회
```

### 2. 사용자 관리 (Users)
```
/api/v1/users          - 사용자 목록 (관리자)
/api/v1/users/{id}     - 사용자 상세 조회
/api/v1/users/{id}     - 사용자 정보 수정
/api/v1/users/{id}     - 사용자 삭제 (관리자)
```

### 3. 게시판 (Posts)
```
/api/v1/posts          - 게시글 목록
/api/v1/posts          - 게시글 작성
/api/v1/posts/{id}     - 게시글 상세
/api/v1/posts/{id}     - 게시글 수정
/api/v1/posts/{id}     - 게시글 삭제
```

### 4. 댓글 (Comments)
```
/api/v1/posts/{id}/comments     - 댓글 목록
/api/v1/posts/{id}/comments     - 댓글 작성
/api/v1/comments/{id}           - 댓글 수정/삭제
```

### 5. 사용자 권한 (Role-Based Access)
```python
# 3가지 권한 레벨
UserRole.ADMIN       # 관리자 - 모든 권한
UserRole.MODERATOR   # 운영자 - 콘텐츠 관리
UserRole.USER        # 일반 - 기본 권한
```

## 문서 학습 순서

이 문서들을 순서대로 읽으면 FastAPI를 완전히 이해할 수 있습니다:

```
학습 순서
─────────────────────────────────────────────────────

1️⃣  00-getting-started.md     ← 현재 문서 (개요)
                │
2️⃣  01-python-basics.md       ← Python 기초 문법
                │
3️⃣  02-fastapi-fundamentals   ← FastAPI 핵심 개념
                │
4️⃣  03-pydantic-schemas.md    ← 데이터 검증
                │
5️⃣  04-sqlalchemy-models.md   ← 데이터베이스 모델
                │
6️⃣  05-database.md            ← DB 연결 설정
                │
7️⃣  06-project-structure.md   ← 프로젝트 구조
                │
8️⃣  07-routers.md             ← API 엔드포인트
                │
9️⃣  08-services.md            ← 비즈니스 로직
                │
🔟  09-dependencies.md        ← 의존성 주입
                │
1️⃣1️⃣  10-authentication.md     ← JWT 인증
                │
1️⃣2️⃣  11-security.md           ← 보안 (해싱, 토큰)
                │
1️⃣3️⃣  12-error-handling.md     ← 에러 처리

─────────────────────────────────────────────────────
```

## 다음 단계

다음 문서 [01-python-basics.md](./01-python-basics.md)에서는 FastAPI를 이해하는 데 필요한 Python 기초 문법을 학습합니다.
