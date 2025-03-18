# Config 모듈 테스트 가이드

## 개요

`config` 모듈은 애플리케이션의 설정 정보를 관리합니다. 주로 환경 변수와 설정 파일을 통해 애플리케이션의 동작을 설정하는 역할을 담당합니다. 이 모듈은 대부분 단순한 설정값을 제공하지만, 환경 변수에 의존성이 있어 테스트 시 이를 고려해야 합니다.

## 테스트 용이성

- **난이도**: 쉬움-중간
- **이유**:
  - 환경 변수와 설정 파일에 의존
  - 대부분의 기능이 순수하고 결정적임
  - 테스트 환경과 프로덕션 환경의 분리가 필요함

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **설정 로드 기능**
   - 환경 변수에서 설정 로드
   - 기본값 적용
   - 설정 파일 로드

2. **설정 검증 기능**
   - 필수 설정값 존재 확인
   - 설정값 타입 검증
   - 설정값 범위 검증

3. **설정 변환 기능**
   - 문자열에서 적절한 타입으로 변환
   - 경로, URL 등 특수 형식 처리

## 테스트 접근법

Config 모듈 테스트 시 다음 접근법을 권장합니다:

1. **환경 격리**: 테스트 실행 전후로 환경 변수를 백업하고 복원하여 다른 테스트에 영향을 주지 않도록 합니다.
2. **여러 환경 테스트**: 개발, 테스트, 프로덕션 등 다양한 환경 설정을 테스트합니다.
3. **오류 케이스 테스트**: 잘못된 설정, 누락된 필수 설정 등 오류 상황을 테스트합니다.

## 테스트 예시

### 환경 변수 설정 테스트

```python
# tests/test_config/test_settings.py
import os
import pytest
from app.common.config.settings import Settings

# 테스트 전후로 환경 변수 백업 및 복원
@pytest.fixture
def env_vars_setup():
    # 기존 환경 변수 백업
    original_env = os.environ.copy()
    yield
    # 테스트 후 환경 변수 복원
    os.environ.clear()
    os.environ.update(original_env)

def test_settings_load_from_env(env_vars_setup):
    # 환경 변수 설정
    os.environ["APP_NAME"] = "테스트앱"
    os.environ["DEBUG"] = "True"
    os.environ["API_PREFIX"] = "/api/v2"
    
    # 설정 로드
    settings = Settings()
    
    # 설정값 검증
    assert settings.app_name == "테스트앱"
    assert settings.debug is True
    assert settings.api_prefix == "/api/v2"
```

### 기본값 테스트

```python
# tests/test_config/test_settings_defaults.py
import os
import pytest
from app.common.config.settings import Settings

@pytest.fixture
def clear_env_vars():
    # 테스트에 관련된 환경 변수 제거
    env_vars = ["APP_NAME", "DEBUG", "API_PREFIX", "LOG_LEVEL"]
    original_values = {}
    
    # 기존 값 저장 및 제거
    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # 원래 값 복원
    for var, value in original_values.items():
        os.environ[var] = value

def test_settings_default_values(clear_env_vars):
    # 환경 변수 없이 기본값 테스트
    settings = Settings()
    
    # 기본값 검증
    assert settings.app_name == "FastAPI 템플릿"  # 기본값
    assert settings.debug is False  # 기본값
    assert settings.api_prefix == "/api"  # 기본값
    assert settings.log_level == "INFO"  # 기본값
```

### 설정 검증 테스트

```python
# tests/test_config/test_settings_validation.py
import os
import pytest
from app.common.config.settings import Settings, ValidationError

@pytest.fixture
def env_setup():
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

def test_database_url_validation(env_setup):
    # 올바른 DB URL 설정
    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/dbname"
    settings = Settings()
    assert settings.database_url == "postgresql://user:password@localhost:5432/dbname"
    
    # 잘못된 DB URL 설정
    os.environ["DATABASE_URL"] = "invalid-url"
    with pytest.raises(ValidationError):
        settings = Settings()

def test_required_settings(env_setup):
    # 필수 설정 제거
    if "SECRET_KEY" in os.environ:
        del os.environ["SECRET_KEY"]
    
    # 필수 설정이 없을 때 예외 발생 확인
    with pytest.raises(ValidationError) as exc:
        settings = Settings(validate_required=True)
    
    assert "SECRET_KEY is required" in str(exc.value)
```

### 설정 파일 로드 테스트

```python
# tests/test_config/test_config_file.py
import os
import tempfile
import pytest
from app.common.config.settings import load_config_from_file

def test_load_config_from_file():
    # 임시 설정 파일 생성
    config_content = """
    APP_NAME=파일 설정 테스트
    DEBUG=true
    API_PREFIX=/api/v3
    """
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(config_content)
        temp_name = temp.name
    
    try:
        # 설정 파일 로드
        config = load_config_from_file(temp_name)
        
        # 설정값 검증
        assert config["APP_NAME"] == "파일 설정 테스트"
        assert config["DEBUG"] == "true"
        assert config["API_PREFIX"] == "/api/v3"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)

def test_load_nonexistent_config_file():
    # 존재하지 않는 파일
    result = load_config_from_file("/path/to/nonexistent/file")
    assert result == {}  # 빈 딕셔너리 반환 확인
```

## 모킹 전략

Config 모듈 테스트 시 다음과 같은 접근법을 사용할 수 있습니다:

1. **환경 변수 모킹**: `os.environ`을 직접 수정하는 대신 패치하여 테스트
2. **파일 시스템 모킹**: 실제 파일 대신 `StringIO`나 임시 파일 사용
3. **설정 로더 모킹**: 설정을 로드하는 함수를 모의 함수로 대체

예시:

```python
# 환경 변수 모킹 예시
from unittest.mock import patch

def test_settings_with_mocked_env():
    mock_env = {
        "APP_NAME": "모킹 테스트",
        "DEBUG": "True"
    }
    
    with patch.dict('os.environ', mock_env):
        settings = Settings()
        assert settings.app_name == "모킹 테스트"
        assert settings.debug is True
```

## 테스트 커버리지 확인

Config 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.config tests/test_config/
```

## 모범 사례

1. 테스트 간 환경 변수 격리를 철저히 하여 다른 테스트에 영향을 주지 않도록 합니다.
2. 여러 환경(개발, 테스트, 프로덕션)에 대한 설정을 테스트합니다.
3. 기본값, 환경 변수 오버라이드, 설정 파일 로드 등 다양한 설정 로드 방식을 테스트합니다.
4. 잘못된 설정, 필수 설정 누락 등 오류 상황에 대한 처리를 테스트합니다.

## 주의사항

1. 실제 환경 변수를 변경하는 테스트는 다른 테스트나 시스템에 영향을 줄 수 있으므로 주의하세요.
2. 민감한 설정(비밀키, API 키 등)을 테스트할 때는 가짜 값을 사용하세요.
3. 테스트 환경과 실제 환경의 설정을 혼동하지 않도록 주의하세요.
4. 설정 파일 경로는 상대 경로가 아닌 절대 경로를 사용하거나 테스트 디렉토리 기준으로 지정하세요.
