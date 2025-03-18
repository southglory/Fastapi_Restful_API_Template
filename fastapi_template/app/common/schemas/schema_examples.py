"""
# File: fastapi_template/app/common/schemas/schema_examples.py
# Description: 스키마 분류 체계 사용 예시
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field, EmailStr

from app.common.schemas.base_schema import (
    BaseSchema,
    CreateSchema,
    ReadSchema,
    UpdateSchema,
    ServiceSchema,
    EventSchema,
    TimeStampMixin,
)


# 사용자 스키마 예시
class UserCreateSchema(CreateSchema):
    """사용자 생성 요청 스키마"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserUpdateSchema(UpdateSchema):
    """사용자 정보 업데이트 요청 스키마"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserReadSchema(ReadSchema, TimeStampMixin):
    """사용자 정보 응답 스키마"""

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


# 서비스 계층 스키마 예시
class UserServiceSchema(ServiceSchema, TimeStampMixin):
    """사용자 서비스 내부 스키마"""

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    hashed_password: str  # 내부 처리용 필드
    login_attempts: int = 0
    last_login: Optional[datetime] = None
    permissions: List[str] = []


# 이벤트 메시지 예시
class UserCreatedEvent(EventSchema):
    """사용자 생성 이벤트"""

    event_type: str = "user.created"
    payload: Dict[str, Any]  # 사용자 ID, 이메일 등 포함


# 스키마 사용 예시 (의사 코드)
"""
# API 계층
@router.post("/users/", response_model=ResponseSchema[UserReadSchema])
async def create_user(user_data: UserCreateSchema):
    # 서비스 계층 호출
    user_service = UserService()
    new_user = await user_service.create_user(user_data)
    
    # 결과를 API 응답 스키마로 변환
    return ResponseSchema.success(
        data=UserReadSchema.model_validate(new_user),
        message="사용자가 성공적으로 생성되었습니다"
    )

# 서비스 계층
class UserService:
    async def create_user(self, user_data: UserCreateSchema) -> UserServiceSchema:
        # 비즈니스 로직 처리 (해시 비밀번호 등)
        hashed_password = hash_password(user_data.password)
        
        # 데이터베이스 저장
        db_user = await repository.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        # 서비스 스키마로 변환
        user_service_data = UserServiceSchema.model_validate(db_user)
        
        # 이벤트 발행
        event = UserCreatedEvent(
            timestamp=datetime.now(),
            payload={
                "user_id": user_service_data.id,
                "username": user_service_data.username,
                "email": user_service_data.email
            }
        )
        await event_publisher.publish(event)
        
        return user_service_data
"""
