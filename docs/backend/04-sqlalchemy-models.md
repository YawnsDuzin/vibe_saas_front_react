# SQLAlchemy 모델

## 개요

**SQLAlchemy**는 Python에서 가장 널리 사용되는 **ORM(Object-Relational Mapping)** 라이브러리입니다. ORM을 사용하면 SQL 쿼리를 직접 작성하지 않고 **Python 코드로 데이터베이스를 조작**할 수 있습니다.

## 1. ORM이란?

### SQL vs ORM

```python
# 순수 SQL
cursor.execute("""
    SELECT * FROM users WHERE id = 1
""")
user = cursor.fetchone()

# SQLAlchemy ORM
user = db.query(User).filter(User.id == 1).first()
```

**ORM의 장점:**
```
┌─────────────────────────────────────────────────────────────┐
│  ORM 장점                                                   │
├─────────────────────────────────────────────────────────────┤
│  ✅ SQL 몰라도 사용 가능                                     │
│  ✅ Python 객체로 데이터 조작                                │
│  ✅ SQL Injection 방지                                      │
│  ✅ 다양한 DB 지원 (PostgreSQL, MySQL, SQLite 등)           │
│  ✅ 관계(relationship) 자동 처리                            │
│  ✅ IDE 자동완성 지원                                       │
└─────────────────────────────────────────────────────────────┘
```

### 개념 매핑

```
┌────────────────────────────────────────────────────────────┐
│  데이터베이스          SQLAlchemy                          │
├────────────────────────────────────────────────────────────┤
│  테이블 (Table)    →  클래스 (Class)                       │
│  행 (Row)          →  객체 (Instance)                      │
│  열 (Column)       →  속성 (Attribute)                     │
│  외래 키 (FK)      →  관계 (Relationship)                  │
└────────────────────────────────────────────────────────────┘

예:
┌──────────────────────────────────────────────────────────┐
│  users 테이블              User 클래스                    │
│  ┌─────┬──────────┐       class User(Base):              │
│  │ id  │ username │           id = Column(Integer)       │
│  ├─────┼──────────┤           username = Column(String)  │
│  │  1  │ "alice"  │                                      │
│  │  2  │ "bob"    │       user = User(username="alice")  │
│  └─────┴──────────┘       user.id = 1                    │
└──────────────────────────────────────────────────────────┘
```

## 2. 기본 모델 정의

### 가장 간단한 모델

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    """
    users 테이블과 매핑되는 모델
    """
    __tablename__ = "users"  # 테이블 이름

    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
```

**핵심 개념:**
```
class User(Base):
    │         │
    │         └── Base: 모든 모델의 부모 클래스 (declarative_base)
    │
    └── __tablename__: 데이터베이스 테이블 이름

    id = Column(Integer, primary_key=True)
    │     │      │            │
    │     │      │            └── primary_key: 기본 키 설정
    │     │      └── Integer: 정수 타입
    │     └── Column: 컬럼 정의
    └── id: Python에서 사용할 속성 이름
```

### Column 옵션

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    # 기본 키 (자동 증가)
    id = Column(Integer, primary_key=True, index=True)

    # 유니크 제약 조건
    email = Column(String(255), unique=True, nullable=False)

    # 인덱스 (검색 성능 향상)
    username = Column(String(50), unique=True, index=True)

    # NULL 허용
    full_name = Column(String(100), nullable=True)

    # 기본값
    is_active = Column(Boolean, default=True)

    # 자동 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow  # 수정 시 자동 갱신
    )

    # 긴 텍스트
    bio = Column(Text, nullable=True)
```

**Column 옵션 정리:**
```
┌────────────────┬─────────────────────────────────────────┐
│  옵션          │  설명                                   │
├────────────────┼─────────────────────────────────────────┤
│  primary_key   │  기본 키 설정                           │
│  index         │  인덱스 생성 (검색 빠름)                │
│  unique        │  중복 불가                              │
│  nullable      │  NULL 허용 여부 (기본 True)             │
│  default       │  기본값                                 │
│  onupdate      │  업데이트 시 자동 실행                  │
│  server_default│  DB 서버 기본값                         │
└────────────────┴─────────────────────────────────────────┘
```

## 3. 이 프로젝트의 모델

### User 모델 (app/models/user.py)

```python
# app/models/user.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """
    사용자 역할 Enum

    str을 상속받아 JSON 직렬화가 쉬움
    """
    ADMIN = "admin"          # 관리자
    MODERATOR = "moderator"  # 운영자
    USER = "user"            # 일반 사용자


class User(Base):
    """
    사용자 모델

    users 테이블과 매핑됩니다.
    """
    __tablename__ = "users"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # Enum 타입 컬럼
    role = Column(
        SQLEnum(UserRole),         # Python Enum을 DB Enum으로 변환
        default=UserRole.USER,     # 기본값: 일반 사용자
        nullable=False
    )

    # 상태 필드
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 관계 설정 (다음 섹션에서 설명)
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    theme = relationship("UserTheme", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        """디버깅용 문자열 표현"""
        return f"<User(id={self.id}, username='{self.username}')>"

    @property
    def is_admin(self) -> bool:
        """관리자 여부 확인"""
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """운영자 이상 권한 확인"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
```

### Post 모델 (app/models/post.py)

```python
# app/models/post.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """게시글 카테고리 모델"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계: 하나의 카테고리 → 여러 게시글
    posts = relationship("Post", back_populates="category")


class Post(Base):
    """게시글 모델"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    slug = Column(String(250), unique=True, nullable=False, index=True)

    # 외래 키: users 테이블의 id 참조
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 외래 키: categories 테이블의 id 참조 (선택적)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # 메타데이터
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """댓글 모델"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    # 외래 키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 대댓글

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")  # 자기 참조
```

## 4. 관계 (Relationships)

### 1:N 관계 (One-to-Many)

한 명의 사용자가 여러 게시글을 작성할 수 있습니다.

```python
# User 모델 (1)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

    # 관계: User → Post (1:N)
    posts = relationship("Post", back_populates="author")

# Post 모델 (N)
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)

    # 외래 키: users 테이블의 id 참조
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계: Post → User (N:1)
    author = relationship("User", back_populates="posts")
```

**관계 사용:**
```python
# 사용자의 모든 게시글 조회
user = db.query(User).first()
for post in user.posts:  # 자동으로 관련 게시글 로드
    print(post.title)

# 게시글의 작성자 조회
post = db.query(Post).first()
print(post.author.username)  # 자동으로 작성자 로드
```

**관계 다이어그램:**
```
┌─────────────────────────────────────────────────────────────┐
│                     1:N 관계                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User (1)                          Post (N)                │
│   ┌─────────────┐                   ┌─────────────┐         │
│   │ id          │←────────────────┐ │ id          │         │
│   │ username    │                 │ │ title       │         │
│   │             │                 └─│ author_id   │ (FK)    │
│   │ posts ──────│────────────────→  │             │         │
│   └─────────────┘   relationship    │ author ─────│──→ User │
│                                     └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1:1 관계 (One-to-One)

한 명의 사용자가 하나의 테마 설정을 가집니다.

```python
# User 모델
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

    # 관계: User → UserTheme (1:1)
    theme = relationship(
        "UserTheme",
        back_populates="user",
        uselist=False  # ← 1:1 관계 표시 (리스트가 아닌 단일 객체)
    )

# UserTheme 모델
class UserTheme(Base):
    __tablename__ = "user_themes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # unique로 1:1 보장

    # 관계: UserTheme → User (1:1)
    user = relationship("User", back_populates="theme")
```

### 자기 참조 관계 (Self-Referential)

대댓글을 구현할 때 사용합니다.

```python
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    # 부모 댓글 참조 (자기 참조 외래 키)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # 관계 설정
    parent = relationship(
        "Comment",
        remote_side=[id],  # ← id가 원격 측 (부모)
        backref="replies"   # ← 자식들을 replies로 접근
    )
```

**사용:**
```python
# 부모 댓글 조회
comment = db.query(Comment).first()
print(comment.parent)  # 부모 댓글 또는 None

# 대댓글 조회
for reply in comment.replies:  # 자식 댓글들
    print(reply.content)
```

### cascade 옵션

부모 삭제 시 자식도 함께 삭제됩니다.

```python
class User(Base):
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"  # ← 사용자 삭제 시 게시글도 삭제
    )
```

**cascade 옵션:**
```
┌────────────────────┬─────────────────────────────────────────┐
│  옵션              │  설명                                   │
├────────────────────┼─────────────────────────────────────────┤
│  save-update       │  부모 저장 시 자식도 저장               │
│  merge             │  부모 병합 시 자식도 병합               │
│  delete            │  부모 삭제 시 자식도 삭제               │
│  delete-orphan     │  고아 객체 자동 삭제                    │
│  all               │  위의 모든 옵션                         │
└────────────────────┴─────────────────────────────────────────┘
```

## 5. 쿼리 (Query)

### 기본 CRUD

```python
from sqlalchemy.orm import Session
from app.models.user import User

# Create (생성)
def create_user(db: Session, username: str, email: str):
    user = User(username=username, email=email)
    db.add(user)      # 세션에 추가
    db.commit()       # 커밋 (실제 저장)
    db.refresh(user)  # 최신 데이터로 갱신 (id 등)
    return user

# Read (조회)
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

# Update (수정)
def update_user(db: Session, user_id: int, username: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.username = username
        db.commit()
        db.refresh(user)
    return user

# Delete (삭제)
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
```

### 필터링

```python
from sqlalchemy import and_, or_, not_

# 단일 조건
db.query(User).filter(User.is_active == True).all()

# 여러 조건 (AND)
db.query(User).filter(
    User.is_active == True,
    User.role == "admin"
).all()

# 또는 and_() 사용
db.query(User).filter(
    and_(
        User.is_active == True,
        User.role == "admin"
    )
).all()

# OR 조건
db.query(User).filter(
    or_(
        User.role == "admin",
        User.role == "moderator"
    )
).all()

# NOT 조건
db.query(User).filter(not_(User.is_active == True)).all()

# LIKE (문자열 검색)
db.query(User).filter(User.username.like("%john%")).all()

# IN (목록에 포함)
db.query(User).filter(User.id.in_([1, 2, 3])).all()

# NULL 확인
db.query(User).filter(User.last_login == None).all()
db.query(User).filter(User.last_login.is_(None)).all()  # 권장
```

### 정렬과 페이징

```python
from sqlalchemy import desc, asc

# 정렬
db.query(User).order_by(User.created_at.desc()).all()  # 최신순
db.query(User).order_by(asc(User.username)).all()      # 이름순

# 페이징
db.query(User).offset(10).limit(10).all()  # 11~20번째

# 첫 번째만
db.query(User).first()

# 개수
db.query(User).count()

# 존재 여부
db.query(User).filter(User.email == email).exists()
```

### 조인 (Join)

```python
# 명시적 조인
db.query(Post, User).join(User, Post.author_id == User.id).all()

# relationship 사용 시 자동 조인
post = db.query(Post).first()
print(post.author.username)  # 자동으로 User 테이블 조인

# Eager Loading (N+1 문제 해결)
from sqlalchemy.orm import joinedload

# 게시글과 작성자를 한 번에 로드
posts = db.query(Post).options(joinedload(Post.author)).all()
```

## 6. 마이그레이션 (Alembic)

### 마이그레이션이란?

데이터베이스 스키마 변경을 버전 관리합니다.

```
┌─────────────────────────────────────────────────────────────┐
│  마이그레이션 없이                                           │
│  ─────────────────                                          │
│  모델 변경 → 수동으로 ALTER TABLE 실행 → 실수 가능성!        │
│                                                             │
│  마이그레이션 사용                                           │
│  ─────────────────                                          │
│  모델 변경 → 마이그레이션 파일 생성 → 마이그레이션 실행       │
│            (변경 사항 추적)        (자동으로 ALTER TABLE)    │
└─────────────────────────────────────────────────────────────┘
```

### Alembic 명령어

```bash
# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "Add user table"

# 마이그레이션 적용 (최신으로)
alembic upgrade head

# 한 단계 롤백
alembic downgrade -1

# 현재 버전 확인
alembic current

# 히스토리 확인
alembic history
```

### 개발 환경에서의 테이블 생성

개발 환경에서는 간단히 테이블을 생성할 수 있습니다.

```python
# app/database.py
def init_db() -> None:
    """
    개발 환경용 테이블 생성

    운영 환경에서는 Alembic 마이그레이션을 사용하세요.
    """
    from app.models import user, post, theme, menu  # 모델 import
    Base.metadata.create_all(bind=engine)  # 테이블 생성
```

## 7. 모델 설계 Best Practices

### 1. 공통 필드 믹스인 (Mixin)

```python
from datetime import datetime
from sqlalchemy import Column, DateTime

class TimestampMixin:
    """공통 타임스탬프 필드"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    # created_at, updated_at 자동 포함
```

### 2. 인덱스 설정

```python
from sqlalchemy import Index

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), index=True)  # 단일 인덱스
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    # 복합 인덱스
    __table_args__ = (
        Index("ix_post_author_created", "author_id", "created_at"),
    )
```

### 3. Soft Delete 패턴

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # 실제 삭제 대신
    # user.is_deleted = True
    # user.deleted_at = datetime.utcnow()

    # 쿼리 시 삭제된 항목 제외
    # db.query(User).filter(User.is_deleted == False).all()
```

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| Base | 모델 기본 클래스 | `class User(Base)` |
| Column | 컬럼 정의 | `Column(Integer)` |
| ForeignKey | 외래 키 | `ForeignKey("users.id")` |
| relationship | 관계 설정 | `relationship("Post")` |
| query | 데이터 조회 | `db.query(User)` |
| filter | 조건 필터링 | `.filter(User.id == 1)` |
| cascade | 연쇄 삭제 | `cascade="all, delete-orphan"` |

## 다음 단계

다음 문서 [05-database.md](./05-database.md)에서는 데이터베이스 연결 설정을 학습합니다.
