"""
# File: fastapi_template/app/db/schemas/__init__.py
# Description: Pydantic 스키마 패키지 초기화
# - 모든 스키마 클래스 export
# - 사용자, 아이템, 토큰 관련 스키마
"""

# 사용자 관련 스키마
from app.db.schemas.user import (
    User,  # 사용자 응답 스키마 (ReadSchema)
    UserCreate,  # 사용자 생성 스키마 (CreateSchema)
    UserUpdate,  # 사용자 수정 스키마 (UpdateSchema)
    UserInDB,  # 내부용 사용자 스키마 (InternalSchema)
)

# 아이템 관련 스키마
from app.db.schemas.item import (
    Item,  # 아이템 응답 스키마 (ReadSchema)
    ItemCreate,  # 아이템 생성 스키마 (CreateSchema)
    ItemUpdate,  # 아이템 수정 스키마 (UpdateSchema)
    ItemInDB,  # 내부용 아이템 스키마 (InternalSchema)
)

# 토큰 관련 스키마
from app.db.schemas.token import (
    Token,  # 토큰 응답 스키마 (OutputSchema)
    TokenPayload,  # 내부용 토큰 페이로드 스키마 (InternalSchema)
)

__all__ = [
    # 사용자 스키마
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # 아이템 스키마
    "Item",
    "ItemCreate",
    "ItemUpdate",
    "ItemInDB",
    # 토큰 스키마
    "Token",
    "TokenPayload",
]
