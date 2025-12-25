"""
Storage Factory
================

환경 변수에 따라 적절한 스토리지 백엔드를 생성하는 팩토리입니다.
"""

from functools import lru_cache
from typing import Optional

from app.storage.base import BaseStorage


@lru_cache()
def get_storage() -> BaseStorage:
    """
    환경 변수에 따라 스토리지 인스턴스를 생성합니다.

    환경 변수:
        STORAGE_TYPE: 스토리지 타입 (local, supabase, cloudflare, s3)

    Local Storage:
        STORAGE_LOCAL_DIR: 업로드 디렉토리 (기본: uploads)
        STORAGE_LOCAL_URL: 파일 URL 베이스 (기본: /uploads)

    Supabase Storage:
        SUPABASE_URL: Supabase 프로젝트 URL
        SUPABASE_KEY: Supabase anon/service key
        SUPABASE_BUCKET: 스토리지 버킷 (기본: uploads)

    Cloudflare R2:
        CF_ACCOUNT_ID: Cloudflare 계정 ID
        CF_R2_ACCESS_KEY_ID: R2 Access Key ID
        CF_R2_SECRET_ACCESS_KEY: R2 Secret Access Key
        CF_R2_BUCKET: R2 버킷 이름 (기본: uploads)
        CF_R2_PUBLIC_URL: 공개 URL (선택)

    AWS S3:
        AWS_ACCESS_KEY_ID: AWS Access Key ID
        AWS_SECRET_ACCESS_KEY: AWS Secret Access Key
        AWS_S3_BUCKET: S3 버킷 이름
        AWS_S3_REGION: AWS 리전 (기본: ap-northeast-2)
        AWS_S3_ENDPOINT_URL: 커스텀 엔드포인트 (선택)
        AWS_S3_PUBLIC_URL: 공개 URL (선택)

    Returns:
        BaseStorage: 스토리지 인스턴스
    """
    import os

    storage_type = os.getenv("STORAGE_TYPE", "local").lower()

    if storage_type == "local":
        from app.storage.local import LocalStorage
        return LocalStorage(
            upload_dir=os.getenv("STORAGE_LOCAL_DIR", "uploads"),
            base_url=os.getenv("STORAGE_LOCAL_URL", "/uploads")
        )

    elif storage_type == "supabase":
        from app.storage.supabase import SupabaseStorage

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "Supabase 스토리지를 사용하려면 SUPABASE_URL과 SUPABASE_KEY가 필요합니다."
            )

        return SupabaseStorage(
            url=url,
            key=key,
            bucket=os.getenv("SUPABASE_BUCKET", "uploads")
        )

    elif storage_type == "cloudflare":
        from app.storage.cloudflare import CloudflareR2Storage

        account_id = os.getenv("CF_ACCOUNT_ID")
        access_key = os.getenv("CF_R2_ACCESS_KEY_ID")
        secret_key = os.getenv("CF_R2_SECRET_ACCESS_KEY")

        if not all([account_id, access_key, secret_key]):
            raise ValueError(
                "Cloudflare R2를 사용하려면 CF_ACCOUNT_ID, "
                "CF_R2_ACCESS_KEY_ID, CF_R2_SECRET_ACCESS_KEY가 필요합니다."
            )

        return CloudflareR2Storage(
            account_id=account_id,
            access_key_id=access_key,
            secret_access_key=secret_key,
            bucket=os.getenv("CF_R2_BUCKET", "uploads"),
            public_url=os.getenv("CF_R2_PUBLIC_URL")
        )

    elif storage_type == "s3":
        from app.storage.s3 import S3Storage

        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        bucket = os.getenv("AWS_S3_BUCKET")

        if not all([access_key, secret_key, bucket]):
            raise ValueError(
                "AWS S3를 사용하려면 AWS_ACCESS_KEY_ID, "
                "AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET이 필요합니다."
            )

        return S3Storage(
            access_key_id=access_key,
            secret_access_key=secret_key,
            bucket=bucket,
            region=os.getenv("AWS_S3_REGION", "ap-northeast-2"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
            public_url=os.getenv("AWS_S3_PUBLIC_URL")
        )

    else:
        raise ValueError(f"지원하지 않는 스토리지 타입: {storage_type}")


# 전역 스토리지 인스턴스
storage = get_storage()
