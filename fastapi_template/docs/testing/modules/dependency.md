# Dependency 모듈 테스트 가이드

## 개요

`dependency` 모듈(`app/common/dependencies`)은 FastAPI의 의존성 주입 시스템을 활용하여 요청 처리 과정에서 필요한 다양한 종속성을 제공합니다. 이 모듈은 사용자 인증, 데이터베이스 세션 관리, 권한 검증, 요청 유효성 검사 등을 처리하는 재사용 가능한 구성 요소들을 포함합니다.

> **참고**: 의존성 모듈은 이전에 `app/api/dependencies.py`에 위치했으나, 재사용성을 높이기 위해 `app/common/dependencies/` 디렉토리로 이동되었습니다. 하위 호환성을 위해 `app/api/dependencies.py`는 `app/common/dependencies` 모듈을 임포트하여 동일한 인터페이스를 제공합니다.

## 테스트 용이성

- **난이도**: 중간-어려움
- **이유**:
  - FastAPI의 의존성 주입 시스템과 통합되어 있음
  - 종속성 간의 복잡한 상호작용이 발생할 수 있음
  - 인증/권한 관련 의존성은 보안 컨텍스트를 필요로 함
  - 데이터베이스, 캐시 등 외부 서비스에 의존하는 경우가 많음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **사용자 인증 의존성**
   - 토큰 유효성 검증
   - 현재 사용자 식별/검색
   - 권한 확인

2. **데이터베이스 의존성**
   - 세션 생성 및 관리
   - 트랜잭션 처리
   - 세션 종료 및 정리

3. **유효성 검사 의존성**
   - 요청 파라미터 검증
   - 헤더/쿠키 검증
   - 입력 데이터 정제

4. **서비스 의존성**
   - API 클라이언트 의존성
   - 캐시 관리자 의존성
   - 비즈니스 로직 의존성

## 테스트 접근법

Dependency 모듈 테스트 시 다음 접근법을 권장합니다:

1. **단위 테스트**: 의존성 함수/클래스를 독립적으로 테스트
2. **통합 테스트**: FastAPI의 TestClient를 사용하여 실제 엔드포인트에서 의존성 작동 검증
3. **모의 객체 사용**: 복잡한 의존성을 단순화하기 위해 모의 객체 활용

## 테스트 예시

### 인증 의존성 테스트

```python
# tests/test_dependencies/test_auth_dependencies.py
import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.common.dependencies.auth import get_current_user, has_permission

# 테스트용 앱 설정
@pytest.fixture
def app():
    app = FastAPI()
    
    # 테스트용 엔드포인트 정의
    @app.get("/me")
    async def read_users_me(current_user = Depends(get_current_user)):
        return current_user
    
    @app.get("/admin-only")
    async def admin_only(user = Depends(has_permission("admin"))):
        return {"message": "Admin access granted", "user": user}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_get_current_user_valid_token(client):
    # 유효한 토큰으로 get_current_user 테스트
    with patch("app.common.dependencies.auth.decode_token") as mock_decode:
        # 유효한 토큰 디코딩 결과 모의 설정
        mock_decode.return_value = {"sub": "user123", "role": "user"}
        
        # 테스트 요청 실행
        response = client.get(
            "/me", 
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json()["sub"] == "user123"
        assert response.json()["role"] == "user"

def test_get_current_user_invalid_token(client):
    # 유효하지 않은 토큰으로 get_current_user 테스트
    with patch("app.common.dependencies.auth.decode_token") as mock_decode:
        # 토큰 디코딩 실패 시뮬레이션
        mock_decode.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
        # 테스트 요청 실행
        response = client.get(
            "/me", 
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        # 응답 확인
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]

def test_get_current_user_missing_token(client):
    # 토큰 없이 get_current_user 테스트
    response = client.get("/me")
    
    # 응답 확인
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_has_permission_authorized(client):
    # 올바른 권한으로 has_permission 테스트
    with patch("app.common.dependencies.auth.get_current_user") as mock_get_user:
        # 관리자 권한을 가진 사용자 모의 설정
        mock_get_user.return_value = {"sub": "admin123", "role": "admin"}
        
        # 테스트 요청 실행
        response = client.get(
            "/admin-only", 
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json()["message"] == "Admin access granted"

def test_has_permission_unauthorized(client):
    # 권한이 없는 사용자로 has_permission 테스트
    with patch("app.common.dependencies.auth.get_current_user") as mock_get_user:
        # 일반 사용자 권한을 가진 사용자 모의 설정
        mock_get_user.return_value = {"sub": "user123", "role": "user"}
        
        # 테스트 요청 실행
        response = client.get(
            "/admin-only", 
            headers={"Authorization": "Bearer user_token"}
        )
        
        # 응답 확인
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]
```

### 데이터베이스 의존성 테스트

```python
# tests/test_dependencies/test_db_dependencies.py
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies.database import get_db, get_db_transaction

@pytest.fixture
def mock_session():
    # 비동기 세션 모의 객체
    mock = AsyncMock(spec=AsyncSession)
    
    # commit, rollback, close 메서드 설정
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.close = AsyncMock()
    
    return mock

@pytest.fixture
def app(mock_session):
    app = FastAPI()
    
    # 트랜잭션 테스트용 엔드포인트
    @app.get("/transaction")
    async def with_transaction(db = Depends(get_db_transaction)):
        # DB 작업 시뮬레이션
        await db.execute("SELECT 1")
        return {"transaction": "committed"}
    
    # 일반 세션 테스트용 엔드포인트
    @app.get("/session")
    async def with_session(db = Depends(get_db)):
        # DB 작업 시뮬레이션
        await db.execute("SELECT 1")
        return {"session": "used"}
    
    # 오류 발생 테스트용 엔드포인트
    @app.get("/error")
    async def with_error(db = Depends(get_db_transaction)):
        # DB 작업 후 오류 발생 시뮬레이션
        await db.execute("SELECT 1")
        raise ValueError("Test error")
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.mark.asyncio
async def test_get_db_session():
    # get_db 의존성 직접 테스트
    with patch("app.common.dependencies.database.AsyncSession") as mock_session_class:
        # 세션 모의 객체 설정
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        
        # get_db 의존성 호출
        session_gen = get_db()
        session = await session_gen.__anext__()
        
        # 올바른 세션 객체가 반환되었는지 확인
        assert session == mock_session
        
        try:
            # 제너레이터 완료
            await session_gen.__anext__()
        except StopAsyncIteration:
            pass
        
        # 세션이 닫혔는지 확인
        assert mock_session.close.called

def test_get_db_endpoint(client, mock_session):
    # get_db 의존성을 사용하는 엔드포인트 테스트
    with patch("app.common.dependencies.database.get_db") as mock_get_db:
        # get_db가 모의 세션 반환하도록 설정
        async def mock_db_gen():
            yield mock_session
        
        mock_get_db.return_value = mock_db_gen()
        
        # 엔드포인트 호출
        response = client.get("/session")
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json() == {"session": "used"}
        
        # execute 호출 확인
        assert mock_session.execute.called
        # close 호출 확인
        assert mock_session.close.called

def test_get_db_transaction_success(client, mock_session):
    # 성공적인 트랜잭션 테스트
    with patch("app.common.dependencies.database.get_db_transaction") as mock_get_tx:
        # get_db_transaction이 모의 세션 반환하도록 설정
        async def mock_tx_gen():
            yield mock_session
        
        mock_get_tx.return_value = mock_tx_gen()
        
        # 엔드포인트 호출
        response = client.get("/transaction")
        
        # 응답 확인
        assert response.status_code == 200
        assert response.json() == {"transaction": "committed"}
        
        # 트랜잭션 커밋 확인
        assert mock_session.commit.called
        assert not mock_session.rollback.called

def test_get_db_transaction_error(client, mock_session):
    # 오류 발생 시 트랜잭션 롤백 테스트
    with patch("app.common.dependencies.database.get_db_transaction") as mock_get_tx:
        # get_db_transaction이 모의 세션 반환하도록 설정
        async def mock_tx_gen():
            yield mock_session
        
        mock_get_tx.return_value = mock_tx_gen()
        
        # 오류 발생 엔드포인트 호출
        response = client.get("/error")
        
        # 응답은 500이어야 함
        assert response.status_code == 500
        
        # 트랜잭션 롤백 확인
        assert mock_session.rollback.called
        assert not mock_session.commit.called
```

### 캐시 의존성 테스트

```python
# tests/test_dependencies/test_cache_dependencies.py
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.common.dependencies.cache import get_cache_manager, use_cached_result

@pytest.fixture
def mock_cache():
    # 캐시 관리자 모의 객체
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    return cache

@pytest.fixture
def app(mock_cache):
    app = FastAPI()
    
    # 캐시 모의 객체를 반환하는 의존성 함수
    async def get_test_cache():
        yield mock_cache
    
    # 캐시 의존성 오버라이드
    app.dependency_overrides[get_cache_manager] = get_test_cache
    
    # 캐시된 결과 사용 테스트용 엔드포인트
    @app.get("/cached/{item_id}")
    @use_cached_result(prefix="test", ttl=300)
    async def cached_endpoint(item_id: int, cache = Depends(get_cache_manager)):
        # 이 함수는 캐시된 결과가 없을 때만 실행됨
        return {"item_id": item_id, "computed": True}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_get_cache_hit(client, mock_cache):
    # 캐시 적중 케이스 테스트
    # 캐시에서 값을 반환하도록 설정
    mock_cache.get.return_value = {"item_id": 123, "cached": True}
    
    # 요청 실행
    response = client.get("/cached/123")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json() == {"item_id": 123, "cached": True}
    
    # 캐시 get 호출 확인
    mock_cache.get.assert_called_once()
    # 캐시 set은 호출되지 않아야 함 (이미 캐시에 있으므로)
    mock_cache.set.assert_not_called()

def test_get_cache_miss(client, mock_cache):
    # 캐시 미스 케이스 테스트
    # 캐시에 값이 없음을 시뮬레이션
    mock_cache.get.return_value = None
    
    # 요청 실행
    response = client.get("/cached/456")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json() == {"item_id": 456, "computed": True}
    
    # 캐시 get 호출 확인
    mock_cache.get.assert_called_once()
    # 캐시 set 호출 확인 (결과를 캐시에 저장)
    mock_cache.set.assert_called_once()
    # 캐시 키와 TTL 확인
    cache_key = f"test:456"
    mock_cache.set.assert_called_with(cache_key, {"item_id": 456, "computed": True}, 300)
```

### 모의 의존성 테스트

```python
# tests/test_dependencies/test_dependency_overrides.py
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from app.common.dependencies.auth import get_current_user
from app.common.dependencies.database import get_db

@pytest.fixture
def app():
    app = FastAPI()
    
    # 의존성을 사용하는 엔드포인트
    @app.get("/user-db")
    async def user_with_db(user = Depends(get_current_user), db = Depends(get_db)):
        # 실제로는 DB에서 사용자 데이터를 조회할 것
        return {"user_id": user["sub"], "db_connected": True}
    
    return app

@pytest.fixture
def client(app):
    # 테스트용 의존성 오버라이드
    
    # 인증된 사용자 모의 의존성
    async def mock_current_user():
        return {"sub": "test_user", "role": "tester"}
    
    # DB 세션 모의 의존성
    async def mock_db():
        # 실제 DB 대신 더미 객체 반환
        yield {"connected": True}
    
    # 앱의 의존성 오버라이드 설정
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_db] = mock_db
    
    return TestClient(app)

def test_dependency_overrides(client):
    # 모의 의존성을 사용한 엔드포인트 테스트
    response = client.get("/user-db")
    
    # 응답 확인
    assert response.status_code == 200
    assert response.json() == {"user_id": "test_user", "db_connected": True}
```

## 통합 테스트

여러 의존성이 함께 작동하는 통합 테스트:

```python
# tests/test_dependencies/test_dependency_integration.py
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.common.dependencies.auth import get_current_user
from app.common.dependencies.database import get_db
from app.common.dependencies.cache import get_cache_manager

@pytest.fixture
def app():
    app = FastAPI()
    
    # 여러 의존성을 사용하는 엔드포인트
    @app.get("/user-data")
    async def get_user_data(
        user = Depends(get_current_user),
        db = Depends(get_db),
        cache = Depends(get_cache_manager)
    ):
        # 캐시에서 사용자 데이터 확인
        cache_key = f"user_data:{user['sub']}"
        data = await cache.get(cache_key)
        
        if not data:
            # 캐시에 없으면 DB에서 조회
            query = f"SELECT * FROM users WHERE id = '{user['sub']}'"
            result = await db.execute(query)
            data = {"user_id": user["sub"], "db_result": result}
            
            # 결과를 캐시에 저장
            await cache.set(cache_key, data, 300)
        
        return data
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_complex_dependency_chain(client):
    # 각 의존성에 대한 모의 객체 설정
    with patch("app.common.dependencies.auth.decode_token") as mock_decode, \
         patch("app.common.dependencies.database.get_db") as mock_get_db, \
         patch("app.common.dependencies.cache.get_cache_manager") as mock_get_cache:
        
        # 사용자 토큰 디코딩 모의 설정
        mock_decode.return_value = {"sub": "user123", "role": "user"}
        
        # 모의 DB 세션 설정
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value={"row_count": 1})
        
        async def mock_db_gen():
            yield mock_db
        
        mock_get_db.return_value = mock_db_gen()
        
        # 모의 캐시 관리자 설정
        mock_cache = AsyncMock()
        # 첫 번째 호출에서는 캐시 미스, 두 번째 호출에서는 캐시 적중
        mock_cache.get = AsyncMock(side_effect=[None, {"user_id": "user123", "cached": True}])
        
        async def mock_cache_gen():
            yield mock_cache
        
        mock_get_cache.return_value = mock_cache_gen()
        
        # 첫 번째 요청 - 캐시 미스, DB 조회 필요
        response1 = client.get(
            "/user-data", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 응답 확인
        assert response1.status_code == 200
        assert response1.json()["user_id"] == "user123"
        assert "db_result" in response1.json()
        
        # DB 실행 및 캐시 저장 확인
        assert mock_db.execute.called
        assert mock_cache.set.called
        
        # 두 번째 요청 - 캐시 적중, DB 조회 불필요
        response2 = client.get(
            "/user-data", 
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 응답 확인
        assert response2.status_code == 200
        assert response2.json()["user_id"] == "user123"
        assert response2.json()["cached"] == True
        
        # DB는 한 번만 호출되어야 함
        assert mock_db.execute.call_count == 1
```

## 모킹 전략

[공통 테스트 패턴](../common_test_patterns.md)의 모킹 전략을 참조하세요. Dependency 모듈에 특화된 모킹 전략은 다음과 같습니다:

1. **FastAPI의 dependency_overrides**: 테스트 중에 의존성 함수를 모의 함수로 대체
2. **컨텍스트 모킹**: 세션, 트랜잭션 등 컨텍스트 매니저 모킹
3. **AsyncMock**: 비동기 의존성 함수/메서드의 모의 객체 생성
4. **TestClient 통합**: FastAPI의 `TestClient`를 사용하여 의존성 체인 테스트

## 테스트 커버리지 확인

Dependency 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.dependencies tests/test_dependencies/
```

## 모범 사례

[공통 테스트 패턴](../common_test_patterns.md)의 모범 사례와 함께 Dependency 모듈에 특화된 모범 사례는 다음과 같습니다:

1. **단순화된 테스트**: 복잡한 의존성은 더 작은 단위로 분리하여 테스트
2. **의존성 오버라이드 활용**: 테스트에서 실제 구현 대신 모의 객체 사용
3. **시나리오 테스트**: 다양한 조건에서 의존성 동작 검증 (성공, 실패, 예외 등)
4. **yield 의존성 테스트**: 의존성 함수가 yield를 사용하는 경우 전/후처리 로직 테스트

## 주의사항

[공통 테스트 패턴](../common_test_patterns.md)의 주의사항과 함께 Dependency 모듈 테스트 시 추가로 고려해야 할 사항:

1. **비동기 코드 처리**: 비동기 의존성 함수는 `pytest-asyncio`를 사용하여 테스트
2. **의존성 주입 순서**: FastAPI에서 의존성 주입 순서가 중요할 수 있으므로 순서 확인
3. **의존성 체인**: 의존성이 다른 의존성에 의존하는 복잡한 체인 테스트 시 주의
4. **FastAPI 통합**: 테스트가 FastAPI 프레임워크와 올바르게 통합되는지 확인
