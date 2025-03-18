# 테스트 개요 및 구조

이 문서는 FastAPI 템플릿 프로젝트의 테스트 방법론, 접근 방식 및 코드 구조에 대한 개요를 제공합니다.

## 테스트 철학

이 프로젝트는 다음과 같은 테스트 철학을 따릅니다:

1. **테스트 자동화**: 모든 테스트는 자동화되어 CI/CD 파이프라인에서 실행될 수 있어야 합니다.
2. **테스트 피라미드**: 단위 테스트 > 통합 테스트 > E2E 테스트 비율을 유지합니다.
3. **격리된 테스트**: 각 테스트는 독립적으로 실행될 수 있어야 합니다.
4. **테스트 가독성**: 테스트 코드는 명확하고 이해하기 쉬워야 합니다.

## 테스트 유형

이 프로젝트는 다음과 같은 테스트 유형을 지원합니다:

1. **단위 테스트**: 개별 함수나 메서드의 기능 테스트
2. **통합 테스트**: 여러 모듈 간의 상호작용 테스트
3. **API 테스트**: HTTP 엔드포인트 테스트
4. **E2E 테스트**: 전체 애플리케이션 흐름 테스트

## 테스트 도구

프로젝트에서 사용하는 주요 테스트 도구:

- **pytest**: 기본 테스트 프레임워크
- **pytest-asyncio**: 비동기 코드 테스트
- **pytest-cov**: 코드 커버리지 측정
- **TestClient**: FastAPI의 내장 테스트 클라이언트

## 테스트 환경

테스트는 다음과 같은 환경에서 실행될 수 있습니다:

1. **로컬 개발 환경**: 개발자의 로컬 머신에서 실행
2. **CI 환경**: GitHub Actions 또는 다른 CI 도구에서 자동으로 실행
3. **스테이징 환경**: 배포 전 최종 검증을 위한 환경

## 테스트 데이터 관리

테스트 데이터는 다음과 같은 방식으로 관리됩니다:

1. **픽스처(Fixture)**: pytest 픽스처를 사용하여 테스트 데이터 제공
2. **팩토리(Factory)**: 테스트 객체 생성을 위한 팩토리 함수
3. **모킹(Mocking)**: 외부 의존성에 대한 모의 객체 사용
4. **인메모리 데이터베이스**: 테스트용 SQLite 인메모리 데이터베이스 활용

## 테스트 문서 구조

테스트 문서는 다음과 같은 구조로 정리되어 있습니다:

```
fastapi_template/
└── docs/
    ├── testing/
    │   ├── 01-test_overview.md    # 테스트 개요 및 구조 (현재 문서)
    │   ├── 02-test_guide.md       # 테스트 시작 및 실행 방법
    │   ├── 03-test_practices.md   # 테스트 모범 사례 및 패턴
    │   ├── 04-test_modules.md     # 모듈별 테스트 가이드
    │   ├── 05-test_tools.md       # 테스트 도구 가이드
    │   └── modules/               # 모듈별 상세 테스트 가이드
    │       ├── validators.md
    │       ├── security.md
    │       └── ...
    └── ...
```

## 디렉토리 구조

테스트 코드는 다음과 같은 디렉토리 구조로 정리되어 있습니다:

```
fastapi_template/
├── tests/
│   ├── conftest.py          # 테스트 설정 및 공통 fixture
│   ├── test_main.py         # 메인 애플리케이션 테스트
│   ├── test_common_modules.py # 공통 모듈 테스트
│   ├── test_api/            # API 엔드포인트 테스트
│   │   ├── test_health.py
│   │   ├── test_auth.py
│   │   └── test_users.py
│   ├── test_auth/           # 인증 모듈 테스트
│   │   ├── test_jwt.py
│   │   ├── test_password.py
│   │   └── test_deps.py
│   ├── test_validators/     # 유효성 검증 모듈 테스트
│   │   ├── test_string_validators.py
│   │   ├── test_data_validators.py
│   │   └── test_file_validators.py
│   ├── test_security/       # 보안 모듈 테스트
│   │   ├── test_encryption.py
│   │   └── test_hashing.py
│   ├── test_config/         # 설정 모듈 테스트
│   │   └── test_settings.py
│   ├── test_utils/          # 유틸리티 모듈 테스트
│   │   ├── test_date_utils.py
│   │   ├── test_string_utils.py
│   │   └── test_file_utils.py
│   ├── test_schemas/        # 스키마 모듈 테스트
│   │   └── test_base_schema.py
│   ├── test_exceptions/     # 예외 처리 모듈 테스트
│   │   └── test_custom_exceptions.py
│   ├── test_middleware/     # 미들웨어 모듈 테스트
│   │   └── test_request_id_middleware.py
│   ├── test_cache/          # 캐싱 모듈 테스트
│   │   └── test_redis_cache.py
│   ├── test_db/             # 데이터베이스 모듈 테스트
│   │   ├── test_models.py
│   │   └── test_session.py
│   └── test_monitoring/     # 모니터링 모듈 테스트
│       ├── test_health.py
│       └── test_logging.py
```

## 테스트 모듈 구성

각 테스트 모듈은 다음과 같은 구성으로 작성됩니다:

1. **가져오기**: 필요한 모듈, 클래스, 함수 가져오기
2. **fixture 정의**: 테스트에 필요한 fixture 정의
3. **테스트 함수**: 개별 테스트 함수 구현
4. **보조 함수**: 테스트에 필요한 헬퍼 함수 정의

```python
# 테스트 모듈 예시
import pytest
from app.common.validators.string_validators import validate_email

# fixture 정의
@pytest.fixture
def sample_emails():
    return {
        "valid": ["user@example.com", "user.name@company.co.kr"],
        "invalid": ["invalid_email", "user@", "@domain.com"]
    }

# 테스트 함수
def test_validate_email_with_valid_emails(sample_emails):
    for email in sample_emails["valid"]:
        assert validate_email(email) == True

def test_validate_email_with_invalid_emails(sample_emails):
    for email in sample_emails["invalid"]:
        assert validate_email(email) == False

# 보조 함수
def generate_random_email():
    import random
    import string
    username = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
    return f"{username}@{domain}.com"
```

## conftest.py 파일

`conftest.py` 파일은 여러 테스트 모듈에서 공유되는 fixture를 정의합니다:

```python
# tests/conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# 테스트 데이터베이스 설정
@pytest.fixture(scope="session")
def test_db_engine():
    # 인메모리 SQLite 데이터베이스 사용
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    # 세션 생성
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    
    yield session
    
    # 세션 정리
    session.rollback()
    session.close()

# FastAPI 의존성 오버라이드
@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db

@pytest.fixture(scope="function")
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# 테스트 사용자 데이터
@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "테스트 사용자"
    }

# 환경 변수 설정
@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    # 원래 환경 변수 저장
    original_vars = {}
    test_vars = {
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/1",
        "SECRET_KEY": "test_secret_key",
        "ENVIRONMENT": "test"
    }
    
    # 환경 변수 백업 및 설정
    for key, value in test_vars.items():
        original_vars[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # 원래 환경 변수 복원
    for key, value in original_vars.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value
```

## 테스트 태그 및 마커

테스트에 태그와 마커를 사용하여 필터링하고 그룹화할 수 있습니다:

```python
# pytest.ini 파일 예시
[pytest]
markers =
    slow: 실행 시간이 긴 테스트
    integration: 통합 테스트
    api: API 엔드포인트 테스트
    unit: 단위 테스트
    auth: 인증 관련 테스트
    db: 데이터베이스 관련 테스트
    
# 마커 사용 예시
@pytest.mark.slow
@pytest.mark.db
def test_database_migration():
    # 데이터베이스 마이그레이션 테스트
    pass
```

## 테스트 레벨 구분

테스트는 다음과 같은 레벨로 구분됩니다:

1. **단위 테스트**: 개별 함수나 메서드를 테스트합니다.

2. **통합 테스트**: 모듈 간의 상호작용을 테스트합니다.

3. **API 테스트**: HTTP 엔드포인트의 동작을 테스트합니다.

4. **E2E 테스트**: 전체 애플리케이션 흐름을 테스트합니다.
