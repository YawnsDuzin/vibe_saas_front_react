"""
Cloudflare R2 Storage
======================

Cloudflare R2를 사용하는 스토리지 백엔드입니다.
R2는 S3 호환 API를 제공하므로 boto3를 사용합니다.
"""

from typing import Optional, BinaryIO

from app.storage.base import BaseStorage, StorageFile


class CloudflareR2Storage(BaseStorage):
    """Cloudflare R2 Storage 백엔드"""

    storage_type = "cloudflare"

    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket: str = "uploads",
        public_url: str = None
    ):
        """
        Cloudflare R2 스토리지 초기화

        Args:
            account_id: Cloudflare 계정 ID
            access_key_id: R2 Access Key ID
            secret_access_key: R2 Secret Access Key
            bucket: R2 버킷 이름
            public_url: 공개 URL (R2.dev 또는 커스텀 도메인)
        """
        self.account_id = account_id
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket = bucket
        self.public_url = public_url.rstrip("/") if public_url else None
        self._client = None

    @property
    def client(self):
        """boto3 S3 클라이언트를 지연 로딩합니다."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "s3",
                    endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name="auto"
                )
            except ImportError:
                raise ImportError(
                    "boto3 패키지가 필요합니다. "
                    "'pip install boto3' 명령으로 설치하세요."
                )
        return self._client

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = ""
    ) -> StorageFile:
        """파일을 Cloudflare R2에 업로드합니다."""
        key = self._generate_key(filename, folder)
        content = file.read()

        # R2에 업로드
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=content_type
        )

        # URL 생성
        if self.public_url:
            url = f"{self.public_url}/{key}"
        else:
            url = await self.get_url(key)

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
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        """서명된 URL을 반환합니다."""
        if self.public_url:
            return f"{self.public_url}/{key}"

        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in
        )

    async def exists(self, key: str) -> bool:
        """파일 존재 여부를 확인합니다."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    async def get_file(self, key: str) -> Optional[bytes]:
        """파일 내용을 반환합니다."""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception:
            return None
