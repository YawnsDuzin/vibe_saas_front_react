"""
Menu Model
===========

메뉴 구조를 저장하는 모델입니다.

Features:
- 계층적 메뉴 구조 (부모-자식)
- 역할별 접근 제한
- 아이콘 및 URL 설정
- 정렬 순서
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Menu(Base):
    """
    메뉴 모델

    Attributes:
        id (int): 기본 키
        name (str): 메뉴 이름
        url (str): 메뉴 URL/라우트
        icon (str): 아이콘 클래스 (예: fa-home)
        parent_id (int): 부모 메뉴 FK
        order (int): 정렬 순서
        is_active (bool): 활성화 여부
        required_role (str): 필요한 최소 역할
        created_at (datetime): 생성 일시
    """

    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=True)

    # 계층 구조
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)

    # 메타데이터
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # 접근 제한 (null이면 모든 사용자, 값이 있으면 해당 역할 이상)
    required_role = Column(String(20), nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 관계 설정 (자기 참조)
    parent = relationship("Menu", remote_side=[id], backref="children")

    def __repr__(self) -> str:
        return f"<Menu(id={self.id}, name='{self.name}', url='{self.url}')>"

    def to_dict(self, include_children: bool = True) -> dict:
        """
        메뉴를 딕셔너리로 변환

        Args:
            include_children: 자식 메뉴 포함 여부

        Returns:
            dict: 메뉴 정보
        """
        result = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "icon": self.icon,
            "order": self.order,
            "required_role": self.required_role
        }

        if include_children and self.children:
            result["children"] = [
                child.to_dict(include_children=True)
                for child in sorted(self.children, key=lambda x: x.order)
                if child.is_active
            ]

        return result
