# Exceptions 모듈 테스트 가이드

이 문서는 FastAPI 템플릿 프로젝트의 Exceptions 모듈을 테스트하는 방법에 대한 상세 가이드를 제공합니다.

## 개요

Exceptions 모듈은 애플리케이션에서 발생하는 다양한 예외를 정의하고 처리하는 역할을 합니다. 이 모듈의 테스트는 다음과 같은 요소를 포함합니다:

- 커스텀 예외 클래스의 동작 검증
- 예외 처리기(Exception handlers)의 기능 검증
- 오류 응답 형식 및 내용 검증
- 에러 코드 및 메시지 정확성 검증

## 테스트 난이도: 중간

Exceptions 모듈은 테스트하기 비교적 쉬운 편이지만, 예외 처리기의 경우 HTTP 컨텍스트와 상호작용해야 하므로 약간의 복잡성이 있습니다.

## 테스트 대상

```
app/
├── exceptions/
│   ├── __init__.py
│   ├── base.py            # 기본 예외 클래스
│   ├── http.py            # HTTP 관련 예외
│   ├── auth.py            # 인증 관련 예외
│   ├── validation.py      # 유효성 검증 예외
│   ├── database.py        # 데이터베이스 관련 예외
│   └── handlers.py        # 예외 처리기
```

## 테스트 디렉토리 구조

```
tests/
├── test_exceptions/
│   ├── __init__.py
│   ├── test_base.py            # 기본 예외 테스트
│   ├── test_http.py            # HTTP 예외 테스트
│   ├── test_auth.py            # 인증 예외 테스트
│   ├── test_validation.py      # 유효성 검증 예외 테스트
│   ├── test_database.py        # 데이터베이스 예외 테스트
│   └── test_handlers.py        # 예외 처리기 테스트
```

## 테스트 접근 방식

### 1. 커스텀 예외 클래스 테스트

커스텀 예외 클래스는 일반적으로 다음과 같은 요소를 테스트합니다:

- 예외가 올바르게 초기화되는지
- 에러 코드와 메시지가 올바르게 설정되는지
- 오류 응답 형식이 API 스펙을 따르는지

#### 예시: 기본 예외 테스트

```python
# tests/test_exceptions/test_base.py
import pytest
from app.exceptions.base import AppException, ErrorCode

def test_app_exception_initialization():
    # 기본 파라미터로 초기화
    exception = AppException(
        error_code=ErrorCode.UNKNOWN_ERROR,
        message="테스트 오류 메시지"
    )
    
    assert exception.error_code == ErrorCode.UNKNOWN_ERROR
    assert exception.message == "테스트 오류 메시지"
    assert exception.status_code == 500  # 기본값
    
    # 모든 파라미터로 초기화
    exception = AppException(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="유효성 검증 실패",
        status_code=400,
        details={"field": "username", "issue": "required"}
    )
    
    assert exception.error_code == ErrorCode.VALIDATION_ERROR
    assert exception.message == "유효성 검증 실패"
    assert exception.status_code == 400
    assert exception.details == {"field": "username", "issue": "required"}

def test_app_exception_to_dict():
    # to_dict 메서드가 올바른 형식을 반환하는지 테스트
    exception = AppException(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="유효성 검증 실패",
        details={"field": "email"}
    )
    
    error_dict = exception.to_dict()
    
    assert "errorCode" in error_dict
    assert "message" in error_dict
    assert "details" in error_dict
    assert error_dict["errorCode"] == ErrorCode.VALIDATION_ERROR.value
    assert error_dict["message"] == "유효성 검증 실패"
    assert error_dict["details"] == {"field": "email"}
```

### 2. HTTP 예외 테스트

HTTP 예외의 경우 HTTP 상태 코드가 올바르게 설정되는지도 검증해야 합니다.

```python
# tests/test_exceptions/test_http.py
import pytest
from app.exceptions.http import (
    BadRequestException, 
    NotFoundException, 
    ForbiddenException,
    UnauthorizedException
)
from app.exceptions.base import ErrorCode

def test_bad_request_exception():
    exception = BadRequestException(message="잘못된 요청")
    
    assert exception.status_code == 400
    assert exception.error_code == ErrorCode.BAD_REQUEST
    assert exception.message == "잘못된 요청"
    
    # 세부 정보가 있는 경우
    exception = BadRequestException(
        message="잘못된 요청",
        details={"invalid_param": "user_id"}
    )
    
    assert exception.details == {"invalid_param": "user_id"}

def test_not_found_exception():
    exception = NotFoundException(message="리소스를 찾을 수 없음")
    
    assert exception.status_code == 404
    assert exception.error_code == ErrorCode.RESOURCE_NOT_FOUND
    assert exception.message == "리소스를 찾을 수 없음"
    
    # 리소스 ID가 있는 경우
    exception = NotFoundException(
        message="사용자를 찾을 수 없음",
        details={"resource_type": "user", "resource_id": 123}
    )
    
    error_dict = exception.to_dict()
    assert error_dict["details"]["resource_type"] == "user"
    assert error_dict["details"]["resource_id"] == 123
```

### 3. 예외 처리기 테스트

예외 처리기는 FastAPI 컨텍스트에서 작동하므로, 테스트 클라이언트를 사용하여 통합 테스트 접근 방식으로 테스트합니다.

```python
# tests/test_exceptions/test_handlers.py
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from app.exceptions.base import AppException, ErrorCode
from app.exceptions.http import NotFoundException, BadRequestException
from app.exceptions.handlers import (
    register_exception_handlers, 
    app_exception_handler
)

# 테스트용 API 앱 생성
@pytest.fixture
def test_app():
    app = FastAPI()
    register_exception_handlers(app)  # 예외 처리기 등록
    
    # 예외를 발생시킬 엔드포인트 추가
    @app.get("/not-found")
    async def not_found_endpoint():
        raise NotFoundException(message="리소스를 찾을 수 없습니다")
    
    @app.get("/bad-request")
    async def bad_request_endpoint():
        raise BadRequestException(message="잘못된 요청입니다")
    
    @app.get("/app-exception")
    async def generic_exception_endpoint():
        raise AppException(
            error_code=ErrorCode.UNKNOWN_ERROR,
            message="알 수 없는 오류가 발생했습니다",
            status_code=500
        )
    
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def test_not_found_handler(client):
    response = client.get("/not-found")
    
    assert response.status_code == 404
    data = response.json()
    assert data["errorCode"] == ErrorCode.RESOURCE_NOT_FOUND.value
    assert data["message"] == "리소스를 찾을 수 없습니다"

def test_bad_request_handler(client):
    response = client.get("/bad-request")
    
    assert response.status_code == 400
    data = response.json()
    assert data["errorCode"] == ErrorCode.BAD_REQUEST.value
    assert data["message"] == "잘못된 요청입니다"

def test_app_exception_handler(client):
    response = client.get("/app-exception")
    
    assert response.status_code == 500
    data = response.json()
    assert data["errorCode"] == ErrorCode.UNKNOWN_ERROR.value
    assert data["message"] == "알 수 없는 오류가 발생했습니다"

def test_global_exception_handler(test_app, client):
    # 처리되지 않은 예외 발생시키는 엔드포인트 추가
    @test_app.get("/unhandled-error")
    async def unhandled_error():
        # 의도적으로 인덱스 오류 발생
        x = [1, 2, 3]
        return x[10]
    
    response = client.get("/unhandled-error")
    
    # 500 오류 반환 확인
    assert response.status_code == 500
    data = response.json()
    # 에러 코드가 INTERNAL_SERVER_ERROR인지 확인
    assert data["errorCode"] == ErrorCode.INTERNAL_SERVER_ERROR.value
    # 메시지가 존재하는지 확인
    assert "message" in data
```

## 모의(Mock) 객체 사용

일부 예외 처리는 로깅, 외부 시스템 알림 등의 사이드 이펙트가 있을 수 있습니다. 이런 경우 모의(mock) 객체를 사용하여 테스트합니다.

```python
# tests/test_exceptions/test_handlers.py (확장)
from unittest.mock import patch, MagicMock

def test_exception_handler_with_logging(test_app, client):
    # 로깅 모의 객체 생성
    with patch("app.exceptions.handlers.logger") as mock_logger:
        # 처리되지 않은 예외 발생시키는 엔드포인트 추가
        @test_app.get("/log-error")
        async def log_error():
            raise ValueError("심각한 오류 발생")
        
        response = client.get("/log-error")
        
        # 500 오류 반환 확인
        assert response.status_code == 500
        
        # 로거가 호출되었는지 확인
        mock_logger.error.assert_called_once()
        # 로그 메시지에 오류 내용이 포함되었는지 확인
        assert "ValueError" in str(mock_logger.error.call_args)
        assert "심각한 오류 발생" in str(mock_logger.error.call_args)
```

## 테스트 모범 사례

1. **모든 커스텀 예외 클래스 테스트**: 모든 커스텀 예외 클래스에 대해 초기화 및 기본 동작을 테스트합니다.

2. **경계 조건 테스트**: 예외가 발생하는 다양한 경계 조건을 테스트합니다. 예를 들어, 빈 메시지, 큰 세부 정보 객체 등의 경우를 테스트합니다.

3. **실제 HTTP 응답 테스트**: FastAPI의 테스트 클라이언트를 사용하여 예외 처리기가 올바른 HTTP 응답을 생성하는지 테스트합니다.

4. **로깅 및 사이드 이펙트 테스트**: 로깅이나 알림 같은 사이드 이펙트가 있는 경우, 모의 객체를 사용하여 이를 테스트합니다.

5. **통합 테스트**: 실제 API 호출을 시뮬레이션하여 예외 처리 흐름이 전체 애플리케이션에서 올바르게 작동하는지 확인합니다.

## 일반적인 문제 및 해결 방법

### 1. 전역 예외 처리기 테스트의 어려움

FastAPI의 전역 예외 처리기는 테스트하기 어려울 수 있습니다. 이런 경우 테스트 애플리케이션 인스턴스를 생성하고 실제 요청을 시뮬레이션합니다.

### 2. 로깅 의존성

예외 처리 중 로깅이 발생하는 경우, `unittest.mock` 모듈을 사용하여 로거를 모의하고 예상대로 호출되는지 확인합니다.

### 3. 복잡한 예외 계층 구조

예외 클래스가 복잡한 계층 구조를 가질 때는 상속 계층 구조의 각 레벨을 신중하게 테스트해야 합니다.

## 테스트 사례 목록

다음은 Exceptions 모듈을 포괄적으로 테스트하기 위한 테스트 사례 목록입니다:

1. **기본 예외 클래스 테스트**
   - 초기화 테스트
   - `to_dict()` 메서드 테스트
   - 상속 관계 테스트

2. **HTTP 예외 테스트**
   - 각 HTTP 예외 유형 테스트 (400, 401, 403, 404, 422, 500 등)
   - 상태 코드 확인
   - 에러 코드 확인
   - 커스텀 메시지 확인

3. **인증 예외 테스트**
   - 토큰 관련 예외 테스트
   - 권한 예외 테스트

4. **데이터베이스 예외 테스트**
   - DB 연결 예외 테스트
   - DB 쿼리 예외 테스트
   - DB 트랜잭션 예외 테스트

5. **예외 처리기 테스트**
   - 애플리케이션 예외 처리 테스트
   - 내부 서버 오류 처리 테스트
   - 유효성 검증 예외 처리 테스트

## 참고 자료

- [FastAPI 예외 처리 공식 문서](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pytest 모킹 가이드](https://docs.pytest.org/en/stable/monkeypatch.html)
- [HTTP 상태 코드](https://developer.mozilla.org/ko/docs/Web/HTTP/Status)

## 요약

Exceptions 모듈을 테스트할 때는 다음 핵심 사항을 기억하세요:

1. 모든 커스텀 예외 클래스의 동작을 확인합니다.
2. 예외 처리기가 올바른 HTTP 응답을 생성하는지 테스트합니다.
3. 로깅 및 기타 사이드 이펙트를 모의 객체로 테스트합니다.
4. 통합 테스트를 통해 전체 예외 처리 흐름을 확인합니다.
5. 예외의 계층 구조 및 상속 관계를 고려합니다.
