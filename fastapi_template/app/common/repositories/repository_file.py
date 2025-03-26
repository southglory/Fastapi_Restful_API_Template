"""
# File: fastapi_template/app/common/repositories/repository_file.py
# Description: 파일 관련 리포지토리 클래스
"""

from typing import Any, Dict, List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_template.app.db.models import File
from fastapi_template.app.common.repositories.repositories_base import BaseRepository
from fastapi_template.app.db.schemas.file import FileCreate, FileUpdate


class FileRepository(BaseRepository[File, FileCreate, FileUpdate]):
    """파일 데이터 관리를 위한 리포지토리 클래스"""

    def __init__(self):
        super().__init__(File)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[File]:
        """
        파일명으로 파일을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            name: 파일명
            
        Returns:
            Optional[File]: 조회된 파일 또는 None
        """
        query = select(File).where(File.name == name)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_path(self, db: AsyncSession, path: str) -> Optional[File]:
        """
        경로로 파일을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            path: 파일 경로
            
        Returns:
            Optional[File]: 조회된 파일 또는 None
        """
        query = select(File).where(File.path == path)
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_user_id(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[File]:
        """
        사용자 ID로 파일을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            List[File]: 조회된 파일 목록
        """
        return await self.get_multi(db=db, skip=skip, limit=limit, user_id=user_id)
        
    async def get_by_type(
        self, db: AsyncSession, file_type: str, skip: int = 0, limit: int = 100
    ) -> List[File]:
        """
        파일 타입으로 파일을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            file_type: 파일 타입 (예: 'image', 'document', 'video')
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            List[File]: 조회된 파일 목록
        """
        return await self.get_multi(db=db, skip=skip, limit=limit, type=file_type)
        
    async def update_file_size(
        self, db: AsyncSession, *, file_id: int, size: int
    ) -> Optional[File]:
        """
        파일 크기를 업데이트합니다.
        
        Args:
            db: 데이터베이스 세션
            file_id: 파일 ID
            size: 파일 크기 (바이트)
            
        Returns:
            Optional[File]: 업데이트된 파일 또는 None
        """
        file = await self.get(db=db, id=file_id)
        if not file:
            return None
            
        file.size = size
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file 