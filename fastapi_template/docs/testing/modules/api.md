# API 모듈 테스트 가이드

## 개요

`api` 모듈은 FastAPI 애플리케이션의 엔드포인트와 라우터를 정의하는 핵심 모듈입니다. API 라우트는 HTTP 요청을 처리하고 비즈니스 로직을 호출하며 적절한 응답을 반환합니다. 이 모듈은 사용자 인증, 데이터 검증, 예외 처리, 데이터베이스 상호 작용 등 다양한 기능을 통합합니다.

## 테스트 용이성

- **난이도**: 어려움
- **이유**:
  - 여러 모듈과 의존성의 통합이 필요함
  - 인증, 데이터베이스, 캐싱 등 외부 서비스에 대한 모의가 필요
  - 비동기 작업의 복잡성
  - 상태 변경을 포함하는 작업의 테스트 복잡성

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **라우트 핸들러**
   - 엔드포인트 기능 및 로직
   - 상태 코드 및 응답 형식
   - 오류 처리 및 예외 발생

2. **요청 처리**
   - 파라미터 및 본문 검증
   - 파라미터 유형 변환
   - 요청 헤더 및 쿠키 처리

3. **응답 생성**
   - 성공 응답 포맷
   - 오류 응답 포맷
   - 헤더 및 쿠키 설정

4. **인증 및 권한**
   - 토큰 기반 인증
   - 역할 기반 접근 제어
   - 권한 검증

## 테스트 접근법

API 모듈 테스트 시 다음 접근법을 권장합니다:

1. **통합 테스트**: FastAPI의 TestClient를 사용한 엔드투엔드 테스트
2. **모의 테스트**: 외부 서비스 및 의존성을 모의 객체로 대체한 테스트
3. **파라미터화 테스트**: 다양한 입력 데이터로 동일한 엔드포인트 테스트
4. **경계 조건 테스트**: 유효하지 않은 입력값, 경계값 등으로 테스트

## 테스트 예시

### 기본 API 테스트

```python
# tests/test_api/test_users.py
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.api.v1.users import router as users_router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(users_router, prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_get_users(client):
    # 사용자 목록 조회 API 테스트
    response = client.get("/api/v1/users")
    
    # 응답 확인
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user_by_id(client):
    # 특정 사용자 조회 API 테스트
    user_id = 1
    response = client.get(f"/api/v1/users/{user_id}")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_get_user_not_found(client):
    # 존재하지 않는 사용자 조회 API 테스트
    response = client.get("/api/v1/users/999")
    
    # 응답 확인
    assert response.status_code == 404
    assert "Not found" in response.json()["detail"]

def test_create_user(client):
    # 사용자 생성 API 테스트
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword"
    }
    
    response = client.post("/api/v1/users", json=user_data)
    
    # 응답 확인
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]
    assert "password" not in response.json()  # 패스워드는 응답에 포함되지 않아야 함

def test_update_user(client):
    # 사용자 정보 업데이트 API 테스트
    user_id = 1
    update_data = {"username": "updateduser"}
    
    response = client.patch(f"/api/v1/users/{user_id}", json=update_data)
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json()["username"] == update_data["username"]

def test_delete_user(client):
    # 사용자 삭제 API 테스트
    user_id = 1
    
    response = client.delete(f"/api/v1/users/{user_id}")
    
    # 응답 확인
    assert response.status_code == 204
    assert response.content == b''  # 204 응답은 본문이 없어야 함
```

### 의존성 모의(Mocking)를 활용한 테스트

```python
# tests/test_api/test_auth.py
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.api.v1.auth import router as auth_router
from app.common.dependencies.auth import get_current_user
from app.common.schemas.token import TokenResponse

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_login_success(client):
    # 로그인 성공 API 테스트
    with patch("app.api.v1.auth.authenticate_user") as mock_auth, \
         patch("app.api.v1.auth.create_access_token") as mock_token:
        
        # 인증 함수 모의 설정
        mock_auth.return_value = {"id": 1, "username": "testuser"}
        # 토큰 생성 함수 모의 설정
        mock_token.return_value = "mocked_access_token"
        
        # 로그인 요청
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "password"}
        )
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json()["access_token"] == "mocked_access_token"
        assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    # 로그인 실패 API 테스트
    with patch("app.api.v1.auth.authenticate_user") as mock_auth:
        # 인증 실패 모의 설정
        mock_auth.return_value = None
        
        # 로그인 요청
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "wronguser", "password": "wrongpassword"}
        )
        
        # 응답 확인
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

def test_get_current_user_profile(client, app):
    # 현재 사용자 정보 조회 API 테스트
    
    # get_current_user 의존성 오버라이드
    async def mock_current_user():
        return {"id": 1, "username": "testuser", "email": "test@example.com"}
    
    app.dependency_overrides[get_current_user] = mock_current_user
    
    # 사용자 프로필 요청
    response = client.get("/api/v1/auth/me")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    
    # 의존성 오버라이드 제거
    app.dependency_overrides.clear()
```

### 파라미터화된 테스트

```python
# tests/test_api/test_items.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.items import router as items_router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(items_router, prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.mark.parametrize("query_params,expected_status,expected_count", [
    ({}, 200, 10),  # 기본 파라미터
    ({"skip": 0, "limit": 5}, 200, 5),  # 제한된 결과
    ({"skip": 10, "limit": 10}, 200, 10),  # 건너뛰기
    ({"category": "electronics"}, 200, 3),  # 카테고리 필터
    ({"price_gt": 100}, 200, 2),  # 가격 필터
    ({"limit": -1}, 422, None),  # 유효하지 않은 제한값
])
def test_get_items_with_filters(client, query_params, expected_status, expected_count):
    # 다양한 필터와 함께 아이템 목록 조회 API 테스트
    response = client.get("/api/v1/items", params=query_params)
    
    # 응답 상태 코드 확인
    assert response.status_code == expected_status
    
    # 성공 응답인 경우 결과 수 확인
    if expected_status == 200:
        items = response.json()
        assert len(items) == expected_count
```

### 인증된 API 테스트

```python
# tests/test_api/test_secure_endpoints.py
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.common.dependencies.auth import get_current_user
from app.api.v1.secure import router as secure_router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(secure_router, prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def admin_token():
    # 관리자 토큰 생성 모의
    with patch("app.common.security.jwt.create_access_token") as mock_token:
        mock_token.return_value = "admin_token"
        yield "admin_token"

@pytest.fixture
def user_token():
    # 일반 사용자 토큰 생성 모의
    with patch("app.common.security.jwt.create_access_token") as mock_token:
        mock_token.return_value = "user_token"
        yield "user_token"

def test_admin_endpoint_with_admin_token(client, app, admin_token):
    # 관리자 권한이 필요한 엔드포인트 테스트 (관리자 토큰 사용)
    
    # 관리자 사용자 모의 설정
    async def mock_admin_user():
        return {"id": 1, "username": "admin", "role": "admin"}
    
    # 의존성 오버라이드
    app.dependency_overrides[get_current_user] = mock_admin_user
    
    # 관리자 엔드포인트 요청
    response = client.get(
        "/api/v1/secure/admin",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 응답 확인
    assert response.status_code == 200
    assert "admin access" in response.json()["message"]
    
    # 의존성 오버라이드 제거
    app.dependency_overrides.clear()

def test_admin_endpoint_with_user_token(client, app, user_token):
    # 관리자 권한이 필요한 엔드포인트 테스트 (일반 사용자 토큰 사용)
    
    # 일반 사용자 모의 설정
    async def mock_regular_user():
        return {"id": 2, "username": "user", "role": "user"}
    
    # 의존성 오버라이드
    app.dependency_overrides[get_current_user] = mock_regular_user
    
    # 관리자 엔드포인트 요청
    response = client.get(
        "/api/v1/secure/admin",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    # 응답 확인 (403 권한 없음)
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    
    # 의존성 오버라이드 제거
    app.dependency_overrides.clear()

def test_user_endpoint_with_no_token(client):
    # 인증이 필요한 엔드포인트 테스트 (토큰 없음)
    
    # 인증 없이 요청
    response = client.get("/api/v1/secure/user")
    
    # 응답 확인 (401 인증되지 않음)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
```

## 비동기 API 테스트

```python
# tests/test_api/test_async_endpoints.py
import pytest
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.api.v1.async_endpoints import router as async_router

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(async_router, prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_async_data_retrieval(client):
    # 비동기 데이터 조회 엔드포인트 테스트
    with patch("app.api.v1.async_endpoints.get_data_async") as mock_get_data:
        # 비동기 함수 모의 설정
        async_mock = AsyncMock()
        async_mock.return_value = {"data": "async result"}
        mock_get_data.return_value = async_mock()
        
        # 비동기 엔드포인트 요청
        response = client.get("/api/v1/async/data")
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json() == {"data": "async result"}

@pytest.mark.asyncio
async def test_async_function_directly():
    # 비동기 함수 직접 테스트
    from app.api.v1.async_endpoints import process_data_async
    
    # 테스트 데이터
    test_data = {"input": "test"}
    
    # 비동기 함수 호출
    result = await process_data_async(test_data)
    
    # 결과 확인
    assert result["processed"] == True
    assert "input" in result
    assert result["input"] == "test"
```

## 데이터베이스 통합 테스트

```python
# tests/test_api/test_db_integration.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.common.dependencies.database import get_db
from app.common.database.models import Base
from app.api.v1.db_endpoints import router as db_router

# 테스트용 비동기 SQLite 데이터베이스 설정
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

@pytest.fixture
async def setup_database():
    # 테스트 전 데이터베이스 스키마 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 테스트 실행
    yield
    
    # 테스트 후 데이터베이스 스키마 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def app(setup_database):
    app = FastAPI()
    app.include_router(db_router, prefix="/api/v1")
    
    # 의존성 오버라이드: 테스트용 데이터베이스 세션 사용
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_create_and_get_db_item(client):
    # 데이터베이스 아이템 생성 테스트
    item_data = {"name": "Test Item", "description": "Test Description"}
    create_response = client.post("/api/v1/db/items", json=item_data)
    
    # 생성 응답 확인
    assert create_response.status_code == 201
    created_item = create_response.json()
    assert created_item["name"] == item_data["name"]
    assert created_item["description"] == item_data["description"]
    assert "id" in created_item
    
    # 생성된 아이템 조회 테스트
    item_id = created_item["id"]
    get_response = client.get(f"/api/v1/db/items/{item_id}")
    
    # 조회 응답 확인
    assert get_response.status_code == 200
    retrieved_item = get_response.json()
    assert retrieved_item["id"] == item_id
    assert retrieved_item["name"] == item_data["name"]
    assert retrieved_item["description"] == item_data["description"]
```

## 모킹 전략

API 모듈 테스트에 적용할 수 있는 모킹 전략은 [공통 테스트 패턴](../common_test_patterns.md)의 모킹 전략을 참조하세요. 추가로 API 모듈에 특화된 모킹 전략은 다음과 같습니다:

1. **FastAPI TestClient**: `TestClient`를 사용하여 실제 HTTP 요청 없이 엔드포인트 테스트
2. **의존성 오버라이드**: FastAPI의 `app.dependency_overrides`를 사용하여 인증, DB 세션 등 의존성 대체
3. **모의 라우터 연결**: 테스트용 라우터를 생성하고 필요한 엔드포인트만 등록

## 테스트 커버리지 확인

API 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.api tests/test_api/
```

## 모범 사례

[공통 테스트 패턴](../common_test_patterns.md)의 모범 사례와 함께 API 모듈에 특화된 모범 사례는 다음과 같습니다:

1. **엔드포인트 분리 테스트**: 각 API 엔드포인트를 별도의 테스트 함수로 테스트
2. **HTTP 메서드별 테스트**: 같은 엔드포인트라도 다른 HTTP 메서드는 별도 테스트
3. **상태 코드 검증**: 성공/실패 상태 코드뿐만 아니라 리다이렉트, 인증 오류 등 테스트
4. **헤더 및 쿠키 테스트**: 응답 헤더와 쿠키 설정을 검증
5. **응답 형식 검증**: JSON 스키마 검증 또는 구조 검증

## 주의사항

[공통 테스트 패턴](../common_test_patterns.md)의 주의사항과 함께 API 모듈 테스트 시 추가로 고려해야 할 사항:

1. **인증 컨텍스트**: API 테스트 시 인증 토큰 관리 및 권한 검증 로직 테스트
2. **요청 제한 처리**: 속도 제한(rate limiting)이 있는 경우 테스트에 미치는 영향 고려
3. **파일 업로드/다운로드**: 파일 처리 엔드포인트는 적절한 파일 모킹 사용
4. **엔드포인트 간 의존성**: 데이터 생성 후 조회 등 연속된 작업의 테스트 순서 관리
