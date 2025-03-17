# 서비스 레이어

이 문서는 FastAPI 프로젝트에서 서비스 레이어 구현 방법을 설명합니다.

## 목차

1. [서비스 레이어 소개](#서비스-레이어-소개)
2. [기본 서비스 클래스](#기본-서비스-클래스)
3. [사용자 서비스](#사용자-서비스)
4. [아이템 서비스](#아이템-서비스)
5. [의존성 주입](#의존성-주입)

## 서비스 레이어 소개

서비스 레이어는 비즈니스 로직을 처리하는 계층으로, 다음과 같은 역할을 합니다:

- 데이터베이스 작업 추상화
- 비즈니스 로직 구현
- 라우터와 데이터베이스 모델 간의 중간 계층
- 코드 재사용성 향상

서비스 레이어를 사용하면 라우터는 HTTP 요청 처리에만 집중하고, 데이터베이스 작업과 비즈니스 로직은 서비스 레이어에서 처리할 수 있습니다.

## 기본 서비스 클래스

`app/services/base.py`에 기본 서비스 클래스를 정의합니다:

```python
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database.base import BaseModel as DBBaseModel

ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD 작업을 위한 기본 서비스 클래스
    """
    def __init__(self, model: Type[ModelType]):
        """
        모델 클래스를 매개변수로 받는 생성자
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        ID로 객체 조회
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        여러 객체 조회
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        새 객체 생성
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        객체 업데이트
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        """
        객체 삭제
        """
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()
        return obj
```

## 사용자 서비스

`app/services/user.py`에 사용자 서비스를 구현합니다:

```python
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.security.password import get_password_hash, verify_password
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    사용자 관련 서비스
    """
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        새 사용자 생성 (비밀번호 해싱 포함)
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        사용자 인증
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """
        사용자 활성화 상태 확인
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        관리자 권한 확인
        """
        return user.is_superuser


# 싱글톤 인스턴스 생성
user_service = UserService(User)
```

## 아이템 서비스

`app/services/item.py`에 아이템 서비스를 구현합니다:

```python
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.item import Item
from app.db.schemas.item import ItemCreate, ItemUpdate
from app.services.base import BaseService


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """
    아이템 관련 서비스
    """
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        """
        소유자 ID와 함께 아이템 생성
        """
        obj_in_data = obj_in.model_dump()
        db_obj = Item(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        """
        소유자 ID로 아이템 목록 조회
        """
        query = select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# 싱글톤 인스턴스 생성
item_service = ItemService(Item)
```

## 의존성 주입

FastAPI 라우터에서 서비스 레이어를 사용하는 방법:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database.session import get_db
from app.common.security.auth import get_current_active_user
from app.db.models.user import User
from app.db.schemas.item import ItemCreate, ItemResponse
from app.services.item import item_service

router = APIRouter()


@router.post("/items/", response_model=ItemResponse)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    현재 로그인한 사용자의 아이템 생성
    """
    item = await item_service.create_with_owner(
        db=db, obj_in=item_in, owner_id=current_user.id
    )
    return item


@router.get("/items/", response_model=list[ItemResponse])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    현재 로그인한 사용자의 아이템 목록 조회
    """
    items = await item_service.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return items
```

## 서비스 레이어의 장점

1. **관심사 분리**: 비즈니스 로직과 HTTP 요청 처리를 분리
2. **코드 재사용**: 여러 라우터에서 동일한 서비스 로직 사용 가능
3. **테스트 용이성**: 서비스 레이어만 독립적으로 테스트 가능
4. **유지보수성**: 비즈니스 로직 변경 시 라우터 코드 수정 불필요

## 다음 단계

다음 문서에서는 [Docker 환경 설정](./06-docker.md)에 대해 알아보겠습니다.
