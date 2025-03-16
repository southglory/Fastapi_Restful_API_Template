"""
# File: fastapi_template/app/common/utils/cache.py
# Description: Redis 캐싱 유틸리티
"""

import json
import pickle
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

import aioredis
from fastapi import Depends, Request
from pydantic import BaseModel

from app.core.config import settings

# Redis 연결을 위한 글로벌 변수
redis = None

T = TypeVar("T")


async def get_redis_connection() -> aioredis.Redis:
    """
    Redis 연결 반환 (싱글톤 패턴)
    """
    global redis
    if redis is None:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        redis = await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    return redis


class RedisCacheBackend:
    """
    Redis 캐시 백엔드 클래스
    """
    def __init__(self, redis_conn: aioredis.Redis, ttl: int = settings.REDIS_TTL):
        self.redis = redis_conn
        self.ttl = ttl

    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회
        """
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장
        """
        await self.redis.set(key, value, ex=ttl or self.ttl)

    async def delete(self, key: str) -> None:
        """
        캐시에서 키 삭제
        """
        await self.redis.delete(key)
        
    async def clear_pattern(self, pattern: str) -> None:
        """
        패턴과 일치하는 모든 키 삭제
        """
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    """
    캐시 키 생성 유틸리티
    """
    key_parts = [prefix]
    
    # 위치 인자 처리
    if args:
        key_parts.extend([str(arg) for arg in args])
    
    # 키워드 인자 처리 (정렬하여 일관성 유지)
    if kwargs:
        key_parts.extend([f"{k}:{kwargs[k]}" for k in sorted(kwargs.keys())])
    
    return ":".join(key_parts)


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Callable = cache_key_builder
):
    """
    함수 결과 캐싱 데코레이터
    
    Example:
        @cached("user_profile", ttl=300)
        async def get_user_profile(user_id: int) -> dict:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Redis 연결 가져오기
            redis_conn = await get_redis_connection()
            cache = RedisCacheBackend(redis_conn, ttl=ttl or settings.REDIS_TTL)
            
            # 캐시 키 생성
            cache_key = key_builder(prefix, *args, **kwargs)
            
            # 캐시에서 값 조회
            cached_value = await cache.get(cache_key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    # JSON 디코딩 실패 시 원본 문자열 반환
                    return cached_value
            
            # 원본 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과가 None이 아니면 캐싱
            if result is not None:
                if isinstance(result, (dict, list, str, int, float, bool)):
                    # 기본 타입은 JSON으로 직렬화
                    await cache.set(cache_key, json.dumps(result))
                elif isinstance(result, BaseModel):
                    # Pydantic 모델은 JSON으로 직렬화
                    await cache.set(cache_key, result.model_dump_json())
                else:
                    # 그 외는 pickle로 직렬화 (bytes로 저장)
                    await cache.set(cache_key, pickle.dumps(result))
            
            return result
        return wrapper
    return decorator


# 응용 예제: 캐시 무효화 데코레이터
def invalidate_cache(pattern: str):
    """
    패턴과 일치하는 캐시 무효화 데코레이터
    
    Example:
        @invalidate_cache("user_profile:*")
        async def update_user_profile(user_id: int, data: dict) -> dict:
            ...
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
 