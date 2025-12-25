"""
Database Configuration
=======================

데이터베이스 연결 및 세션 관리를 담당하는 모듈입니다.
SQLAlchemy를 사용하여 다양한 데이터베이스를 지원합니다.

지원 데이터베이스:
- PostgreSQL (기본)
- MySQL
- MariaDB
- SQLite
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.config import settings


def get_engine():
    """
    데이터베이스 엔진을 생성합니다.

    DB_TYPE에 따라 적절한 옵션으로 엔진을 구성합니다.

    Returns:
        Engine: SQLAlchemy 엔진 인스턴스
    """
    database_url = settings.database_url

    if settings.db_type == "sqlite":
        # SQLite의 경우 디렉토리가 없으면 생성
        db_dir = os.path.dirname(settings.sqlite_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # SQLite 특수 설정
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            # poolclass=StaticPool,  # 멀티스레드 트랜잭션 충돌 방지
            echo=settings.debug
        )

        # SQLite 외래키 활성화
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    else:
        # PostgreSQL, MySQL, MariaDB
        return create_engine(
            database_url,
            pool_pre_ping=True,  # 연결 유효성 검사
            pool_size=10,        # 커넥션 풀 크기
            max_overflow=20,     # 최대 추가 연결 수
            echo=settings.debug  # SQL 로깅 (디버그 모드)
        )


# 데이터베이스 엔진 생성
engine = get_engine()

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 모델의 기본 클래스
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션을 생성하고 제공합니다.

    FastAPI의 Depends()와 함께 사용하여
    요청마다 새로운 세션을 생성하고, 요청 종료 시 자동으로 닫습니다.

    Yields:
        Session: SQLAlchemy 세션 인스턴스

    Example:
        ```python
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    데이터베이스 테이블을 초기화합니다.

    모든 모델의 테이블을 생성합니다.
    개발 환경에서 사용하며, 운영 환경에서는 Alembic 마이그레이션을 권장합니다.
    """
    # 모든 모델을 import하여 Base.metadata에 등록
    from app.models import user, post, theme, menu  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    모든 데이터베이스 테이블을 삭제합니다.

    주의: 이 함수는 모든 데이터를 삭제합니다!
    테스트 환경에서만 사용하세요.
    """
    Base.metadata.drop_all(bind=engine)
