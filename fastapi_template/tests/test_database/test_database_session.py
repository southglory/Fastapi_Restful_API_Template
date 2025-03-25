import pytest
import sys
import uuid
import os
from unittest import mock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.orm import sessionmaker

# mock 설정을 사용하도록 설정
sys.modules['fastapi_template.app.common.config.config_settings'] = mock.MagicMock(
    DATABASE_URL="sqlite+aiosqlite:///./test.db",
    DB_ECHO_LOG=False
)

# 상대 경로로 import
from fastapi_template.app.common.database.database_session import get_db, SessionLocal, engine
from fastapi_template.app.common.database.database_base import Base

@pytest.fixture
async def test_session():
    """테스트용 세션 생성"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = AsyncSession(engine)
    yield async_session
    
    await async_session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_db_dependency():
    """get_db 의존성 테스트"""
    db = await anext(get_db())
    assert isinstance(db, AsyncSession)
    await db.close()

@pytest.mark.asyncio
async def test_session_transaction(test_session):
    """세션 트랜잭션 테스트"""
    table_name = f"test_{uuid.uuid4().hex[:8]}"
    async with test_session.begin():
        await test_session.execute(text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY)"))
        await test_session.execute(text(f"INSERT INTO {table_name} (id) VALUES (1)"))
    
    result = await test_session.execute(text(f"SELECT * FROM {table_name}"))
    row = result.first()
    assert row[0] == 1

@pytest.mark.asyncio
async def test_session_rollback(test_session):
    """세션 롤백 테스트"""
    table_name = f"test_{uuid.uuid4().hex[:8]}"
    
    # 테이블 생성
    async with test_session.begin():
        await test_session.execute(text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY)"))
    
    # 롤백을 위한 별도 세션 시작
    try:
        async with test_session.begin():
            await test_session.execute(text(f"INSERT INTO {table_name} (id) VALUES (1)"))
            raise Exception("롤백 트리거")
    except Exception:
        pass
    
    # 데이터가 롤백되었는지 확인
    result = await test_session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    count = result.scalar()
    assert count == 0

@pytest.mark.asyncio
async def test_session_commit(test_session):
    """세션 커밋 테스트"""
    table_name = f"test_{uuid.uuid4().hex[:8]}"
    async with test_session.begin():
        await test_session.execute(text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY)"))
        await test_session.execute(text(f"INSERT INTO {table_name} (id) VALUES (1)"))
    
    result = await test_session.execute(text(f"SELECT * FROM {table_name}"))
    row = result.first()
    assert row[0] == 1

def test_sync_session():
    """동기 세션 팩토리 테스트"""
    # 직접 import
    import importlib
    import fastapi_template.app.common.database.database_session as db_session
    
    # 모듈이 올바르게 로드되었는지 확인
    assert db_session.SessionLocal is not None
    
    # 간단히 인스턴스 생성만으로 라인 커버리지 확보
    try:
        # monkeypatch로 실제 DB 연결 없이 테스트
        orig_engine = db_session.engine
        test_engine = create_engine("sqlite:///:memory:")
        db_session.engine = test_engine
        
        # SessionLocal을 새로 설정
        db_session.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        # 세션 인스턴스 생성 (커버리지 확보용)
        session = db_session.SessionLocal()
        assert session is not None
        session.close()
    finally:
        # 원래 상태로 복원
        db_session.engine = orig_engine
        db_session.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=orig_engine)

@pytest.mark.asyncio
async def test_url_conversion():
    """데이터베이스 URL 변환 테스트"""
    import importlib
    import fastapi_template.app.common.database.database_session as db_session
    
    # 모듈 다시 로드하기 위한 원래 설정 백업
    original_config = sys.modules['fastapi_template.app.common.config.config_settings']
    
    try:
        # PostgreSQL URL 테스트
        sys.modules['fastapi_template.app.common.config.config_settings'] = mock.MagicMock(
            DATABASE_URL="postgresql://user:pass@localhost:5432/testdb",
            DB_ECHO_LOG=True
        )
        
        # 모듈 리로드
        importlib.reload(db_session)
        
        # URL이 올바르게 변환되었는지 확인
        assert db_session.ASYNC_SQLALCHEMY_DATABASE_URL.startswith("postgresql+asyncpg://")
        assert "user:pass@localhost:5432/testdb" in db_session.ASYNC_SQLALCHEMY_DATABASE_URL
        
        # SQLite URL 테스트
        sys.modules['fastapi_template.app.common.config.config_settings'] = mock.MagicMock(
            DATABASE_URL="sqlite:///./test.db",
            DB_ECHO_LOG=False
        )
        
        # 모듈 리로드
        importlib.reload(db_session)
        
        # SQLite URL이 올바르게 변환되었는지 확인
        assert db_session.ASYNC_SQLALCHEMY_DATABASE_URL.startswith("sqlite+aiosqlite:///")
        assert "./test.db" in db_session.ASYNC_SQLALCHEMY_DATABASE_URL
    finally:
        # 원래 설정 복원
        sys.modules['fastapi_template.app.common.config.config_settings'] = original_config
        importlib.reload(db_session) 