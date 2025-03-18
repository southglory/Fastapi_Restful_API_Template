# 공통 데이터베이스 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 공통 데이터베이스 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

1. [데이터베이스 연결](#데이터베이스-연결)
2. [세션 관리](#세션-관리)
3. [기본 모델](#기본-모델)
4. [트랜잭션 처리](#트랜잭션-처리)
5. [데이터베이스 유틸리티](#데이터베이스-유틸리티)
6. [심화 가이드](#심화-가이드)

## 데이터베이스 연결

`app.common.database` 모듈은 SQLAlchemy를 사용하여 비동기 데이터베이스 연결을 제공합니다.

### 지원 데이터베이스

이 프로젝트는 다음 데이터베이스를 지원합니다:

- **PostgreSQL**: 프로덕션 환경에서 권장 (asyncpg 드라이버 사용)
- **SQLite**: 개발 및 테스트 환경에서 권장 (aiosqlite 드라이버 사용)

### 연결 설정

```python
from app.common.database.base import engine

# 데이터베이스 URL은 자동으로 적절한 비동기 드라이버로 변환됩니다
# PostgreSQL URL: postgresql://user:password@localhost:5432/dbname
# SQLite URL: sqlite:///./dev.db
```

## 세션 관리

### 데이터베이스 세션 사용

```python
from app.common.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/items/")
async def get_items(db: AsyncSession = Depends(get_db)):
    # 비동기 데이터베이스 작업 수행
    result = await db.execute(select(Item))
    return result.scalars().all()
```

### 컨텍스트 매니저로 세션 사용

```python
from app.common.database import get_async_session

async def some_function():
    async with get_async_session() as session:
        # 비동기 세션 사용
        result = await session.execute(select(Item).where(Item.id == 1))
        item = result.scalar_one_or_none()
        return item
```

## 기본 모델

### 기본 모델 정의

```python
from app.common.database.base import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 공통 모델 믹스인

```python
from app.common.database.mixins import TimestampMixin, UUIDMixin

class User(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "users"
    
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    # UUID 필드와 타임스탬프 필드는 믹스인에서 자동으로 추가됨
```

## 트랜잭션 처리

### 명시적 트랜잭션

```python
from app.common.database import get_db

@app.post("/transfer/")
async def transfer_funds(
    from_account: int,
    to_account: int,
    amount: float,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 송금 계좌에서 인출
        await db.execute(
            update(Account)
            .where(Account.id == from_account)
            .values(balance=Account.balance - amount)
        )
        
        # 수신 계좌에 입금
        await db.execute(
            update(Account)
            .where(Account.id == to_account)
            .values(balance=Account.balance + amount)
        )
        
        # 트랜잭션 커밋
        await db.commit()
        return {"message": "송금 완료"}
    except Exception as e:
        # 오류 발생 시 롤백
        await db.rollback()
        raise Exception(f"송금 실패: {str(e)}")
```

### 트랜잭션 데코레이터

```python
from app.common.database.utils import transactional

@app.post("/users/")
@transactional()
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 사용자 생성
    db_user = User(**user_data.dict())
    db.add(db_user)
    await db.flush()
    
    # 사용자 프로필 생성
    db_profile = UserProfile(user_id=db_user.id)
    db.add(db_profile)
    
    # 트랜잭션은 데코레이터에 의해 자동으로 커밋됨
    return db_user
```

## 데이터베이스 유틸리티

### 페이지네이션

```python
from app.common.database.utils import paginate

@app.get("/users/")
async def get_users(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).order_by(User.id)
    return await paginate(db, query, page, size)
```

### 벌크 연산

```python
from app.common.database.utils import bulk_insert, bulk_update

@app.post("/items/bulk")
async def create_bulk_items(
    items: list[ItemCreate],
    db: AsyncSession = Depends(get_db)
):
    # 대량 삽입
    item_dicts = [item.dict() for item in items]
    await bulk_insert(db, Item, item_dicts)
    return {"message": f"{len(items)}개 아이템 생성 완료"}
```

## 심화 가이드

데이터베이스 모듈에 대한 더 자세한 가이드는 다음 문서를 참조하세요:

1. [데이터베이스 설정](./database/01-db-setup.md) - 연결 설정 및 세션 관리
2. [모델 정의](./database/02-models.md) - SQLAlchemy 모델 정의
3. [마이그레이션 설정](./database/03-migrations.md) - Alembic을 사용한 마이그레이션
4. [스키마 정의](./database/04-schemas.md) - Pydantic 스키마 정의
5. [서비스 레이어](./database/05-services.md) - 비즈니스 로직 구현
6. [Docker 환경 설정](./database/06-docker.md) - 컨테이너 환경 설정
