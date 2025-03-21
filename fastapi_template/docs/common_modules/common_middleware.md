# 공통 미들웨어 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 공통 미들웨어 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [미들웨어 개요](#미들웨어-개요)
- [로깅 미들웨어](#로깅-미들웨어)
- [인증 미들웨어](#인증-미들웨어)
- [CORS 미들웨어](#cors-미들웨어)
- [요청 ID 미들웨어](#요청-id-미들웨어)
- [속도 제한 미들웨어](#속도-제한-미들웨어)
- [압축 미들웨어](#압축-미들웨어)
- [사용자 정의 미들웨어](#사용자-정의-미들웨어)

## 미들웨어 개요

미들웨어는 요청이 라우트 핸들러에 도달하기 전이나 응답이 클라이언트에게 반환되기 전에 실행되는 컴포넌트입니다. FastAPI 애플리케이션에 여러 미들웨어를 추가할 수 있습니다.

### 미들웨어 등록

```python
from fastapi import FastAPI
from app.common.middleware import setup_middlewares

app = FastAPI()

# 모든 미들웨어 설정
setup_middlewares(app)
```

## 로깅 미들웨어

[@logging](/fastapi_template/app/common/middleware/logging.py)

요청 및 응답 정보를 로깅하는 미들웨어입니다.

```python
from fastapi import FastAPI
from app.common.middleware.logging import LoggingMiddleware

app = FastAPI()
app.add_middleware(LoggingMiddleware)
```

### 로깅 설정

```python
from fastapi import FastAPI
from app.common.middleware.logging import LoggingMiddleware

app = FastAPI()
app.add_middleware(
    LoggingMiddleware,
    log_request_body=True,  # 요청 본문 로깅
    log_response_body=False,  # 응답 본문 로깅 비활성화
    exclude_paths=["/health", "/metrics"],  # 특정 경로 제외
    log_level="INFO"  # 로그 레벨 설정
)
```

## 인증 미들웨어

[@auth](/fastapi_template/app/common/middleware/auth.py)

API 요청에 대한 인증을 처리하는 미들웨어입니다.

```python
from fastapi import FastAPI
from app.common.middleware.auth import AuthenticationMiddleware

app = FastAPI()
app.add_middleware(
    AuthenticationMiddleware,
    auth_required_paths=["/api/v1"],  # 인증이 필요한 경로
    exclude_paths=["/api/v1/auth/login", "/docs"],  # 인증 제외 경로
    auth_header_name="Authorization",  # 인증 헤더 이름
    auth_scheme="Bearer"  # 인증 스키마
)
```

## CORS 미들웨어

[@cors](/fastapi_template/app/common/middleware/cors.py)

Cross-Origin Resource Sharing(CORS)를 지원하는 미들웨어입니다.

```python
from fastapi import FastAPI
from app.common.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frontend.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    allow_credentials=True,
    max_age=3600
)
```

## 요청 ID 미들웨어

[@request_id](/fastapi_template/app/common/middleware/request_id.py)

각 요청에 고유한 ID를 할당하는 미들웨어입니다.

```python
from fastapi import FastAPI, Request
from app.common.middleware.request_id import RequestIDMiddleware

app = FastAPI()
app.add_middleware(
    RequestIDMiddleware,
    header_name="X-Request-ID",  # 요청 ID 헤더 이름
    generate_id=True  # ID가 없는 경우 생성
)

# 라우트 핸들러에서 요청 ID 사용
@app.get("/items")
async def get_items(request: Request):
    request_id = request.state.request_id
    print(f"Processing request {request_id}")
    return {"request_id": request_id}
```

## 속도 제한 미들웨어

[@rate_limit](/fastapi_template/app/common/middleware/rate_limit.py)

API 요청 속도를 제한하는 미들웨어입니다.

```python
from fastapi import FastAPI
from app.common.middleware.rate_limit import RateLimitMiddleware

app = FastAPI()
app.add_middleware(
    RateLimitMiddleware,
    limit=100,  # 기본 최대 요청 수
    period=60,  # 시간 범위(초)
    key_func=lambda request: request.client.host,  # IP 기반 제한
    limits={  # 경로별 다른 제한 설정
        "/api/heavy": {"limit": 10, "period": 60},
        "/api/users": {"limit": 50, "period": 60}
    },
    exclude_paths=["/health", "/metrics"]  # 제한에서 제외할 경로
)
```

## 압축 미들웨어

[@compression](/fastapi_template/app/common/middleware/compression.py)

응답 데이터를 압축하는 미들웨어입니다.

```python
from fastapi import FastAPI
from app.common.middleware.compression import CompressionMiddleware

app = FastAPI()
app.add_middleware(
    CompressionMiddleware,
    minimum_size=1000,  # 최소 압축 크기 (바이트)
    compression_level=6,  # 압축 레벨 (1-9)
    include_content_types=["text/html", "application/json", "text/css", "application/javascript"]
)
```

## 사용자 정의 미들웨어

[@base](/fastapi_template/app/common/middleware/base.py)

필요에 따라 사용자 정의 미들웨어를 생성할 수 있습니다.

### 함수 기반 미들웨어

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.common.middleware.base import create_middleware

# 함수형 미들웨어
async def timing_middleware(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
    return response

app = FastAPI()
app.middleware("http")(timing_middleware)
```

### 클래스 기반 미들웨어

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Custom-Header"] = "Custom Value"
        return response

app = FastAPI()
app.add_middleware(CustomHeaderMiddleware)
```

### 미들웨어 팩토리

```python
from fastapi import FastAPI
from app.common.middleware.factory import create_middleware

# 미들웨어 팩토리 함수
def create_telemetry_middleware(app_name: str):
    async def telemetry_middleware(request, call_next):
        response = await call_next(request)
        response.headers["X-App-Name"] = app_name
        return response
    
    return telemetry_middleware

app = FastAPI()
app.middleware("http")(create_telemetry_middleware("my-app"))
```
