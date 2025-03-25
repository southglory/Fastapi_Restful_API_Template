# Services 모듈 테스트 가이드

[@services](/fastapi_template/app/common/services)

## 개요

`services` 모듈은 애플리케이션의 비즈니스 로직을 구현하는 핵심 모듈입니다. 데이터베이스 작업, 외부 API 통신, 복잡한 비즈니스 규칙 등을 처리하며, 다른 모듈들이 이 서비스를 통해 기능을 구현합니다.

## 현재 모듈 구조

```
app/common/services/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── services_base.py            # 기본 서비스 클래스
├── services_user.py            # 사용자 관련 서비스
├── services_auth.py            # 인증 관련 서비스
├── services_email.py           # 이메일 관련 서비스
└── services_file.py            # 파일 관련 서비스
```

## 테스트 용이성

- **난이도**: 어려움
- **이유**:
  - 복잡한 비즈니스 로직 테스트 필요
  - 외부 서비스(DB, API, 이메일 등) 의존성
  - 비동기 작업 처리
  - 트랜잭션 관리
  - 에러 처리 및 복구

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 서비스** (`services_base.py`)
   - 서비스 초기화
   - 공통 메서드
   - 에러 처리

2. **사용자 서비스** (`services_user.py`)
   - 사용자 CRUD
   - 사용자 검색
   - 권한 관리

3. **인증 서비스** (`services_auth.py`)
   - 로그인/로그아웃
   - 토큰 관리
   - 권한 검증

4. **이메일 서비스** (`services_email.py`)
   - 이메일 발송
   - 템플릿 처리
   - 발송 상태 관리

5. **파일 서비스** (`services_file.py`)
   - 파일 업로드/다운로드
   - 파일 저장
   - 파일 검증

## 테스트 접근법

Services 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 서비스 메서드의 동작을 격리하여 테스트
2. **통합 테스트**: 여러 서비스 간의 상호작용을 테스트
3. **모킹**: 외부 의존성을 모킹하여 격리된 테스트 환경 구성

## 구현된 테스트 코드

각 서비스 유형별 테스트 코드:

### 기본 서비스 테스트

- [기본 서비스 테스트 코드](/fastapi_template/tests/test_services/test_services_base.py)

### 사용자 서비스 테스트

- [사용자 서비스 테스트 코드](/fastapi_template/tests/test_services/test_services_user.py)

### 인증 서비스 테스트

- [인증 서비스 테스트 코드](/fastapi_template/tests/test_services/test_services_auth.py)

### 이메일 서비스 테스트

- [이메일 서비스 테스트 코드](/fastapi_template/tests/test_services/test_services_email.py)

### 파일 서비스 테스트

- [파일 서비스 테스트 코드](/fastapi_template/tests/test_services/test_services_file.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_services/
    ├── __init__.py
    ├── test_services_base.py
    ├── test_services_user.py
    ├── test_services_auth.py
    ├── test_services_email.py
    └── test_services_file.py
```

## 테스트 커버리지 확인

Services 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.services tests/test_services/ -v
```

## 모범 사례

1. 모든 서비스 메서드에 대한 성공/실패 케이스를 테스트합니다.
2. 트랜잭션 롤백과 에러 복구를 검증합니다.
3. 외부 서비스 통신은 모킹하여 테스트합니다.
4. 비동기 메서드는 `pytest-asyncio`를 사용하여 테스트합니다.

## 주의사항

1. 실제 데이터베이스나 외부 서비스를 사용하지 않고 모킹을 활용합니다.
2. 트랜잭션 격리를 위해 각 테스트 후 롤백을 수행합니다.
3. 비동기 작업의 완료를 적절히 대기합니다.
4. 민감한 데이터는 테스트용 더미 데이터를 사용합니다.
