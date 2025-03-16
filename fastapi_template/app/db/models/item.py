"""
# File: fastapi_template/app/db/models/item.py
# Description: 아이템 데이터베이스 모델 정의
# - 아이템 테이블 구조
# - 사용자와의 관계 설정
# - 모델 메서드
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.common.database import BaseModel

class Item(BaseModel):
    """
    아이템 모델
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # 관계 설정
    owner = relationship("User", back_populates="items")
