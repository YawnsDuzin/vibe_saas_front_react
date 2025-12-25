"""
File Schemas
=============

파일 관련 Pydantic 스키마입니다.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FileBase(BaseModel):
    """파일 기본 스키마"""
    alt_text: Optional[str] = Field(None, max_length=255, description="대체 텍스트")
    description: Optional[str] = Field(None, max_length=500, description="설명")


class FileCreate(FileBase):
    """파일 생성 스키마 (업로드 시 추가 정보)"""
    folder: str = Field("", description="저장할 폴더")


class FileUpdate(FileBase):
    """파일 수정 스키마"""
    pass


class FileResponse(FileBase):
    """파일 응답 스키마"""
    id: int
    filename: str
    storage_key: str
    content_type: str
    size: int
    url: str
    storage_type: str
    folder: str
    uploader_id: int
    created_at: datetime
    updated_at: datetime

    # 계산된 필드
    extension: str
    is_image: bool
    size_formatted: str

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """파일 목록 응답 스키마"""
    items: List[FileResponse]
    total: int
    page: int
    size: int
    pages: int


class FileUploadResponse(BaseModel):
    """파일 업로드 응답 스키마"""
    id: int
    filename: str
    url: str
    content_type: str
    size: int
    size_formatted: str

    class Config:
        from_attributes = True


class StorageInfoResponse(BaseModel):
    """스토리지 정보 응답 스키마"""
    storage_type: str
    max_file_size: int  # bytes
    allowed_types: List[str]
    allowed_extensions: List[str]
