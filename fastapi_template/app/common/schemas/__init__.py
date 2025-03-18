"""
# File: fastapi_template/app/common/schemas/__init__.py
# Description: 스키마 모듈 패키지
# - 데이터 흐름 방향과 생명주기 기반 스키마 클래스 정의
"""

from app.common.schemas.base_schema import (
    # 기본 스키마
    BaseSchema,
    TimeStampMixin,
    ResponseSchema,
    # 데이터 흐름 방향 기반 스키마
    InputSchema,
    OutputSchema,
    InternalSchema,
    # 데이터 생명주기 기반 스키마
    CreateSchema,
    ReadSchema,
    UpdateSchema,
    # 서비스 간 통신 스키마
    ServiceSchema,
    EventSchema,
)

__all__ = [
    # 기본 스키마
    "BaseSchema",
    "TimeStampMixin",
    "ResponseSchema",
    # 데이터 흐름 방향 기반 스키마
    "InputSchema",
    "OutputSchema",
    "InternalSchema",
    # 데이터 생명주기 기반 스키마
    "CreateSchema",
    "ReadSchema",
    "UpdateSchema",
    # 서비스 간 통신 스키마
    "ServiceSchema",
    "EventSchema",
]
