"""
# File: fastapi_template/app/db/models/user.py
# Description: 사용자 데이터베이스 모델 정의
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_template.app.common.database.database_base import BaseModel

class User(BaseModel):
    """
    사용자 모델
    """
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    
    # 관계 설정 - 사용자가 삭제되면 연관된 아이템도 함께 삭제
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    # 파일 관계 설정
    files = relationship("File", back_populates="owner", cascade="all, delete-orphan")
    # 토큰 관계 설정
    tokens = relationship("Token", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, username={self.username})"
