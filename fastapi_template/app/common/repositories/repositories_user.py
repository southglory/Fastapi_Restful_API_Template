"""
# File: fastapi_template/app/common/repositories/repositories_user.py
# Description: 사용자 관련 리포지토리 클래스
"""

from typing import Any, Dict, List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_template.app.db.models import User
from fastapi_template.app.common.repositories.repositories_base import BaseRepository
from fastapi_template.app.db.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """사용자 데이터 관리를 위한 리포지토리 클래스"""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        이메일로 사용자를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            email: 사용자 이메일
            
        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        사용자명으로 사용자를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            username: 사용자명
            
        Returns:
            Optional[User]: 조회된 사용자 또는 None
        """
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first()

    async def create_with_password(
        self, db: AsyncSession, *, obj_in: UserCreate, hashed_password: str
    ) -> User:
        """
        해시된 비밀번호로 사용자를 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 사용자 데이터
            hashed_password: 해시된 비밀번호
            
        Returns:
            User: 생성된 사용자
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_last_login(self, db: AsyncSession, *, user_id: Any) -> Optional[User]:
        """
        사용자의 마지막 로그인 시간을 업데이트합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            Optional[User]: 업데이트된 사용자 또는 None
        """
        from datetime import datetime
        
        user = await self.get(db=db, id=user_id)
        if not user:
            return None
            
        user.last_login = datetime.utcnow()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        이메일과 비밀번호로 사용자를 인증합니다.
        
        Args:
            db: 데이터베이스 세션
            email: 사용자 이메일
            password: 평문 비밀번호
            
        Returns:
            Optional[User]: 인증된 사용자 또는 None
        """
        from fastapi_template.app.core.security import verify_password
        
        user = await self.get_by_email(db=db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def change_password(
        self, db: AsyncSession, *, user_id: Any, new_hashed_password: str
    ) -> Optional[User]:
        """
        사용자의 비밀번호를 변경합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            new_hashed_password: 새 해시된 비밀번호
            
        Returns:
            Optional[User]: 업데이트된 사용자 또는 None
        """
        user = await self.get(db=db, id=user_id)
        if not user:
            return None
            
        user.hashed_password = new_hashed_password
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def is_active(self, user: User) -> bool:
        """
        사용자가 활성 상태인지 확인합니다.
        
        Args:
            user: 사용자 객체
            
        Returns:
            bool: 활성 상태 여부
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        사용자가 슈퍼유저인지 확인합니다.
        
        Args:
            user: 사용자 객체
            
        Returns:
            bool: 슈퍼유저 여부
        """
        return user.is_superuser

    async def get_active_users(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        활성 상태인 사용자만 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            List[User]: 활성 사용자 목록
        """
        return await self.get_multi(db=db, skip=skip, limit=limit, is_active=True) 