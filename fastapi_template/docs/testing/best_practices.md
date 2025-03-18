# 테스트 작성 모범 사례

이 문서는 FastAPI 템플릿 프로젝트의 테스트 코드 작성에 관한 모범 사례를 제공합니다.

## 테스트 격리

각 테스트는 독립적으로 실행되어야 합니다:

- 테스트 사이에 공유 상태를 최소화합니다.
- 하나의 테스트가 다른 테스트에 영향을 주지 않도록 합니다.
- 테스트가 끝날 때 시스템 상태를 정리합니다.

```python
# 테스트 격리 예시
def test_example():
    # 테스트 설정
    db = setup_test_db()
    
    # 테스트 실행
    db.create_user(name="홍길동")
    user = db.get_user_by_name("홍길동")
    assert user.name == "홍길동"
    
    # 테스트 정리
    db.clear_all()
```

## 테스트 명명 규칙

테스트 함수와 클래스의 이름을 명확하게 지정하세요:

- 테스트 함수는 `test_`로 시작해야 합니다.
- 테스트 클래스는 `Test`로 시작해야 합니다.
- 이름은 테스트 대상과 테스트 상황을 명확히 설명해야 합니다.

```python
# 좋은 테스트 명명 예시
def test_user_creation_with_valid_data():
    # ...

def test_user_creation_with_duplicate_email_raises_error():
    # ...
```

## 테스트 구조화

테스트 코드를 논리적으로 구조화하세요:

- AAA (Arrange-Act-Assert) 패턴을 따르세요:
  - Arrange: 테스트 환경 설정
  - Act: 테스트 대상 실행
  - Assert: 결과 검증
- 각 테스트는 하나의 동작만 테스트하도록 하세요.

```python
# AAA 패턴 예시
def test_user_login():
    # Arrange
    user = create_test_user(email="user@example.com", password="password123")
    
    # Act
    result = authenticate_user(email="user@example.com", password="password123")
    
    # Assert
    assert result.is_authenticated == True
    assert result.user.email == "user@example.com"
```

## Fixture 활용

반복적으로 사용되는 설정이나 객체는 pytest fixture로 정의하세요:

```python
# fixtures.py
import pytest

@pytest.fixture
def test_user():
    """테스트용 사용자 객체를 생성하는 fixture"""
    user = create_test_user(
        email="test@example.com",
        password="password123",
        name="테스트 사용자"
    )
    yield user
    # 테스트 후 정리
    delete_user(user.id)

# test_auth.py
def test_user_authentication(test_user):
    """사용자 인증을 테스트합니다."""
    result = authenticate_user(email=test_user.email, password="password123")
    assert result.is_authenticated == True
```

## 파라미터화된 테스트

유사한 테스트 케이스가 여러 개 있을 경우 `@pytest.mark.parametrize`를 활용하세요:

```python
import pytest
from app.common.validators.data_validators import validate_numeric_range

@pytest.mark.parametrize("value,min_val,max_val,expected", [
    (5, 0, 10, True),      # 범위 내
    (0, 0, 10, True),      # 최소값
    (10, 0, 10, True),     # 최대값
    (-1, 0, 10, False),    # 범위 미만
    (11, 0, 10, False),    # 범위 초과
    (5, None, 10, True),   # 최소값 없음
    (5, 0, None, True),    # 최대값 없음
])
def test_validate_numeric_range(value, min_val, max_val, expected):
    assert validate_numeric_range(value, min_val, max_val) == expected
```

## 모킹 및 패치

외부 의존성에 대한 테스트는 모킹을 사용하세요:

```python
from unittest.mock import patch, MagicMock

def test_external_api_call():
    # API 호출 결과 모킹
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test_data"}
    
    # 요청 라이브러리 패치
    with patch("requests.get", return_value=mock_response):
        result = call_external_api("https://api.example.com/data")
        
    assert result == "test_data"
```

## 예외 테스트

예외가 발생하는 상황을 테스트하려면 `pytest.raises`를 사용하세요:

```python
import pytest
from app.common.exceptions import ValidationError
from app.services.user_service import create_user

def test_user_creation_with_invalid_email():
    with pytest.raises(ValidationError) as excinfo:
        create_user(email="invalid_email", password="password123")
    
    assert "유효한 이메일 주소를 입력하세요" in str(excinfo.value)
```

## 테스트 스킵 및 표시

특정 상황에서 테스트를 스킵하거나 특별히 표시하려면 pytest 마커를 사용하세요:

```python
import pytest

@pytest.mark.skip(reason="현재 구현 중인 기능")
def test_feature_in_development():
    # 아직 개발 중인 기능 테스트
    pass

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows에서는 지원되지 않는 기능"
)
def test_unix_only_feature():
    # Unix 환경에서만 지원되는 기능 테스트
    pass

@pytest.mark.slow
def test_time_consuming_operation():
    # 시간이 오래 걸리는 테스트
    pass
```

## 데이터베이스 테스트

데이터베이스 테스트를 위한 모범 사례:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db

# 인메모리 SQLite 데이터베이스 사용
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

# get_db 의존성 오버라이드
@pytest.fixture
def override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db

# FastAPI 의존성 오버라이드
@pytest.fixture
def app(override_get_db):
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)
```

## 비동기 코드 테스트

비동기 코드 테스트는 `pytest-asyncio`를 사용하세요:

```python
import pytest
from app.async_service import fetch_data

@pytest.mark.asyncio
async def test_fetch_data():
    data = await fetch_data("test")
    assert data is not None
    assert isinstance(data, dict)
```

## 코드 커버리지 향상

테스트 커버리지를 향상시키는 모범 사례:

- 경계값 분석(Boundary Value Analysis)을 수행하세요.
- 모든 코드 경로를 테스트하세요.
- 예외 케이스도 테스트하세요.
- 정기적으로 커버리지 보고서를 확인하세요.

```bash
pytest --cov=app --cov-report=html tests/
```

## 테스트 환경 변수 관리

테스트 환경 변수는 `conftest.py`에서 설정하세요:

```python
# conftest.py
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    """테스트 환경 변수를 설정합니다"""
    # 원래 환경 변수 저장
    original_vars = {}
    for key in ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]:
        original_vars[key] = os.environ.get(key)
    
    # 테스트 환경 변수 설정
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["SECRET_KEY"] = "test_secret_key"
    
    yield
    
    # 원래 환경 변수 복원
    for key, value in original_vars.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value
```

## 테스트 문서화

각 테스트 함수와 클래스에 문서 문자열을 추가하세요:

```python
def test_user_registration():
    """
    사용자 등록 기능을 테스트합니다.
    
    테스트 케이스:
    1. 유효한 사용자 데이터로 등록이 성공하는지 확인
    2. 사용자가 데이터베이스에 올바르게 저장되는지 확인
    3. 가입 이메일이 올바르게 전송되는지 확인
    """
    # 테스트 구현
    pass
```
