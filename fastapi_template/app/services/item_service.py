"""
# File: fastapi_template/app/services/item_service.py
# Description: 아이템 관련 비즈니스 로직 구현
# - 아이템 CRUD 작업 처리
# - 아이템 권한 검증
# - 아이템 필터링 및 정렬
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.common.exceptions import NotFoundError
from app.db.models.item import Item
from app.db.schemas.item import ItemCreate, ItemUpdate

class ItemService:
    @staticmethod
    async def get_item(db: AsyncSession, item_id: int):
        """ID로 아이템 조회"""
        result = await db.execute(select(Item).filter(Item.id == item_id))
        return result.scalars().first()

    @staticmethod
    async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
        """아이템 목록 조회"""
        result = await db.execute(select(Item).offset(skip).limit(limit))
        return result.scalars().all()
        
    @staticmethod
    async def get_user_items(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
        """특정 사용자의 아이템 목록 조회"""
        result = await db.execute(
            select(Item).filter(Item.owner_id == user_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create_item(db: AsyncSession, item: ItemCreate, owner_id: int):
        """새 아이템 생성"""
        db_item = Item(**item.dict(), owner_id=owner_id)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def update_item(db: AsyncSession, item_id: int, item: ItemUpdate):
        """아이템 정보 업데이트"""
        update_data = item.dict(exclude_unset=True)
        
        query = update(Item).where(Item.id == item_id).values(**update_data)
        result = await db.execute(query)
        await db.commit()
        
        if result.rowcount == 0:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        return await ItemService.get_item(db, item_id)

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int):
        """아이템 삭제"""
        query = delete(Item).where(Item.id == item_id)
        result = await db.execute(query)
        await db.commit()
        
        if result.rowcount == 0:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        return True 