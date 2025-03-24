# Config 모듈 테스트 가이드

[@config](/fastapi_template/app/common/config/)

## 개요

`config` 모듈은 애플리케이션의 설정 정보를 관리합니다. 주로 환경 변수와 설정 파일을 통해 애플리케이션의 동작을 설정하는 역할을 담당합니다. 이 모듈은 환경별(개발, 테스트, 프로덕션) 설정을 `Settings` 클래스 및 하위 클래스(`DevSettings`, `TstSettings`, `ProdSettings`)를 통해 통합 관리합니다.

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
   - 환경별 설정 클래스(`DevSettings`, `TstSettings`, `ProdSettings`) 전환

2. **설정 검증 기능**
   - 필수 설정값 존재 확인
   - 설정값 타입 검증
   - 설정값 범위 검증
   - 필드별 유효성 검사(`field_validator`)
   - 모델 수준의 유효성 검사(`model_validator`)
   - 환경별 특수 유효성 검사

3. **설정 변환 기능**
   - 문자열에서 적절한 타입으로 변환
   - 경로, URL 등 특수 형식 처리
   - 설정 캐싱(`@lru_cache`) 기능

4. **환경 분류 기능**
   - `EnvironmentType` 열거형을 통한 환경 분류
   - 환경별 설정 클래스 자동 선택

5. **유틸리티 메서드**
   - 데이터베이스 설정 반환(`get_db_settings`)
   - Redis 설정 반환(`get_redis_settings`)
   - 설정 딕셔너리 변환(`dict_config`)

## 테스트 접근법

Config 모듈 테스트 시 다음 접근법을 권장합니다:

1. **환경 격리**: 테스트 실행 전후로 환경 변수를 백업하고 복원하여 다른 테스트에 영향을 주지 않도록 합니다.
2. **여러 환경 테스트**: 개발, 테스트, 프로덕션 등 다양한 환경 설정을 테스트합니다.
3. **오류 케이스 테스트**: 잘못된 설정, 누락된 필수 설정 등 오류 상황을 테스트합니다.
4. **캐싱 테스트**: `get_settings()` 함수의 캐싱 기능이 제대로 작동하는지 확인합니다.
5. **모킹 활용**: 환경 변수, 파일 시스템, 외부 라이브러리 등을 모킹하여 다양한 상황을 테스트합니다.
6. **100% 커버리지 목표**: 모든 코드 경로를 실행하는 테스트를 작성하여 완전한 테스트 커버리지를 달성합니다.

## 구현된 테스트 코드

각 설정 유형별 테스트 코드:

- [설정 로드 테스트 코드](/fastapi_template/tests/test_config/test_settings.py)
- [기본값 테스트 코드](/fastapi_template/tests/test_config/test_settings_defaults.py)
- [설정 검증 테스트 코드](/fastapi_template/tests/test_config/test_settings_validation.py)
- [설정 파일 로드 테스트 코드](/fastapi_template/tests/test_config/test_config_file.py)
- [환경별 설정 테스트 코드](/fastapi_template/tests/test_config/test_environment_settings.py)
- [완전 커버리지 테스트 코드](/fastapi_template/tests/test_config/test_full_coverage.py)

## 테스트 커버리지 확인

Config 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.config tests/test_config/ -v
```

현재 Config 모듈은 100% 테스트 커버리지를 달성했습니다:

```
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
app\common\config\__init__.py       2      0   100%
app\common\config\settings.py     117      0   100%
-------------------------------------------------------------
TOTAL                             119      0   100%
```

## 모범 사례

1. 테스트 간 환경 변수 격리를 철저히 하여 다른 테스트에 영향을 주지 않도록 합니다.

   ```python
   @pytest.fixture
   def env_setup():
       # 기존 환경 변수 백업
       original_env = os.environ.copy()
       
       # 테스트 실행
       yield
       
       # 원래 환경 변수로 복원
       os.environ.clear()
       os.environ.update(original_env)
   ```

2. 여러 환경(개발, 테스트, 프로덕션)에 대한 설정을 테스트합니다.

   ```python
   def test_get_settings_testing_environment():
       get_settings.cache_clear()
       with mock.patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
           settings = get_settings()
           assert settings.ENVIRONMENT == EnvironmentType.TESTING
           assert isinstance(settings, TstSettings)
   ```

3. 로깅 모킹을 통해 로그 관련 코드도 테스트합니다.

   ```python
   with mock.patch('logging.debug') as mock_debug:
       db_settings = settings.get_db_settings()
       assert mock_debug.called
   ```

4. 설정 검증 전략을 이해합니다:
   - `field_validator`: 개별 필드 수준에서 유효성 검사를 수행합니다.
   - `model_validator`: 여러 필드 간의 관계나 전체 모델 수준에서 유효성 검사를 수행합니다.

5. 환경별 설정 클래스를 이해합니다:
   - `DevSettings`: 개발 환경용 설정으로 디버깅 활성화, 문서화 기능 활성화 등 개발에 필요한 설정을 포함합니다.
   - `TstSettings`: 테스트 환경용 설정으로 테스트 데이터베이스, 테스트용 비밀키 등을 사용합니다.
   - `ProdSettings`: 프로덕션 환경용 설정으로 보안 강화, 디버깅 비활성화 등 실제 서비스에 필요한 설정을 포함합니다.

6. 메서드 동적 모킹을 통해 테스트하기 어려운 클래스 메서드도 테스트합니다.

   ```python
   def settings_utility_methods():
       settings = DevSettings()
       with mock.patch('logging.debug') as mock_debug:
           db_settings = settings.get_db_settings()
           assert db_settings["url"] == "postgresql://user:pass@localhost/db"
           assert mock_debug.called
   ```

7. 설정 캐싱을 이해합니다:
   - `@lru_cache`를 사용하여 `get_settings()` 함수의 결과를 캐시합니다.
   - 환경 변수가 변경되지 않는 한 동일한 설정 객체를 반환하여 성능을 향상시킵니다.
   - 테스트 간에는 `get_settings.cache_clear()`를 호출하여 캐시를 초기화합니다.

## 주의사항

1. 실제 환경 변수를 변경하는 테스트는 다른 테스트나 시스템에 영향을 줄 수 있으므로 `mock.patch.dict(os.environ, {...})`를 사용하세요.
2. 민감한 설정(비밀키, API 키 등)을 테스트할 때는 가짜 값을 사용하세요.
3. 테스트 환경과 실제 환경의 설정을 혼동하지 않도록 주의하세요.
4. 설정 파일 경로는 상대 경로가 아닌 절대 경로를 사용하거나 테스트 디렉토리 기준으로 지정하세요.
5. `load_dotenv`를 테스트에서 사용할 때는 `override=True` 옵션과 함께 `dotenv.reset_environment()`를 활용하여 테스트 후 환경을 원래대로 복원하세요.
6. `dotenv` 모듈 임포트 실패와 같은 예외 상황도 테스트하세요.

   ```python
   def test_dotenv_import_error():
       with mock.patch('builtins.__import__', side_effect=mock_import):
           with mock.patch('os.path.exists', return_value=True):
               result = load_config_from_file(".env.test")
               assert result == {}
   ```

7. 프로덕션 환경 설정 객체를 생성할 때는 필수 매개변수를 제공하세요.

   ```python
   settings_prod = ProdSettings(
       SECRET_KEY="테스트용_프로덕션_시크릿키",
       DATABASE_URL="postgresql://user:pass@localhost/db",
       CORS_ORIGINS="https://example.com"
   )
   ```

8. 테스트 클래스 이름이 `Test`로 시작하면 pytest가 이를 테스트 클래스로 인식할 수 있으므로, 테스트가 아닌 설정 클래스는 이름을 적절히 지정하세요(예: `TstSettings` 대신 `TestSettings` 사용 금지).
