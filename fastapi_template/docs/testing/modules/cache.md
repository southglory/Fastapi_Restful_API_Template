# Cache 모듈 테스트 가이드

## 개요

`cache` 모듈은 애플리케이션의 성능을 향상시키기 위한 캐싱 기능을 제공합니다. 주로 Redis를 사용하여 데이터를 저장하고 검색하는 기능을 제공하며, 비동기 처리를 지원합니다. 외부 의존성(Redis)과 비동기 코드로 인해 테스트가 복잡할 수 있습니다.

## 테스트 용이성

- **난이도**: 어려움
- **이유**:
  - Redis 의존성으로 인해 통합 테스트가 필요함
  - 모킹을 통한 단위 테스트도 가능하나 설정이 복잡함
  - 비동기 코드로 인해 테스트 설정이 더 복잡함
  - 캐시 데코레이터와 같은 고급 기능 테스트가 까다로움

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **Redis 연결 관리**
   - 연결 풀 생성 및 관리
   - 연결 오류 처리
   - 자동 재연결 기능

2. **캐시 CRUD 작업**
   - 캐시 값 설정 (set)
   - 캐시 값 조회 (get)
   - 캐시 값 삭제 (delete)
   - 캐시 만료 시간 설정 (expire)

3. **캐시 데코레이터**
   - 함수 결과 캐싱
   - 캐시 키 생성 로직
   - 캐시 무효화 기능

## 테스트 접근법

Cache 모듈 테스트 시 다음 접근법을 권장합니다:

1. **모킹 기반 단위 테스트**: Redis 인스턴스를 모의 객체로 대체하여 외부 의존성 없이 테스트
2. **통합 테스트**: 실제 Redis 인스턴스나 테스트용 Redis 컨테이너를 사용한 테스트
3. **비동기 테스트**: pytest-asyncio를 사용하여 비동기 함수 테스트

## 테스트 예시

### Redis 클라이언트 모킹 테스트

```python
# tests/test_cache/test_redis_client.py
import pytest
from unittest.mock import patch, MagicMock
from app.common.cache.redis_client import get_redis_connection, RedisClient

# Redis 연결 테스트
def test_get_redis_connection():
    # Redis 클라이언트 모킹
    with patch('app.common.cache.redis_client.redis.asyncio.Redis') as mock_redis:
        # 모의 Redis 인스턴스 설정
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        
        # 연결 함수 호출
        client = get_redis_connection(
            host="localhost",
            port=6379,
            db=0,
            password=None
        )
        
        # 검증
        assert client == mock_instance
        mock_redis.assert_called_once_with(
            host="localhost", 
            port=6379, 
            db=0, 
            password=None,
            decode_responses=True
        )

# 연결 실패 테스트
def test_connection_error_handling():
    with patch('app.common.cache.redis_client.redis.asyncio.Redis') as mock_redis:
        # 연결 예외 발생 시뮬레이션
        mock_redis.side_effect = Exception("Connection failed")
        
        # 오류 처리 검증
        with pytest.raises(Exception) as exc:
            client = get_redis_connection()
        
        assert "Connection failed" in str(exc.value)
```

### 기본 캐시 작업 테스트

```python
# tests/test_cache/test_redis_operations.py
import pytest
from unittest.mock import patch, MagicMock
from app.common.cache.redis_client import RedisClient

@pytest.mark.asyncio
async def test_cache_set_get():
    # 모의 Redis 인스턴스 생성
    mock_redis = MagicMock()
    
    # set 메서드 설정
    mock_redis.set = MagicMock(return_value=True)
    
    # get 메서드 설정
    mock_redis.get = MagicMock(return_value="cached_value")
    
    # Redis 클라이언트 초기화
    with patch('app.common.cache.redis_client.get_redis_connection', return_value=mock_redis):
        client = RedisClient()
        
        # set 작업 테스트
        success = await client.set("test_key", "test_value", 60)
        assert success is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=60)
        
        # get 작업 테스트
        value = await client.get("test_key")
        assert value == "cached_value"
        mock_redis.get.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_cache_delete():
    mock_redis = MagicMock()
    mock_redis.delete = MagicMock(return_value=1)  # 1은 삭제된 키 수
    
    with patch('app.common.cache.redis_client.get_redis_connection', return_value=mock_redis):
        client = RedisClient()
        
        # delete 작업 테스트
        deleted_count = await client.delete("test_key")
        assert deleted_count == 1
        mock_redis.delete.assert_called_once_with("test_key")
```

### 캐시 데코레이터 테스트

```python
# tests/test_cache/test_cache_decorator.py
import pytest
from unittest.mock import patch, MagicMock
from app.common.cache.redis_client import cached, RedisClient

# 캐시 데코레이터 테스트
@pytest.mark.asyncio
async def test_cached_decorator():
    # 모의 Redis 인스턴스 설정
    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # 처음에는 캐시 미스
    mock_redis.set.return_value = True
    
    with patch('app.common.cache.redis_client.get_redis_connection', return_value=mock_redis):
        # 캐싱할 테스트 함수 정의
        call_count = 0
        
        @cached(prefix="test", ttl=60)
        async def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result:{param1}:{param2}"
        
        # 첫 번째 호출 (캐시 미스)
        result1 = await test_function("a", "b")
        assert result1 == "result:a:b"
        assert call_count == 1
        assert mock_redis.get.called
        assert mock_redis.set.called
        
        # 두 번째 호출에 대한 캐시 히트 시뮬레이션
        mock_redis.get.return_value = "result:a:b"
        
        # 두 번째 호출 (캐시 히트)
        result2 = await test_function("a", "b")
        assert result2 == "result:a:b"
        assert call_count == 1  # 함수가 다시 호출되지 않아야 함
```

### 캐시 키 생성 테스트

```python
# tests/test_cache/test_cache_keys.py
import pytest
import json
from app.common.cache.redis_client import generate_cache_key

def test_generate_cache_key():
    # 기본 캐시 키 생성
    key = generate_cache_key("test_prefix", ["arg1", "arg2"], {"key1": "value1"})
    
    # 기본 형식 검증
    assert key.startswith("test_prefix:")
    
    # 복잡한 케이스 테스트
    key = generate_cache_key(
        "complex",
        [1, "string", {"nested": "dict"}],
        {"option1": True, "option2": [1, 2, 3]}
    )
    
    # 키 포맷 검증
    assert key.startswith("complex:")
    
    # 동일한 입력에 대해 동일한 키 생성 확인
    key1 = generate_cache_key("test", [1, 2], {"a": "b"})
    key2 = generate_cache_key("test", [1, 2], {"a": "b"})
    assert key1 == key2
    
    # 다른 입력에 대해 다른 키 생성 확인
    key3 = generate_cache_key("test", [1, 3], {"a": "b"})
    assert key1 != key3
```

## 통합 테스트

실제 Redis 인스턴스를 사용한 통합 테스트:

```python
# tests/test_cache/test_redis_integration.py
import pytest
import redis.asyncio
from app.common.cache.redis_client import RedisClient, cached

# Redis 서버 정보 (테스트용)
TEST_REDIS_HOST = "localhost"
TEST_REDIS_PORT = 6379
TEST_REDIS_DB = 15  # 테스트용 별도 DB 사용

@pytest.fixture
async def redis_client():
    # 실제 Redis 연결
    client = RedisClient(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        db=TEST_REDIS_DB
    )
    
    # 테스트 전 Redis 데이터 초기화
    redis_conn = await client.get_connection()
    await redis_conn.flushdb()
    
    yield client
    
    # 테스트 후 정리
    redis_conn = await client.get_connection()
    await redis_conn.flushdb()

@pytest.mark.asyncio
async def test_integration_set_get(redis_client):
    # 실제 Redis에 데이터 설정
    await redis_client.set("integration_test_key", "integration_test_value", 10)
    
    # 데이터 조회
    value = await redis_client.get("integration_test_key")
    assert value == "integration_test_value"

@pytest.mark.asyncio
async def test_integration_cached_decorator(redis_client):
    # Redis 클라이언트 패치
    with patch('app.common.cache.redis_client.get_redis_connection', return_value=redis_client.redis):
        call_count = 0
        
        @cached(prefix="integration", ttl=10)
        async def cached_function(param):
            nonlocal call_count
            call_count += 1
            return f"value_{param}"
        
        # 첫 번째 호출 (캐시 미스)
        result1 = await cached_function("test")
        assert result1 == "value_test"
        assert call_count == 1
        
        # 두 번째 호출 (캐시 히트)
        result2 = await cached_function("test")
        assert result2 == "value_test"
        assert call_count == 1  # 함수가 다시 호출되지 않음
        
        # 다른 파라미터로 호출 (캐시 미스)
        result3 = await cached_function("different")
        assert result3 == "value_different"
        assert call_count == 2
```

## 모킹 전략

Cache 모듈 테스트 시 다음과 같은 모킹 전략을 사용할 수 있습니다:

1. **Redis 클라이언트 모킹**: `redis.asyncio.Redis` 클래스 자체를 모킹
2. **개별 메서드 모킹**: get, set, delete 등의 메서드만 모킹
3. **연결 함수 모킹**: `get_redis_connection` 함수를 모킹하여 테스트용 클라이언트 반환

## 테스트 커버리지 확인

Cache 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.cache tests/test_cache/
```

## 모범 사례

1. 단위 테스트와 통합 테스트를 모두 작성하되, CI/CD 환경에서는 단위 테스트를 중심으로 실행합니다.
2. 통합 테스트는 테스트용 Redis 인스턴스나 컨테이너를 사용하여 실제 환경과 격리합니다.
3. 캐시 키 생성 로직을 철저히 테스트하여 키 충돌이 발생하지 않도록 합니다.
4. 데코레이터 테스트 시 내부 함수 호출 횟수를 추적하여 캐싱 효과를 검증합니다.

## 주의사항

1. 테스트 시 실제 Redis 서버를 사용할 경우, 테스트 전용 DB 인덱스를 사용하고 테스트 후 데이터를 정리하세요.
2. 비동기 테스트에서 모킹할 때는 async/await 구문을 올바르게 처리해야 합니다.
3. Redis 연결 실패, 타임아웃 등의 오류 상황도 테스트하세요.
4. 병렬 테스트 실행 시 캐시 키 충돌에 주의하세요. 테스트마다 고유한 접두사를 사용하는 것이 좋습니다.
