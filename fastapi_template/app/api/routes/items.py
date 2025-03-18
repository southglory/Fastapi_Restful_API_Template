"""
# File: fastapi_template/app/api/routes/items.py
# Description: 아이템 관련 CRUD API 엔드포인트 정의
# - 아이템 생성, 조회, 수정, 삭제 기능
# - 아이템 목록 조회 및 필터링
# - 권한 기반 아이템 접근 제어
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.api.dependencies import get_current_active_user
from app.common.database import get_db
from app.common.exceptions import NotFoundError, PermissionDeniedError
from app.common.utils.pagination import PaginationParams, PaginatedResponse
from app.common.utils import get_python_value
from app.db.models.user import User
from app.db.models.item import Item
from app.db.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter()


@router.get("/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    특정 ID의 아이템 조회
    """
    item = await ItemService.get_item(db, item_id)
    if not item:
        raise NotFoundError(f"Item with ID {item_id} not found")

    # 본인의 아이템이 아니고 관리자도 아니면 접근 거부
    if item.owner_id != current_user.id and not current_user.is_admin:
        raise PermissionDeniedError("Not enough permissions")

    return item


@router.get("/", response_model=PaginatedResponse[ItemSchema])
async def list_items(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    아이템 목록 조회
    - 관리자: 모든 아이템 조회 가능
    - 일반 사용자: 본인의 아이템만 조회 가능
    """
    # 관리자는 모든 아이템 조회 가능
    if current_user.is_admin:
        items = await ItemService.get_items(
            db, skip=pagination.skip, limit=pagination.page_size
        )
        total_count = await db.execute(select(func.count()).select_from(Item))
    else:
        # 일반 사용자는 본인의 아이템만 조회 가능
        user_id = get_python_value(current_user.id)

        items = await ItemService.get_user_items(
            db, user_id, skip=pagination.skip, limit=pagination.page_size
        )
        total_count = await db.execute(
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )

    total_items = total_count.scalar()

    return PaginatedResponse.create(
        items=list(items), total_items=total_items or 0, params=pagination
    )


@router.post("/", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    새 아이템 생성
    """
    owner_id = get_python_value(current_user.id)
    return await ItemService.create_item(db, item, owner_id=owner_id)


@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    아이템 정보 업데이트
    """
    current_item = await ItemService.get_item(db, item_id)
    if not current_item:
        raise NotFoundError(f"Item with ID {item_id} not found")

    # 본인의 아이템이 아니고 관리자도 아니면 접근 거부
    if current_item.owner_id != current_user.id and not current_user.is_admin:
        raise PermissionDeniedError("Not enough permissions")

    return await ItemService.update_item(db, item_id, item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    아이템 삭제
    """
    current_item = await ItemService.get_item(db, item_id)
    if not current_item:
        raise NotFoundError(f"Item with ID {item_id} not found")

    # 본인의 아이템이 아니고 관리자도 아니면 접근 거부
    if current_item.owner_id != current_user.id and not current_user.is_admin:
        raise PermissionDeniedError("Not enough permissions")

    await ItemService.delete_item(db, item_id)
