# Exceptions 모듈 테스트 가이드

[@exceptions](/fastapi_template/app/common/exceptions)

## 개요

`exceptions` 모듈은 애플리케이션에서 발생하는 다양한 예외를 정의하고 처리하는 역할을 합니다. 이 모듈은 HTTP 응답, 에러 코드, 오류 메시지 등을 일관된 형식으로 제공합니다.

## 현재 모듈 구조

```
app/common/exceptions/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── exceptions_base.py          # 기본 예외 클래스 정의
├── exceptions_http.py          # HTTP 관련 예외
├── exceptions_auth.py          # 인증 관련 예외
├── exceptions_database.py      # 데이터베이스 관련 예외
├── exceptions_validation.py    # 유효성 검증 관련 예외
└── exceptions_handlers.py      # 예외 처리기
```

파일 이름에 `exceptions_` 접두사를 추가하여 명확히 구분하였습니다.

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 예외 자체는 테스트하기 쉽지만, 예외 처리기는 HTTP 컨텍스트와 상호작용
  - 로깅이나 외부 시스템 알림 등의 사이드 이펙트 처리가 필요한 경우 있음
  - 다양한 경계 조건과 예외 상황을 고려해야 함

## 테스트 대상

테스트 대상은 다음과 같습니다:

1. **기본 예외 클래스** (`exceptions_base.py`)
   - `AppException` 및 파생 클래스의 초기화 검증
   - 상태 코드, 에러 메시지 설정 확인

2. **HTTP 예외 클래스** (`exceptions_http.py`)
   - 각 HTTP 상태 코드별 예외 클래스 검증
   - 응답 형식 및 상태 코드 확인

3. **인증 관련 예외** (`exceptions_auth.py`)
   - 인증 및 권한 관련 예외 클래스 검증
   - 토큰 오류, 계정 관련 예외 확인

4. **데이터베이스 관련 예외** (`exceptions_database.py`)
   - 데이터베이스 오류 관련 예외 클래스 검증
   - 엔티티 관련 예외 확인

5. **유효성 검증 관련 예외** (`exceptions_validation.py`)
   - 파라미터 및 필드 유효성 검증 예외 검증
   - 동적 오류 메시지 생성 확인

6. **예외 처리기** (`exceptions_handlers.py`)
   - 애플리케이션 예외 처리
   - Pydantic 검증 오류 처리
   - SQLAlchemy 오류 처리
   - 일반 예외 처리

## 테스트 접근법

Exceptions 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 예외 클래스의 동작을 검증합니다.
2. **통합 테스트**: 예외 처리기와 FastAPI 엔드포인트의 통합을 검증합니다.
3. **모의 객체 사용**: 로깅 등의 사이드 이펙트를 테스트합니다.

## 테스트 구현 방법

### 기본 예외 테스트 (`test_exceptions_base.py`)

```python
# tests/test_exceptions/test_exceptions_base.py
import pytest
from fastapi import status
from app.common.exceptions.exceptions_base import AppException

def test_app_exception_default():
    # 기본 파라미터로 초기화
    exc = AppException()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "서버 오류가 발생했습니다."
    assert exc.headers == {}

def test_app_exception_custom():
    # 커스텀 파라미터로 초기화
    exc = AppException(
        detail="테스트 오류",
        status_code=status.HTTP_400_BAD_REQUEST,
        headers={"X-Custom-Header": "test"}
    )
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.detail == "테스트 오류"
    assert exc.headers == {"X-Custom-Header": "test"}

def test_app_exception_partial_custom():
    # 일부 파라미터만 커스텀
    exc = AppException(detail="테스트 오류")
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "테스트 오류"
    assert exc.headers == {}
```

### 예외 처리기 테스트 (`test_exceptions_handlers.py`)

```python
# tests/test_exceptions/test_exceptions_handlers.py
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.common.exceptions.exceptions_base import AppException
from app.common.exceptions.exceptions_validation import ValidationError
from app.common.exceptions.exceptions_database import DatabaseError
from app.common.exceptions.exceptions_handlers import add_exception_handlers

@pytest.fixture
def test_app():
    app = FastAPI()
    add_exception_handlers(app)
    return app

@pytest.fixture
def mock_request():
    return Request(scope={"type": "http"})

def test_handle_app_exception(test_app, mock_request):
    exc = AppException(detail="테스트 예외")
    handler = test_app.exception_handlers[AppException]
    response = handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == b'{"detail":"테스트 예외"}'

def test_handle_validation_error(test_app, mock_request):
    exc = PydanticValidationError(errors=[])
    handler = test_app.exception_handlers[PydanticValidationError]
    response = handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    assert response.body == b'{"detail":[]}'

def test_handle_sql_error(test_app, mock_request):
    exc = SQLAlchemyError("DB 오류")
    handler = test_app.exception_handlers[SQLAlchemyError]
    response = handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == b'{"detail":"데이터베이스 오류가 발생했습니다."}'

def test_handle_general_exception(test_app, mock_request):
    exc = Exception("일반 오류")
    handler = test_app.exception_handlers[Exception]
    response = handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == b'{"detail":"서버 내부 오류가 발생했습니다."}'
```

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_exceptions/
    ├── __init__.py
    ├── test_exceptions_base.py
    ├── test_exceptions_http.py
    ├── test_exceptions_auth.py
    ├── test_exceptions_database.py
    ├── test_exceptions_validation.py
    └── test_exceptions_handlers.py
```

## 테스트 커버리지 확인

Exceptions 모듈은 높은 테스트 커버리지를 목표로 합니다:

```bash
pytest --cov=app.common.exceptions tests/test_exceptions/ -v
```

현재 모든 예외 클래스와 처리기에 대한 테스트가 구현되어 있으며, 100% 커버리지를 달성했습니다.

## 모범 사례

1. 모든 커스텀 예외 클래스의 초기화와 속성을 철저히 테스트합니다.
2. 통합 테스트에서는 FastAPI 테스트 클라이언트를 활용하여 실제 응답을 검증합니다.
3. 로깅이나 외부 시스템 알림 등의 사이드 이펙트는 적절히 모킹하여 테스트합니다.
4. 예외 처리기가 일관된 형식의 응답을 반환하는지 검증합니다.
5. 모든 파일 이름에 `exceptions_` 접두사를 일관되게 적용하여 명확히 구분합니다.

## 주의사항

1. 예외 처리기는 HTTP 컨텍스트에 의존하므로 적절한 테스트 환경 설정이 필요합니다.
2. 전역 예외 처리기는 다양한 예외 상황을 시뮬레이션하여 테스트해야 합니다.
3. 로깅 관련 코드는 모킹하여 테스트 결과의 일관성을 유지합니다.
4. 너무 많은 예외 유형을 만들면 관리가 어려워지므로 필요에 따라 점진적으로 확장합니다.
