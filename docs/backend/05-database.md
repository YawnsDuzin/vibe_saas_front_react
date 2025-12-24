# 데이터베이스 설정

## 개요

이 문서에서는 FastAPI 프로젝트에서 **데이터베이스 연결을 설정**하는 방법을 설명합니다. 이 프로젝트는 **다중 데이터베이스(PostgreSQL, MySQL, MariaDB, SQLite)**를 지원합니다.

## 1. 데이터베이스 연결 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                  데이터베이스 연결 흐름                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  .env 파일                                                  │
│  ├── DB_TYPE=postgresql                                     │
│  ├── DB_HOST=localhost                                      │
│  └── DB_PORT=5432                                           │
│         │                                                   │
│         ▼                                                   │
│  Settings (config.py)                                       │
│  └── database_url 프로퍼티                                  │
│         │                                                   │
│         ▼                                                   │
│  create_engine() (database.py)                              │
│  └── SQLAlchemy 엔진 생성                                   │
│         │                                                   │
│         ▼                                                   │
│  sessionmaker()                                             │
│  └── 세션 팩토리 생성                                       │
│         │                                                   │
│         ▼                                                   │
│  get_db()                                                   │
│  └── 요청마다 세션 제공                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. 환경 설정 (config.py)

### 데이터베이스 설정

```python
# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 데이터베이스 타입 선택
    db_type: str = Field(default="postgresql", alias="DB_TYPE")

    # 서버 연결 정보
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    db_name: str = Field(default="fastapi_db", alias="DB_NAME")

    # SQLite 전용
    sqlite_file: str = Field(default="./data/app.db", alias="SQLITE_FILE")

    @property
    def database_url(self) -> str:
        """
        DB 타입에 따른 연결 문자열 생성

        Returns:
            SQLAlchemy 데이터베이스 URL
        """
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_file}"

        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

        elif self.db_type in ["mysql", "mariadb"]:
            return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

        else:
            raise ValueError(f"지원하지 않는 DB 타입: {self.db_type}")

    class Config:
        env_file = ".env"
```

### 환경 변수 파일 (.env)

```env
# .env

# 데이터베이스 설정
DB_TYPE=sqlite          # sqlite, postgresql, mysql, mariadb
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=fastapi_db
SQLITE_FILE=./data/app.db

# 디버그 모드
DEBUG=true
```

## 3. 엔진 생성 (database.py)

### SQLAlchemy 엔진이란?

엔진은 **데이터베이스와의 연결 풀**을 관리합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   SQLAlchemy 엔진                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Engine                                                    │
│   ├── Connection Pool (연결 풀)                             │
│   │   ├── Connection 1 ─┐                                  │
│   │   ├── Connection 2  ├─→ 데이터베이스                   │
│   │   └── Connection 3 ─┘                                  │
│   │                                                         │
│   └── Dialect (방언)                                        │
│       └── PostgreSQL / MySQL / SQLite 전용 쿼리 변환        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 엔진 생성 코드

```python
# app/database.py

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.config import settings


def get_engine():
    """
    DB 타입에 따른 엔진 생성
    """
    database_url = settings.database_url

    if settings.db_type == "sqlite":
        # ───────────────────────────────────
        # SQLite 설정 (개발용)
        # ───────────────────────────────────

        # 디렉토리 자동 생성
        db_dir = os.path.dirname(settings.sqlite_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},  # 멀티스레드 허용
            poolclass=StaticPool,  # 단일 연결 풀
            echo=settings.debug    # SQL 로깅
        )

        # SQLite 외래키 활성화
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    else:
        # ───────────────────────────────────
        # PostgreSQL, MySQL, MariaDB 설정
        # ───────────────────────────────────

        return create_engine(
            database_url,
            pool_pre_ping=True,   # 연결 유효성 검사
            pool_size=10,         # 기본 연결 풀 크기
            max_overflow=20,      # 추가 연결 허용 수
            echo=settings.debug   # SQL 로깅 (디버그용)
        )


# 엔진 생성
engine = get_engine()
```

**엔진 옵션 설명:**
```
┌───────────────────┬─────────────────────────────────────────────┐
│  옵션             │  설명                                       │
├───────────────────┼─────────────────────────────────────────────┤
│  pool_pre_ping    │  연결 사용 전 유효성 확인                    │
│  pool_size        │  동시에 유지할 연결 수 (기본 5)              │
│  max_overflow     │  pool_size 초과 시 추가 연결 수              │
│  echo             │  SQL 쿼리 콘솔 출력                          │
│  connect_args     │  드라이버 전용 설정                          │
└───────────────────┴─────────────────────────────────────────────┘
```

## 4. 세션 관리

### 세션이란?

세션은 **데이터베이스와의 대화 단위**입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   세션 (Session)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  세션의 역할:                                                │
│  1. 객체 추적 - 변경 사항 감지                               │
│  2. 트랜잭션 관리 - commit/rollback                         │
│  3. 쿼리 실행 - db.query(User).all()                        │
│                                                             │
│  세션 생명주기:                                              │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐         │
│  │ 생성   │ → │ 작업   │ → │ 커밋   │ → │ 닫기   │         │
│  │Session │   │add,    │   │commit  │   │close   │         │
│  │Local() │   │query   │   │        │   │        │         │
│  └────────┘   └────────┘   └────────┘   └────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 세션 팩토리 생성

```python
# app/database.py (계속)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,   # 수동 커밋 (명시적 commit 필요)
    autoflush=False,    # 수동 플러시 (쿼리 전 자동 flush 안함)
    bind=engine         # 엔진과 바인딩
)

# 모델의 기본 클래스
Base = declarative_base()
```

**sessionmaker 옵션:**
```
┌────────────────┬──────────────────────────────────────────────┐
│  옵션          │  설명                                        │
├────────────────┼──────────────────────────────────────────────┤
│  autocommit    │  False: 수동 커밋 (권장)                     │
│                │  True: 자동 커밋                             │
├────────────────┼──────────────────────────────────────────────┤
│  autoflush     │  False: 수동 플러시                          │
│                │  True: 쿼리 전 자동 플러시                   │
├────────────────┼──────────────────────────────────────────────┤
│  bind          │  사용할 엔진 지정                            │
└────────────────┴──────────────────────────────────────────────┘
```

### get_db 의존성

```python
# app/database.py (계속)

def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션을 생성하고 제공합니다.

    FastAPI의 Depends()와 함께 사용합니다.
    요청마다 새 세션을 생성하고, 완료 후 자동으로 닫습니다.

    Yields:
        Session: SQLAlchemy 세션

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()  # 세션 생성
    try:
        yield db         # 세션 제공 (여기서 요청 처리)
    finally:
        db.close()       # 세션 닫기 (항상 실행)
```

**get_db 동작 흐름:**
```
┌─────────────────────────────────────────────────────────────┐
│  요청: GET /users                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. get_db() 호출                                           │
│     └── db = SessionLocal()  # 세션 생성                    │
│                                                             │
│  2. yield db                                                │
│     └── 세션이 라우터 함수로 전달됨                          │
│                                                             │
│  3. 라우터 함수 실행                                         │
│     └── db.query(User).all()                                │
│                                                             │
│  4. 응답 반환 후                                             │
│     └── db.close()  # finally 블록 실행                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 5. 테이블 초기화

### init_db 함수

```python
# app/database.py (계속)

def init_db() -> None:
    """
    데이터베이스 테이블을 초기화합니다.

    모든 모델의 테이블을 생성합니다.
    개발 환경에서 사용하며, 운영 환경에서는 Alembic을 권장합니다.
    """
    # 모든 모델을 import (Base.metadata에 등록됨)
    from app.models import user, post, theme, menu  # noqa: F401

    # 테이블 생성 (없는 테이블만 생성)
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    모든 테이블 삭제 (테스트용)

    주의: 모든 데이터가 삭제됩니다!
    """
    Base.metadata.drop_all(bind=engine)
```

### 앱 시작 시 테이블 생성

```python
# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 이벤트"""

    # 시작 시
    print("🚀 서버 시작...")
    init_db()  # 테이블 생성
    print("✅ 데이터베이스 초기화 완료")

    yield  # 앱 실행

    # 종료 시
    print("👋 서버 종료...")


app = FastAPI(lifespan=lifespan)
```

## 6. 다중 데이터베이스 지원

### 지원 데이터베이스별 설정

```python
# PostgreSQL
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=fastapi_db

# MySQL / MariaDB
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=fastapi_db

# SQLite (개발용)
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
```

### 연결 문자열 형식

```
┌─────────────────────────────────────────────────────────────┐
│  데이터베이스별 연결 문자열                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PostgreSQL:                                                │
│  postgresql://user:pass@host:5432/dbname                    │
│                                                             │
│  MySQL/MariaDB:                                             │
│  mysql+pymysql://user:pass@host:3306/dbname                 │
│  │     │                                                    │
│  │     └── PyMySQL 드라이버 사용                            │
│  │                                                          │
│  SQLite:                                                    │
│  sqlite:///./data/app.db                                    │
│         │││                                                 │
│         ││└── 파일 경로                                     │
│         │└── 상대 경로                                      │
│         └── 빈 호스트 (파일 기반)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### SQLite 특별 설정

SQLite는 다른 DB와 다르게 **파일 기반**입니다.

```python
if settings.db_type == "sqlite":
    engine = create_engine(
        database_url,
        # SQLite는 기본적으로 단일 스레드
        # 멀티스레드 허용을 위해 설정
        connect_args={"check_same_thread": False},

        # 단일 연결 풀 사용
        poolclass=StaticPool,
    )

    # SQLite 외래키 기본 비활성화
    # PRAGMA로 활성화 필요
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

## 7. FastAPI에서 사용하기

### 라우터에서 DB 세션 사용

```python
# app/routers/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """
    모든 사용자 조회

    Depends(get_db)가 자동으로:
    1. 세션 생성
    2. 세션 주입
    3. 세션 정리
    """
    users = db.query(User).all()
    return users

@router.post("/users")
def create_user(username: str, db: Session = Depends(get_db)):
    """
    사용자 생성

    세션을 통해 데이터 저장
    """
    user = User(username=username)
    db.add(user)       # 세션에 추가
    db.commit()        # 커밋 (저장)
    db.refresh(user)   # 최신 데이터 갱신
    return user
```

### 트랜잭션 패턴

```python
@router.post("/transfer")
def transfer_money(
    from_id: int,
    to_id: int,
    amount: int,
    db: Session = Depends(get_db)
):
    """
    계좌 이체 (트랜잭션 필요)
    """
    try:
        # 출금
        from_account = db.query(Account).filter(Account.id == from_id).first()
        from_account.balance -= amount

        # 입금
        to_account = db.query(Account).filter(Account.id == to_id).first()
        to_account.balance += amount

        # 모든 작업 성공 시 커밋
        db.commit()
        return {"message": "이체 완료"}

    except Exception as e:
        # 실패 시 롤백 (모든 변경 취소)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### 서비스 레이어에서 사용

```python
# app/services/user.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserService:
    """사용자 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """사용자 생성"""
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password)
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> User:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()


# 라우터에서 사용
@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.create_user(user_data)
    return user
```

## 8. 테스트 환경 설정

### 테스트용 인메모리 DB

```python
# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# 테스트용 인메모리 SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """테스트용 DB 세션"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # 테스트 후 정리


@pytest.fixture
def client(db_session):
    """테스트 클라이언트"""

    # get_db를 테스트 세션으로 대체
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

### 테스트 작성

```python
# tests/test_users.py

def test_create_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

## 요약

| 구성 요소 | 역할 | 파일 |
|----------|------|------|
| Settings | 환경 변수 관리 | config.py |
| Engine | DB 연결 풀 관리 | database.py |
| SessionLocal | 세션 팩토리 | database.py |
| get_db | 세션 제공 의존성 | database.py |
| init_db | 테이블 초기화 | database.py |

## 다음 단계

다음 문서 [06-project-structure.md](./06-project-structure.md)에서는 프로젝트 전체 구조를 학습합니다.
