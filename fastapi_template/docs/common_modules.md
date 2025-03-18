# 공통 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 공통 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [인증 모듈](#인증-모듈)
- [설정 모듈](#설정-모듈)
- [데이터베이스 모듈](#데이터베이스-모듈)
- [예외 처리 모듈](#예외-처리-모듈)
- [스키마 모듈](#스키마-모듈)
- [유틸리티 모듈](#유틸리티-모듈)

## 인증 모듈

경로: `app/common/auth/`

### JWT 인증

```python
from app.common.auth import create_access_token, verify_token

# 토큰 생성
token = create_access_token(subject=user_id)

# 토큰 검증
payload = verify_token(token)
```

### 비밀번호 해싱

```python
from app.common.auth import get_password_hash, verify_password

# 비밀번호 해싱
hashed_password = get_password_hash("raw_password")

# 비밀번호 검증
is_valid = verify_password("raw_password", hashed_password)
```

## 설정 모듈

경로: `app/common/config/`

### 설정 사용하기

```python
from app.common.config import settings

# 데이터베이스 URL
db_url = settings.DATABASE_URL

# Redis 설정
redis_host = settings.REDIS_HOST
redis_port = settings.REDIS_PORT

# JWT 설정
secret_key = settings.SECRET_KEY
token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

### 개발 환경 설정

```python
from app.common.config import dev_settings

# 개발 환경 전용 설정
debug_mode = dev_settings.DEBUG
```

## 데이터베이스 모듈

경로: `app/common/database/`

### 데이터베이스 지원

이 프로젝트는 다음 데이터베이스를 지원합니다:

- **PostgreSQL**: 프로덕션 환경에서 권장 (asyncpg 드라이버 사용)
- **SQLite**: 개발 및 테스트 환경에서 권장 (aiosqlite 드라이버 사용)

데이터베이스 URL 설정은 자동으로 적절한 비동기 드라이버로 변환됩니다:

```python
# PostgreSQL URL
postgresql://user:password@localhost:5432/dbname
# SQLite URL
sqlite:///./dev.db
```

### 데이터베이스 세션

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

### 기본 모델

```python
from app.common.database.base import Base
from sqlalchemy import Column, Integer, String

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
```

## 예외 처리 모듈

경로: `app/common/exceptions/`

### 사용자 정의 예외

```python
from app.common.exceptions import AuthenticationError, PermissionDeniedError, ValidationError

# 인증 오류
raise AuthenticationError("인증 토큰이 유효하지 않습니다")

# 권한 오류
raise PermissionDeniedError("이 리소스에 접근할 권한이 없습니다")

# 유효성 검사 오류
raise ValidationError("입력 데이터가 유효하지 않습니다")
```

### 전역 예외 처리

FastAPI 애플리케이션에 전역 예외 핸들러가 자동으로 등록됩니다.

## 스키마 모듈

경로: `app/common/schemas/`

### 기본 응답 스키마

```python
from app.common.schemas.base_schema import ResponseSchema

# 성공 응답
return ResponseSchema.success(data={"id": 1, "name": "Item 1"})

# 실패 응답
return ResponseSchema.error(message="오류가 발생했습니다", code="ITEM_NOT_FOUND")
```

## 유틸리티 모듈

경로: `app/common/utils/`

### 캐싱 유틸리티

```python
from app.common.utils.cache import cached, invalidate_cache

# 함수 결과 캐싱
@cached(prefix="user_profile", ttl=300)
async def get_user_profile(user_id: int):
    # 데이터베이스에서 사용자 프로필 조회
    return await db.get_user(user_id)

# 캐시 무효화
@invalidate_cache("user_profile:*")
async def update_user_profile(user_id: int, data: dict):
    # 사용자 프로필 업데이트
    return await db.update_user(user_id, data)
```

### 암호화 유틸리티

```python
from app.common.utils.encryption import encrypt_data, decrypt_data

# 데이터 암호화
encrypted = encrypt_data("민감한 정보")

# 데이터 복호화
decrypted = decrypt_data(encrypted)
```
