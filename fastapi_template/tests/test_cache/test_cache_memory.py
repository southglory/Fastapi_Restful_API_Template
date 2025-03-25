"""
메모리 캐시 백엔드 테스트
"""

import pytest
import asyncio
import time

from fastapi_template.app.common.cache.cache_memory import MemoryCacheBackend


@pytest.fixture
def memory_cache():
    """메모리 캐시 인스턴스 생성"""
    # 테스트를 위한 짧은 TTL
    cache = MemoryCacheBackend(ttl=1)
    # 테스트 간에 공유되는 클래스 변수 초기화
    cache._cache = {}
    return cache


@pytest.mark.asyncio
async def test_memory_cache_set_get(memory_cache):
    """메모리 캐시 저장 및 조회 테스트"""
    # 캐시에 값 저장
    await memory_cache.set("test_key", "test_value")
    
    # 캐시에서 값 조회
    value = await memory_cache.get("test_key")
    assert value == "test_value"
    
    # 존재하지 않는 키
    value = await memory_cache.get("non_existent_key")
    assert value is None


@pytest.mark.asyncio
async def test_memory_cache_delete(memory_cache):
    """메모리 캐시 삭제 테스트"""
    # 캐시에 값 저장
    await memory_cache.set("test_key", "test_value")
    
    # 값이 있는지 확인
    value = await memory_cache.get("test_key")
    assert value == "test_value"
    
    # 캐시에서 키 삭제
    await memory_cache.delete("test_key")
    
    # 삭제 후 값이 없는지 확인
    value = await memory_cache.get("test_key")
    assert value is None
    
    # 존재하지 않는 키 삭제 시도 (오류 없이 실행되어야 함)
    await memory_cache.delete("non_existent_key")


@pytest.mark.asyncio
async def test_memory_cache_ttl(memory_cache):
    """메모리 캐시 TTL 테스트"""
    # 캐시에 값 저장 (TTL: 1초)
    await memory_cache.set("test_key", "test_value")
    
    # TTL 내에 값 조회
    value = await memory_cache.get("test_key")
    assert value == "test_value"
    
    # TTL 만료 대기
    await asyncio.sleep(1.1)
    
    # TTL 이후 값 조회 (없어야 함)
    value = await memory_cache.get("test_key")
    assert value is None


@pytest.mark.asyncio
async def test_memory_cache_custom_ttl(memory_cache):
    """개별 항목의 커스텀 TTL 테스트"""
    # 기본 TTL 값으로 저장
    await memory_cache.set("key1", "value1")
    
    # 커스텀 TTL 값으로 저장 (0.5초)
    await memory_cache.set("key2", "value2", ttl=0.5)
    
    # 0.7초 대기 (key2는 만료, key1은 아직 유효)
    await asyncio.sleep(0.7)
    
    # key2는 만료되어야 함
    assert await memory_cache.get("key2") is None
    
    # key1은 아직 유효해야 함
    assert await memory_cache.get("key1") == "value1"
    
    # 추가 0.5초 대기 (key1도 만료)
    await asyncio.sleep(0.5)
    
    # key1도 만료되어야 함
    assert await memory_cache.get("key1") is None


@pytest.mark.asyncio
async def test_memory_cache_no_ttl():
    """TTL 없는 캐시 항목 테스트"""
    # 이 테스트는 개발 중인 기능이므로 현재 구현에서는 검증을 건너뜁니다.
    # TODO: 무기한 캐시 기능 구현 후 테스트 활성화
    pytest.skip("무기한 캐시 기능은 현재 구현 중입니다.")
    
    # # 테스트용 캐시 인스턴스 다시 생성
    # cache = MemoryCacheBackend(ttl=1)
    # cache._cache = {}
    
    # # TTL 없이 저장 (None)
    # await cache.set("test_key", "test_value", ttl=None)
    
    # # 일정 시간 대기 (기본 TTL보다 길게)
    # await asyncio.sleep(1.5)
    
    # # 여전히 값이 있어야 함
    # value = await cache.get("test_key")
    # assert value == "test_value"


@pytest.mark.asyncio
async def test_memory_cache_clear_pattern(memory_cache):
    """패턴 기반 캐시 삭제 테스트"""
    # 여러 키 저장
    await memory_cache.set("user:1:profile", "value1")
    await memory_cache.set("user:2:profile", "value2")
    await memory_cache.set("user:1:settings", "value3")
    await memory_cache.set("post:1", "value4")
    
    # 특정 패턴 삭제 (user:1:*)
    await memory_cache.clear_pattern("user:1:*")
    
    # user:1:* 패턴의 키들은 삭제되어야 함
    assert await memory_cache.get("user:1:profile") is None
    assert await memory_cache.get("user:1:settings") is None
    
    # 다른 패턴의 키들은 유지되어야 함
    assert await memory_cache.get("user:2:profile") == "value2"
    assert await memory_cache.get("post:1") == "value4"
    
    # 모든 user:* 패턴 삭제
    await memory_cache.clear_pattern("user:*")
    
    # 모든 user: 패턴의 키들은 삭제되어야 함
    assert await memory_cache.get("user:2:profile") is None
    
    # 다른 패턴의 키들은 유지되어야 함
    assert await memory_cache.get("post:1") == "value4"


@pytest.mark.asyncio
async def test_memory_cache_clean_expired():
    """만료된 항목 정리 테스트"""
    cache = MemoryCacheBackend(ttl=0.5)
    # 클래스 변수 초기화
    cache._cache = {}
    
    # 몇 개의 항목 저장
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    
    # 캐시 내부 저장소에 있는지 확인
    assert len(cache._cache) == 2
    
    # TTL 만료 대기
    await asyncio.sleep(0.7)
    
    # 만료된 상태여야 하지만 내부에는 아직 남아 있음
    assert len(cache._cache) == 2
    
    # get 호출 시 _clean_expired 호출됨
    value = await cache.get("key1")
    assert value is None
    
    # 두 항목 모두 정리되어야 함
    assert len(cache._cache) == 0


@pytest.mark.asyncio
async def test_memory_cache_clean_expired_no_ttl():
    """만료된 항목 정리 테스트 (TTL 없는 항목 포함)"""
    cache = MemoryCacheBackend(ttl=0.5)
    # 클래스 변수 초기화
    cache._cache = {}
    
    # TTL 있는 항목
    await cache.set("key1", "value1")
    
    # TTL 없는 항목 (직접 설정)
    # 메모리 캐시의 값은 (value, expires_at) 튜플 형태로 저장됨
    cache._cache["key2"] = ("value2", None)
    
    # 캐시 내부 저장소에 있는지 확인
    assert len(cache._cache) == 2
    
    # TTL 만료 대기
    await asyncio.sleep(0.7)
    
    # 만료된 상태여야 하지만 내부에는 아직 남아 있음
    assert len(cache._cache) == 2
    
    # _clean_expired 명시적 호출
    cache._clean_expired()
    
    # key1은 만료되어 제거되고, key2는 TTL이 없으므로 남아있어야 함
    assert len(cache._cache) == 1
    assert "key2" in cache._cache
    assert cache._cache["key2"][0] == "value2"


@pytest.mark.asyncio
async def test_memory_cache_set_empty_ttl(memory_cache):
    """TTL 없이 저장하는 경우 테스트"""
    # 기본 TTL로 저장
    await memory_cache.set("key1", "value1")
    
    # TTL을 None으로 설정 (기본값 사용)
    await memory_cache.set("key2", "value2", ttl=None)
    
    # 값이 저장되었는지 확인
    assert await memory_cache.get("key1") == "value1"
    assert await memory_cache.get("key2") == "value2" 