"""
# File: fastapi_template/app/db/models/file.py
# Description: 파일 데이터베이스 모델 정의
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_template.app.common.database.database_base import BaseModel


class File(BaseModel):
    """
    파일 모델
    """
    name: Mapped[str] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(index=True)
    type: Mapped[str] = mapped_column(index=True)
    mime_type: Mapped[str]
    size: Mapped[int] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)
    
    # 관계 설정
    owner = relationship("User", back_populates="files")
    
    def __repr__(self) -> str:
        return f"File(id={self.id}, name={self.name}, type={self.type})" 