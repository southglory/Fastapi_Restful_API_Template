# 테스트 퀵 스타트 가이드

이 문서는 FastAPI 템플릿 프로젝트의 테스트를 빠르게 시작할 수 있는 가이드를 제공합니다.

## 1. 환경 설정

### 의존성 설치

```bash
pip install -r requirements-dev.txt
```

### 테스트 환경 설정

`.env.test` 파일을 프로젝트 루트에 생성하고 테스트용 환경 변수를 설정하세요:

```bash
# .env.test 예시
APP_ENV=test
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test_secret_key
```

## 2. 테스트 실행

### 전체 테스트 실행

```bash
pytest
```

### 특정 테스트 파일 실행

```bash
pytest tests/test_api/test_health.py
```

### 테스트 커버리지 측정

```bash
pytest --cov=app tests/
```

## 3. 테스트 작성 예시

### 단위 테스트 예시

```python
# tests/test_validators/test_string_validators.py
import pytest
from app.common.validators.string_validators import validate_email

def test_validate_email():
    # 유효한 이메일 테스트
    assert validate_email("user@example.com") == True
    
    # 유효하지 않은 이메일 테스트
    assert validate_email("invalid_email") == False
```

### API 테스트 예시

```python
# tests/test_api/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

### 비동기 테스트 예시

```python
# tests/test_services/test_async_service.py
import pytest
from app.services.data_service import get_data

@pytest.mark.asyncio
async def test_get_data():
    # 비동기 함수 테스트
    data = await get_data(1)
    assert data is not None
    assert "id" in data
```

## 4. 픽스처 사용 예시

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# DB 픽스처
@pytest.fixture
def test_db():
    # 테스트 DB 설정
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # DB 세션 제공
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 테스트 후 테이블 삭제
        Base.metadata.drop_all(bind=engine)

# API 테스트 클라이언트
@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

## 5. 모킹 예시

```python
# tests/test_services/test_user_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.user_service import get_user_data

def test_get_user_data():
    # 외부 API 호출 모킹
    with patch("app.services.user_service.requests.get") as mock_get:
        # 모의 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test User"}
        mock_get.return_value = mock_response
        
        # 테스트 실행
        result = get_user_data(1)
        
        # 검증
        assert result["id"] == 1
        assert result["name"] == "Test User"
        mock_get.assert_called_once_with("https://api.example.com/users/1")
```

## 6. 테스트 파라미터화

```python
# tests/test_utils/test_math_utils.py
import pytest
from app.common.utils.math_utils import calculate_total

@pytest.mark.parametrize("items,expected", [
    ([10, 20, 30], 60),
    ([], 0),
    ([5], 5),
    ([-5, 10], 5)
])
def test_calculate_total(items, expected):
    assert calculate_total(items) == expected
```

## 다음 단계

더 자세한 내용은 다음 문서를 참조하세요:

- [테스트 개요](overview.md)
- [테스트 구조](structure.md)
- [모듈별 테스트 가이드](module_guides.md)
- [테스트 작성 모범 사례](best_practices.md)
- [테스트 도구 가이드](tools.md)
