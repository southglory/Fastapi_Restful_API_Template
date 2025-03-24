"""
# File: fastapi_template/app/common/schemas/__init__.py
# Description: 스키마 모듈 패키지
# - 데이터 흐름 방향과 생명주기 기반 스키마 클래스 정의
"""

# 기본 스키마 클래스 내보내기
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

# 페이지네이션 스키마 내보내기
from app.common.schemas.pagination_schema import (
    PaginationParams,
    PageInfo,
    PaginatedResponse,
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
    # 페이지네이션 스키마
    "PaginationParams",
    "PageInfo",
    "PaginatedResponse",
]
