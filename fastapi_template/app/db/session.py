"""
# File: fastapi_template/app/db/session.py
# Description: 호환성을 위한 세션 관리 함수 리다이렉트
"""

# common 모듈로 리다이렉트
from app.common.database import get_db, engine, async_engine, SessionLocal, AsyncSessionLocal

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 비동기 데이터베이스 URL (postgresql+asyncpg://)
ASYNC_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# 비동기 엔진 생성
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DB_ECHO_LOG
)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 동기 엔진 (마이그레이션 등의 용도)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    """비동기 데이터베이스 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
