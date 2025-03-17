"""
# File: fastapi_template/app/db/schemas/item.py
# Description: 아이템 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from app.common.schemas.base_schema import BaseSchema, TimeStampMixin

class ItemBase(BaseSchema):
    """아이템 기본 스키마"""
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    """아이템 생성 스키마"""
    pass

class ItemUpdate(ItemBase):
    """아이템 수정 스키마"""
    pass

class ItemInDB(ItemBase, TimeStampMixin):
    """데이터베이스 아이템 스키마"""
    id: int
    owner_id: int

class Item(ItemBase, TimeStampMixin):
    """아이템 응답 스키마"""
    id: int
    owner_id: int
