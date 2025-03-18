# Monitoring 모듈 테스트 가이드

이 문서는 FastAPI 템플릿 프로젝트의 Monitoring 모듈을 테스트하는 방법에 대한 상세 가이드를 제공합니다.

## 개요

Monitoring 모듈은 애플리케이션의 상태 모니터링, 로깅, 성능 측정, 알림 기능을 담당합니다. 이 모듈의 테스트는 다음과 같은 요소를 포함합니다:

- 로깅 기능 테스트
- 헬스 체크 엔드포인트 테스트
- 메트릭 수집 및 보고 기능 테스트
- 알림 시스템 테스트
- 분산 추적 기능 테스트

## 테스트 난이도: 어려움

Monitoring 모듈은 외부 시스템에 의존하는 경우가 많고, 비동기 코드와 사이드 이펙트가 많아 테스트하기 어려운 편입니다.

## 테스트 대상

```
app/
├── monitoring/
│   ├── __init__.py
│   ├── logger.py          # 로깅 설정 및 유틸리티
│   ├── metrics.py         # 메트릭 수집 및 보고
│   ├── health.py          # 헬스 체크 기능
│   ├── alerts.py          # 알림 시스템
│   └── tracing.py         # 분산 추적 기능
```

## 테스트 디렉토리 구조

```
tests/
├── test_monitoring/
│   ├── __init__.py
│   ├── test_logger.py     # 로깅 기능 테스트
│   ├── test_metrics.py    # 메트릭 수집 테스트
│   ├── test_health.py     # 헬스 체크 테스트
│   ├── test_alerts.py     # 알림 시스템 테스트
│   └── test_tracing.py    # 분산 추적 테스트
```

## 테스트 접근 방식

### 1. 로깅 기능 테스트

로깅 기능은 파일, 콘솔, 외부 서비스 등 다양한 출력 대상을 가질 수 있습니다. 테스트할 때는 모의(mock) 객체를 사용하여 로깅 출력을 검증합니다.

#### 예시: 로거 초기화 테스트

```python
# tests/test_monitoring/test_logger.py
import logging
import pytest
from unittest.mock import patch, MagicMock
from app.monitoring.logger import setup_logger, get_logger

def test_setup_logger():
    # 로거 설정 테스트
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        setup_logger("test", level=logging.INFO)
        
        # 로거 이름 확인
        mock_get_logger.assert_called_once_with("test")
        # 로그 레벨 설정 확인
        assert mock_logger.setLevel.called
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        # 핸들러 추가 확인
        assert mock_logger.addHandler.called

def test_get_logger():
    # 로거 가져오기 테스트
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger = get_logger("test_module")
        
        # 올바른 이름으로 로거 요청 확인
        mock_get_logger.assert_called_once_with("test_module")
```

#### 예시: 로그 메시지 테스트

```python
# tests/test_monitoring/test_logger.py (확장)
import tempfile
import os

def test_log_message_to_file():
    # 파일로 로그 메시지 출력 테스트
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # 파일 핸들러로 로거 설정
        with patch('app.monitoring.logger.setup_logger') as mock_setup:
            from app.monitoring.logger import log_to_file
            
            # 파일에 로그 기록
            log_to_file("테스트 메시지", "ERROR", file_path=temp_path)
            
            # 파일에 로그가 기록되었는지 확인
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "테스트 메시지" in content
                assert "ERROR" in content
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.unlink(temp_path)
```

### 2. 메트릭 수집 테스트

메트릭 수집은 일반적으로 외부 메트릭 서비스(Prometheus, Datadog 등)에 의존합니다. 테스트에서는 외부 의존성을 모의하여 검증합니다.

#### 예시: 메트릭 수집 테스트

```python
# tests/test_monitoring/test_metrics.py
import pytest
from unittest.mock import patch, MagicMock
from app.monitoring.metrics import (
    increment_counter, 
    record_timing, 
    gauge_set, 
    initialize_metrics
)

def test_initialize_metrics():
    # 메트릭 초기화 테스트
    with patch('app.monitoring.metrics.PrometheusClient') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        initialize_metrics(app_name="test_app")
        
        # 클라이언트 초기화 확인
        mock_client.assert_called_once_with(app_name="test_app")
        
        # 기본 메트릭 등록 확인 (예: 애플리케이션 시작 카운터)
        assert mock_instance.register_counter.called

def test_increment_counter():
    # 카운터 증가 테스트
    with patch('app.monitoring.metrics._client') as mock_client:
        increment_counter("api_calls", tags={"endpoint": "/users"})
        
        # 카운터 증가 호출 확인
        mock_client.increment.assert_called_once_with(
            "api_calls", 1, tags={"endpoint": "/users"}
        )

def test_record_timing():
    # 타이밍 기록 테스트
    with patch('app.monitoring.metrics._client') as mock_client:
        record_timing("api_response_time", 0.35, tags={"endpoint": "/users"})
        
        # 타이밍 기록 호출 확인
        mock_client.timing.assert_called_once_with(
            "api_response_time", 0.35, tags={"endpoint": "/users"}
        )

def test_gauge_set():
    # 게이지 설정 테스트
    with patch('app.monitoring.metrics._client') as mock_client:
        gauge_set("active_users", 42)
        
        # 게이지 설정 호출 확인
        mock_client.gauge.assert_called_once_with("active_users", 42, tags=None)
```

### 3. 헬스 체크 테스트

헬스 체크 기능은 애플리케이션 및 의존 서비스(데이터베이스, 캐시 등)의 상태를 확인합니다. 통합 테스트 및 모의 응답을 사용하여 검증합니다.

#### 예시: 헬스 체크 테스트

```python
# tests/test_monitoring/test_health.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.monitoring.health import (
    HealthStatus, 
    check_database_health, 
    check_redis_health,
    setup_health_routes
)

@pytest.fixture
def test_app():
    app = FastAPI()
    # 헬스 체크 라우트 설정
    setup_health_routes(app)
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_health_endpoint(client):
    # 헬스 체크 엔드포인트 테스트
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "timestamp" in data

def test_database_health_check():
    # 데이터베이스 헬스 체크 테스트
    with patch('app.db.engine.connect') as mock_connect:
        # 정상 케이스
        mock_connect.return_value = MagicMock()
        
        status = check_database_health()
        
        assert status.status == HealthStatus.HEALTHY
        
        # 오류 케이스
        mock_connect.side_effect = Exception("DB Connection Error")
        
        status = check_database_health()
        
        assert status.status == HealthStatus.UNHEALTHY
        assert "DB Connection Error" in status.details

def test_redis_health_check():
    # Redis 헬스 체크 테스트
    with patch('app.cache.redis_client.ping') as mock_ping:
        # 정상 케이스
        mock_ping.return_value = True
        
        status = check_redis_health()
        
        assert status.status == HealthStatus.HEALTHY
        
        # 오류 케이스
        mock_ping.side_effect = Exception("Redis Connection Error")
        
        status = check_redis_health()
        
        assert status.status == HealthStatus.UNHEALTHY
        assert "Redis Connection Error" in status.details
```

### 4. 알림 시스템 테스트

알림 시스템은 이메일, 슬랙, 기타 알림 채널과 같은 외부 서비스에 의존합니다. 모의 객체를 사용하여 알림이 올바르게 전송되는지 테스트합니다.

#### 예시: 알림 시스템 테스트

```python
# tests/test_monitoring/test_alerts.py
import pytest
from unittest.mock import patch, MagicMock
from app.monitoring.alerts import (
    send_alert, 
    send_slack_alert, 
    send_email_alert, 
    AlertLevel
)

def test_send_alert():
    # 통합 알림 전송 테스트
    with patch('app.monitoring.alerts.send_slack_alert') as mock_slack:
        with patch('app.monitoring.alerts.send_email_alert') as mock_email:
            # 중요 알림은 슬랙과 이메일 모두 전송
            send_alert(
                "높은 CPU 사용량", 
                "서버 CPU 사용량이 90%를 초과했습니다.", 
                level=AlertLevel.CRITICAL
            )
            
            mock_slack.assert_called_once()
            mock_email.assert_called_once()
            
            # 슬랙 호출 인자 확인
            slack_args = mock_slack.call_args[0]
            assert "높은 CPU 사용량" in slack_args[0]
            assert "90%" in slack_args[1]
            
            # 낮은 레벨 알림은 슬랙만 전송
            mock_slack.reset_mock()
            mock_email.reset_mock()
            
            send_alert(
                "디스크 공간 부족", 
                "디스크 공간이 75%를 초과했습니다.", 
                level=AlertLevel.WARNING
            )
            
            mock_slack.assert_called_once()
            assert not mock_email.called

def test_send_slack_alert():
    # 슬랙 알림 전송 테스트
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_slack_alert(
            "API 오류 증가", 
            "지난 5분간 API 오류율이 10%를 초과했습니다."
        )
        
        assert result is True
        assert mock_post.called
        
        # 요청 형식 검증
        call_args = mock_post.call_args
        assert "hooks.slack.com" in call_args[0][0]
        
        # 요청 내용 검증
        payload = call_args[1]["json"]
        assert "API 오류 증가" in str(payload)
        assert "10%" in str(payload)
        
        # 오류 케이스
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = send_slack_alert("테스트", "테스트 메시지")
        
        assert result is False

def test_send_email_alert():
    # 이메일 알림 전송 테스트
    with patch('app.monitoring.alerts.send_email') as mock_send:
        result = send_email_alert(
            "서버 다운", 
            "프로덕션 서버가 응답하지 않습니다."
        )
        
        assert result is True
        assert mock_send.called
        
        # 이메일 형식 검증
        call_args = mock_send.call_args
        assert "서버 다운" in call_args[1]["subject"]
        assert "프로덕션 서버" in call_args[1]["body"]
        assert "alerts@example.com" in call_args[1]["to_emails"]
```

### 5. 분산 추적 테스트

분산 추적은 요청의 전체 경로를 추적하는 기능으로, 일반적으로 OpenTelemetry, Jaeger, Zipkin 등의 시스템과 연동됩니다. 컨텍스트 전파와 추적 데이터 수집을 테스트합니다.

#### 예시: 분산 추적 테스트

```python
# tests/test_monitoring/test_tracing.py
import pytest
from unittest.mock import patch, MagicMock
from app.monitoring.tracing import (
    setup_tracing, 
    create_span, 
    get_current_span, 
    add_span_attribute
)

def test_setup_tracing():
    # 추적 시스템 초기화 테스트
    with patch('opentelemetry.sdk.trace.TracerProvider') as mock_provider:
        with patch('opentelemetry.sdk.trace.export.BatchSpanProcessor') as mock_processor:
            mock_instance = MagicMock()
            mock_provider.return_value = mock_instance
            
            setup_tracing(service_name="test-service")
            
            # 트레이서 프로바이더 생성 확인
            mock_provider.assert_called_once()
            
            # 서비스 이름 설정 확인
            resource_args = mock_instance.resource.merge.call_args
            assert "service.name" in str(resource_args)
            assert "test-service" in str(resource_args)
            
            # 기본 내보내기 설정 확인
            assert mock_processor.called

def test_create_span():
    # 스팬 생성 테스트
    with patch('app.monitoring.tracing._tracer') as mock_tracer:
        mock_span = MagicMock()
        mock_context = MagicMock()
        mock_span.__enter__.return_value = mock_context
        mock_tracer.start_as_current_span.return_value = mock_span
        
        # 컨텍스트 매니저로 스팬 생성
        with create_span("test-operation") as span:
            # 올바른 이름으로 스팬 생성 확인
            mock_tracer.start_as_current_span.assert_called_once_with(
                "test-operation", None
            )
            
            # 반환된 스팬이 올바른지 확인
            assert span == mock_context
            
            # 속성 추가
            span.set_attribute("test-key", "test-value")
            mock_context.set_attribute.assert_called_once_with(
                "test-key", "test-value"
            )

def test_add_span_attribute():
    # 스팬 속성 추가 테스트
    with patch('app.monitoring.tracing.get_current_span') as mock_get_span:
        mock_span = MagicMock()
        mock_get_span.return_value = mock_span
        
        add_span_attribute("user.id", "123")
        
        # 현재 스팬 조회 확인
        mock_get_span.assert_called_once()
        
        # 스팬 속성 설정 확인
        mock_span.set_attribute.assert_called_once_with("user.id", "123")
```

## 모의(Mock) 객체 사용

모니터링 모듈은 외부 서비스에 크게 의존하므로, 모의 객체를 적극 활용하여 테스트합니다.

### 모의 라이브러리 선택

- **단순 모의**: `unittest.mock`의 `patch`, `MagicMock` 등 사용
- **HTTP 요청 모의**: `responses`, `requests-mock` 라이브러리 활용
- **분산 시스템 모의**: `opentelemetry.sdk.trace.export.InMemorySpanExporter` 활용

### 모의 객체 사용 시 주의사항

1. **현실적인 모의**: 실제 외부 서비스와 유사하게 동작하도록 모의 객체를 구성합니다.
2. **양성 및 음성 테스트**: 성공 케이스와 실패 케이스 모두 테스트합니다.
3. **모의 검증**: 모의 객체가 예상대로 호출되었는지 검증합니다.

## 통합 테스트

모니터링 기능의 통합 테스트는 FastAPI의 테스트 클라이언트를 사용하여 실제 HTTP 요청과 응답을 시뮬레이션합니다.

```python
# tests/test_monitoring/test_integration.py
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.monitoring.metrics import increment_counter
from app.monitoring.tracing import create_span
from app.monitoring.logger import get_logger

# 테스트용 로거
logger = get_logger("test.integration")

def add_test_routes(app: FastAPI):
    @app.get("/test/monitoring")
    async def test_monitoring_endpoint():
        # 메트릭 증가
        increment_counter("test_api_call")
        
        # 로깅
        logger.info("테스트 엔드포인트 호출")
        
        # 추적 스팬 생성
        with create_span("test-operation") as span:
            span.set_attribute("test", True)
            return {"status": "success"}

@pytest.fixture
def test_app():
    app = FastAPI()
    add_test_routes(app)
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_monitoring_integration(client):
    # 메트릭 수집 모의
    with patch('app.monitoring.metrics.increment_counter') as mock_increment:
        # 로깅 모의
        with patch('app.monitoring.logger.get_logger') as mock_logger:
            # 추적 모의
            with patch('app.monitoring.tracing.create_span') as mock_span:
                mock_context = patch('app.monitoring.tracing._tracer').start()
                
                # 테스트 엔드포인트 호출
                response = client.get("/test/monitoring")
                
                # 응답 검증
                assert response.status_code == 200
                assert response.json() == {"status": "success"}
                
                # 메트릭 호출 검증
                mock_increment.assert_called_once_with("test_api_call")
                
                # 추적 호출 검증
                mock_span.assert_called_once()
                
                # 정리
                patch.stopall()
```

## 테스트 모범 사례

1. **독립적인 테스트**: 각 테스트가 다른 테스트와 독립적으로 실행될 수 있도록 설계합니다.

2. **외부 의존성 모의화**: 로깅, 메트릭, 추적 시스템과 같은 외부 의존성을 모의하여 테스트합니다.

3. **역할별 테스트 분리**: 로깅, 메트릭, 헬스 체크 등 모니터링의 각 영역을 분리하여 테스트합니다.

4. **실패 케이스 테스트**: 외부 서비스 실패 시 애플리케이션이 올바르게 처리하는지 테스트합니다.

5. **성능 영향 검증**: 모니터링 기능이 애플리케이션 성능에 과도한 영향을 미치지 않는지 테스트합니다.

## 일반적인 문제 및 해결 방법

### 1. 외부 서비스 의존성

**문제**: 모니터링 모듈은 외부 서비스(로깅 시스템, 메트릭 서버 등)에 의존합니다.

**해결방법**: 테스트 환경에서는 이러한 의존성을 모의하거나, 인메모리 구현으로 대체합니다.

### 2. 비동기 코드

**문제**: 모니터링 코드가 비동기적으로 실행되어 테스트가 어려울 수 있습니다.

**해결방법**: `asyncio`의 `wait_for` 또는 테스트 유틸리티를 사용하여 비동기 코드가 완료될 때까지 기다립니다.

### 3. 사이드 이펙트

**문제**: 모니터링 코드는 로그 파일 작성, 메트릭 전송 등의 사이드 이펙트를 가질 수 있습니다.

**해결방법**: 테스트에서 이러한 사이드 이펙트를 캡처하고 검증하거나, 모의 객체로 대체합니다.

## 테스트 사례 목록

다음은 Monitoring 모듈을 포괄적으로 테스트하기 위한 테스트 사례 목록입니다:

1. **로깅 테스트**
   - 로거 초기화 및 설정 테스트
   - 다양한 로그 레벨 테스트
   - 로그 형식 및 컨텐츠 테스트
   - 로그 파일 저장 및 회전 테스트

2. **메트릭 테스트**
   - 메트릭 클라이언트 초기화 테스트
   - 카운터, 게이지, 히스토그램 기록 테스트
   - 태그 및 레이블 처리 테스트
   - 메트릭 집계 테스트

3. **헬스 체크 테스트**
   - 헬스 체크 엔드포인트 테스트
   - 개별 서비스 헬스 테스트 (DB, Redis 등)
   - 상태 보고 형식 테스트
   - 상태 변화 감지 테스트

4. **알림 시스템 테스트**
   - 알림 트리거 조건 테스트
   - 다양한 알림 채널 테스트 (이메일, 슬랙 등)
   - 알림 형식 및 컨텐츠 테스트
   - 알림 중복 방지 테스트

5. **분산 추적 테스트**
   - 추적 초기화 테스트
   - 스팬 생성 및 종료 테스트
   - 컨텍스트 전파 테스트
   - 추적 내보내기 테스트

## 참고 자료

- [FastAPI 테스트 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
- [OpenTelemetry 테스트 가이드](https://opentelemetry.io/docs/instrumentation/python/cookbook/)
- [Prometheus 클라이언트 라이브러리 문서](https://github.com/prometheus/client_python)
- [Python 로깅 가이드](https://docs.python.org/3/howto/logging.html)

## 요약

Monitoring 모듈을 테스트할 때는 다음 핵심 사항을 기억하세요:

1. 외부 서비스와의 상호작용은 모의 객체로 대체합니다.
2. 로깅, 메트릭, 헬스 체크, 알림 등 모든 모니터링 구성 요소를 포괄적으로 테스트합니다.
3. 정상 사례뿐만 아니라 장애 상황에서의 동작도 테스트합니다.
4. 통합 테스트를 통해 모니터링 구성 요소 간의 상호작용을 확인합니다.
5. 모니터링 코드가 애플리케이션 성능에 과도한 영향을 주지 않도록 주의합니다.
