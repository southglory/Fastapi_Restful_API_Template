"""
테스트 설정 모듈
"""
import pytest
import asyncio
import os
import sys
from unittest import mock
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 현재 경로를 시스템 경로에 추가
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 테스트 환경변수 설정
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DB_ECHO_LOG"] = "False"

# Mock 설정
sys.modules['fastapi_template.app.common.config.config_settings'] = mock.MagicMock(
    DATABASE_URL="sqlite+aiosqlite:///./test.db",
    DB_ECHO_LOG=False
)

@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio를 위한 이벤트 루프 고정"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db_engine():
    """테스트용 비동기 데이터베이스 엔진"""
    # 매 테스트마다 고유한 인메모리 DB 사용
    db_url = f"sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(db_url, echo=False)
    
    from fastapi_template.app.common.database.database_base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_db_engine):
    """테스트용 비동기 세션"""
    async_session = sessionmaker(
        test_db_engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
