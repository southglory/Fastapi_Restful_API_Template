"""
# File: fastapi_template/app/common/database/base.py
# Description: SQLAlchemy 기본 설정 및 공통 모델
"""

from datetime import datetime, UTC
from typing import Any, ClassVar

from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr


class Base(DeclarativeBase):
    """
    모든 SQLAlchemy 모델의 기본 클래스
    """

    # 테이블명 자동 생성 (클래스명의 snake_case 형태)
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimeStampMixin:
    """
    생성 및 수정 시간 필드를 제공하는 Mixin
    """

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class BaseModel(Base, TimeStampMixin):
    """
    ID와 타임스탬프를 포함한 기본 모델 클래스
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
