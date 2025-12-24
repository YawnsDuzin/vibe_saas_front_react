# 서비스 계층 (Services)

## 개요

서비스 계층은 **비즈니스 로직을 처리**하는 계층입니다. 라우터에서 요청을 받아 실제 데이터 처리를 수행하고 결과를 반환합니다.

## 1. 서비스 계층의 역할

```
┌─────────────────────────────────────────────────────────────┐
│                    서비스 계층의 역할                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Router (라우터)                                            │
│  - HTTP 요청 받기                                           │
│  - 응답 반환                                                │
│  - 스키마 검증                                              │
│         │                                                   │
│         ▼                                                   │
│  Service (서비스) ← 비즈니스 로직 담당                       │
│  - 데이터 처리                                              │
│  - 규칙 검증                                                │
│  - 여러 모델 조합                                           │
│  - 외부 서비스 연동                                         │
│  - 트랜잭션 관리                                            │
│         │                                                   │
│         ▼                                                   │
│  Model (모델)                                               │
│  - 데이터베이스 조작                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**왜 서비스 계층이 필요한가?**

```python
# ❌ 나쁜 예: 라우터에 비즈니스 로직 작성
@router.post("/users")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 중복 확인
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(400, "이미 존재하는 이메일")

    # 비밀번호 해싱
    hashed = get_password_hash(user_data.password)

    # 사용자 생성
    user = User(email=user_data.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    return user

# ✅ 좋은 예: 서비스로 분리
@router.post("/users")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user_data)
```

**분리의 장점:**
- 테스트 용이
- 재사용성
- 유지보수 편리
- 관심사 분리

## 2. 서비스 클래스 패턴

### 기본 구조

```python
# app/services/user.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash


class UserService:
    """
    사용자 관련 비즈니스 로직을 처리하는 서비스

    Attributes:
        db: SQLAlchemy 세션
    """

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: 데이터베이스 세션 (라우터에서 주입)
        """
        self.db = db

    # ==============================
    # 조회 메서드
    # ==============================

    def get_user(self, user_id: int) -> Optional[User]:
        """
        ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            User 또는 None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 조회"""
        return self.db.query(User).filter(User.username == username).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """
        사용자 목록 조회

        Args:
            skip: 건너뛸 항목 수
            limit: 최대 조회 수

        Returns:
            User 리스트
        """
        return self.db.query(User).offset(skip).limit(limit).all()

    # ==============================
    # 생성 메서드
    # ==============================

    def create_user(self, user_data: UserCreate) -> User:
        """
        새 사용자 생성

        Args:
            user_data: 사용자 생성 데이터

        Returns:
            생성된 User

        Raises:
            HTTPException: 이메일/사용자명 중복 시
        """
        # 중복 검사
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )

        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다."
            )

        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)

        # 사용자 생성
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )

        # DB에 저장
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    # ==============================
    # 수정 메서드
    # ==============================

    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        """
        사용자 정보 수정

        Args:
            user_id: 수정할 사용자 ID
            user_data: 수정 데이터

        Returns:
            수정된 User 또는 None
        """
        user = self.get_user(user_id)
        if not user:
            return None

        # 변경된 필드만 업데이트
        update_data = user_data.model_dump(exclude_unset=True)

        # 비밀번호가 있으면 해싱
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        # 속성 업데이트
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    # ==============================
    # 삭제 메서드
    # ==============================

    def delete_user(self, user_id: int) -> bool:
        """
        사용자 삭제

        Args:
            user_id: 삭제할 사용자 ID

        Returns:
            성공 여부
        """
        user = self.get_user(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True
```

## 3. 이 프로젝트의 서비스

### 인증 서비스 (auth.py)

```python
# app/services/auth.py

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import Token, TokenData
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)


class AuthService:
    """인증 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        사용자 인증

        이메일 또는 사용자명으로 사용자를 찾고,
        비밀번호를 검증합니다.
        """
        # 이메일 또는 사용자명으로 찾기
        user = self.db.query(User).filter(
            (User.email == username) | (User.username == username)
        ).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def login(self, username: str, password: str) -> Token:
        """
        로그인 수행

        인증 후 JWT 토큰을 발급합니다.
        """
        user = self.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일/사용자명 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 계정입니다."
            )

        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        self.db.commit()

        # 토큰 생성
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def refresh_tokens(self, refresh_token: str) -> Token:
        """
        토큰 갱신

        리프레시 토큰으로 새 액세스 토큰을 발급합니다.
        """
        # 토큰 타입 확인
        if not verify_token_type(refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다."
            )

        # 토큰 디코딩
        payload = decode_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었거나 유효하지 않습니다."
            )

        # 사용자 확인
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다."
            )

        # 새 토큰 생성
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
```

### 게시글 서비스 (post.py)

```python
# app/services/post.py

from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import re

from app.models.post import Post, Comment, Category
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """게시글 서비스"""

    def __init__(self, db: Session):
        self.db = db

    # ==============================
    # 게시글 조회
    # ==============================

    def get_posts(
        self,
        skip: int = 0,
        limit: int = 10,
        category_id: Optional[int] = None,
        is_published: bool = True
    ) -> List[Post]:
        """게시글 목록 조회"""
        query = self.db.query(Post)

        # 필터 적용
        if is_published:
            query = query.filter(Post.is_published == True)

        if category_id:
            query = query.filter(Post.category_id == category_id)

        # 정렬 및 페이징
        return query.order_by(
            Post.is_pinned.desc(),   # 고정글 우선
            Post.created_at.desc()   # 최신순
        ).offset(skip).limit(limit).all()

    def get_post(self, post_id: int) -> Optional[Post]:
        """게시글 상세 조회"""
        return self.db.query(Post).filter(Post.id == post_id).first()

    # ==============================
    # 게시글 생성
    # ==============================

    def create_post(
        self,
        post_data: PostCreate,
        author_id: int
    ) -> Post:
        """게시글 생성"""

        # 슬러그 생성 (URL 친화적 문자열)
        slug = self._generate_slug(post_data.title)

        post = Post(
            title=post_data.title,
            content=post_data.content,
            slug=slug,
            author_id=author_id,
            category_id=post_data.category_id,
            is_published=post_data.is_published
        )

        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        return post

    def _generate_slug(self, title: str) -> str:
        """제목에서 슬러그 생성"""
        # 특수문자 제거, 소문자 변환, 공백을 하이픈으로
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_]+', '-', slug)

        # 중복 확인 및 번호 추가
        base_slug = slug
        counter = 1
        while self.db.query(Post).filter(Post.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    # ==============================
    # 게시글 수정
    # ==============================

    def update_post(
        self,
        post_id: int,
        post_data: PostUpdate
    ) -> Optional[Post]:
        """게시글 수정"""
        post = self.get_post(post_id)
        if not post:
            return None

        update_data = post_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(post, field, value)

        self.db.commit()
        self.db.refresh(post)

        return post

    # ==============================
    # 게시글 삭제
    # ==============================

    def delete_post(self, post_id: int) -> bool:
        """게시글 삭제"""
        post = self.get_post(post_id)
        if not post:
            return False

        self.db.delete(post)
        self.db.commit()

        return True

    # ==============================
    # 부가 기능
    # ==============================

    def increment_view_count(self, post_id: int) -> None:
        """조회수 증가"""
        post = self.get_post(post_id)
        if post:
            post.view_count += 1
            self.db.commit()
```

## 4. 서비스 설계 패턴

### 트랜잭션 처리

```python
class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: OrderCreate) -> Order:
        """
        주문 생성 (트랜잭션 필요)

        1. 재고 확인
        2. 재고 차감
        3. 주문 생성
        4. 결제 처리

        하나라도 실패하면 모두 롤백
        """
        try:
            # 1. 재고 확인
            product = self.db.query(Product).filter(
                Product.id == order_data.product_id
            ).first()

            if product.stock < order_data.quantity:
                raise HTTPException(400, "재고 부족")

            # 2. 재고 차감
            product.stock -= order_data.quantity

            # 3. 주문 생성
            order = Order(
                product_id=order_data.product_id,
                quantity=order_data.quantity,
                total_price=product.price * order_data.quantity
            )
            self.db.add(order)

            # 4. 커밋 (모든 작업이 성공하면)
            self.db.commit()
            self.db.refresh(order)

            return order

        except Exception as e:
            # 실패 시 롤백
            self.db.rollback()
            raise HTTPException(500, f"주문 생성 실패: {str(e)}")
```

### 여러 서비스 조합

```python
class DashboardService:
    """여러 서비스를 조합하는 서비스"""

    def __init__(self, db: Session):
        self.db = db
        # 다른 서비스 인스턴스 생성
        self.user_service = UserService(db)
        self.post_service = PostService(db)

    def get_stats(self) -> dict:
        """대시보드 통계"""
        return {
            "total_users": self.db.query(User).count(),
            "total_posts": self.db.query(Post).count(),
            "recent_users": self.user_service.get_users(limit=5),
            "recent_posts": self.post_service.get_posts(limit=5)
        }
```

### 외부 서비스 연동

```python
import httpx

class NotificationService:
    """외부 서비스 연동 예시"""

    def __init__(self, db: Session):
        self.db = db
        self.email_api_url = "https://api.email.com/send"

    async def send_welcome_email(self, user: User) -> bool:
        """가입 환영 이메일 발송"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.email_api_url,
                json={
                    "to": user.email,
                    "subject": "가입을 환영합니다!",
                    "body": f"안녕하세요, {user.username}님!"
                }
            )
            return response.status_code == 200
```

## 5. 라우터에서 서비스 사용

```python
# app/routers/posts.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.post import PostService

router = APIRouter()

@router.get("/")
def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # 서비스 인스턴스 생성
    service = PostService(db)

    # 서비스 메서드 호출
    return service.get_posts(skip=skip, limit=limit)


@router.post("/")
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    service = PostService(db)
    return service.create_post(post_data, author_id=user.id)
```

## 6. 테스트

### 서비스 단위 테스트

```python
# tests/test_user_service.py

import pytest
from sqlalchemy.orm import Session
from app.services.user import UserService
from app.schemas.user import UserCreate

def test_create_user(db_session: Session):
    """사용자 생성 테스트"""
    service = UserService(db_session)

    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPass123"
    )

    user = service.create_user(user_data)

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password != "TestPass123"  # 해싱됨

def test_duplicate_email(db_session: Session):
    """중복 이메일 테스트"""
    service = UserService(db_session)

    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPass123"
    )

    service.create_user(user_data)

    # 같은 이메일로 다시 생성 시도
    with pytest.raises(HTTPException) as exc:
        service.create_user(user_data)

    assert exc.value.status_code == 400
    assert "이미 등록된 이메일" in exc.value.detail
```

## 요약

| 메서드 패턴 | 역할 | 예시 |
|------------|------|------|
| get_* | 단일/목록 조회 | `get_user()`, `get_users()` |
| create_* | 생성 | `create_user()` |
| update_* | 수정 | `update_user()` |
| delete_* | 삭제 | `delete_user()` |
| find_by_* | 특정 조건 조회 | `get_user_by_email()` |

## 다음 단계

다음 문서 [09-dependencies.md](./09-dependencies.md)에서는 FastAPI 의존성 주입을 학습합니다.
