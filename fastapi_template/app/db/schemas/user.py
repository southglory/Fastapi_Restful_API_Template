"""
# File: fastapi_template/app/db/schemas/user.py
# Description: 사용자 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from pydantic import EmailStr

from app.common.schemas.base_schema import BaseSchema, TimeStampMixin

class UserBase(BaseSchema):
    """사용자 기본 스키마"""
    email: EmailStr
    username: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str

class UserUpdate(UserBase):
    """사용자 수정 스키마"""
    password: str | None = None

class UserInDB(UserBase, TimeStampMixin):
    """데이터베이스 사용자 스키마"""
    id: int
    hashed_password: str

class User(UserBase, TimeStampMixin):
    """사용자 응답 스키마"""
    id: int


