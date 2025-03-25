# Database 모듈 상세 가이드

[@database](/fastapi_template/app/common/database)

## 개요

`database` 모듈은 애플리케이션의 데이터베이스 연결과 관리 기능을 구현하는 모듈입니다. SQLAlchemy를 사용하여 데이터베이스 세션, 모델, 마이그레이션 등을 제공하며, 데이터의 영구 저장소 역할을 합니다.

## 현재 모듈 구조

```
app/common/database/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── database_base.py            # 기본 데이터베이스 클래스
└── database_session.py         # 세션 관리
```

## 주요 기능

### 1. 기본 데이터베이스 (`database_base.py`)

- 데이터베이스 초기화
- 연결 설정
- 공통 기능

### 2. 세션 관리 (`database_session.py`)

- 세션 생성
- 세션 관리
- 트랜잭션 처리

## 사용 예시

### 데이터베이스 연결 설정

```python
from app.common.database.database_base import engine

# 데이터베이스 URL은 자동으로 적절한 비동기 드라이버로 변환됩니다
# PostgreSQL URL: postgresql://user:password@localhost:5432/dbname
# SQLite URL: sqlite:///./dev.db
```

### 세션 사용

```python
from app.common.database.database_session import get_db
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
from app.common.database.database_session import get_async_session

async def some_function():
    async with get_async_session() as session:
        # 비동기 세션 사용
        result = await session.execute(select(Item).where(Item.id == 1))
        item = result.scalar_one_or_none()
        return item
```

### 기본 모델 정의

```python
from app.common.database.database_base import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 트랜잭션 처리

```python
from app.common.database.database_session import get_db

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

## 모범 사례

1. 모든 데이터베이스 작업의 성공/실패를 처리합니다.
2. 트랜잭션의 원자성을 보장합니다.
3. 모델 관계와 제약조건을 적절히 설정합니다.
4. 마이그레이션의 안전성을 확인합니다.

## 주의사항

1. 실제 데이터베이스 대신 테스트용 데이터베이스를 사용합니다.
2. 각 작업 후 데이터베이스를 초기화합니다.
3. 트랜잭션 격리 수준을 고려합니다.
4. 마이그레이션 롤백을 준비합니다.

## 심화 가이드

데이터베이스 모듈에 대한 더 자세한 가이드는 다음 문서를 참조하세요:

1. [데이터베이스 설정](./database/01-db-setup.md) - 연결 설정 및 세션 관리
2. [모델 정의](./database/02-models.md) - SQLAlchemy 모델 정의
3. [마이그레이션 설정](./database/03-migrations.md) - Alembic을 사용한 마이그레이션
4. [스키마 정의](./database/04-schemas.md) - Pydantic 스키마 정의
5. [서비스 레이어](./database/05-services.md) - 비즈니스 로직 구현
6. [Docker 환경 설정](./database/06-docker.md) - 컨테이너 환경 설정
