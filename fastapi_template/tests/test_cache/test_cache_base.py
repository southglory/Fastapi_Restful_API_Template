"""
캐시 모듈 기본 기능 테스트
"""

import pytest
import pickle
import base64
import json
from pydantic import BaseModel
from typing import Optional

from fastapi_template.app.common.cache.cache_base import (
    cache_key_builder,
    serialize_value,
    deserialize_value,
    CacheBackend
)


# 테스트용 커스텀 객체 (전역 레벨에 정의하여 Pickle 가능하도록 함)
class CustomObject:
    def __init__(self, value):
        self.value = value


def test_cache_key_builder():
    """캐시 키 생성 유틸리티 테스트"""
    # 기본 접두사만 있는 경우
    key = cache_key_builder("test")
    assert key == "test"
    
    # 위치 인자가 있는 경우
    key = cache_key_builder("users", 123, "profile")
    assert key == "users:123:profile"
    
    # 키워드 인자가 있는 경우 (정렬됨)
    key = cache_key_builder("items", limit=10, offset=20)
    assert key == "items:limit:10:offset:20"
    
    # 복합 케이스
    key = cache_key_builder("data", 123, type="user", active=True)
    assert key == "data:123:active:True:type:user"


def test_serialize_value_primitive():
    """기본 데이터 타입 직렬화 테스트"""
    # 문자열
    assert serialize_value("test") == '"test"'
    
    # 정수
    assert serialize_value(123) == '123'
    
    # 부동소수점
    assert serialize_value(3.14) == '3.14'
    
    # 불리언
    assert serialize_value(True) == 'true'
    
    # 리스트
    assert serialize_value([1, 2, 3]) == '[1, 2, 3]'
    
    # 딕셔너리
    assert serialize_value({"name": "test"}) == '{"name": "test"}'


def test_serialize_value_pydantic():
    """Pydantic 모델 직렬화 테스트"""
    class User(BaseModel):
        id: int
        name: str
        active: bool = True
    
    user = User(id=1, name="test")
    serialized = serialize_value(user)
    
    # JSON 형식으로 직렬화되었는지 확인
    parsed = json.loads(serialized)
    assert parsed["id"] == 1
    assert parsed["name"] == "test"
    assert parsed["active"] is True


def test_serialize_value_complex():
    """복합 객체 직렬화 테스트"""
    obj = CustomObject("test")
    serialized = serialize_value(obj)
    
    # Base64로 인코딩된 Pickle 형식인지 확인
    try:
        # Base64 디코딩
        pickled_data = base64.b64decode(serialized.encode("utf-8"))
        # Pickle 역직렬화
        unpickled = pickle.loads(pickled_data)
        assert isinstance(unpickled, CustomObject)
        assert unpickled.value == "test"
    except Exception as e:
        pytest.fail(f"Pickle 직렬화 실패: {e}")


def test_deserialize_value_json():
    """JSON 값 역직렬화 테스트"""
    # 문자열
    assert deserialize_value('"test"') == "test"
    
    # 정수
    assert deserialize_value('123') == 123
    
    # 부동소수점
    assert deserialize_value('3.14') == 3.14
    
    # 불리언
    assert deserialize_value('true') == True
    
    # 리스트
    assert deserialize_value('[1, 2, 3]') == [1, 2, 3]
    
    # 딕셔너리
    assert deserialize_value('{"name": "test"}') == {"name": "test"}


def test_deserialize_value_pickle():
    """Pickle 값 역직렬화 테스트"""
    # 객체 생성
    obj = CustomObject("test")
    
    # 직접 Pickle 및 Base64 인코딩
    pickled_data = pickle.dumps(obj)
    encoded = base64.b64encode(pickled_data).decode("utf-8")
    
    # 역직렬화
    deserialized = deserialize_value(encoded)
    
    # 타입 및 값 확인
    assert isinstance(deserialized, CustomObject)
    assert deserialized.value == "test"


def test_deserialize_value_invalid():
    """유효하지 않은 값 역직렬화 테스트"""
    # JSON 형식이 아닌 일반 문자열
    value = "hello world"
    try:
        result = deserialize_value(value)
        assert result == value
    except Exception as e:
        pytest.fail(f"일반 문자열 역직렬화 실패: {e}")
    
    # Base64 형식이 아닌 문자열
    value = "!@#$%^&*()"
    try:
        result = deserialize_value(value)
        assert result == value
    except Exception as e:
        pytest.fail(f"비표준 문자열 역직렬화 실패: {e}")


class ConcreteCache(CacheBackend):
    """테스트용 구체적 캐시 구현"""
    
    def __init__(self):
        self.storage = {}
    
    async def get(self, key: str) -> Optional[str]:
        return self.storage.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        self.storage[key] = value
    
    async def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]
    
    async def clear_pattern(self, pattern: str) -> None:
        keys_to_delete = [k for k in self.storage.keys() if k.startswith(pattern.replace("*", ""))]
        for key in keys_to_delete:
            del self.storage[key]


def test_cache_backend_interface():
    """캐시 백엔드 인터페이스 테스트"""
    # 구체적인 구현 클래스 생성
    cache = ConcreteCache()
    
    # 인스턴스 타입 확인
    assert isinstance(cache, CacheBackend)
    
    # 필수 메서드가 모두 구현되었는지 확인
    assert hasattr(cache, 'get')
    assert hasattr(cache, 'set')
    assert hasattr(cache, 'delete')
    assert hasattr(cache, 'clear_pattern')


@pytest.mark.asyncio
async def test_cache_backend_abstract_methods():
    """캐시 백엔드 추상 메서드 테스트"""
    # 추상 클래스 직접 인스턴스화가 불가능하므로 메서드만 확인
    methods = ['get', 'set', 'delete', 'clear_pattern']
    
    for method_name in methods:
        method = getattr(CacheBackend, method_name)
        # 각 메서드가 동적으로 생성된 비동기 함수인지 확인
        assert method.__name__ == method_name
        assert hasattr(method, '__isabstractmethod__')
        assert method.__isabstractmethod__ is True


class TestConcreteCache(CacheBackend):
    """테스트용 추상 메서드를 구현하지 않은 캐시 클래스"""
    pass

@pytest.mark.asyncio
async def test_cache_base_abstract_get():
    """캐시 백엔드 추상 get 메서드 테스트"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        TestConcreteCache()
        
    # 상속 및 추상 메서드 테스트
    methods = ['get', 'set', 'delete', 'clear_pattern']
    for method_name in methods:
        method = getattr(CacheBackend, method_name)
        assert hasattr(method, '__isabstractmethod__')
        assert method.__isabstractmethod__ is True 