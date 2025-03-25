"""
# File: fastapi_template/app/common/database/database_session.py
# Description: 데이터베이스 세션 관리
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from fastapi_template.app.common.config import config_settings

# 비동기 데이터베이스 URL 처리
# SQLite와 PostgreSQL 모두 지원
ASYNC_SQLALCHEMY_DATABASE_URL = config_settings.DATABASE_URL
if ASYNC_SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    ASYNC_SQLALCHEMY_DATABASE_URL = ASYNC_SQLALCHEMY_DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
elif ASYNC_SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    # SQLite는 asyncio 지원을 위해 aiosqlite 드라이버 사용
    ASYNC_SQLALCHEMY_DATABASE_URL = ASYNC_SQLALCHEMY_DATABASE_URL.replace(
        "sqlite:///", "sqlite+aiosqlite:///"
    )

# 비동기 엔진 생성
async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=config_settings.DB_ECHO_LOG
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)

# 동기 엔진 (마이그레이션 등의 용도)
engine = create_engine(config_settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 데이터베이스 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
