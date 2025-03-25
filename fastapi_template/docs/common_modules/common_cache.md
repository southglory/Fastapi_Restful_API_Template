# 캐싱 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 캐싱 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [캐시 백엔드 사용하기](#캐시-백엔드-사용하기)
- [함수 캐싱 데코레이터](#함수-캐싱-데코레이터)
- [캐시 무효화](#캐시-무효화)
- [다양한 캐시 백엔드](#다양한-캐시-백엔드)

## 캐시 백엔드 사용하기

[@cache_base](/fastapi_template/app/common/cache/cache_base.py)

이 모듈은 다양한 캐시 백엔드의 인터페이스를 제공합니다. 설정에 따라 기본 백엔드가 선택됩니다.

### 기본 캐시 사용

```python
from fastapi_template.app.common.cache import cache

# 캐시 직접 사용
await cache.set("key", "value", ttl=60)  # 60초 유효
value = await cache.get("key")
await cache.delete("key")
```

### Redis 캐시 명시적 사용

```python
from fastapi_template.app.common.cache import RedisCacheBackend, get_redis_connection

# Redis 연결
redis_conn = await get_redis_connection()
redis_cache = RedisCacheBackend(redis_conn, ttl=300)

# Redis 캐시 사용
await redis_cache.set("key", "value")
value = await redis_cache.get("key")
```

### 메모리 캐시 명시적 사용

```python
from fastapi_template.app.common.cache import MemoryCacheBackend

# 메모리 캐시
memory_cache = MemoryCacheBackend(ttl=60)

# 메모리 캐시 사용
await memory_cache.set("key", "value")
value = await memory_cache.get("key")
```

### 파일 캐시 명시적 사용

```python
from fastapi_template.app.common.cache import FileCacheBackend

# 파일 캐시
file_cache = FileCacheBackend(cache_dir="/path/to/cache", ttl=3600)

# 파일 캐시 사용
await file_cache.set("key", "value")
value = await file_cache.get("key")
```

## 함수 캐싱 데코레이터

[@cache_decorators](/fastapi_template/app/common/cache/cache_redis.py)

함수 결과를 자동으로 캐싱하는 데코레이터를 제공합니다.

### 기본 캐싱

```python
from fastapi_template.app.common.cache import cached

# 함수 결과를 60초 동안 캐싱
@cached(prefix="users", ttl=60)
async def get_user(user_id: int):
    # 데이터베이스에서 사용자 조회 (비용이 많이 드는 작업)
    return await db.get_user(user_id)

# 캐싱된 함수 호출
user = await get_user(123)  # 첫 호출: DB에서 가져옴
user = await get_user(123)  # 두 번째 호출: 캐시에서 가져옴
```

### 고급 캐싱 옵션

```python
from fastapi_template.app.common.cache import cached, cache_key_builder

# 커스텀 키 생성기 함수
def user_profile_key(prefix, user_id, **kwargs):
    return f"{prefix}:user:{user_id}"

# 접두사와 키 생성기 지정
@cached(
    prefix="profiles",  # 캐시 키 접두사
    ttl=300,  # 5분 유효
    key_builder=user_profile_key  # 커스텀 캐시 키 생성 함수
)
async def get_user_profile(user_id: int, with_details: bool = False):
    # 사용자 프로필 조회
    user = await db.get_user(user_id)
    if with_details:
        user["details"] = await db.get_user_details(user_id)
    return user
```

## 캐시 무효화

캐시된 데이터를 무효화하는 방법을 제공합니다.

### 특정 패턴 무효화

```python
from fastapi_template.app.common.cache import invalidate_cache

# 특정 패턴의 캐시 키 무효화
@invalidate_cache("users:123:*")
async def update_user(user_id: int, data: dict):
    # 사용자 업데이트 후 캐시 무효화
    await db.update_user(user_id, data)
    return {"success": True}
```

### 수동 캐시 무효화

```python
from fastapi_template.app.common.cache import cache

# 특정 패턴의 캐시 지우기
await cache.clear_pattern("users:*")

# 특정 키 삭제
await cache.delete("users:123")
```

## 다양한 캐시 백엔드

### 캐시 백엔드 선택

이 모듈은 세 가지 캐시 백엔드를 제공합니다:

1. **Redis 캐시 백엔드** (기본):
   - 분산 환경에 적합
   - 영구 저장 지원
   - 다양한 데이터 타입 지원

2. **메모리 캐시 백엔드**:
   - 단일 프로세스 환경에 적합
   - 서버 재시작 시 캐시 초기화
   - 매우 빠른 액세스 속도

3. **파일 캐시 백엔드**:
   - 서버 재시작 후에도 캐시 유지
   - 로컬 파일 시스템에 의존
   - 패턴 기반 키 삭제에 제한

### 설정 구성

`config_settings.py`에서 사용할 캐시 백엔드를 설정할 수 있습니다:

```python
# 개발 환경 설정
ENVIRONMENT = "development"
CACHE_TYPE = "memory"  # "redis", "memory", "file" 중 선택

# Redis 설정 (Redis 캐시 사용 시)
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TTL = 3600  # 기본 TTL (초)
```

### 캐시 모듈 구조

```
app/common/cache/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── cache_base.py               # 기본 캐시 클래스 및 유틸리티
├── cache_redis.py              # Redis 캐시 구현
├── cache_memory.py             # 메모리 캐시 구현
└── cache_file.py               # 파일 시스템 캐시 구현
```
