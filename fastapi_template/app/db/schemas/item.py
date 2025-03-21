"""
# File: fastapi_template/app/db/schemas/item.py
# Description: 아이템 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from typing import Optional
from pydantic import Field

from app.common.schemas.base_schema import (
    CreateSchema,
    ReadSchema,
    UpdateSchema,
    InternalSchema,
    TimeStampMixin,
    BaseSchema,
)


# 아이템 공통 속성
class ItemBase(BaseSchema):
    """아이템 공통 속성"""

    title: str = Field(..., min_length=1, max_length=100, description="아이템 제목")
    description: Optional[str] = Field(None, max_length=1000, description="아이템 설명")


class ItemCreate(CreateSchema, ItemBase):
    """아이템 생성 요청 스키마 (외부 → 시스템)"""

    pass


class ItemUpdate(UpdateSchema, ItemBase):
    """아이템 정보 업데이트 요청 스키마 (외부 → 시스템)"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=100, description="아이템 제목", exclude=True
    )


class ItemInDB(InternalSchema, ItemBase, TimeStampMixin):
    """데이터베이스 아이템 스키마 (시스템 내부용)"""

    id: int = Field(..., description="아이템 ID")
    owner_id: int = Field(..., description="소유자 ID")


class Item(ReadSchema, ItemBase, TimeStampMixin):
    """아이템 응답 스키마 (시스템 → 외부)"""

    id: int = Field(..., description="아이템 ID")
    owner_id: int = Field(..., description="소유자 ID")
