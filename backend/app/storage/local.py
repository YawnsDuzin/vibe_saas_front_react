"""
Local Storage
==============

로컬 파일 시스템을 사용하는 스토리지 백엔드입니다.
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO

from app.storage.base import BaseStorage, StorageFile


class LocalStorage(BaseStorage):
    """로컬 파일 시스템 스토리지"""

    storage_type = "local"

    def __init__(self, upload_dir: str = "uploads", base_url: str = "/uploads"):
        """
        로컬 스토리지 초기화

        Args:
            upload_dir: 업로드 디렉토리 경로
            base_url: 파일 접근 URL 베이스 경로
        """
        self.upload_dir = Path(upload_dir)
        self.base_url = base_url.rstrip("/")

        # 업로드 디렉토리 생성
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = ""
    ) -> StorageFile:
        """파일을 로컬에 업로드합니다."""
        key = self._generate_key(filename, folder)
        file_path = self.upload_dir / key

        # 폴더 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 저장
        content = file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        size = len(content)
        url = f"{self.base_url}/{key}"

        return StorageFile(
            key=key,
            filename=filename,
            content_type=content_type,
            size=size,
            url=url,
            storage_type=self.storage_type
        )

    async def delete(self, key: str) -> bool:
        """파일을 삭제합니다."""
        file_path = self.upload_dir / key
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        """파일 URL을 반환합니다. (로컬은 만료 없음)"""
        return f"{self.base_url}/{key}"

    async def exists(self, key: str) -> bool:
        """파일 존재 여부를 확인합니다."""
        file_path = self.upload_dir / key
        return file_path.exists()

    async def get_file(self, key: str) -> Optional[bytes]:
        """파일 내용을 반환합니다."""
        file_path = self.upload_dir / key
        if not file_path.exists():
            return None

        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
