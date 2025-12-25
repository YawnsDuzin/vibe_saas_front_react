"""
Base Storage Interface
=======================

모든 스토리지 백엔드가 구현해야 하는 추상 베이스 클래스입니다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, BinaryIO
from datetime import datetime


@dataclass
class StorageFile:
    """스토리지에 저장된 파일 정보"""
    key: str  # 스토리지 내 파일 경로/키
    filename: str  # 원본 파일명
    content_type: str  # MIME 타입
    size: int  # 파일 크기 (bytes)
    url: str  # 접근 가능한 URL
    storage_type: str  # 스토리지 타입 (local, s3, supabase, cloudflare)
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BaseStorage(ABC):
    """스토리지 추상 베이스 클래스"""

    storage_type: str = "base"

    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = ""
    ) -> StorageFile:
        """
        파일을 업로드합니다.

        Args:
            file: 파일 객체 (바이너리 모드)
            filename: 원본 파일명
            content_type: MIME 타입
            folder: 저장할 폴더 경로

        Returns:
            StorageFile: 업로드된 파일 정보
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        파일을 삭제합니다.

        Args:
            key: 파일 키/경로

        Returns:
            bool: 삭제 성공 여부
        """
        pass

    @abstractmethod
    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        파일 접근 URL을 반환합니다.

        Args:
            key: 파일 키/경로
            expires_in: URL 만료 시간 (초)

        Returns:
            str: 파일 접근 URL
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        파일 존재 여부를 확인합니다.

        Args:
            key: 파일 키/경로

        Returns:
            bool: 파일 존재 여부
        """
        pass

    @abstractmethod
    async def get_file(self, key: str) -> Optional[bytes]:
        """
        파일 내용을 반환합니다.

        Args:
            key: 파일 키/경로

        Returns:
            Optional[bytes]: 파일 내용 또는 None
        """
        pass

    def _generate_key(self, filename: str, folder: str = "") -> str:
        """
        고유한 파일 키를 생성합니다.

        Args:
            filename: 원본 파일명
            folder: 폴더 경로

        Returns:
            str: 생성된 파일 키
        """
        import uuid
        from pathlib import Path

        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"

        if folder:
            return f"{folder.strip('/')}/{unique_name}"
        return unique_name
