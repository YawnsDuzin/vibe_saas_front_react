"""
Supabase Storage
=================

Supabase Storage를 사용하는 스토리지 백엔드입니다.
"""

from typing import Optional, BinaryIO

from app.storage.base import BaseStorage, StorageFile


class SupabaseStorage(BaseStorage):
    """Supabase Storage 백엔드"""

    storage_type = "supabase"

    def __init__(
        self,
        url: str,
        key: str,
        bucket: str = "uploads"
    ):
        """
        Supabase 스토리지 초기화

        Args:
            url: Supabase 프로젝트 URL
            key: Supabase anon/service key
            bucket: 스토리지 버킷 이름
        """
        self.url = url.rstrip("/")
        self.key = key
        self.bucket = bucket
        self._client = None

    @property
    def client(self):
        """Supabase 클라이언트를 지연 로딩합니다."""
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self.url, self.key)
            except ImportError:
                raise ImportError(
                    "supabase 패키지가 필요합니다. "
                    "'pip install supabase' 명령으로 설치하세요."
                )
        return self._client

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = ""
    ) -> StorageFile:
        """파일을 Supabase에 업로드합니다."""
        key = self._generate_key(filename, folder)
        content = file.read()

        # Supabase Storage에 업로드
        self.client.storage.from_(self.bucket).upload(
            path=key,
            file=content,
            file_options={"content-type": content_type}
        )

        # 공개 URL 가져오기
        url = self.client.storage.from_(self.bucket).get_public_url(key)

        return StorageFile(
            key=key,
            filename=filename,
            content_type=content_type,
            size=len(content),
            url=url,
            storage_type=self.storage_type
        )

    async def delete(self, key: str) -> bool:
        """파일을 삭제합니다."""
        try:
            self.client.storage.from_(self.bucket).remove([key])
            return True
        except Exception:
            return False

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        """파일 URL을 반환합니다."""
        # 서명된 URL 생성 (비공개 버킷용)
        result = self.client.storage.from_(self.bucket).create_signed_url(
            path=key,
            expires_in=expires_in
        )
        return result.get("signedURL", "")

    async def exists(self, key: str) -> bool:
        """파일 존재 여부를 확인합니다."""
        try:
            # 파일 목록에서 확인
            folder = "/".join(key.split("/")[:-1]) or ""
            filename = key.split("/")[-1]
            files = self.client.storage.from_(self.bucket).list(folder)
            return any(f.get("name") == filename for f in files)
        except Exception:
            return False

    async def get_file(self, key: str) -> Optional[bytes]:
        """파일 내용을 반환합니다."""
        try:
            response = self.client.storage.from_(self.bucket).download(key)
            return response
        except Exception:
            return None
