# CRUD 작업

이 문서에서는 FastAPI에서 완전한 CRUD(Create, Read, Update, Delete) 작업을 구현하는 방법을 설명합니다.

## 목차

1. [CRUD 패턴 개요](#crud-패턴-개요)
2. [서비스 레이어](#서비스-레이어)
3. [Create (생성)](#create-생성)
4. [Read (조회)](#read-조회)
5. [Update (수정)](#update-수정)
6. [Delete (삭제)](#delete-삭제)
7. [페이지네이션](#페이지네이션)
8. [파일 첨부 연결](#파일-첨부-연결)

---

## CRUD 패턴 개요

### 아키텍처

```
Router (API 엔드포인트)
    ↓
Service (비즈니스 로직)
    ↓
Model (데이터베이스)
```

### 이점

- **관심사 분리**: 각 레이어가 명확한 책임
- **테스트 용이성**: 서비스 로직을 독립적으로 테스트
- **재사용성**: 서비스 로직을 여러 라우터에서 재사용
- **유지보수성**: 로직 변경 시 해당 레이어만 수정

---

## 서비스 레이어

### 기본 서비스 클래스 (app/services/post.py)

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """게시글 서비스"""

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db
```

### 라우터에서 사용

```python
from app.services.post import PostService

@router.get("/", response_model=PostListResponse)
def get_posts(db: Session = Depends(get_db)):
    post_service = PostService(db)
    posts, total = post_service.get_posts()
    return {"items": posts, "total": total}
```

---

## Create (생성)

### 서비스 메서드

```python
def create_post(self, post_data: PostCreate, author_id: int) -> Post:
    """
    게시글 생성

    Args:
        post_data: 게시글 데이터
        author_id: 작성자 ID

    Returns:
        생성된 게시글
    """
    # 모델 인스턴스 생성
    post = Post(
        title=post_data.title,
        content=post_data.content,
        slug=generate_slug(post_data.title),
        author_id=author_id,
        category_id=post_data.category_id,
        is_published=post_data.is_published
    )

    # 세션에 추가
    self.db.add(post)

    # flush로 ID 생성 (commit 전)
    self.db.flush()

    # 슬러그에 ID 추가 (고유성 보장)
    post.slug = generate_slug(post_data.title, post.id)

    # 커밋
    self.db.commit()

    # 새로고침 (DB 값 로드)
    self.db.refresh(post)

    return post
```

### 라우터 엔드포인트

```python
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성"
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 작성

    로그인이 필요합니다.
    """
    post_service = PostService(db)
    post = post_service.create_post(post_data, current_user.id)

    return {
        **post.__dict__,
        "author": post.author,
        "category": post.category,
        "comment_count": 0
    }
```

### 중복 검사가 필요한 경우 (사용자 생성)

```python
def create_user(self, user_data: UserCreate) -> User:
    """
    사용자 생성

    이메일과 사용자명 중복을 확인합니다.
    """
    # 이메일 중복 확인
    if self.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 사용자명 중복 확인
    if self.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다."
        )

    # 사용자 생성
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.USER
    )

    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)

    return user
```

---

## Read (조회)

### 단일 항목 조회

```python
def get_post(self, post_id: int) -> Optional[Post]:
    """
    ID로 게시글 조회

    관계된 데이터(작성자, 카테고리)도 함께 로드합니다.
    """
    return self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    ).filter(Post.id == post_id).first()


def get_post_by_slug(self, slug: str) -> Optional[Post]:
    """슬러그로 게시글 조회"""
    return self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    ).filter(Post.slug == slug).first()
```

### 라우터 엔드포인트

```python
@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 상세 조회"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 미공개 글 권한 확인
    if not post.is_published:
        if not current_user:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post_service.increment_view_count(post_id)

    return post
```

### 목록 조회 (필터링, 검색)

```python
def get_posts(
    self,
    page: int = 1,
    size: int = 10,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    include_unpublished: bool = False
) -> Tuple[List[Post], int]:
    """
    게시글 목록 조회

    Args:
        page: 페이지 번호
        size: 페이지당 항목 수
        category_id: 카테고리 필터
        search: 검색어
        include_unpublished: 미공개 글 포함 여부

    Returns:
        (게시글 목록, 전체 개수)
    """
    query = self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    )

    # 공개 여부 필터
    if not include_unpublished:
        query = query.filter(Post.is_published == True)

    # 카테고리 필터
    if category_id:
        query = query.filter(Post.category_id == category_id)

    # 검색
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_pattern)) |
            (Post.content.ilike(search_pattern))
        )

    # 전체 개수
    total = query.count()

    # 정렬 및 페이지네이션
    posts = query.order_by(
        desc(Post.is_pinned),   # 고정글 먼저
        desc(Post.created_at)   # 최신순
    ).offset((page - 1) * size).limit(size).all()

    return posts, total
```

---

## Update (수정)

### 서비스 메서드

```python
def update_post(
    self,
    post_id: int,
    post_data: PostUpdate,
    user: User
) -> Post:
    """
    게시글 수정

    Args:
        post_id: 게시글 ID
        post_data: 수정할 데이터
        user: 요청한 사용자

    Returns:
        수정된 게시글

    Raises:
        HTTPException: 권한이 없거나 게시글이 없는 경우
    """
    post = self.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 권한 확인 (작성자 또는 관리자)
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다."
        )

    # 필드 업데이트 (None이 아닌 값만)
    if post_data.title is not None:
        post.title = post_data.title
        post.slug = generate_slug(post_data.title, post.id)

    if post_data.content is not None:
        post.content = post_data.content

    if post_data.category_id is not None:
        post.category_id = post_data.category_id

    if post_data.is_published is not None:
        post.is_published = post_data.is_published

    if post_data.is_pinned is not None:
        post.is_pinned = post_data.is_pinned

    # 커밋
    self.db.commit()
    self.db.refresh(post)

    return post
```

### 부분 업데이트 (PATCH) 스키마

```python
class PostUpdate(BaseModel):
    """
    게시글 수정 스키마

    모든 필드가 선택적입니다.
    """
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_pinned: Optional[bool] = None
```

### 라우터 엔드포인트

```python
@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """게시글 수정"""
    post_service = PostService(db)
    post = post_service.update_post(post_id, post_data, current_user)

    return {
        **post.__dict__,
        "author": post.author,
        "category": post.category,
        "comment_count": post_service.get_comment_count(post_id)
    }
```

---

## Delete (삭제)

### 하드 삭제

```python
def delete_post(self, post_id: int, user: User) -> bool:
    """
    게시글 삭제

    관련 댓글도 함께 삭제됩니다 (cascade).
    """
    post = self.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 권한 확인
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다."
        )

    self.db.delete(post)
    self.db.commit()

    return True
```

### 소프트 삭제 (권장)

```python
def delete_comment(self, comment_id: int, user: User) -> bool:
    """
    댓글 소프트 삭제

    실제로 삭제하지 않고 is_active를 False로 설정합니다.
    """
    comment = self.db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다."
        )

    # 소프트 삭제
    comment.is_active = False
    comment.content = "삭제된 댓글입니다."

    self.db.commit()

    return True
```

### 라우터 엔드포인트

```python
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """게시글 삭제"""
    post_service = PostService(db)
    post_service.delete_post(post_id, current_user)
    # 204 No Content - 본문 없이 반환
```

---

## 페이지네이션

### 응답 스키마

```python
from typing import List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PostListResponse(BaseModel):
    """페이지네이션된 게시글 목록"""
    items: List[PostResponse] = Field(..., description="게시글 목록")
    total: int = Field(..., description="전체 게시글 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지당 항목 수")
    pages: int = Field(..., description="전체 페이지 수")
```

### 라우터에서 구현

```python
from math import ceil

@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 목록 조회 (페이지네이션)"""
    post_service = PostService(db)

    include_unpublished = current_user and current_user.is_admin

    posts, total = post_service.get_posts(
        page=page,
        size=size,
        category_id=category_id,
        search=search,
        include_unpublished=include_unpublished
    )

    # 댓글 수 추가
    items = []
    for post in posts:
        items.append({
            **post.__dict__,
            "author": post.author,
            "category": post.category,
            "comment_count": post_service.get_comment_count(post.id)
        })

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0
    )
```

### 커서 기반 페이지네이션 (대용량)

```python
def get_posts_cursor(
    self,
    cursor: Optional[int] = None,
    size: int = 10
) -> Tuple[List[Post], Optional[int]]:
    """
    커서 기반 페이지네이션

    대용량 데이터에서 더 효율적입니다.

    Args:
        cursor: 마지막으로 본 게시글 ID
        size: 가져올 항목 수

    Returns:
        (게시글 목록, 다음 커서)
    """
    query = self.db.query(Post).filter(Post.is_published == True)

    if cursor:
        query = query.filter(Post.id < cursor)

    posts = query.order_by(desc(Post.id)).limit(size + 1).all()

    # 다음 페이지 존재 여부 확인
    has_next = len(posts) > size
    if has_next:
        posts = posts[:size]
        next_cursor = posts[-1].id
    else:
        next_cursor = None

    return posts, next_cursor
```

---

## 파일 첨부 연결

게시글에 파일을 첨부하는 기능은 다대다(Many-to-Many) 관계를 사용합니다.

### 연결 모델 (app/models/post_file.py)

```python
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class PostFile(Base):
    """게시글-파일 연결 모델"""
    __tablename__ = "post_files"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 유니크 제약 조건
    __table_args__ = (
        UniqueConstraint('post_id', 'file_id', name='uq_post_file'),
    )

    # 관계 설정
    post = relationship("Post", back_populates="post_files")
    file = relationship("File", back_populates="post_files")
```

### 스키마에 file_ids 추가

```python
class PostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None
    is_published: bool = True
    file_ids: List[int] = []  # 첨부할 파일 ID 목록

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    file_ids: Optional[List[int]] = None  # 파일 목록 업데이트

class PostResponse(BaseModel):
    # ... 기존 필드
    files: List[FileResponse] = []  # 첨부된 파일 목록
```

### 서비스에서 파일 연결

```python
def create_post(self, post_data: PostCreate, author_id: int) -> Post:
    """게시글 생성 (파일 첨부 포함)"""
    post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=author_id,
        # ...
    )

    self.db.add(post)
    self.db.flush()  # ID 생성

    # 파일 연결
    if post_data.file_ids:
        self._attach_files_to_post(post.id, post_data.file_ids, author_id)

    self.db.commit()
    self.db.refresh(post)
    return post

def _attach_files_to_post(
    self,
    post_id: int,
    file_ids: List[int],
    user_id: int
) -> None:
    """게시글에 파일 연결"""
    for order, file_id in enumerate(file_ids):
        # 파일 존재 및 소유권 확인
        file = self.db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(404, f"파일을 찾을 수 없습니다. (ID: {file_id})")

        if file.uploader_id != user_id:
            raise HTTPException(403, f"파일에 대한 권한이 없습니다. (ID: {file_id})")

        # 연결 생성
        post_file = PostFile(
            post_id=post_id,
            file_id=file_id,
            display_order=order
        )
        self.db.add(post_file)

def _update_post_files(
    self,
    post_id: int,
    file_ids: List[int],
    user_id: int
) -> None:
    """게시글 파일 목록 업데이트"""
    # 기존 연결 삭제
    self.db.query(PostFile).filter(PostFile.post_id == post_id).delete()

    # 새 연결 생성
    if file_ids:
        self._attach_files_to_post(post_id, file_ids, user_id)
```

### 프론트엔드 사용 예시

```typescript
// 게시글 작성 시 파일 첨부
const createPost = async () => {
  // 1. 먼저 파일 업로드
  const uploadedFiles = await Promise.all(
    files.map(file => filesApi.upload(file))
  );

  // 2. 게시글 생성 시 file_ids 포함
  const post = await postsApi.create({
    title: "제목",
    content: "내용",
    file_ids: uploadedFiles.map(f => f.id)
  });
};

// 게시글 수정 시 파일 목록 변경
const updatePost = async () => {
  await postsApi.update(postId, {
    title: "수정된 제목",
    file_ids: [1, 3, 5]  // 새로운 파일 ID 목록
  });
};
```

---

## 다음 단계

- [테스트](06_testing.md)
