"""
캐시 데코레이터 기능 테스트
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi_template.app.common.cache.cache_redis import (
    cached,
    invalidate_cache,
    RedisCacheBackend
)


# 테스트용 캐시 백엔드 클래스 생성
class TestCache:
    def __init__(self):
        self.data = {}
        self.patterns = []
        
    async def get(self, key):
        return self.data.get(key)
        
    async def set(self, key, value, ttl=None):
        self.data[key] = value
        
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
            
    async def clear_pattern(self, pattern):
        self.patterns.append(pattern)
        keys_to_delete = [k for k in self.data.keys() if k.startswith(pattern.replace("*", ""))]
        for key in keys_to_delete:
            del self.data[key]


@pytest.fixture
def mock_redis_connection():
    """Redis 연결 모킹"""
    with patch('fastapi_template.app.common.cache.cache_redis.get_redis_connection') as mock:
        # 테스트용 캐시 인스턴스 반환
        test_cache = TestCache()
        mock.return_value = AsyncMock()
        
        # RedisCacheBackend의 메서드를 모킹하여 실제로 테스트용 캐시를 사용하도록 함
        with patch.object(RedisCacheBackend, 'get', test_cache.get), \
             patch.object(RedisCacheBackend, 'set', test_cache.set), \
             patch.object(RedisCacheBackend, 'delete', test_cache.delete), \
             patch.object(RedisCacheBackend, 'clear_pattern', test_cache.clear_pattern):
            
            yield test_cache


@pytest.mark.asyncio
async def test_cached_decorator(mock_redis_connection):
    """캐싱 데코레이터 테스트"""
    # 테스트용 함수에 캐싱 데코레이터 적용
    call_count = 0
    
    @cached(prefix="test", ttl=60)
    async def test_function(a, b):
        nonlocal call_count
        call_count += 1
        return a + b
    
    # 첫 번째 호출 - 캐시 미스
    result1 = await test_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # 같은 인자로 두 번째 호출 - 캐시 히트
    result2 = await test_function(1, 2)
    assert result2 == 3
    assert call_count == 1  # 함수 내부가 실행되지 않았음
    
    # 다른 인자로 세 번째 호출 - 캐시 미스
    result3 = await test_function(2, 3)
    assert result3 == 5
    assert call_count == 2


@pytest.mark.asyncio
async def test_cached_with_none_result(mock_redis_connection):
    """None 결과를 반환하는 함수의 캐싱 테스트"""
    call_count = 0
    
    @cached(prefix="test", ttl=60)
    async def test_function(value):
        nonlocal call_count
        call_count += 1
        return None
    
    # 첫 번째 호출
    result1 = await test_function(1)
    assert result1 is None
    assert call_count == 1
    
    # 두 번째 호출 - None 결과는 캐싱되지 않음
    result2 = await test_function(1)
    assert result2 is None
    assert call_count == 2  # 함수가 다시 실행됨


@pytest.mark.asyncio
async def test_cached_with_custom_key_builder(mock_redis_connection):
    """커스텀 키 생성기를 사용한 캐싱 테스트"""
    call_count = 0
    
    # 커스텀 키 생성기
    def custom_key_builder(prefix, *args, **kwargs):
        return f"{prefix}:custom:{args[0]}"
    
    @cached(prefix="test", ttl=60, key_builder=custom_key_builder)
    async def test_function(value, ignored=None):
        nonlocal call_count
        call_count += 1
        return value * 2
    
    # 첫 번째 호출
    result1 = await test_function(5, ignored="abc")
    assert result1 == 10
    assert call_count == 1
    
    # 같은 첫 번째 인자로 호출 (ignored 값이 달라도 캐시 히트)
    result2 = await test_function(5, ignored="xyz")
    assert result2 == 10
    assert call_count == 1  # 함수가 실행되지 않음
    
    # 다른 첫 번째 인자로 호출
    result3 = await test_function(10)
    assert result3 == 20
    assert call_count == 2


@pytest.mark.asyncio
async def test_invalidate_cache_decorator(mock_redis_connection):
    """캐시 무효화 데코레이터 테스트"""
    # 테스트용 데이터
    mock_redis_connection.data = {
        "user:1:profile": "data1",
        "user:2:profile": "data2",
        "post:1": "data3"
    }
    
    # 캐시 무효화 데코레이터 적용
    @invalidate_cache("user:*")
    async def update_user_data(user_id):
        return {"success": True}
    
    # 함수 호출 전 캐시 상태 확인
    assert len(mock_redis_connection.data) == 3
    
    # 함수 호출
    result = await update_user_data(1)
    assert result == {"success": True}
    
    # 패턴 호출 확인
    assert "user:*" in mock_redis_connection.patterns
    
    # user: 패턴의 캐시가 삭제되었는지 확인
    assert "user:1:profile" not in mock_redis_connection.data
    assert "user:2:profile" not in mock_redis_connection.data
    
    # 다른 패턴의 캐시는 유지되는지 확인
    assert "post:1" in mock_redis_connection.data


@pytest.mark.asyncio
async def test_cached_complex_arguments(mock_redis_connection):
    """복잡한 인자를 사용한 캐싱 테스트"""
    call_count = 0
    
    @cached(prefix="complex")
    async def test_function(a, b=None, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        return a
    
    # 다양한 인자 조합으로 호출
    await test_function(1)
    assert call_count == 1
    
    await test_function(1, 2)
    assert call_count == 2
    
    # (1, b=2)는 (1, 2)와 다른 캐시 키를 생성하므로 함수가 다시 호출됨
    # 현재 구현에서는 kwargs의 키 이름까지 포함하여 캐시 키를 생성함
    await test_function(1, b=2)
    assert call_count == 3
    
    # 같은 키워드 인자로 다시 호출 - 캐시 히트 발생
    await test_function(1, b=2)
    assert call_count == 3
    
    await test_function(1, 2, 3)
    assert call_count == 4
    
    await test_function(1, 2, x=3)
    assert call_count == 5
    
    # 같은 인자 조합으로 다시 호출
    await test_function(1, 2, x=3)
    assert call_count == 5  # 캐시 히트 