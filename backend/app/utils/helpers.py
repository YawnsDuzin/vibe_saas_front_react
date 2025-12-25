"""
Helper Functions
=================

일반적인 헬퍼 함수들입니다.
"""

import re
import unicodedata
from typing import TypeVar, Generic, List
from math import ceil

from pydantic import BaseModel


def generate_slug(title: str, id: int = None) -> str:
    """
    제목에서 URL용 슬러그를 생성합니다.

    한글, 영문, 숫자를 지원합니다.

    Args:
        title: 원본 제목
        id: 고유성을 위한 ID (선택)

    Returns:
        str: 생성된 슬러그

    Example:
        ```python
        slug = generate_slug("FastAPI 시작하기", 1)
        # 'fastapi-시작하기-1'
        ```
    """
    # 유니코드 정규화
    text = unicodedata.normalize("NFKC", title)

    # 소문자 변환
    text = text.lower()

    # 특수문자를 공백으로 변환 (한글, 영문, 숫자 제외)
    text = re.sub(r"[^\w\s가-힣-]", "", text)

    # 연속 공백을 하이픈으로 변환
    text = re.sub(r"\s+", "-", text.strip())

    # 연속 하이픈 제거
    text = re.sub(r"-+", "-", text)

    # 앞뒤 하이픈 제거
    text = text.strip("-")

    # ID 추가 (고유성 보장)
    if id is not None:
        text = f"{text}-{id}"

    return text[:250]  # 최대 250자


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션 응답 모델

    Attributes:
        items: 현재 페이지의 항목들
        total: 전체 항목 수
        page: 현재 페이지 번호
        size: 페이지당 항목 수
        pages: 전체 페이지 수
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(
    items: list,
    page: int = 1,
    size: int = 10
) -> dict:
    """
    리스트를 페이지네이션합니다.

    Args:
        items: 전체 항목 리스트
        page: 요청 페이지 (1부터 시작)
        size: 페이지당 항목 수

    Returns:
        dict: 페이지네이션된 결과

    Example:
        ```python
        result = paginate(items, page=2, size=10)
        # {
        #     "items": [...],
        #     "total": 100,
        #     "page": 2,
        #     "size": 10,
        #     "pages": 10
        # }
        ```
    """
    total = len(items)
    pages = ceil(total / size) if size > 0 else 0

    # 페이지 범위 검증
    page = max(1, min(page, pages)) if pages > 0 else 1

    # 슬라이싱
    start = (page - 1) * size
    end = start + size
    page_items = items[start:end]

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


def format_datetime(dt, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    datetime 객체를 문자열로 포맷합니다.

    Args:
        dt: datetime 객체
        format_str: 포맷 문자열

    Returns:
        str: 포맷된 날짜 문자열
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    텍스트를 지정된 길이로 자릅니다.

    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        suffix: 자른 후 붙일 접미사

    Returns:
        str: 잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
