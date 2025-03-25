"""
# File: fastapi_template/app/common/cache/__init__.py
# Description: 캐싱 모듈 패키지
"""

from fastapi_template.app.common.cache.cache_base import (
    CacheBackend,
    cache_key_builder,
    serialize_value,
    deserialize_value
)
from fastapi_template.app.common.cache.cache_redis import (
    RedisCacheBackend,
    get_redis_connection,
    cached,
    invalidate_cache
)
from fastapi_template.app.common.cache.cache_memory import MemoryCacheBackend
from fastapi_template.app.common.cache.cache_file import FileCacheBackend
from fastapi_template.app.common.config import config_settings

# 기본 캐시 타입 설정
CACHE_TYPE = config_settings.CACHE_TYPE.lower() if hasattr(config_settings, 'CACHE_TYPE') else 'redis'

# 기본 캐시 백엔드 선택
if CACHE_TYPE == 'memory':
    cache = MemoryCacheBackend()
elif CACHE_TYPE == 'file':
    cache = FileCacheBackend()
else:  # 기본값은 'redis'
    # Redis 캐시는 비동기로 초기화되므로, 사용 시점에 연결됨
    cache = None  # 실제 사용 시 get_redis_connection()으로 초기화

__all__ = [
    "CacheBackend",
    "RedisCacheBackend",
    "MemoryCacheBackend",
    "FileCacheBackend",
    "cache_key_builder",
    "serialize_value",
    "deserialize_value",
    "cached",
    "invalidate_cache",
    "get_redis_connection",
    "cache",
]
