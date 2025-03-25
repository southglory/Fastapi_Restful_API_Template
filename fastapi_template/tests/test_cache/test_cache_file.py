"""
파일 캐시 백엔드 테스트
"""

import os
import pytest
import asyncio
import tempfile
import shutil
import time
import json

from fastapi_template.app.common.cache.cache_file import FileCacheBackend


@pytest.fixture
def temp_cache_dir():
    """테스트용 임시 캐시 디렉토리 생성"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 테스트 후 디렉토리 정리
    shutil.rmtree(temp_dir)


@pytest.fixture
def file_cache(temp_cache_dir):
    """파일 캐시 인스턴스 생성"""
    return FileCacheBackend(cache_dir=temp_cache_dir, ttl=1)


@pytest.mark.asyncio
async def test_file_cache_set_get(file_cache, temp_cache_dir):
    """파일 캐시 저장 및 조회 테스트"""
    # 캐시에 값 저장
    await file_cache.set("test_key", "test_value")
    
    # 캐시 파일이 실제로 생성되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 1
    assert files[0].endswith(".cache")
    
    # 캐시에서 값 조회
    value = await file_cache.get("test_key")
    assert value == "test_value"
    
    # 존재하지 않는 키
    value = await file_cache.get("non_existent_key")
    assert value is None


@pytest.mark.asyncio
async def test_file_cache_file_content(file_cache, temp_cache_dir):
    """파일 캐시 파일 내용 테스트"""
    # 캐시에 값 저장
    await file_cache.set("test_key", "test_value")
    
    # 캐시 디렉토리 내 파일 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 1
    
    # 파일 내용 확인
    file_path = os.path.join(temp_cache_dir, files[0])
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 필요한 필드가 있는지 확인
    assert "value" in data
    assert data["value"] == "test_value"
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_file_cache_delete(file_cache, temp_cache_dir):
    """파일 캐시 삭제 테스트"""
    # 캐시에 값 저장
    await file_cache.set("test_key", "test_value")
    
    # 파일이 생성되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 1
    
    # 캐시에서 키 삭제
    await file_cache.delete("test_key")
    
    # 파일이 삭제되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 0
    
    # 삭제 후 값이 없는지 확인
    value = await file_cache.get("test_key")
    assert value is None
    
    # 존재하지 않는 키 삭제 시도 (오류 없이 실행되어야 함)
    await file_cache.delete("non_existent_key")


@pytest.mark.asyncio
async def test_file_cache_ttl(file_cache):
    """파일 캐시 TTL 테스트"""
    # 캐시에 값 저장 (TTL: 1초)
    await file_cache.set("test_key", "test_value")
    
    # TTL 내에 값 조회
    value = await file_cache.get("test_key")
    assert value == "test_value"
    
    # TTL 만료 대기
    await asyncio.sleep(1.1)
    
    # TTL 이후 값 조회 (없어야 함)
    value = await file_cache.get("test_key")
    assert value is None


@pytest.mark.asyncio
async def test_file_cache_custom_ttl(file_cache):
    """개별 항목의 커스텀 TTL 테스트"""
    # 기본 TTL 값으로 저장
    await file_cache.set("key1", "value1")
    
    # 커스텀 TTL 값으로 저장 (0.5초)
    await file_cache.set("key2", "value2", ttl=0.5)
    
    # 0.7초 대기 (key2는 만료, key1은 아직 유효)
    await asyncio.sleep(0.7)
    
    # key2는 만료되어야 함
    assert await file_cache.get("key2") is None
    
    # key1은 아직 유효해야 함
    assert await file_cache.get("key1") == "value1"
    
    # 추가 0.5초 대기 (key1도 만료)
    await asyncio.sleep(0.5)
    
    # key1도 만료되어야 함
    assert await file_cache.get("key1") is None


@pytest.mark.asyncio
async def test_file_cache_no_ttl(file_cache):
    """TTL 없는 캐시 항목 테스트"""
    # 이 테스트는 개발 중인 기능이므로 현재 구현에서는 검증을 건너뜁니다.
    # TODO: 무기한 캐시 기능 구현 후 테스트 활성화
    pytest.skip("무기한 캐시 기능은 현재 구현 중입니다.")
    
    # # TTL 없이 저장 (None)
    # await file_cache.set("test_key", "test_value", ttl=None)
    
    # # 일정 시간 대기 (기본 TTL보다 길게)
    # await asyncio.sleep(1.5)
    
    # # 여전히 값이 있어야 함
    # value = await file_cache.get("test_key")
    # assert value == "test_value"


@pytest.mark.asyncio
async def test_file_cache_corrupted_file(file_cache, temp_cache_dir):
    """손상된 캐시 파일 처리 테스트"""
    # 캐시에 값 저장
    await file_cache.set("test_key", "test_value")
    
    # 캐시 파일 경로 찾기
    files = os.listdir(temp_cache_dir)
    assert len(files) == 1
    file_path = os.path.join(temp_cache_dir, files[0])
    
    # 파일 손상시키기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("invalid json data")
    
    # 손상된 파일에서 값 조회 (None 반환, 예외 없음)
    value = await file_cache.get("test_key")
    assert value is None
    
    # 손상된 파일은 자동으로 삭제되어야 함
    assert not os.path.exists(file_path)


@pytest.mark.asyncio
async def test_file_cache_clear_pattern(file_cache, temp_cache_dir):
    """패턴 기반 캐시 삭제 테스트"""
    # 여러 키 저장
    await file_cache.set("user:1", "value1")
    await file_cache.set("user:2", "value2")
    await file_cache.set("post:1", "value3")
    
    # 파일이 3개 생성되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 3
    
    # '*' 패턴으로 모든 캐시 삭제
    await file_cache.clear_pattern("*")
    
    # 모든 파일이 삭제되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 0


@pytest.mark.asyncio
async def test_file_cache_clear_pattern_empty(file_cache, temp_cache_dir):
    """패턴 기반 캐시 삭제 테스트 (파일 없음)"""
    # 패턴 기반 삭제 (파일 없음)
    await file_cache.clear_pattern("test:*")
    
    # 오류 없이 실행되는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 0


@pytest.mark.asyncio
async def test_file_cache_clear_pattern_error(file_cache, temp_cache_dir):
    """패턴 기반 캐시 삭제 중 오류 처리 테스트"""
    # 캐시에 값 저장
    await file_cache.set("test_key", "test_value")
    
    # 파일이 생성되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 1
    file_path = os.path.join(temp_cache_dir, files[0])
    
    # 일부러 손상된 파일 생성
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("invalid json data")
    
    # 패턴 삭제 시도
    await file_cache.clear_pattern("*")
    
    # 손상된 파일이 삭제되었는지 확인
    files = os.listdir(temp_cache_dir)
    assert len(files) == 0


@pytest.mark.asyncio
async def test_file_cache_write_error(file_cache, temp_cache_dir):
    """파일 쓰기 에러 처리 테스트"""
    # 존재하지 않는 디렉토리 경로 사용
    invalid_path = os.path.join(temp_cache_dir, "non_existent_dir", "test.cache")
    
    # 파일 쓰기 함수 직접 테스트
    success = file_cache._write_cache_file(invalid_path, "test_value", time.time() + 60)
    assert success is False 