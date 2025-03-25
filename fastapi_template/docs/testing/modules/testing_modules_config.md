# Config 모듈 테스트 가이드

[@config](/fastapi_template/app/common/config)

## 개요

`config` 모듈은 애플리케이션의 설정을 관리하는 모듈입니다. 환경 변수, 설정 파일, 기본값 등을 관리하며, 애플리케이션의 다양한 설정을 중앙화된 방식으로 제공합니다.

## 현재 모듈 구조

```
app/common/config/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── config_base.py              # 기본 설정 클래스
├── config_app.py               # 애플리케이션 설정
├── config_db.py                # 데이터베이스 설정
└── config_security.py          # 보안 설정
```

## 테스트 용이성

- **난이도**: 쉬움
- **이유**:
  - 순수 설정 클래스
  - 명확한 기본값
  - 외부 의존성 없음
  - 결정적 동작

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 설정** (`config_base.py`)
   - 기본 설정 클래스
   - 환경 변수 로드
   - 기본값 처리

2. **애플리케이션 설정** (`config_app.py`)
   - 앱 이름/버전
   - 디버그 모드
   - 로깅 설정

3. **데이터베이스 설정** (`config_db.py`)
   - DB URL
   - 연결 풀
   - 타임아웃

4. **보안 설정** (`config_security.py`)
   - JWT 설정
   - 암호화 키
   - CORS 설정

## 테스트 접근법

Config 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 설정 클래스 테스트
2. **환경 테스트**: 환경 변수 처리 테스트
3. **기본값 테스트**: 기본값 동작 테스트

## 구현된 테스트 코드

Config 모듈의 테스트 코드:

- [설정 테스트](/fastapi_template/tests/test_config/test_settings.py)
- [기본값 설정 테스트](/fastapi_template/tests/test_config/test_settings_defaults.py)
- [설정 파일 테스트](/fastapi_template/tests/test_config/test_config_file.py)
- [환경 설정 테스트](/fastapi_template/tests/test_config/test_environment_settings.py)
- [설정 검증 테스트](/fastapi_template/tests/test_config/test_settings_validation.py)
- [전체 커버리지 테스트](/fastapi_template/tests/test_config/test_full_coverage.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_config/
    ├── __init__.py
    ├── test_settings.py
    ├── test_settings_defaults.py
    ├── test_config_file.py
    ├── test_environment_settings.py
    ├── test_settings_validation.py
    └── test_full_coverage.py
```

## 테스트 커버리지 확인

Config 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.config tests/test_config/ -v
```

## 모범 사례

1. 모든 설정 값의 기본값을 테스트합니다.
2. 환경 변수 처리를 검증합니다.
3. 설정 유효성 검사를 테스트합니다.
4. 설정 변경 시 동작을 확인합니다.

## 주의사항

1. 실제 환경 변수를 테스트에 영향을 주지 않습니다.
2. 민감한 설정 값은 테스트용 더미 데이터를 사용합니다.
3. 설정 파일의 경로를 올바르게 처리합니다.
4. 설정 변경의 부작용을 고려합니다.
