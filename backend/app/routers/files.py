"""
Files Router
=============

파일 업로드/관리 API 엔드포인트입니다.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.file import File
from app.services.file import FileService
from app.schemas.file import (
    FileResponse,
    FileListResponse,
    FileUpdate,
    FileUploadResponse,
    StorageInfoResponse
)

router = APIRouter()


@router.get("/info", response_model=StorageInfoResponse)
async def get_storage_info():
    """스토리지 정보를 조회합니다."""
    return FileService.get_storage_info()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder: str = "",
    alt_text: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    단일 파일을 업로드합니다.

    - **file**: 업로드할 파일
    - **folder**: 저장할 폴더 (선택)
    - **alt_text**: 대체 텍스트 (선택)
    - **description**: 설명 (선택)
    """
    service = FileService(db)
    db_file = await service.upload(
        file=file,
        uploader=current_user,
        folder=folder,
        alt_text=alt_text,
        description=description
    )
    return db_file


@router.post("/upload/multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = FastAPIFile(...),
    folder: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    여러 파일을 업로드합니다.

    - **files**: 업로드할 파일 목록
    - **folder**: 저장할 폴더 (선택)
    """
    service = FileService(db)
    db_files = await service.upload_multiple(
        files=files,
        uploader=current_user,
        folder=folder
    )
    return db_files


@router.get("", response_model=FileListResponse)
async def get_files(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    folder: Optional[str] = None,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    파일 목록을 조회합니다.

    - **page**: 페이지 번호
    - **size**: 페이지 크기
    - **folder**: 폴더 필터 (선택)
    - **content_type**: 콘텐츠 타입 필터 (선택, 예: image/)
    """
    service = FileService(db)

    # 관리자가 아니면 자신이 업로드한 파일만 조회
    uploader_id = None if current_user.role.value == "admin" else current_user.id

    files, total = service.get_list(
        page=page,
        size=size,
        folder=folder,
        content_type=content_type,
        uploader_id=uploader_id
    )

    pages = (total + size - 1) // size

    return FileListResponse(
        items=files,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/my", response_model=FileListResponse)
async def get_my_files(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    folder: Optional[str] = None,
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    내가 업로드한 파일 목록을 조회합니다.
    """
    service = FileService(db)
    files, total = service.get_list(
        page=page,
        size=size,
        folder=folder,
        content_type=content_type,
        uploader_id=current_user.id
    )

    pages = (total + size - 1) // size

    return FileListResponse(
        items=files,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """파일 정보를 조회합니다."""
    service = FileService(db)
    file = service.get_by_id(file_id)

    if not file:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    # 권한 확인: 본인 파일이거나 관리자
    if file.uploader_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    return file


@router.patch("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    update_data: FileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """파일 메타데이터를 수정합니다."""
    service = FileService(db)
    file = service.get_by_id(file_id)

    if not file:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    # 권한 확인: 본인 파일이거나 관리자
    if file.uploader_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    updated_file = service.update(
        file=file,
        alt_text=update_data.alt_text,
        description=update_data.description
    )
    return updated_file


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """파일을 삭제합니다."""
    service = FileService(db)
    file = service.get_by_id(file_id)

    if not file:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    # 권한 확인: 본인 파일이거나 관리자
    if file.uploader_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    await service.delete(file)
    return {"message": "파일이 삭제되었습니다."}


# 관리자 전용 엔드포인트
@router.get("/admin/all", response_model=FileListResponse)
async def admin_get_all_files(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    folder: Optional[str] = None,
    content_type: Optional[str] = None,
    uploader_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    [관리자] 모든 파일 목록을 조회합니다.
    """
    service = FileService(db)
    files, total = service.get_list(
        page=page,
        size=size,
        folder=folder,
        content_type=content_type,
        uploader_id=uploader_id
    )

    pages = (total + size - 1) // size

    return FileListResponse(
        items=files,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
