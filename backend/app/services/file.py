"""
File Service
=============

파일 업로드/관리 비즈니스 로직입니다.
"""

import os
from typing import Optional, List, BinaryIO
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from app.models.file import File
from app.models.user import User
from app.storage import get_storage


# 설정값
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 기본 10MB
ALLOWED_TYPES = os.getenv(
    "ALLOWED_FILE_TYPES",
    "image/jpeg,image/png,image/gif,image/webp,application/pdf,text/plain"
).split(",")
ALLOWED_EXTENSIONS = os.getenv(
    "ALLOWED_FILE_EXTENSIONS",
    "jpg,jpeg,png,gif,webp,pdf,txt"
).split(",")


class FileService:
    """파일 서비스 클래스"""

    def __init__(self, db: Session):
        self.db = db
        self.storage = get_storage()

    async def upload(
        self,
        file: UploadFile,
        uploader: User,
        folder: str = "",
        alt_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> File:
        """
        파일을 업로드합니다.

        Args:
            file: 업로드할 파일
            uploader: 업로드하는 사용자
            folder: 저장할 폴더
            alt_text: 대체 텍스트
            description: 설명

        Returns:
            File: 생성된 파일 레코드
        """
        # 파일 검증
        await self._validate_file(file)

        # 스토리지에 업로드
        storage_file = await self.storage.upload(
            file=file.file,
            filename=file.filename,
            content_type=file.content_type,
            folder=folder
        )

        # DB에 레코드 생성
        db_file = File(
            filename=file.filename,
            storage_key=storage_file.key,
            content_type=file.content_type,
            size=storage_file.size,
            url=storage_file.url,
            storage_type=storage_file.storage_type,
            folder=folder,
            alt_text=alt_text,
            description=description,
            uploader_id=uploader.id
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)

        return db_file

    async def upload_multiple(
        self,
        files: List[UploadFile],
        uploader: User,
        folder: str = ""
    ) -> List[File]:
        """
        여러 파일을 업로드합니다.

        Args:
            files: 업로드할 파일 목록
            uploader: 업로드하는 사용자
            folder: 저장할 폴더

        Returns:
            List[File]: 생성된 파일 레코드 목록
        """
        uploaded_files = []
        for file in files:
            db_file = await self.upload(file, uploader, folder)
            uploaded_files.append(db_file)
        return uploaded_files

    def get_by_id(self, file_id: int) -> Optional[File]:
        """ID로 파일을 조회합니다."""
        return self.db.query(File).filter(File.id == file_id).first()

    def get_list(
        self,
        page: int = 1,
        size: int = 20,
        folder: Optional[str] = None,
        content_type: Optional[str] = None,
        uploader_id: Optional[int] = None
    ) -> tuple[List[File], int]:
        """
        파일 목록을 조회합니다.

        Args:
            page: 페이지 번호
            size: 페이지 크기
            folder: 폴더 필터
            content_type: 콘텐츠 타입 필터
            uploader_id: 업로더 ID 필터

        Returns:
            tuple: (파일 목록, 전체 개수)
        """
        query = self.db.query(File)

        if folder is not None:
            query = query.filter(File.folder == folder)
        if content_type:
            query = query.filter(File.content_type.startswith(content_type))
        if uploader_id:
            query = query.filter(File.uploader_id == uploader_id)

        total = query.count()
        files = (
            query.order_by(File.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return files, total

    def update(
        self,
        file: File,
        alt_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> File:
        """파일 메타데이터를 수정합니다."""
        if alt_text is not None:
            file.alt_text = alt_text
        if description is not None:
            file.description = description

        self.db.commit()
        self.db.refresh(file)
        return file

    async def delete(self, file: File) -> bool:
        """
        파일을 삭제합니다.

        스토리지에서 파일을 삭제하고 DB 레코드를 제거합니다.
        """
        # 스토리지에서 삭제
        await self.storage.delete(file.storage_key)

        # DB에서 삭제
        self.db.delete(file)
        self.db.commit()
        return True

    async def _validate_file(self, file: UploadFile):
        """파일을 검증합니다."""
        # 파일명 확인
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없습니다.")

        # 확장자 확인
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # MIME 타입 확인
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 타입입니다. 허용: {', '.join(ALLOWED_TYPES)}"
            )

        # 파일 크기 확인
        file.file.seek(0, 2)  # 끝으로 이동
        size = file.file.tell()
        file.file.seek(0)  # 처음으로 되돌림

        if size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"파일이 너무 큽니다. 최대 {max_mb:.1f}MB까지 허용됩니다."
            )

    @staticmethod
    def get_storage_info() -> dict:
        """스토리지 정보를 반환합니다."""
        storage = get_storage()
        return {
            "storage_type": storage.storage_type,
            "max_file_size": MAX_FILE_SIZE,
            "allowed_types": ALLOWED_TYPES,
            "allowed_extensions": ALLOWED_EXTENSIONS
        }
