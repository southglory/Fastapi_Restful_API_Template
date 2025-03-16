"""
# File: fastapi_template/app/db/models/user.py
# Description: 사용자 데이터베이스 모델 정의
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.common.database import BaseModel

class User(BaseModel):
    """
    사용자 모델
    """
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 관계 설정 - 사용자가 삭제되면 연관된 아이템도 함께 삭제
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
