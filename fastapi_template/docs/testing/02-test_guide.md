# 테스트 시작 및 실행 가이드

이 문서는 FastAPI 템플릿 프로젝트의 테스트를 빠르게 시작하고 다양한 방법으로 실행하는 방법을 설명합니다.

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

## 2. 테스트 실행 방법

### 기본 테스트 실행

모든 테스트를 실행하려면:

```bash
# 프로젝트 루트 디렉토리에서
pytest
```

### 특정 테스트 파일 실행

특정 테스트 파일만 실행하려면:

```bash
# 특정 파일 실행
pytest tests/test_api/test_health.py

# 특정 디렉토리의 모든 테스트 실행
pytest tests/test_api/
```

### 특정 테스트 함수 실행

특정 테스트 함수만 실행하려면:

```bash
# 특정 테스트 함수 실행
pytest tests/test_api/test_health.py::test_health_endpoint

# 특정 함수 이름 패턴으로 테스트 실행
pytest -k "config or auth"
```

### 테스트 출력 상세도 조절

테스트 출력의 상세도를 조절하려면:

```bash
# 자세한 출력
pytest -v

# 매우 자세한 출력
pytest -vv

# 실패한 테스트만 출력
pytest --no-header --no-summary -q
```

### 테스트 커버리지 측정

코드 커버리지를 측정하려면:

```bash
# 기본 커버리지 측정
pytest --cov=app tests/

# 커버리지 보고서 HTML 형식으로 생성
pytest --cov=app --cov-report=html tests/

# 커버리지 보고서 XML 형식으로 생성 (CI 통합용)
pytest --cov=app --cov-report=xml tests/
```

### 병렬 테스트 실행

테스트를 병렬로 실행하려면:

```bash
# 4개의 프로세스로 병렬 실행
pytest -n 4
```

### 테스트 로깅 설정

테스트 중 로그 출력을 보려면:

```bash
# 로그 레벨 설정
pytest --log-cli-level=INFO

# 로그 출력을 파일에 저장
pytest --log-file=test_log.txt
```

### 비동기 테스트 실행

비동기 테스트를 실행하려면:

```bash
# pytest-asyncio 사용
pytest --asyncio-mode=auto
```

### CI 환경에서 테스트 실행

CI 환경에서는 다음과 같은 명령을 사용하는 것이 좋습니다:

```bash
pytest --cov=app --cov-report=xml --junitxml=test-results.xml
```

이 명령은 코드 커버리지 보고서와 테스트 결과를 CI 도구에서 처리할 수 있는 형식으로 생성합니다.

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

## 데이터베이스 테스트

데이터베이스 테스트를 위해 인메모리 데이터베이스를 사용하려면 환경 변수를 설정하세요:

```bash
# SQLite 인메모리 데이터베이스 사용
export DATABASE_URL=sqlite:///./test.db
```

또는 `.env.test` 파일에 다음을 추가하세요:

```
DATABASE_URL=sqlite:///./test.db
```

## 다음 단계

더 자세한 내용은 다음 문서를 참조하세요:

- [테스트 개요 및 구조](01-test_overview.md)
- [테스트 모범 사례 및 패턴](03-test_practices.md)
- [모듈별 테스트 가이드](04-test_modules.md)
- [테스트 도구 가이드](05-test_tools.md) 