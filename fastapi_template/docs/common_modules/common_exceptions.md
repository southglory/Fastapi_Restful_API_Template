# 예외 처리 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 예외 처리 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [사용자 정의 예외](#사용자-정의-예외)
- [전역 예외 핸들러](#전역-예외-핸들러)
- [예외 처리 미들웨어](#예외-처리-미들웨어)
- [에러 코드 관리](#에러-코드-관리)

## 사용자 정의 예외

[@base](/fastapi_template/app/common/exceptions/base.py)

`app.common.exceptions` 모듈은 다양한 유형의 예외를 정의합니다.

### 기본 예외 유형

```python
from app.common.exceptions import (
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
)

# 인증 오류 (401)
raise AuthenticationError("인증 토큰이 유효하지 않습니다")

# 권한 오류 (403)
raise PermissionDeniedError("이 리소스에 접근할 권한이 없습니다")

# 유효성 검사 오류 (422)
raise ValidationError("입력 데이터가 유효하지 않습니다")

# 리소스 찾을 수 없음 (404)
raise NotFoundError("요청한 사용자를 찾을 수 없습니다")

# 리소스 충돌 (409)
raise ConflictError("이미 동일한 이름의 리소스가 존재합니다")

# 속도 제한 (429)
raise RateLimitError("요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.")

# 서버 오류 (500)
raise ServerError("내부 서버 오류가 발생했습니다")
```

### 사용자 정의 예외 생성

특정 요구사항에 맞는 사용자 정의 예외를 만들 수 있습니다.

```python
from app.common.exceptions import APIError

class PaymentError(APIError):
    status_code = 402
    default_message = "결제 처리 중 오류가 발생했습니다"
    default_error_code = "PAYMENT_ERROR"
    
# 사용 예시
raise PaymentError("신용카드가 만료되었습니다", error_code="EXPIRED_CARD")
```

## 전역 예외 핸들러

[@handlers](/fastapi_template/app/common/exceptions/handlers.py)

FastAPI 애플리케이션에 자동으로 등록되는 전역 예외 핸들러가 있습니다.

### 예외 핸들러 등록

```python
from fastapi import FastAPI, Request
from app.common.exceptions import add_exception_handlers

app = FastAPI()

# 모든 예외 핸들러 등록
add_exception_handlers(app)
```

### 예외 응답 형식

예외가 발생하면 다음과 같은 표준 형식의 JSON 응답이 반환됩니다:

```json
{
    "success": false,
    "message": "인증 토큰이 유효하지 않습니다",
    "error_code": "INVALID_TOKEN",
    "status_code": 401,
    "timestamp": "2023-03-17T12:34:56.789Z"
}
```

## 예외 처리 미들웨어

[@middleware](/fastapi_template/app/common/exceptions/middleware.py)

애플리케이션 요청 흐름 중에 예외를 처리하기 위한 미들웨어를 제공합니다.

### 오류 로깅 미들웨어

모든 예외를 캐치하고 로깅하는 미들웨어:

```python
from fastapi import FastAPI
from app.common.exceptions.middleware import ErrorLoggingMiddleware

app = FastAPI()
app.add_middleware(ErrorLoggingMiddleware)
```

### 요청별 에러 추적

각 요청에 고유한 요청 ID를 할당하고 에러 발생 시 이를 포함하는 미들웨어:

```python
from fastapi import FastAPI
from app.common.exceptions.middleware import RequestTracingMiddleware

app = FastAPI()
app.add_middleware(RequestTracingMiddleware)
```

## 에러 코드 관리

[@error_codes](/fastapi_template/app/common/exceptions/error_codes.py)

표준화된 에러 코드를 사용하여 일관된 API 응답을 제공합니다.

### 에러 코드 정의

```python
from app.common.exceptions.error_codes import ErrorCode

# 에러 코드 사용 예시
raise AuthenticationError(
    message="세션이 만료되었습니다. 다시 로그인하세요.",
    error_code=ErrorCode.SESSION_EXPIRED
)
```

### 에러 코드 상수

주요 에러 코드 상수:

```python
class ErrorCode:
    # 인증 관련 에러
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # 권한 관련 에러
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INSUFFICIENT_ROLE = "INSUFFICIENT_ROLE"
    
    # 데이터 검증 에러
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    
    # 리소스 관련 에러
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # 시스템 에러
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
```

### 에러 메시지 국제화

에러 메시지의 국제화를 위한 도우미 함수:

```python
from app.common.exceptions.i18n import get_localized_error_message

# 에러 메시지 번역
message = get_localized_error_message(
    key=ErrorCode.INVALID_CREDENTIALS,
    lang="ko"
)
```
