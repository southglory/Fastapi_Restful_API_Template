"""
# File: fastapi_template/app/db/models/item.py
# Description: 아이템 데이터베이스 모델 정의
# - 아이템 테이블 구조
# - 사용자와의 관계 설정
# - 모델 메서드
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.database.base import BaseModel

class Item(BaseModel):
    """아이템 모델"""
    
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(default=None)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # 관계 설정
    owner = relationship("User", back_populates="items")

    def __repr__(self) -> str:
        return f"Item(id={self.id}, title={self.title}, owner_id={self.owner_id})"
