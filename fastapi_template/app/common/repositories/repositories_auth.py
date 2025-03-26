"""
# File: fastapi_template/app/common/repositories/repositories_auth.py
# Description: 인증 관련 리포지토리 클래스
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_template.app.db.models import Token, User
from fastapi_template.app.common.repositories.repositories_base import BaseRepository
from fastapi_template.app.db.schemas.token import TokenCreate, TokenUpdate


class AuthRepository(BaseRepository[Token, TokenCreate, TokenUpdate]):
    """인증 토큰 관리를 위한 리포지토리 클래스"""

    def __init__(self):
        super().__init__(Token)

    async def create_user_token(
        self, db: AsyncSession, *, user_id: Any, token_value: str, token_type: str, expires_at: datetime
    ) -> Token:
        """
        사용자 토큰을 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            token_value: 토큰 값
            token_type: 토큰 타입(access, refresh 등)
            expires_at: 만료 시간
            
        Returns:
            Token: 생성된 토큰
        """
        token_data = {
            "user_id": user_id,
            "token": token_value,
            "type": token_type,
            "expires_at": expires_at
        }
        return await self.create(db=db, obj_in=token_data)

    async def get_token_by_value(
        self, db: AsyncSession, *, token_value: str, token_type: Optional[str] = None
    ) -> Optional[Token]:
        """
        토큰 값으로 토큰을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            token_value: 토큰 값
            token_type: 토큰 타입(옵션)
            
        Returns:
            Optional[Token]: 조회된 토큰 또는 None
        """
        query = select(Token).where(Token.token == token_value)
        if token_type:
            query = query.where(Token.type == token_type)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_tokens(
        self, db: AsyncSession, *, user_id: Any, token_type: Optional[str] = None
    ) -> list[Token]:
        """
        사용자 ID로 토큰을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            token_type: 토큰 타입(옵션)
            
        Returns:
            list[Token]: 조회된 토큰 목록
        """
        if token_type:
            return await self.get_multi(db=db, user_id=user_id, type=token_type)
        return await self.get_multi(db=db, user_id=user_id)

    async def revoke_token(
        self, db: AsyncSession, *, token_value: str, token_type: Optional[str] = None
    ) -> Optional[Token]:
        """
        토큰을 삭제(취소)합니다.
        
        Args:
            db: 데이터베이스 세션
            token_value: 토큰 값
            token_type: 토큰 타입(옵션)
            
        Returns:
            Optional[Token]: 삭제된 토큰 또는 None
        """
        token = await self.get_token_by_value(db=db, token_value=token_value, token_type=token_type)
        if not token:
            return None
        return await self.delete(db=db, id=token.id)

    async def revoke_all_user_tokens(
        self, db: AsyncSession, *, user_id: Any, token_type: Optional[str] = None
    ) -> int:
        """
        사용자의 모든 토큰을 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            token_type: 토큰 타입(옵션)
            
        Returns:
            int: 삭제된 토큰 수
        """
        query = delete(Token).where(Token.user_id == user_id)
        if token_type:
            query = query.where(Token.type == token_type)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def clean_expired_tokens(self, db: AsyncSession) -> int:
        """
        만료된 토큰을 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            int: 삭제된 토큰 수
        """
        now = datetime.utcnow()
        query = delete(Token).where(Token.expires_at < now)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def is_token_valid(
        self, db: AsyncSession, *, token_value: str, token_type: Optional[str] = None
    ) -> bool:
        """
        토큰의 유효성을 검사합니다.
        
        Args:
            db: 데이터베이스 세션
            token_value: 토큰 값
            token_type: 토큰 타입(옵션)
            
        Returns:
            bool: 토큰 유효 여부
        """
        token = await self.get_token_by_value(db=db, token_value=token_value, token_type=token_type)
        if not token:
            return False
        return token.expires_at > datetime.utcnow()

    async def extend_token_expiry(
        self, db: AsyncSession, *, token_id: Any, extension_hours: int = 24
    ) -> Optional[Token]:
        """
        토큰의 만료 시간을 연장합니다.
        
        Args:
            db: 데이터베이스 세션
            token_id: 토큰 ID
            extension_hours: 연장할 시간(시간 단위)
            
        Returns:
            Optional[Token]: 업데이트된 토큰 또는 None
        """
        token = await self.get(db=db, id=token_id)
        if not token:
            return None
            
        # 현재 시간과 토큰 만료 시간 중 더 큰 값부터 연장
        now = datetime.utcnow()
        base_time = max(now, token.expires_at)
        token.expires_at = base_time + timedelta(hours=extension_hours)
        
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token 