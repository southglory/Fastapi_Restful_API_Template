# Repositories 모듈 테스트 가이드

## 개요

`repositories` 모듈은 데이터베이스와의 상호작용을 추상화하는 계층으로, 데이터 액세스 로직을 캡슐화합니다. 이 모듈은 서비스 계층과 데이터베이스 사이의 중간 역할을 하며, CRUD(생성, 조회, 업데이트, 삭제) 연산을 처리합니다. 리포지토리 패턴을 사용하면 비즈니스 로직과 데이터 액세스 로직을 분리하여 코드의 유지보수성과 테스트 용이성을 높일 수 있습니다.

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 데이터베이스 의존성이 있어 모킹이나 테스트 데이터베이스 설정이 필요함
  - 비동기 코드 테스트가 필요함
  - 다양한 쿼리 조건과 예외 상황 테스트가 필요함
  - 트랜잭션 관리와 롤백 테스트가 필요함

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 CRUD 연산**
   - 데이터 생성 (Create)
   - 데이터 조회 (Read)
   - 데이터 업데이트 (Update)
   - 데이터 삭제 (Delete)

2. **고급 쿼리 연산**
   - 필터링 (여러 조건으로 데이터 조회)
   - 정렬 (데이터 정렬 기준 적용)
   - 페이지네이션 (데이터 분할 조회)
   - 관계 로드 (연관 데이터 함께 조회)

3. **트랜잭션 관리**
   - 트랜잭션 시작 및 커밋
   - 오류 발생 시 롤백
   - 중첩 트랜잭션 처리

## 테스트 접근법

Repository 모듈 테스트 시 다음 접근법을 권장합니다:

1. **단위 테스트**: 모킹을 통해 데이터베이스 의존성 없이 리포지토리 로직 테스트
2. **통합 테스트**: 실제 데이터베이스나 인메모리 데이터베이스를 사용한 테스트
3. **트랜잭션 테스트**: 각 테스트는 독립적인 트랜잭션 내에서 실행하고 테스트 후 롤백

## 테스트 예시

### 기본 CRUD 작업 테스트

```python
# tests/test_repositories/test_user_repository.py
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.user_repository import UserRepository
from app.db.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate

@pytest.fixture
def user_repo():
    # 테스트용 세션 모킹
    session = AsyncMock(spec=AsyncSession)
    return UserRepository(session)

@pytest.mark.asyncio
async def test_create_user(user_repo):
    # 생성할 사용자 데이터
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )
    
    # 예상되는 결과 사용자 객체
    expected_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    
    # 세션 add 및 commit 동작 모킹
    user_repo.session.add = AsyncMock()
    user_repo.session.commit = AsyncMock()
    user_repo.session.refresh = AsyncMock()
    
    # 비밀번호 해싱 함수 모킹
    with patch("app.db.repositories.user_repository.get_password_hash", 
               return_value="hashed_password"):
        # 테스트 메소드 호출
        result = await user_repo.create(user_create)
        
        # 결과 검증
        assert user_repo.session.add.called
        assert user_repo.session.commit.called
        assert user_repo.session.refresh.called
        
        # 결과 사용자 객체 검증
        assert result.username == expected_user.username
        assert result.email == expected_user.email
        assert result.hashed_password == "hashed_password"

@pytest.mark.asyncio
async def test_get_user_by_id(user_repo):
    # 예상되는 사용자 객체
    expected_user = User(
        id=1,
        username="testuser",
        email="test@example.com"
    )
    
    # 세션 execute 결과 모킹
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    user_repo.session.execute.return_value = mock_result
    
    # 테스트 메소드 호출
    result = await user_repo.get_by_id(1)
    
    # 결과 검증
    assert result == expected_user
    assert user_repo.session.execute.called

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_repo):
    # 사용자가 없는 경우 모킹
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    user_repo.session.execute.return_value = mock_result
    
    # 테스트 메소드 호출
    result = await user_repo.get_by_id(999)
    
    # 결과 검증 - 없는 사용자는 None 반환
    assert result is None
    assert user_repo.session.execute.called

@pytest.mark.asyncio
async def test_update_user(user_repo):
    # 업데이트할 기존 사용자
    existing_user = User(
        id=1,
        username="oldname",
        email="old@example.com",
        is_active=True
    )
    
    # 업데이트 데이터
    user_update = UserUpdate(
        username="newname",
        email="new@example.com"
    )
    
    # get_by_id 메소드 모킹
    user_repo.get_by_id = AsyncMock(return_value=existing_user)
    
    # 세션 commit 및 refresh 모킹
    user_repo.session.commit = AsyncMock()
    user_repo.session.refresh = AsyncMock()
    
    # 테스트 메소드 호출
    result = await user_repo.update(1, user_update)
    
    # 결과 검증
    assert result.username == "newname"
    assert result.email == "new@example.com"
    assert user_repo.session.commit.called
    assert user_repo.session.refresh.called

@pytest.mark.asyncio
async def test_delete_user(user_repo):
    # 삭제할 기존 사용자
    existing_user = User(id=1, username="testuser")
    
    # get_by_id 메소드 모킹
    user_repo.get_by_id = AsyncMock(return_value=existing_user)
    
    # 세션 delete, commit 모킹
    user_repo.session.delete = AsyncMock()
    user_repo.session.commit = AsyncMock()
    
    # 테스트 메소드 호출
    result = await user_repo.delete(1)
    
    # 결과 검증
    assert result is True
    assert user_repo.session.delete.called
    assert user_repo.session.commit.called
    
    # 존재하지 않는 사용자 삭제 시도
    user_repo.get_by_id = AsyncMock(return_value=None)
    result = await user_repo.delete(999)
    assert result is False
```

### 고급 쿼리 테스트

```python
# tests/test_repositories/test_item_repository.py
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.item_repository import ItemRepository
from app.db.models.item import Item

@pytest.fixture
def item_repo():
    # 테스트용 세션 모킹
    session = AsyncMock(spec=AsyncSession)
    return ItemRepository(session)

@pytest.mark.asyncio
async def test_get_items_by_owner(item_repo):
    # 소유자 ID
    owner_id = 1
    
    # 반환할 아이템 목록
    expected_items = [
        Item(id=1, title="Item 1", owner_id=owner_id),
        Item(id=2, title="Item 2", owner_id=owner_id)
    ]
    
    # 세션 execute 결과 모킹
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = expected_items
    item_repo.session.execute.return_value = mock_result
    
    # 테스트 메소드 호출
    result = await item_repo.get_by_owner(owner_id)
    
    # 결과 검증
    assert len(result) == 2
    assert all(item.owner_id == owner_id for item in result)
    
    # select 쿼리에 필터 조건이 적용되었는지 확인
    with patch("app.db.repositories.item_repository.select") as mock_select:
        mock_select.return_value = select(Item)
        await item_repo.get_by_owner(owner_id)
        
        # select가 호출되었는지 확인
        assert mock_select.called

@pytest.mark.asyncio
async def test_get_items_with_pagination(item_repo):
    # 반환할 아이템 목록
    expected_items = [
        Item(id=1, title="Item A"),
        Item(id=2, title="Item B"),
        Item(id=3, title="Item C")
    ]
    
    # 페이지네이션 파라미터
    skip = 1
    limit = 2
    
    # 세션 execute 결과 모킹
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = expected_items[skip:skip+limit]
    item_repo.session.execute.return_value = mock_result
    
    # 테스트 메소드 호출
    result = await item_repo.get_multi(skip=skip, limit=limit)
    
    # 결과 검증
    assert len(result) == 2
    
    # select 쿼리에 offset과 limit이 적용되었는지 확인
    with patch("app.db.repositories.item_repository.select") as mock_select:
        mock_select.return_value = select(Item)
        await item_repo.get_multi(skip=skip, limit=limit)
        
        # select가 호출되었는지 확인
        assert mock_select.called

@pytest.mark.asyncio
async def test_get_items_with_filter_and_sort(item_repo):
    # 필터링 및 정렬 파라미터
    category = "electronics"
    sort_by = "price"
    order = "desc"
    
    # 반환할 아이템 목록
    expected_items = [
        Item(id=1, title="Expensive Item", category=category, price=1000),
        Item(id=2, title="Cheap Item", category=category, price=100)
    ]
    
    # 세션 execute 결과 모킹
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = expected_items
    item_repo.session.execute.return_value = mock_result
    
    # 테스트 메소드 호출
    result = await item_repo.get_by_filter(
        category=category,
        sort_by=sort_by,
        order=order
    )
    
    # 결과 검증
    assert len(result) == 2
    assert all(item.category == category for item in result)
    
    # select 쿼리에 필터와 정렬이 적용되었는지 확인
    with patch("app.db.repositories.item_repository.select") as mock_select:
        with patch("sqlalchemy.desc") as mock_desc:
            mock_select.return_value = select(Item)
            await item_repo.get_by_filter(
                category=category,
                sort_by=sort_by,
                order=order
            )
            
            # select와 desc가 호출되었는지 확인
            assert mock_select.called
            assert mock_desc.called
```

### 트랜잭션 테스트

```python
# tests/test_repositories/test_transaction.py
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base_repository import BaseRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.item_repository import ItemRepository
from app.db.models.user import User
from app.db.models.item import Item
from app.db.schemas.user import UserCreate
from app.db.schemas.item import ItemCreate

@pytest.fixture
def session():
    # 테스트용 세션 모킹
    session = AsyncMock(spec=AsyncSession)
    # 트랜잭션 시작 모킹
    session.begin = AsyncMock()
    return session

@pytest.fixture
def base_repo(session):
    return BaseRepository(session)

@pytest.fixture
def user_repo(session):
    return UserRepository(session)

@pytest.fixture
def item_repo(session):
    return ItemRepository(session)

@pytest.mark.asyncio
async def test_transaction_commit(base_repo, user_repo, item_repo):
    # 트랜잭션 컨텍스트 모킹
    transaction_context = AsyncMock()
    base_repo.session.begin.return_value.__aenter__.return_value = transaction_context
    
    # 사용자 생성
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )
    
    # 아이템 생성
    item_create = ItemCreate(
        title="Test Item",
        description="Test Description",
        owner_id=1
    )
    
    # 사용자 및 아이템 repository 메소드 모킹
    user_repo.create = AsyncMock(return_value=User(id=1, username="testuser"))
    item_repo.create = AsyncMock(return_value=Item(id=1, title="Test Item"))
    
    # 트랜잭션 내에서 작업 수행
    async with base_repo.transaction():
        user = await user_repo.create(user_create)
        item = await item_repo.create(item_create)
    
    # 검증
    assert base_repo.session.begin.called
    assert user_repo.create.called
    assert item_repo.create.called
    assert transaction_context.commit.called
    assert not transaction_context.rollback.called

@pytest.mark.asyncio
async def test_transaction_rollback(base_repo, user_repo):
    # 트랜잭션 컨텍스트 모킹
    transaction_context = AsyncMock()
    base_repo.session.begin.return_value.__aenter__.return_value = transaction_context
    
    # 사용자 생성 중 예외 발생 모킹
    user_repo.create = AsyncMock(side_effect=Exception("Database error"))
    
    # 트랜잭션 내에서 예외 발생
    with pytest.raises(Exception) as exc:
        async with base_repo.transaction():
            await user_repo.create(UserCreate(
                username="testuser",
                email="test@example.com",
                password="securepassword"
            ))
    
    # 예외 메시지 확인
    assert "Database error" in str(exc.value)
    
    # 롤백 호출 확인
    assert base_repo.session.begin.called
    assert transaction_context.rollback.called
    assert not transaction_context.commit.called
```

## 통합 테스트

실제 데이터베이스나 인메모리 데이터베이스를 사용한 통합 테스트:

```python
# tests/test_repositories/test_integration.py
import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.common.database.base import Base
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.item_repository import ItemRepository
from app.db.models.user import User
from app.db.models.item import Item
from app.db.schemas.user import UserCreate
from app.db.schemas.item import ItemCreate

# 테스트용 SQLite 인메모리 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="module")
async def test_engine():
    # 테스트용 엔진 생성
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 테스트 종료 후 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    # 테스트용 세션 팩토리
    TestSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # 세션 생성
    async with TestSessionLocal() as session:
        # 트랜잭션 시작
        async with session.begin():
            yield session
            # 테스트 후 롤백
            await session.rollback()

@pytest.fixture
async def user_repo(test_session):
    return UserRepository(test_session)

@pytest.fixture
async def item_repo(test_session):
    return ItemRepository(test_session)

@pytest.mark.asyncio
async def test_create_and_get_user(user_repo):
    # 사용자 생성
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )
    
    # 사용자 저장
    user = await user_repo.create(user_create)
    
    # 검증
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # ID로 사용자 조회
    retrieved_user = await user_repo.get_by_id(user.id)
    
    # 검증
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.username == user.username
    assert retrieved_user.email == user.email

@pytest.mark.asyncio
async def test_create_items_for_user(user_repo, item_repo):
    # 사용자 생성
    user_create = UserCreate(
        username="itemowner",
        email="owner@example.com",
        password="securepassword"
    )
    user = await user_repo.create(user_create)
    
    # 사용자의 아이템 생성
    item1 = await item_repo.create(ItemCreate(
        title="Item 1",
        description="First test item",
        owner_id=user.id
    ))
    
    item2 = await item_repo.create(ItemCreate(
        title="Item 2",
        description="Second test item",
        owner_id=user.id
    ))
    
    # 사용자의 아이템 조회
    items = await item_repo.get_by_owner(user.id)
    
    # 검증
    assert len(items) == 2
    assert all(item.owner_id == user.id for item in items)
    assert any(item.title == "Item 1" for item in items)
    assert any(item.title == "Item 2" for item in items)
```

## 모킹 전략

[공통 테스트 패턴](../common_test_patterns.md)의 모킹 전략을 참조하세요. Repository 모듈에 특화된 모킹 전략은 다음과 같습니다:

1. **세션 모킹**: 데이터베이스 세션을 모킹하여 실제 데이터베이스 연결 없이 테스트
2. **쿼리 결과 모킹**: `execute`, `scalar`, `all` 등의 메서드 반환값 모킹
3. **트랜잭션 모킹**: 트랜잭션 컨텍스트 매니저를 모킹하여 `commit`, `rollback` 테스트
4. **모델 인스턴스 모킹**: SQLAlchemy 모델 인스턴스를 직접 생성하여 리포지토리 반환값 테스트

## 테스트 커버리지 확인

Repository 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.db.repositories tests/test_repositories/
```

## 모범 사례

[공통 테스트 패턴](../common_test_patterns.md)의 모범 사례와 함께 Repository 모듈에 특화된 모범 사례는 다음과 같습니다:

1. **단위 테스트와 통합 테스트 분리**: 모킹을 통한 빠른 단위 테스트와 실제 데이터베이스를 사용한 통합 테스트를 적절히 조합
2. **트랜잭션 격리**: 각 테스트는 독립적인 트랜잭션 내에서 실행하고 테스트 후 롤백하여 테스트 간 상태 격리 유지
3. **예외 상황 테스트**: 정상 케이스뿐만 아니라 데이터 중복, 제약 조건 위반 등 오류 상황에 대한 테스트 작성
4. **쿼리 성능 테스트**: 복잡한 쿼리나 대량 데이터 처리 시 성능 테스트 고려

## 주의사항

[공통 테스트 패턴](../common_test_patterns.md)의 주의사항과 함께 Repository 모듈 테스트 시 추가로 고려해야 할 사항:

1. **트랜잭션 관리**: 테스트에서 트랜잭션을 명시적으로 관리하지 않으면 데이터가 영구적으로 변경될 수 있으므로 항상 롤백 전략 사용
2. **비동기 코드**: 비동기 리포지토리 메서드 테스트 시 `pytest-asyncio`를 사용하고 `async/await` 구문을 올바르게 사용
3. **외래 키 제약 조건**: 통합 테스트에서 모델 간의 관계를 테스트할 때 외래 키 제약 조건 고려
4. **데이터베이스 초기화**: 테스트 데이터베이스는 테스트 시작 전에 적절히 초기화되어야 함
