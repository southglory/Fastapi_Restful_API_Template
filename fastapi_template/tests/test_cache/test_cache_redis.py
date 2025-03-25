"""
Redis 캐시 백엔드 테스트
"""

import pytest
import sys
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

# 모듈 참조를 위한 import 순서 조정
import fastapi_template.app.common.cache.cache_redis
from fastapi_template.app.common.cache.cache_redis import (
    RedisCacheBackend, 
    get_redis_connection,
    cached,
    invalidate_cache
)


@pytest.fixture
def mock_redis_client():
    """Redis 클라이언트 Mock 객체 생성"""
    redis_client = AsyncMock()
    redis_client.get = AsyncMock(return_value="test_value")
    redis_client.set = AsyncMock()
    redis_client.delete = AsyncMock()
    redis_client.keys = AsyncMock(return_value=["key1", "key2"])
    
    return redis_client


def test_redis_connection_code():
    """Redis 연결 함수 소스 코드 확인"""
    # 함수 소스 코드 확인
    source = inspect.getsource(get_redis_connection)
    assert "redis_conn" in source
    assert "redis_url =" in source
    assert "return redis_conn" in source


@pytest.mark.asyncio
async def test_cached_decorator():
    """캐싱 데코레이터 테스트 (Redis 특화)"""
    # Redis 모듈 모킹
    with patch('fastapi_template.app.common.cache.cache_redis.get_redis_connection') as mock_get_conn, \
         patch('fastapi_template.app.common.cache.cache_redis.deserialize_value') as mock_deserialize, \
         patch('fastapi_template.app.common.cache.cache_redis.serialize_value') as mock_serialize:
        
        # 미리 캐싱된 경우
        mock_conn = AsyncMock()
        mock_conn.get = AsyncMock(return_value="cached_value")
        mock_get_conn.return_value = mock_conn
        mock_deserialize.return_value = "deserialized_value"
        
        # 데코레이터 적용 함수
        @cached("test")
        async def test_func(a, b):
            return a + b
            
        # 함수 호출
        result = await test_func(1, 2)
        
        # 캐시에서 가져온 값이 반환되었는지 확인
        assert result == "deserialized_value"
        mock_conn.get.assert_called_once()
        mock_deserialize.assert_called_once_with("cached_value")
        
        # 캐시가 없는 경우
        mock_conn.get = AsyncMock(return_value=None)
        mock_serialize.return_value = "serialized_value"
        
        # 함수 호출
        result = await test_func(3, 4)
        
        # 원본 함수가 실행되고 결과가 캐싱되었는지 확인
        assert result == 7  # 원본 함수의 결과
        mock_conn.set.assert_called_once()
        mock_serialize.assert_called_once_with(7)


@pytest.mark.asyncio
async def test_invalidate_cache_decorator():
    """캐시 무효화 데코레이터 테스트 (Redis 특화)"""
    # Redis 모듈 모킹
    with patch('fastapi_template.app.common.cache.cache_redis.get_redis_connection') as mock_get_conn:
        
        mock_conn = AsyncMock()
        mock_conn.keys = AsyncMock(return_value=["key1", "key2"])
        mock_conn.delete = AsyncMock()
        mock_get_conn.return_value = mock_conn
        
        # 데코레이터 적용 함수
        @invalidate_cache("test:*")
        async def test_func():
            return "result"
            
        # 함수 호출
        result = await test_func()
        
        # 결과 확인
        assert result == "result"
        
        # 캐시 무효화 확인
        mock_get_conn.assert_called_once()


@pytest.mark.asyncio
async def test_redis_cache_backend(mock_redis_client):
    """Redis 캐시 백엔드 메서드 테스트"""
    # 캐시 인스턴스 생성
    cache = RedisCacheBackend(mock_redis_client, ttl=60)
    
    # get 테스트
    value = await cache.get("test_key")
    assert value == "test_value"
    mock_redis_client.get.assert_called_once_with("test_key")
    
    # set 테스트
    await cache.set("test_key", "new_value")
    mock_redis_client.set.assert_called_once_with("test_key", "new_value", ex=60)
    
    # 커스텀 TTL로 set 테스트
    await cache.set("test_key", "new_value", ttl=120)
    mock_redis_client.set.assert_called_with("test_key", "new_value", ex=120)
    
    # delete 테스트
    await cache.delete("test_key")
    mock_redis_client.delete.assert_called_once_with("test_key")
    
    # clear_pattern 테스트
    await cache.clear_pattern("test:*")
    mock_redis_client.keys.assert_called_once_with("test:*")
    mock_redis_client.delete.assert_called_with("key1", "key2") 