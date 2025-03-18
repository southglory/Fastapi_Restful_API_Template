# 스키마 정의

이 문서는 FastAPI 프로젝트에서 Pydantic을 사용한 스키마 정의 방법을 설명합니다.

## 목차

1. [스키마 소개](#스키마-소개)
2. [기본 스키마 클래스](#기본-스키마-클래스)
3. [사용자 스키마](#사용자-스키마)
4. [아이템 스키마](#아이템-스키마)
5. [응답 모델 사용](#응답-모델-사용)

## 스키마 소개

FastAPI에서는 Pydantic 모델을 사용하여 데이터 검증, 직렬화 및 문서화를 처리합니다. 이러한 모델을 "스키마"라고 부릅니다.

스키마는 다음과 같은 용도로 사용됩니다:
- 요청 본문 검증
- 응답 데이터 직렬화
- API 문서 자동 생성
- 데이터베이스 모델과 API 계층 간의 데이터 변환

## 기본 스키마 클래스

`app/common/schemas/base.py`에 기본 스키마 클래스를 정의합니다:

```python
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    모든 스키마의 기본 클래스
    """
    model_config = ConfigDict(
        from_attributes=True,  # ORM 모델 인스턴스에서 데이터 읽기 허용
        populate_by_name=True  # 별칭 필드 지원
    )


class BaseIDSchema(BaseSchema):
    """
    ID 필드를 포함한 기본 스키마
    """
    id: int


class BaseTimeStampSchema(BaseSchema):
    """
    타임스탬프 필드를 포함한 기본 스키마
    """
    created_at: datetime
    updated_at: datetime


class BaseModelSchema(BaseIDSchema, BaseTimeStampSchema):
    """
    ID와 타임스탬프를 포함한 완전한 기본 모델 스키마
    """
    pass
```

## 사용자 스키마

`app/db/schemas/user.py`에 사용자 관련 스키마를 정의합니다:

```python
from typing import List, Optional

from pydantic import EmailStr, Field

from app.common.schemas.base import BaseModelSchema, BaseSchema
from app.db.schemas.item import ItemResponse


class UserBase(BaseSchema):
    """
    사용자 기본 스키마
    """
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """
    사용자 생성 스키마
    """
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """
    사용자 업데이트 스키마
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(BaseModelSchema, UserBase):
    """
    사용자 응답 스키마
    """
    pass


class UserDetailResponse(UserResponse):
    """
    사용자 상세 응답 스키마 (아이템 포함)
    """
    items: List[ItemResponse] = []
```

## 아이템 스키마

`app/db/schemas/item.py`에 아이템 관련 스키마를 정의합니다:

```python
from typing import Optional

from app.common.schemas.base import BaseModelSchema, BaseSchema


class ItemBase(BaseSchema):
    """
    아이템 기본 스키마
    """
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """
    아이템 생성 스키마
    """
    pass


class ItemUpdate(BaseSchema):
    """
    아이템 업데이트 스키마
    """
    title: Optional[str] = None
    description: Optional[str] = None


class ItemResponse(BaseModelSchema, ItemBase):
    """
    아이템 응답 스키마
    """
    owner_id: int
```

## 응답 모델 사용

FastAPI 라우터에서 응답 모델을 사용하는 방법:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database.session import get_db
from app.db.schemas.user import UserCreate, UserResponse
from app.services.user import user_service

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새 사용자 생성
    """
    user = await user_service.create_user(db, user_in)
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 정보 조회
    """
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 스키마 변환 예시

SQLAlchemy 모델과 Pydantic 스키마 간의 변환:

```python
# SQLAlchemy 모델 -> Pydantic 스키마
user_db = await user_service.get_user(db, user_id)
user_schema = UserResponse.model_validate(user_db)

# Pydantic 스키마 -> SQLAlchemy 모델
user_in = UserCreate(email="user@example.com", password="password123")
user_db = User(
    email=user_in.email,
    hashed_password=get_password_hash(user_in.password),
    full_name=user_in.full_name
)
```

## 다음 단계

다음 문서에서는 [서비스 레이어](./05-services.md)에 대해 알아보겠습니다. 