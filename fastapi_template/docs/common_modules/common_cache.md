# 캐싱 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 캐싱 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [Redis 캐싱](#redis-캐싱)
- [함수 캐싱 데코레이터](#함수-캐싱-데코레이터)
- [캐시 무효화](#캐시-무효화)
- [캐시 관리](#캐시-관리)

## Redis 캐싱

Redis를 사용하여 애플리케이션 데이터를 캐싱합니다.

### Redis 연결 설정

```python
from app.common.cache.redis_client import get_redis_connection

# Redis 클라이언트 얻기
redis = await get_redis_connection()

# Redis 명령어 사용
await redis.set("key", "value", expire=60)  # 60초 유효
value = await redis.get("key")
```

### 연결 설정 커스터마이징

```python
from app.common.cache.redis_client import get_redis_connection

# 커스텀 설정으로 Redis 연결
redis = await get_redis_connection(
    host="custom-redis.example.com",
    port=6380,
    db=1,
    password="redis-password"
)
```

## 함수 캐싱 데코레이터

함수 결과를 자동으로 캐싱하는 데코레이터를 제공합니다.

### 기본 캐싱

```python
from app.common.cache.redis_client import cached

# 함수 결과를 60초 동안 캐싱
@cached(ttl=60)
async def get_user(user_id: int):
    # 데이터베이스에서 사용자 조회 (비용이 많이 드는 작업)
    return await db.get_user(user_id)

# 캐싱된 함수 호출
user = await get_user(123)  # 첫 호출: DB에서 가져옴
user = await get_user(123)  # 두 번째 호출: 캐시에서 가져옴
```

### 고급 캐싱 옵션

```python
from app.common.cache.redis_client import cached

# 접두사와 키 생성기 지정
@cached(
    prefix="user_profile",  # 캐시 키 접두사
    ttl=300,  # 5분 유효
    key_builder=lambda user_id, **kwargs: f"user:{user_id}"  # 캐시 키 생성 함수
)
async def get_user_profile(user_id: int, with_details: bool = False):
    # 사용자 프로필 조회
    user = await db.get_user(user_id)
    if with_details:
        user["details"] = await db.get_user_details(user_id)
    return user
```

### JSON 직렬화/역직렬화

기본적으로 캐싱된 데이터는 JSON으로 직렬화됩니다.

```python
from app.common.cache.redis_client import cached
from datetime import datetime

@cached(ttl=60)
async def get_post(post_id: int):
    post = await db.get_post(post_id)
    # datetime 객체를 포함하는 사전 반환
    return {
        "id": post.id,
        "title": post.title,
        "created_at": post.created_at,  # datetime 객체 (자동 직렬화)
    }
```

### 사용자 정의 직렬화/역직렬화

```python
from app.common.cache.redis_client import cached
import pickle

# 커스텀 직렬화기/역직렬화기 사용
@cached(
    ttl=60,
    serializer=lambda obj: pickle.dumps(obj),
    deserializer=lambda data: pickle.loads(data)
)
async def get_complex_object(obj_id: int):
    # 복잡한 객체 반환
    return await db.get_complex_object(obj_id)
```

## 캐시 무효화

캐시된 데이터를 무효화하는 방법을 제공합니다.

### 특정 키 무효화

```python
from app.common.cache.redis_client import invalidate_cache

# 특정 캐시 키 무효화
@invalidate_cache("user_profile:123")
async def update_user(user_id: int, data: dict):
    # 사용자 업데이트 후 캐시 무효화
    await db.update_user(user_id, data)
    return {"success": True}
```

### 패턴 무효화

```python
from app.common.cache.redis_client import invalidate_cache

# 패턴과 일치하는 모든 캐시 무효화
@invalidate_cache("user_profile:*")
async def update_all_users():
    # 모든 사용자 업데이트 후 모든 사용자 프로필 캐시 무효화
    await db.update_all_users()
    return {"success": True}
```

### 특정 함수의 모든 캐시 무효화

```python
from app.common.cache.redis_client import invalidate_function_cache

# get_user_profile 함수의 모든 캐시 무효화
await invalidate_function_cache(get_user_profile)
```

## 캐시 관리

캐시 관리를 위한 유틸리티 기능을 제공합니다.

### 캐시 상태 확인

```python
from app.common.cache.redis_client import get_cache_stats

# 캐시 상태 확인
stats = await get_cache_stats()
print(f"총 캐시 항목: {stats['total_keys']}")
print(f"메모리 사용량: {stats['used_memory_human']}")
```

### 수동 캐싱

```python
from app.common.cache.redis_client import set_cache, get_cache

# 데이터 수동 캐싱
await set_cache("custom_key", {"data": "value"}, ttl=3600)

# 캐시에서 데이터 가져오기
data = await get_cache("custom_key")
```

### 전체 캐시 정리

```python
from app.common.cache.redis_client import clear_cache

# 모든 캐시 지우기
await clear_cache()

# 특정 패턴의 캐시만 지우기
await clear_cache(pattern="user_*")
``` 