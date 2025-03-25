import pytest
import sys
import uuid
from unittest import mock
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text, Column, Integer, String

# mock 설정을 사용하도록 설정
sys.modules['fastapi_template.app.common.config.config_settings'] = mock.MagicMock(
    DATABASE_URL="sqlite+aiosqlite:///./test.db",
    DB_ECHO_LOG=False
)

# 상대 경로로 import
from fastapi_template.app.common.database.database_base import Base

@pytest.fixture
async def test_engine():
    """테스트용 데이터베이스 엔진 생성"""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest.mark.asyncio
async def test_base_metadata(test_engine):
    """Base 메타데이터 테스트"""
    assert Base.metadata is not None
    
@pytest.mark.asyncio
async def test_database_connection(test_engine):
    """데이터베이스 연결 테스트"""
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result is not None
        row = result.first()
        assert row[0] == 1

@pytest.mark.asyncio
async def test_database_transaction(test_engine):
    """트랜잭션 테스트"""
    table_name = f"test_{uuid.uuid4().hex[:8]}"
    async with test_engine.begin() as conn:
        await conn.execute(text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY)"))
        await conn.execute(text(f"INSERT INTO {table_name} (id) VALUES (1)"))
    
    async with test_engine.connect() as conn:
        result = await conn.execute(text(f"SELECT * FROM {table_name}"))
        row = result.first()
        assert row[0] == 1

@pytest.mark.asyncio
async def test_tablename_generation():
    """__tablename__ 메서드 테스트"""
    # 테스트용 모델 클래스 정의
    class TestModel(Base):
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    # 테이블명이 클래스명의 소문자 형태로 생성되는지 확인
    assert TestModel.__tablename__ == 'testmodel' 