from redis import Redis
from typing import Any, Optional
import json
from functools import wraps
import asyncio

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = Redis(host=host, port=port, db=db, decode_responses=True)
        
    async def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        return json.loads(value) if value else None
        
    async def set(self, key: str, value: Any, expire: int = 3600):
        self.redis.setex(
            key,
            expire,
            json.dumps(value)
        )
        
    async def delete(self, key: str):
        self.redis.delete(key)

def cache(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            redis_client = RedisClient()
            
            # 캐시된 결과 확인
            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # 결과 계산 및 캐시
            result = await func(*args, **kwargs)
            await redis_client.set(cache_key, result, expire)
            return result
            
        return wrapper
    return decorator 