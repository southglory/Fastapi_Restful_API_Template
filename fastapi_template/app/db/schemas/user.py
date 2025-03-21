"""
# File: fastapi_template/app/db/schemas/user.py
# Description: 사용자 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from pydantic import EmailStr, Field
from typing import Optional

from app.common.schemas.base_schema import (
    CreateSchema,
    ReadSchema,
    UpdateSchema,
    InternalSchema,
    TimeStampMixin,
    BaseSchema,
)


# 사용자 공통 속성
class UserBase(BaseSchema):
    """사용자 공통 속성"""

    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자 이름")
    is_active: bool = Field(True, description="계정 활성화 상태")
    is_admin: bool = Field(False, description="관리자 권한 여부")


class UserCreate(CreateSchema, UserBase):
    """사용자 생성 요청 스키마 (외부 → 시스템)"""

    password: str = Field(..., min_length=8, description="사용자 비밀번호")


class UserUpdate(UpdateSchema, UserBase):
    """사용자 정보 업데이트 요청 스키마 (외부 → 시스템)"""

    email: Optional[EmailStr] = Field(None, description="사용자 이메일", exclude=True)
    username: Optional[str] = Field(None, description="사용자 이름", exclude=True)
    password: Optional[str] = Field(None, min_length=8, description="사용자 비밀번호")
    is_active: Optional[bool] = Field(
        None, description="계정 활성화 상태", exclude=True
    )
    is_admin: Optional[bool] = Field(None, description="관리자 권한 여부", exclude=True)


class UserInDB(InternalSchema, UserBase, TimeStampMixin):
    """데이터베이스 사용자 스키마 (시스템 내부용)"""

    id: int = Field(..., description="사용자 ID")
    hashed_password: str = Field(..., description="해시된 비밀번호")


class User(ReadSchema, UserBase, TimeStampMixin):
    """사용자 응답 스키마 (시스템 → 외부)"""

    id: int = Field(..., description="사용자 ID")
