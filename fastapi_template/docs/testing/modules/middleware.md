# Middleware 모듈 테스트 가이드

## 개요

`middleware` 모듈은 FastAPI 애플리케이션의 요청/응답 처리 파이프라인에 추가 기능을 제공합니다. 미들웨어는 요청이 라우트 핸들러에 도달하기 전이나 응답이 클라이언트에게 반환되기 전에 실행되는 함수로, 로깅, 인증, 예외 처리, 응답 수정 등의 기능을 담당합니다.

## 테스트 용이성

- **난이도**: 중간-어려움
- **이유**:
  - 요청/응답 사이클을 시뮬레이션해야 함
  - FastAPI의 TestClient를 사용한 통합 테스트 필요
  - 비동기 컨텍스트에서의 테스트가 복잡할 수 있음
  - 미들웨어 간의 상호작용 테스트가 필요할 수 있음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **요청 처리 미들웨어**
   - 요청 헤더 수정/추가
   - 요청 로깅/모니터링
   - 인증/권한 검증

2. **응답 처리 미들웨어**
   - 응답 헤더 수정/추가
   - 응답 본문 변환
   - 캐싱 헤더 추가

3. **예외 처리 미들웨어**
   - 예외 캐치 및 변환
   - 오류 응답 표준화
   - 디버깅 정보 추가/제거

## 테스트 접근법

Middleware 모듈 테스트 시 다음 접근법을 권장합니다:

1. **통합 테스트**: FastAPI TestClient를 사용하여 전체 요청/응답 사이클 테스트
2. **단위 테스트**: 미들웨어 함수 자체를 모의 Request/Response 객체와 함께 테스트
3. **시나리오 테스트**: 다양한 요청 시나리오에서 미들웨어 동작 검증

## 테스트 예시

### 로깅 미들웨어 테스트

```python
# tests/test_middleware/test_logging_middleware.py
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.common.middleware.logging_middleware import LoggingMiddleware

# 테스트용 앱 설정
@pytest.fixture
def app():
    app = FastAPI()
    
    # 로깅 미들웨어 추가
    app.add_middleware(LoggingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_logging_middleware(client):
    # 로거 모킹
    with patch("app.common.middleware.logging_middleware.logger") as mock_logger:
        # 테스트 요청 실행
        response = client.get("/test")
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json() == {"message": "test"}
        
        # 로거 호출 확인
        assert mock_logger.info.called
        # 로그 메시지에 요청 경로가 포함되어 있는지 확인
        log_calls = mock_logger.info.call_args_list
        assert any("/test" in str(call) for call in log_calls)

def test_logging_middleware_exception(client, app):
    # 예외 발생 엔드포인트 추가
    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    # 로거 모킹
    with patch("app.common.middleware.logging_middleware.logger") as mock_logger:
        # 테스트 요청 실행 (예외 발생)
        response = client.get("/error")
        
        # 응답은 500이어야 함
        assert response.status_code == 500
        
        # 오류 로깅 확인
        assert mock_logger.error.called
        # 로그 메시지에 오류 메시지가 포함되어 있는지 확인
        error_call = mock_logger.error.call_args_list[0]
        assert "Test error" in str(error_call)
```

### 요청 ID 미들웨어 테스트

```python
# tests/test_middleware/test_request_id_middleware.py
import pytest
import re
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.common.middleware.request_id_middleware import RequestIDMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    
    # 요청 ID 미들웨어 추가
    app.add_middleware(RequestIDMiddleware)
    
    @app.get("/test")
    async def test_endpoint(request):
        # 미들웨어에서 설정한 요청 ID를 응답에 포함
        return {"request_id": request.state.request_id}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_request_id_generation(client):
    # 테스트 요청 실행
    response = client.get("/test")
    
    # 응답 확인
    assert response.status_code == 200
    
    # 응답 헤더에 X-Request-ID가 있는지 확인
    assert "X-Request-ID" in response.headers
    
    # 요청 ID 형식 확인 (UUID 형식)
    request_id = response.headers["X-Request-ID"]
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    assert re.match(uuid_pattern, request_id, re.IGNORECASE)
    
    # 응답 본문의 request_id가 헤더의 값과 일치하는지 확인
    assert response.json()["request_id"] == request_id

def test_custom_request_id(client):
    # 커스텀 요청 ID 헤더 추가
    custom_id = "test-request-id-123"
    response = client.get("/test", headers={"X-Request-ID": custom_id})
    
    # 응답 확인
    assert response.status_code == 200
    
    # 응답 헤더의 요청 ID가 제공한 값과 일치하는지 확인
    assert response.headers["X-Request-ID"] == custom_id
    
    # 응답 본문의 request_id가 제공한 값과 일치하는지 확인
    assert response.json()["request_id"] == custom_id
```

### 속도 제한 미들웨어 테스트

```python
# tests/test_middleware/test_rate_limiter.py
import pytest
import time
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.common.middleware.rate_limiter import RateLimiterMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    
    # 엄격한 제한의 속도 제한 미들웨어 추가 (테스트용)
    app.add_middleware(
        RateLimiterMiddleware,
        limit=3,  # 3회까지만 허용
        window=60,  # 60초 동안
    )
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_rate_limiter_allowed(client):
    # 허용된 요청 횟수 내에서 테스트
    for _ in range(3):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "test"}
        
        # 응답 헤더에 남은 요청 횟수 확인
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Reset" in response.headers

def test_rate_limiter_exceeded(client):
    # 허용된 요청 횟수를 초과하는 테스트
    
    # 처음 3번은 성공해야 함
    for _ in range(3):
        response = client.get("/test")
        assert response.status_code == 200
    
    # 4번째 요청은 429 Too Many Requests 오류가 발생해야 함
    response = client.get("/test")
    assert response.status_code == 429
    assert "Retry-After" in response.headers

def test_rate_limiter_different_paths(client):
    # 다른 경로에 대한 속도 제한 테스트
    # (경로별로 별도의 제한이 적용되는 경우)
    
    # '/test' 경로에 대한 요청 3회
    for _ in range(3):
        client.get("/test")
    
    # 추가 엔드포인트 정의 (app 픽스처 내에서 정의된 후에는 할 수 없으므로 여기서 처리)
    @client.app.get("/another")
    async def another_endpoint():
        return {"message": "another"}
    
    # '/another' 경로는 별도의 제한이 적용되므로 성공해야 함
    response = client.get("/another")
    assert response.status_code == 200
```

### 비동기 미들웨어 단위 테스트

```python
# tests/test_middleware/test_async_middleware.py
import pytest
from fastapi import Request, Response
from starlette.datastructures import Headers
from starlette.types import Scope, Receive, Send
from unittest.mock import AsyncMock, MagicMock
from app.common.middleware.correlation_middleware import CorrelationMiddleware

@pytest.mark.asyncio
async def test_correlation_middleware_unit():
    # 미들웨어 인스턴스 생성
    middleware = CorrelationMiddleware(app=AsyncMock())
    
    # 모의 scope (요청 정보)
    scope = {
        "type": "http",
        "headers": [(b"x-correlation-id", b"test-correlation-id")]
    }
    
    # 모의 receive, send 함수
    receive = AsyncMock()
    send = AsyncMock()
    
    # 미들웨어 호출
    await middleware(scope, receive, send)
    
    # app 호출 확인 (미들웨어가 다음 미들웨어/앱을 호출했는지)
    assert middleware.app.called
    
    # app 호출 인자 확인
    call_args = middleware.app.call_args
    assert call_args[0][0] == scope  # scope 전달 확인
    assert call_args[0][1] == receive  # receive 함수 전달 확인
    
    # send 함수가 래핑되었는지 확인 (응답 수정을 위해)
    assert call_args[0][2] != send  # 원래 send가 아닌 다른 함수가 전달되어야 함
```

## 통합 테스트

여러 미들웨어가 결합된 경우의 통합 테스트:

```python
# tests/test_middleware/test_middleware_integration.py
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.common.middleware.logging_middleware import LoggingMiddleware
from app.common.middleware.request_id_middleware import RequestIDMiddleware
from app.common.middleware.correlation_middleware import CorrelationMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    
    # 여러 미들웨어 추가 (실행 순서 중요)
    app.add_middleware(LoggingMiddleware)  # 마지막에 실행됨
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RequestIDMiddleware)  # 첫 번째로 실행됨
    
    @app.get("/test")
    async def test_endpoint(request: Request):
        # 미들웨어에서 설정한 속성들을 응답에 포함
        return {
            "request_id": getattr(request.state, "request_id", None),
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_middleware_chain(client):
    # 로거 모킹
    with patch("app.common.middleware.logging_middleware.logger") as mock_logger:
        # 테스트 요청 실행
        response = client.get(
            "/test", 
            headers={"X-Correlation-ID": "test-correlation"}
        )
        
        # 응답 확인
        assert response.status_code == 200
        data = response.json()
        
        # RequestID 미들웨어가 요청 ID를 설정했는지 확인
        assert "request_id" in data
        assert data["request_id"] is not None
        
        # CorrelationID 미들웨어가 상관 ID를 설정했는지 확인
        assert "correlation_id" in data
        assert data["correlation_id"] == "test-correlation"
        
        # LoggingMiddleware가 로깅을 수행했는지 확인
        assert mock_logger.info.called
        
        # 로그에 요청 ID와 상관 ID가 포함되어 있는지 확인
        log_message = str(mock_logger.info.call_args)
        assert data["request_id"] in log_message
        assert "test-correlation" in log_message
```

## 모킹 전략

Middleware 테스트 시 다음과 같은 모킹 전략을 활용할 수 있습니다:

1. **Request/Response 모킹**: `starlette.requests.Request` 및 `starlette.responses.Response` 객체 모킹
2. **Scope/Receive/Send 모킹**: ASGI 인터페이스의 `scope`, `receive`, `send` 함수 모킹
3. **외부 서비스 모킹**: 미들웨어가 사용하는 로거, 캐시, 인증 서비스 등 모킹

## 테스트 커버리지 확인

Middleware 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.middleware tests/test_middleware/
```

## 모범 사례

1. **기능별 분리**: 각 미들웨어의 기능을 독립적으로 테스트하세요.
2. **시나리오 테스트**: 정상 케이스, 오류 케이스, 예외 케이스 등 다양한 시나리오를 테스트하세요.
3. **실행 순서 확인**: 여러 미들웨어가 결합된 경우 실행 순서가 올바른지 확인하세요.
4. **성능 테스트**: 미들웨어가 응답 시간에 미치는 영향을 테스트하세요.

## 주의사항

1. **비동기 코드 테스트**: 미들웨어는 대부분 비동기로 동작하므로 `pytest-asyncio`를 사용하여 테스트하세요.
2. **요청 컨텍스트**: 테스트에서 요청 컨텍스트를 올바르게 설정하는 것이 중요합니다.
3. **상태 관리**: 미들웨어가 요청 간에 상태를 저장하는 경우 테스트 간 격리에 주의하세요.
4. **에러 전파**: 미들웨어에서 발생한 오류가 올바르게 처리되는지 확인하세요.
5. **헤더 케이스 민감성**: HTTP 헤더 이름은 대소문자를 구분하지 않으므로 테스트에서 이를 고려하세요.
