"""
# File: fastapi_template/app/db/models/token.py
# Description: 인증 토큰 데이터베이스 모델 정의
"""

from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_template.app.common.database.database_base import BaseModel


class Token(BaseModel):
    """
    인증 토큰 모델
    """
    token: Mapped[str] = mapped_column(unique=True, index=True)
    type: Mapped[str] = mapped_column(index=True)  # access, refresh 등
    expires_at: Mapped[datetime] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    
    # 관계 설정
    owner = relationship("User", back_populates="tokens")
    
    def __repr__(self) -> str:
        return f"Token(id={self.id}, type={self.type}, expires_at={self.expires_at})" 