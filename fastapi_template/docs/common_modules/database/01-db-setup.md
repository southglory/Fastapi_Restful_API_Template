# 데이터베이스 설정

이 문서는 FastAPI 프로젝트에서 PostgreSQL 데이터베이스 연결 설정 및 세션 관리 방법을 설명합니다.

## 목차

1. [환경 변수 설정](#환경-변수-설정)
2. [데이터베이스 세션 관리](#데이터베이스-세션-관리)
3. [기본 모델 클래스](#기본-모델-클래스)

## 환경 변수 설정

`.env` 파일에 데이터베이스 연결 정보를 설정합니다:

```env
# 데이터베이스 설정
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
```

이 URL은 다음과 같은 형식을 따릅니다:

- `postgresql://`: 데이터베이스 드라이버
- `postgres`: 사용자 이름
- `postgres`: 비밀번호
- `localhost:5432`: 호스트 및 포트
- `fastapi_db`: 데이터베이스 이름

## 데이터베이스 세션 관리

`app/common/database/session.py`에서 데이터베이스 세션을 관리합니다:

```python
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.common.config import settings

# 비동기 데이터베이스 URL 처리
# SQLite와 PostgreSQL 모두 지원
ASYNC_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
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
    ASYNC_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=settings.DB_ECHO_LOG
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
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 데이터베이스 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 주요 구성 요소

- **비동기 엔진**: `asyncpg` 드라이버를 사용하여 비동기 데이터베이스 접근
- **세션 팩토리**: 데이터베이스 세션을 생성하는 팩토리 함수
- **의존성 주입**: `get_db()` 함수를 통해 FastAPI 라우터에 세션 주입

## 기본 모델 클래스

`app/common/database/base.py`에서 모든 모델의 기본 클래스를 정의합니다:

```python
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    모든 SQLAlchemy 모델의 기본 클래스
    """
    id: Any
    __name__: str
    
    # 테이블명 자동 생성 (클래스명의 snake_case 형태)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimeStampMixin:
    """
    생성 및 수정 시간 필드를 제공하는 Mixin
    """
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(UTC), 
        onupdate=lambda: datetime.now(UTC), 
        nullable=False
    )


class BaseModel(Base, TimeStampMixin):
    """
    ID와 타임스탬프를 포함한 기본 모델 클래스
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
```

### 주요 구성 요소

- **Base 클래스**: 모든 모델의 기본 클래스로, 테이블명 자동 생성 기능 제공
- **TimeStampMixin**: 생성 및 수정 시간 필드를 제공하는 믹스인 클래스
- **BaseModel**: `Base`와 `TimeStampMixin`을 상속받은 실제 사용할 기본 모델 클래스

## 다음 단계

다음 문서에서는 [모델 정의](./02-models.md)에 대해 알아보겠습니다.
