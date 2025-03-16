"""
# File: fastapi_template/app/services/user_service.py
# Description: 사용자 관련 비즈니스 로직 구현
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate

class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        """사용자 ID로 사용자 조회"""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        """이메일로 사용자 조회"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        """새 사용자 생성"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            username=user.username,
            is_active=True
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        """사용자 인증"""
        user = await UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate):
        """사용자 정보 업데이트"""
        update_data = user_data.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        query = update(User).where(User.id == user_id).values(**update_data)
        await db.execute(query)
        await db.commit()
        
        return await UserService.get_user(db, user_id) 