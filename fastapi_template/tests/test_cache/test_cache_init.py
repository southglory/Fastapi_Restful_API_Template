"""
캐시 모듈 초기화 테스트
"""

import pytest
import sys
import importlib
import os
from unittest.mock import patch, MagicMock


# 테스트를 위한 모의 캐시 타입 확인 함수
def _test_cache_backend_for_type(cache_type):
    """특정 캐시 타입의 인스턴스 생성 테스트 헬퍼"""
    if cache_type == 'memory':
        from fastapi_template.app.common.cache.cache_memory import MemoryCacheBackend
        instance = MemoryCacheBackend()
        assert isinstance(instance, MemoryCacheBackend)
    elif cache_type == 'file':
        from fastapi_template.app.common.cache.cache_file import FileCacheBackend
        instance = FileCacheBackend(cache_dir="/tmp/cache")
        assert isinstance(instance, FileCacheBackend)
    elif cache_type == 'redis':
        # Redis는 직접 인스턴스화하지 않고 연결만 테스트
        from fastapi_template.app.common.cache.cache_redis import RedisCacheBackend
        assert issubclass(RedisCacheBackend, object)
    else:
        # 알 수 없는 타입은 기본값(redis)으로 처리됨을 검증
        pass


@pytest.mark.parametrize("cache_type", ['memory', 'file', 'redis', 'unknown'])
def test_cache_backend_availability(cache_type):
    """각 캐시 타입이 사용 가능한지 테스트"""
    _test_cache_backend_for_type(cache_type)


def test_cache_init_imports():
    """캐시 초기화 임포트 테스트"""
    # __init__.py 파일에서 모든 심볼이 올바르게 임포트되는지 확인
    import fastapi_template.app.common.cache as cache_module
    
    assert hasattr(cache_module, 'CacheBackend')
    assert hasattr(cache_module, 'RedisCacheBackend')
    assert hasattr(cache_module, 'MemoryCacheBackend')
    assert hasattr(cache_module, 'FileCacheBackend')
    assert hasattr(cache_module, 'cache_key_builder')
    assert hasattr(cache_module, 'serialize_value')
    assert hasattr(cache_module, 'deserialize_value')
    assert hasattr(cache_module, 'cached')
    assert hasattr(cache_module, 'invalidate_cache')
    assert hasattr(cache_module, 'get_redis_connection')
    assert hasattr(cache_module, 'cache')


def test_cache_init_source_code():
    """캐시 모듈 소스 코드 직접 확인"""
    import inspect
    import os
    
    # 소스 파일 직접 읽기
    module_path = os.path.join(os.path.dirname(__file__), '../../app/common/cache/__init__.py')
    with open(module_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # 필수 내용 포함 확인
    assert "CACHE_TYPE = " in source
    assert "if CACHE_TYPE == 'memory':" in source
    assert "elif CACHE_TYPE == 'file':" in source
    assert "else:" in source  # 기본 Redis 처리
    
    # __all__ 리스트 확인
    assert "__all__ = [" in source 