"""
AWS S3 Storage
===============

AWS S3를 사용하는 스토리지 백엔드입니다.
"""

from typing import Optional, BinaryIO

from app.storage.base import BaseStorage, StorageFile


class S3Storage(BaseStorage):
    """AWS S3 Storage 백엔드"""

    storage_type = "s3"

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        bucket: str,
        region: str = "ap-northeast-2",
        endpoint_url: str = None,
        public_url: str = None
    ):
        """
        AWS S3 스토리지 초기화

        Args:
            access_key_id: AWS Access Key ID
            secret_access_key: AWS Secret Access Key
            bucket: S3 버킷 이름
            region: AWS 리전
            endpoint_url: 커스텀 엔드포인트 URL (S3 호환 서비스용)
            public_url: 공개 URL (CloudFront 또는 커스텀 도메인)
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url
        self.public_url = public_url.rstrip("/") if public_url else None
        self._client = None

    @property
    def client(self):
        """boto3 S3 클라이언트를 지연 로딩합니다."""
        if self._client is None:
            try:
                import boto3
                client_config = {
                    "aws_access_key_id": self.access_key_id,
                    "aws_secret_access_key": self.secret_access_key,
                    "region_name": self.region
                }
                if self.endpoint_url:
                    client_config["endpoint_url"] = self.endpoint_url

                self._client = boto3.client("s3", **client_config)
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
        """파일을 S3에 업로드합니다."""
        key = self._generate_key(filename, folder)
        content = file.read()

        # S3에 업로드
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
            url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

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
