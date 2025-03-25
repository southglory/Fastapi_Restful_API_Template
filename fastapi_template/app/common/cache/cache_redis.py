"""
# File: fastapi_template/app/common/cache/cache_redis.py
# Description: Redis 기반 캐시 구현
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import redis.asyncio as redis_async
from fastapi import Depends, Request

from fastapi_template.app.common.config import config_settings
from fastapi_template.app.common.cache.cache_base import (
    CacheBackend,
    cache_key_builder,
    serialize_value,
    deserialize_value,
)

# Redis 연결을 위한 글로벌 변수
redis_conn = None


async def get_redis_connection() -> redis_async.Redis:
    """
    Redis 연결 반환 (싱글톤 패턴)
    
    Returns:
        redis_async.Redis: Redis 연결 객체
    """
    global redis_conn
    if redis_conn is None:
        redis_url = (
            f"redis://{config_settings.REDIS_HOST}:{config_settings.REDIS_PORT}/{config_settings.REDIS_DB}"
        )
        redis_conn = await redis_async.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )
    return redis_conn


class RedisCacheBackend(CacheBackend):
    """
    Redis 캐시 백엔드 클래스
    """

    def __init__(self, redis_conn: redis_async.Redis, ttl: int = config_settings.REDIS_TTL):
        """
        초기화
        
        Args:
            redis_conn: Redis 연결 객체
            ttl: 캐시 유효기간 (초)
        """
        self.redis = redis_conn
        self.ttl = ttl

    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[str]: 조회된 값 또는 None
        """
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 유효기간 (초)
        """
        await self.redis.set(key, value, ex=ttl or self.ttl)

    async def delete(self, key: str) -> None:
        """
        캐시에서 키 삭제
        
        Args:
            key: 삭제할 캐시 키
        """
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str) -> None:
        """
        패턴과 일치하는 모든 키 삭제
        
        Args:
            pattern: 키 패턴 (예: "user:*")
        """
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


def cached(
    prefix: str, ttl: Optional[int] = None, key_builder: Callable = cache_key_builder
):
    """
    함수 결과 캐싱 데코레이터

    Example:
        @cached("user_profile", ttl=300)
        async def get_user_profile(user_id: int) -> dict:
            ...
            
    Args:
        prefix: 캐시 키 접두사
        ttl: 캐시 유효기간 (초)
        key_builder: 캐시 키 생성 함수
        
    Returns:
        Callable: 데코레이터 함수
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Redis 연결 가져오기
            redis_conn = await get_redis_connection()
            cache = RedisCacheBackend(redis_conn, ttl=ttl or config_settings.REDIS_TTL)

            # 캐시 키 생성
            cache_key = key_builder(prefix, *args, **kwargs)

            # 캐시에서 값 조회
            cached_value = await cache.get(cache_key)
            if cached_value:
                return deserialize_value(cached_value)

            # 원본 함수 실행
            result = await func(*args, **kwargs)

            # 결과가 None이 아니면 캐싱
            if result is not None:
                serialized_value = serialize_value(result)
                await cache.set(cache_key, serialized_value)

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """
    패턴과 일치하는 캐시 무효화 데코레이터

    Example:
        @invalidate_cache("user_profile:*")
        async def update_user_profile(user_id: int, data: dict) -> dict:
            ...
            
    Args:
        pattern: 캐시 키 패턴
        
    Returns:
        Callable: 데코레이터 함수
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 원본 함수 실행
            result = await func(*args, **kwargs)

            # Redis 연결 가져오기
            redis_conn = await get_redis_connection()
            cache = RedisCacheBackend(redis_conn)

            # 패턴과 일치하는 캐시 무효화
            await cache.clear_pattern(pattern)

            return result

        return wrapper

    return decorator 