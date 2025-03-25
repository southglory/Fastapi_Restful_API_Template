# Dependency 모듈 테스트 가이드

[@dependency](/fastapi_template/app/common/dependency)

## 개요

`dependency` 모듈은 FastAPI의 의존성 주입 시스템을 활용하여 애플리케이션의 의존성을 관리합니다. 데이터베이스 세션, 인증, 권한 검사 등의 공통 의존성을 제공합니다.

## 현재 모듈 구조

```
app/common/dependency/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── dependency_auth.py          # 인증 관련 의존성
├── dependency_db.py            # 데이터베이스 관련 의존성
├── dependency_cache.py         # 캐시 관련 의존성
└── dependency_common.py        # 공통 의존성
```

## 테스트 용이성

- **난이도**: 중간-어려움
- **이유**:
  - FastAPI 의존성 주입 시스템과의 통합 테스트 필요
  - 다양한 의존성 조합 테스트 필요
  - 비동기 의존성 처리 테스트 필요
  - 의존성 캐싱 동작 테스트 필요

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **인증 의존성** (`dependency_auth.py`)
   - 현재 사용자 가져오기
   - 권한 검사
   - 토큰 검증

2. **데이터베이스 의존성** (`dependency_db.py`)
   - 데이터베이스 세션 관리
   - 트랜잭션 관리
   - 세션 스코프 관리

3. **캐시 의존성** (`dependency_cache.py`)
   - 캐시 연결 관리
   - 캐시 키 관리
   - 캐시 스코프 관리

4. **공통 의존성** (`dependency_common.py`)
   - 공통 설정 의존성
   - 로깅 의존성
   - 유틸리티 의존성

## 테스트 접근법

Dependency 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **FastAPI 테스트 클라이언트 활용**: 실제 의존성 주입 흐름 테스트
2. **의존성 모킹**: 외부 의존성을 모킹하여 격리된 테스트
3. **의존성 조합 테스트**: 여러 의존성이 함께 사용되는 경우 테스트

## 구현된 테스트 코드

각 의존성 유형별 테스트 코드:

### 인증 의존성 테스트

- [인증 의존성 테스트 코드](/fastapi_template/tests/test_dependency/test_dependency_auth.py)

### 데이터베이스 의존성 테스트

- [데이터베이스 의존성 테스트 코드](/fastapi_template/tests/test_dependency/test_dependency_db.py)

### 캐시 의존성 테스트

- [캐시 의존성 테스트 코드](/fastapi_template/tests/test_dependency/test_dependency_cache.py)

### 공통 의존성 테스트

- [공통 의존성 테스트 코드](/fastapi_template/tests/test_dependency/test_dependency_common.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_dependency/
    ├── __init__.py
    ├── test_dependency_auth.py
    ├── test_dependency_db.py
    ├── test_dependency_cache.py
    └── test_dependency_common.py
```

## 테스트 커버리지 확인

Dependency 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.dependency tests/test_dependency/ -v
```

## 모범 사례

1. 모든 의존성 함수에 대한 기본 동작을 테스트합니다.
2. 의존성 캐싱이 제대로 작동하는지 검증합니다.
3. 의존성 조합이 올바르게 동작하는지 테스트합니다.
4. 예외 상황에서의 의존성 동작을 검증합니다.

## 주의사항

1. FastAPI 테스트 클라이언트를 사용할 때는 적절한 테스트 데이터베이스를 사용합니다.
2. 의존성 캐싱이 테스트 간에 영향을 주지 않도록 주의합니다.
3. 비동기 의존성은 `pytest-asyncio`를 사용하여 테스트합니다.
4. 의존성 주입 실패 시의 동작을 반드시 테스트합니다.
