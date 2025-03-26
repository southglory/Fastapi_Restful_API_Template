"""
# File: fastapi_template/app/common/repositories/repositories_base.py
# Description: 기본 데이터베이스 리포지토리 클래스
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from fastapi_template.app.db.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    기본 리포지토리 클래스 - CRUD 작업 구현
    """

    def __init__(self, model: Type[ModelType]):
        """
        모델 클래스를 인자로 받아 초기화합니다.
        
        Args:
            model: SQLAlchemy 모델 클래스
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        ID로 데이터를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            id: 조회할 데이터의 ID
            
        Returns:
            Optional[ModelType]: 조회된 데이터 또는 None
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> List[ModelType]:
        """
        여러 데이터를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            **kwargs: 필터링 조건 (필드명=값)
            
        Returns:
            List[ModelType]: 조회된 데이터 목록
        """
        query = self._build_query(**kwargs)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        새 데이터를 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 데이터 (Pydantic 모델 또는 딕셔너리)
            
        Returns:
            ModelType: 생성된 데이터
        """
        obj_in_data = obj_in.dict() if isinstance(obj_in, BaseModel) else obj_in
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
        데이터를 수정합니다.
        
        Args:
            db: 데이터베이스 세션
            db_obj: 수정할 기존 데이터
            obj_in: 수정할 내용 (Pydantic 모델 또는 딕셔너리)
            
        Returns:
            ModelType: 수정된 데이터
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, BaseModel):
            # Pydantic 모델의 수정할 값만 필터링
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        데이터를 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            id: 삭제할 데이터의 ID
            
        Returns:
            Optional[ModelType]: 삭제된 데이터 또는 None
        """
        obj = await self.get(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    def _build_query(self, **kwargs) -> Select:
        """
        필터링 조건으로 쿼리를 생성합니다.
        
        Args:
            **kwargs: 필터링 조건 (필드명=값)
            
        Returns:
            Select: 생성된 쿼리 객체
        """
        query = select(self.model)
        for field, value in kwargs.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)
        return query

    async def bulk_create(
        self, db: AsyncSession, *, obj_in_list: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """
        여러 데이터를 한 번에 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            obj_in_list: 생성할 데이터 목록
            
        Returns:
            List[ModelType]: 생성된 데이터 목록
        """
        db_objs = []
        for obj_in in obj_in_list:
            obj_in_data = obj_in.dict() if isinstance(obj_in, BaseModel) else obj_in
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db_objs.append(db_obj)

        await db.commit()
        for db_obj in db_objs:
            await db.refresh(db_obj)
        return db_objs

    async def bulk_update(
        self, db: AsyncSession, *, ids: List[Any], obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> int:
        """
        여러 데이터를 한 번에 수정합니다.
        
        Args:
            db: 데이터베이스 세션
            ids: 수정할 데이터의 ID 목록
            obj_in: 수정할 내용
            
        Returns:
            int: 수정된 레코드 수
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in

        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**update_data)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def bulk_delete(self, db: AsyncSession, *, ids: List[Any]) -> int:
        """
        여러 데이터를 한 번에 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            ids: 삭제할 데이터의 ID 목록
            
        Returns:
            int: 삭제된 레코드 수
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def count(self, db: AsyncSession, **kwargs) -> int:
        """
        조건에 맞는 레코드 수를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            **kwargs: 필터링 조건
            
        Returns:
            int: 레코드 수
        """
        from sqlalchemy import func
        
        query = select(func.count()).select_from(self.model)
        for field, value in kwargs.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)
                
        result = await db.execute(query)
        return result.scalar_one() 