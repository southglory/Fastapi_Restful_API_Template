"""
# File: fastapi_template/app/db/schemas/item.py
# Description: 아이템 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
