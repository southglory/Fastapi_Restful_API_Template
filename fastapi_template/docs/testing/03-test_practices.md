# 테스트 모범 사례 및 패턴

이 문서는 FastAPI 템플릿 프로젝트의 테스트 코드 작성에 관한 모범 사례와 공통 패턴을 제공합니다.

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

## 모듈 테스트 문서 구조

각 모듈 테스트 가이드는 다음 구조를 따라야 합니다:

```markdown
# [모듈명] 모듈 테스트 가이드

## 개요

`[모듈명]` 모듈은 [모듈의 주요 목적 및 기능에 대한 간략한 설명]

## 테스트 용이성

- **난이도**: [쉬움|중간|어려움|매우 어려움]
- **이유**:
  - [난이도 평가 이유 1]
  - [난이도 평가 이유 2]
  - ...

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **[테스트 대상 카테고리 1]**
   - [세부 기능 1]
   - [세부 기능 2]
   - ...

2. **[테스트 대상 카테고리 2]**
   - [세부 기능 1]
   - [세부 기능 2]
   - ...
   
3. ...

## 테스트 접근법

[모듈명] 모듈 테스트 시 다음 접근법을 권장합니다:

1. **[접근법 1]**: [설명]
2. **[접근법 2]**: [설명]
3. ...

## 테스트 예시

### [예시 카테고리 1]

```python
# 테스트 코드 예시
```

### [예시 카테고리 2]

```python
# 테스트 코드 예시
```

## 모킹 전략

[모듈명] 모듈 테스트 시 다음과 같은 모킹 전략을 활용할 수 있습니다:

1. **[모킹 전략 1]**: [설명]
2. **[모킹 전략 2]**: [설명]
3. ...

## 테스트 커버리지 확인

[모듈명] 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=[모듈 경로] [테스트 경로]
```

## 모범 사례

1. **[모범 사례 1]**: [설명]
2. **[모범 사례 2]**: [설명]
3. ...

## 주의사항

1. **[주의사항 1]**: [설명]
2. **[주의사항 2]**: [설명]
3. ...

```

## 공통 테스트 접근법

대부분의 모듈에 적용 가능한 일반적인 테스트 접근법:

1. **단위 테스트**: 개별 함수/메서드/클래스를 독립적으로 테스트
2. **통합 테스트**: 모듈 간 또는 외부 시스템과의 상호작용 테스트
3. **기능 테스트**: 특정 기능이나 시나리오의 전체 흐름 테스트
4. **모의 테스트**: 외부 의존성을 모킹하여 테스트
5. **파라미터화 테스트**: 다양한 입력값으로 같은 테스트 반복
6. **예외 테스트**: 오류 상황 및 예외 처리 테스트

## 공통 모킹 전략

여러 모듈 테스트에 공통적으로 적용할 수 있는 모킹 전략:

1. **의존성 대체**: 실제 외부 시스템 대신 테스트용 구현체 사용
2. **함수/메서드 모킹**: `unittest.mock.patch` 또는 `pytest-mock`을 사용
3. **컨텍스트 관리자**: `with` 문을 사용한 임시 모킹
4. **픽스처 기반 모킹**: `pytest` 픽스처를 사용한 재사용 가능한 모킹 설정
5. **인메모리 대체**: 실제 데이터베이스 대신 인메모리 구현체 사용

## 공통 모범 사례

테스트 작성 시 고려해야 할 일반적인 모범 사례:

1. **격리된 테스트**: 각 테스트는 독립적으로 실행 가능해야 함
2. **사전 조건 명확화**: 테스트에 필요한 초기 상태를 명확히 설정
3. **검증 단계 분리**: 준비(Arrange) → 실행(Act) → 검증(Assert) 패턴 사용
4. **복잡성 관리**: 테스트 코드는 간결하고 이해하기 쉽게 작성
5. **명확한 테스트 이름**: 테스트 함수 이름은 테스트 목적을 명확히 설명
6. **테스트 중복 최소화**: 공통 설정은 픽스처나 헬퍼 함수로 추출
7. **코드 커버리지 관리**: 주요 코드 경로와 예외 상황 모두 테스트

## 공통 주의사항

테스트 작성 시 주의해야 할 일반적인 사항:

1. **상태 관리**: 테스트 간 상태 공유 최소화 및 적절한 정리
2. **외부 의존성**: 외부 시스템 의존 테스트는 별도 분리하고 스킵 옵션 제공
3. **테스트 속도**: 테스트는 가능한 빠르게 실행되도록 설계
4. **비결정적 요소**: 날짜/시간, 무작위성 등 비결정적 요소 제어
5. **환경 변수**: 환경 변수에 의존하는 테스트는 환경 격리 제공

## 다음 단계

테스트 작성에 도움이 될 다른 문서를 확인하세요:

- [테스트 개요 및 구조](01-test_overview.md)
- [테스트 시작 및 실행 가이드](02-test_guide.md)
- [모듈별 테스트 가이드](04-test_modules.md)
- [테스트 도구 가이드](05-test_tools.md)
