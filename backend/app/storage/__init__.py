"""
Storage Module
===============

파일 스토리지를 관리하는 패키지입니다.

지원하는 스토리지:
- local: 로컬 파일 시스템
- supabase: Supabase Storage
- cloudflare: Cloudflare R2
- s3: AWS S3
"""

from app.storage.base import BaseStorage, StorageFile
from app.storage.factory import get_storage, storage

__all__ = [
    "BaseStorage",
    "StorageFile",
    "get_storage",
    "storage",
]
