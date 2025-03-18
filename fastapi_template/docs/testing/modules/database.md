# Database 모듈 테스트 가이드

## 개요

`database` 모듈은 애플리케이션의 데이터베이스 연결, 세션 관리, 모델 정의 등 데이터 영속성과 관련된 기능을 제공합니다. 이 모듈은 SQLAlchemy를 사용하여 관계형 데이터베이스와 상호작용하며, 비동기 쿼리와 트랜잭션을 지원합니다.

## 테스트 용이성

- **난이도**: 어려움
- **이유**:
  - 실제 데이터베이스나 테스트용 인메모리 DB 설정 필요
  - 트랜잭션, 롤백 등 복잡한 동작 테스트가 필요함
  - 비동기 ORM 코드로 인해 테스트 복잡도가 높음
  - 데이터베이스 스키마 변경, 마이그레이션 테스트의 어려움

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **데이터베이스 연결 관리**
   - 연결 풀 생성 및 관리
   - 세션 팩토리 설정
   - 비동기 세션 컨텍스트 관리

2. **모델 및 스키마**
   - ORM 모델 정의 및 관계
   - 모델 인스턴스 생성 및 검증
   - 스키마 변환 기능

3. **데이터베이스 작업**
   - CRUD 작업 (생성, 조회, 업데이트, 삭제)
   - 쿼리 빌더 및 필터
   - 관계 로드 및 조인
   - 트랜잭션 및 롤백

## 테스트 접근법

Database 모듈 테스트 시 다음 접근법을 권장합니다:

1. **인메모리 데이터베이스 사용**: SQLite 인메모리 데이터베이스를 사용하여 빠르고 격리된 테스트 환경 구성
2. **픽스처 기반 테스트**: 테스트 데이터를 픽스처로 정의하여 재사용
3. **트랜잭션 범위 테스트**: 각 테스트는 트랜잭션 내에서 실행하고 테스트 후 롤백
4. **팩토리 패턴**: 테스트용 모델 인스턴스를 생성하는 팩토리 함수 활용

## 테스트 예시

### 데이터베이스 연결 테스트

```python
# tests/test_db/test_session.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.database.session import get_session, engine, Base

# 테스트용 데이터베이스 설정
@pytest.fixture(scope="module")
async def setup_database():
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # 테이블 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with get_session() as session:
        # 트랜잭션 시작
        transaction = await session.begin()
        yield session
        # 테스트 후 롤백
        await transaction.rollback()

@pytest.mark.asyncio
async def test_get_session(setup_database, db_session):
    # 세션 인스턴스 확인
    assert isinstance(db_session, AsyncSession)
    
    # 활성 상태 확인
    assert not db_session.closed
    
    # 트랜잭션 활성 상태 확인
    assert db_session.in_transaction()
```

### 모델 인스턴스 생성 및 CRUD 테스트

```python
# tests/test_db/test_models.py
import pytest
from datetime import datetime
from app.db.models.user import User
from app.db.models.item import Item

# 사용자 팩토리 함수
async def create_test_user(session, **kwargs):
    # 기본값과 오버라이드된 값 합치기
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "hashed_password": "hashed_test_password"
    }
    user_data.update(kwargs)
    
    # 사용자 객체 생성
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_create_user(setup_database, db_session):
    # 사용자 생성
    user = await create_test_user(db_session)
    
    # 사용자 ID가 할당되었는지 확인
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    
    # 생성 시간이 설정되었는지 확인
    assert isinstance(user.created_at, datetime)

@pytest.mark.asyncio
async def test_update_user(setup_database, db_session):
    # 사용자 생성
    user = await create_test_user(db_session)
    
    # 사용자 업데이트
    user.username = "updated_username"
    await db_session.commit()
    await db_session.refresh(user)
    
    # 변경사항 확인
    assert user.username == "updated_username"
    
    # 데이터베이스에서 다시 조회하여 확인
    fetched_user = await db_session.get(User, user.id)
    assert fetched_user.username == "updated_username"

@pytest.mark.asyncio
async def test_delete_user(setup_database, db_session):
    # 사용자 생성
    user = await create_test_user(db_session)
    user_id = user.id
    
    # 사용자 삭제
    await db_session.delete(user)
    await db_session.commit()
    
    # 삭제 확인
    deleted_user = await db_session.get(User, user_id)
    assert deleted_user is None
```

### 관계 테스트

```python
# tests/test_db/test_relationships.py
import pytest
from app.db.models.user import User
from app.db.models.item import Item

# 아이템 생성 함수
async def create_test_item(session, owner_id, **kwargs):
    item_data = {
        "title": "Test Item",
        "description": "This is a test item",
        "owner_id": owner_id
    }
    item_data.update(kwargs)
    
    item = Item(**item_data)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

@pytest.mark.asyncio
async def test_user_items_relationship(setup_database, db_session):
    # 사용자 생성
    user = await create_test_user(db_session)
    
    # 사용자의 아이템 생성
    item1 = await create_test_item(db_session, user.id, title="Item 1")
    item2 = await create_test_item(db_session, user.id, title="Item 2")
    
    # 세션 초기화
    await db_session.refresh(user)
    
    # 관계 확인
    assert len(user.items) == 2
    assert user.items[0].title in ["Item 1", "Item 2"]
    assert user.items[1].title in ["Item 1", "Item 2"]
    
    # 역방향 관계 확인
    assert item1.owner_id == user.id
    assert item2.owner_id == user.id
    assert item1.owner.username == user.username
```

### 쿼리 및 필터 테스트

```python
# tests/test_db/test_queries.py
import pytest
from sqlalchemy import select
from app.db.models.user import User

@pytest.mark.asyncio
async def test_simple_query(setup_database, db_session):
    # 여러 사용자 생성
    await create_test_user(db_session, username="user1", email="user1@example.com")
    await create_test_user(db_session, username="user2", email="user2@example.com")
    await create_test_user(db_session, username="admin", email="admin@example.com")
    
    # 모든 사용자 조회
    query = select(User)
    result = await db_session.execute(query)
    users = result.scalars().all()
    
    # 결과 확인
    assert len(users) == 3
    
    # 필터링 쿼리
    query = select(User).where(User.username.startswith("user"))
    result = await db_session.execute(query)
    filtered_users = result.scalars().all()
    
    # 결과 확인
    assert len(filtered_users) == 2
    assert all(user.username.startswith("user") for user in filtered_users)
```

## 통합 테스트

실제 데이터베이스를 사용한 통합 테스트:

```python
# tests/test_db/test_integration.py
import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.common.database.base import Base
from app.common.database.session import get_session
from app.common.config.settings import Settings

# 실제 테스트 데이터베이스 설정
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

@pytest.fixture(scope="module")
async def test_engine():
    # 테스트용 엔진 생성
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_engine):
    # 테스트용 세션 팩토리
    TestSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        async with session.begin():
            yield session

@pytest.mark.asyncio
async def test_real_database_connection(test_db_session):
    # 실제 데이터베이스 연결 테스트
    assert test_db_session.is_active
    
    # 간단한 쿼리 실행 - 버전 확인
    if TEST_DATABASE_URL.startswith("postgresql"):
        result = await test_db_session.execute("SELECT version();")
        version = result.scalar()
        assert "PostgreSQL" in version
    elif TEST_DATABASE_URL.startswith("sqlite"):
        result = await test_db_session.execute("SELECT sqlite_version();")
        version = result.scalar()
        assert version is not None
```

## 모킹 전략

Database 모듈 테스트 시 다음과 같은 모킹 전략을 사용할 수 있습니다:

1. **인메모리 데이터베이스**: 실제 데이터베이스 대신 SQLite 인메모리 데이터베이스 사용
2. **세션 모킹**: `get_session` 함수를 모킹하여 테스트 세션 반환
3. **모델 모킹**: 실제 모델 대신 간소화된 테스트용 모델 사용

## 팩토리 패턴

테스트 시 다음과 같은 팩토리 패턴을 활용하면 효율적입니다:

```python
# tests/conftest.py

# 사용자 팩토리
@pytest.fixture
async def user_factory(db_session):
    async def create_user(**kwargs):
        default_password = "password123"
        defaults = {
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
            "hashed_password": get_password_hash(default_password),
            "is_active": True
        }
        defaults.update(kwargs)
        user = User(**defaults)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    return create_user

# 아이템 팩토리
@pytest.fixture
async def item_factory(db_session):
    async def create_item(owner_id, **kwargs):
        defaults = {
            "title": f"Item {uuid.uuid4().hex[:8]}",
            "description": "Test item description",
            "owner_id": owner_id
        }
        defaults.update(kwargs)
        item = Item(**defaults)
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)
        return item
    return create_item
```

## 테스트 커버리지 확인

Database 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.database tests/test_db/
```

## 모범 사례

1. **트랜잭션 격리**: 각 테스트는 독립적인 트랜잭션 내에서 실행하고 테스트 후 롤백하여 테스트 간 상태 격리
2. **팩토리 사용**: 모델 인스턴스 생성을 위한 재사용 가능한 팩토리 함수 활용
3. **유닛 테스트와 통합 테스트 분리**: 단순한 모델 테스트는 인메모리 DB로, 복잡한 쿼리는 실제 DB로 테스트
4. **비동기 코드 테스트**: `pytest-asyncio`를 사용하여 비동기 ORM 코드 테스트
5. **테스트 데이터베이스 분리**: 개발/운영 데이터베이스와 별도의 테스트 전용 데이터베이스 사용

## 주의사항

1. 실제 데이터베이스로 테스트할 경우, 테스트 전용 데이터베이스나 스키마를 사용하고 테스트 후 정리하세요.
2. 복잡한 마이그레이션 로직은 별도의 통합 테스트로 검증하세요.
3. 비동기 세션 관리에 주의하세요. 세션을 닫지 않으면 리소스 누수가 발생할 수 있습니다.
4. 테스트에서 실제 비밀번호 대신 테스트용 해시 값을 사용하세요.
5. 테스트가 느려지면 너무 많은 데이터를 생성하지 않도록 주의하세요.
