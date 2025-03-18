"""
# File: fastapi_template/app/api/routes/users.py
# Description: 사용자 관련 CRUD API 엔드포인트 정의
# - 사용자 생성, 조회, 수정, 삭제 기능
# - 사용자 인증 및 권한 검증
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.common.database import get_db
from app.common.exceptions import NotFoundError
from app.common.utils.pagination import PaginationParams, PaginatedResponse
from app.common.utils import get_python_value
from app.db.models.user import User
from app.db.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user


@router.patch("/me", response_model=UserSchema)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    현재 로그인한 사용자 정보 수정
    """
    user_id = get_python_value(current_user.id)
    updated_user = await UserService.update_user(db, user_id, user_update)
    return updated_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    특정 ID의 사용자 정보 조회
    """
    # 관리자이거나 자신의 정보를 조회하는 경우에만 허용
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = await UserService.get_user(db, user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    return user


@router.get("/", response_model=PaginatedResponse[UserSchema])
async def read_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    사용자 목록 조회 (관리자 전용)
    """
    # 여기서는 간단한 구현이지만, 실제로는 더 복잡한 필터링 로직이 필요할 수 있음
    # 예: 이름 검색, 등록일 필터링 등
    users = await db.execute(
        select(User).offset(pagination.skip).limit(pagination.page_size)
    )
    users_list = users.scalars().all()

    total_count = await db.execute(select(func.count()).select_from(User))
    total_items = total_count.scalar()

    return PaginatedResponse.create(
        items=list(users_list), total_items=total_items or 0, params=pagination
    )


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    새 사용자 생성 (관리자 전용)
    """
    # 이메일 중복 체크
    user = await UserService.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return await UserService.create_user(db, user_in)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    사용자 정보 업데이트 (관리자 전용)
    """
    return await UserService.update_user(db, user_id, user_in)
