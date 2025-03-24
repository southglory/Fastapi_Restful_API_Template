# Config 모듈 테스트 가이드

[@config](/fastapi_template/app/common/config/)

## 개요

`config` 모듈은 애플리케이션의 설정 정보를 관리합니다. 주로 환경 변수와 설정 파일을 통해 애플리케이션의 동작을 설정하는 역할을 담당합니다. 이 모듈은 환경별(개발, 테스트, 프로덕션) 설정을 `Settings` 클래스 및 하위 클래스(`DevSettings`, `TestSettings`, `ProdSettings`)를 통해 통합 관리합니다.

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
   - 환경별 설정 클래스(`DevSettings`, `TestSettings`, `ProdSettings`) 전환

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

## 테스트 접근법

Config 모듈 테스트 시 다음 접근법을 권장합니다:

1. **환경 격리**: 테스트 실행 전후로 환경 변수를 백업하고 복원하여 다른 테스트에 영향을 주지 않도록 합니다.
2. **여러 환경 테스트**: 개발, 테스트, 프로덕션 등 다양한 환경 설정을 테스트합니다.
3. **오류 케이스 테스트**: 잘못된 설정, 누락된 필수 설정 등 오류 상황을 테스트합니다.
4. **캐싱 테스트**: `get_settings()` 함수의 캐싱 기능이 제대로 작동하는지 확인합니다.

## 구현된 테스트 코드

각 설정 유형별 테스트 코드:

- [설정 로드 테스트 코드](/fastapi_template/tests/test_config/test_settings.py)
- [기본값 테스트 코드](/fastapi_template/tests/test_config/test_settings_defaults.py)
- [설정 검증 테스트 코드](/fastapi_template/tests/test_config/test_settings_validation.py)
- [설정 파일 로드 테스트 코드](/fastapi_template/tests/test_config/test_config_file.py)
- [설정 로더 테스트 코드](/fastapi_template/tests/test_config/test_loader.py)
- [환경별 설정 테스트 코드](/fastapi_template/tests/test_config/test_environment_settings.py)

## 테스트 커버리지 확인

Config 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.config tests/test_config/ -v
```

## 모범 사례

1. 테스트 간 환경 변수 격리를 철저히 하여 다른 테스트에 영향을 주지 않도록 합니다.
2. 여러 환경(개발, 테스트, 프로덕션)에 대한 설정을 테스트합니다.
3. 기본값, 환경 변수 오버라이드, 설정 파일 로드 등 다양한 설정 로드 방식을 테스트합니다.
4. 잘못된 설정, 필수 설정 누락 등 오류 상황에 대한 처리를 테스트합니다.
5. `dotenv_values`와 `load_dotenv` 사용 시 차이점을 이해합니다:
   - `dotenv_values`: 환경 변수를 딕셔너리로 반환하여 격리된 설정 관리가 가능합니다. 테스트에 더 적합하며 다양한 설정 소스 병합에 용이합니다.
   - `load_dotenv`: 환경 변수를 `os.environ`에 직접 로드하여 프로세스 전체에 영향을 줍니다. 간편하지만 테스트 간 격리가 어려울 수 있습니다.
6. 설정 검증 전략을 이해합니다:
   - `field_validator`: 개별 필드 수준에서 유효성 검사를 수행합니다.
   - `model_validator`: 여러 필드 간의 관계나 전체 모델 수준에서 유효성 검사를 수행합니다.
7. `validators` 모듈과의 통합:
   - `validators` 모듈은 순수 Python 함수로 구현되어 있어 Pydantic에 의존하지 않는 유연한 검증 로직을 제공합니다.
   - Config 모듈과 validators 모듈을 효과적으로 통합하면 복잡한 설정 검증과 사용자 입력 검증을 일관된 방식으로 처리할 수 있습니다.
   - 통합 방법:
     - Settings 클래스의 validator 메서드 내에서 validators 모듈의 함수 호출
     - 설정 로드 후 추가 검증 단계에서 validators 모듈 활용
     - API 엔드포인트에서 설정값과 함께 validators를 사용하여 입력 검증
8. 환경별 설정 클래스를 이해합니다:
   - `DevSettings`: 개발 환경용 설정으로 디버깅 활성화, 문서화 기능 활성화 등 개발에 필요한 설정을 포함합니다.
   - `TestSettings`: 테스트 환경용 설정으로 테스트 데이터베이스, 테스트용 비밀키 등을 사용합니다.
   - `ProdSettings`: 프로덕션 환경용 설정으로 보안 강화, 디버깅 비활성화 등 실제 서비스에 필요한 설정을 포함합니다.
9. 설정 캐싱을 이해합니다:
   - `@lru_cache`를 사용하여 `get_settings()` 함수의 결과를 캐시합니다.
   - 환경 변수가 변경되지 않는 한 동일한 설정 객체를 반환하여 성능을 향상시킵니다.

## 주의사항

1. 실제 환경 변수를 변경하는 테스트는 다른 테스트나 시스템에 영향을 줄 수 있으므로 주의하세요.
2. 민감한 설정(비밀키, API 키 등)을 테스트할 때는 가짜 값을 사용하세요.
3. 테스트 환경과 실제 환경의 설정을 혼동하지 않도록 주의하세요.
4. 설정 파일 경로는 상대 경로가 아닌 절대 경로를 사용하거나 테스트 디렉토리 기준으로 지정하세요.
5. `load_dotenv`를 테스트에서 사용할 때는 `override=True` 옵션과 함께 `dotenv.reset_environment()`를 활용하여 테스트 후 환경을 원래대로 복원하세요.
6. 캐싱된 설정을 테스트할 때는 `get_settings.cache_clear()`를 사용하여 캐시를 초기화할 수 있습니다.
7. 환경별 설정 클래스를 테스트할 때는 적절한 환경 변수(`ENVIRONMENT`)를 설정하여 올바른 클래스가 선택되는지 확인하세요.
