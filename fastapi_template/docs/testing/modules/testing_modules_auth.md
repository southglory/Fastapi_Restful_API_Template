# Auth 모듈 테스트 가이드

[@auth](/fastapi_template/app/common/auth)

## 개요

`auth` 모듈은 애플리케이션의 인증 및 권한 관리 기능을 구현하는 모듈입니다. JWT 토큰 기반 인증, OAuth2, 권한 관리 등을 제공하며, 사용자 인증과 접근 제어를 담당합니다.

## 현재 모듈 구조

```
app/common/auth/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── auth_base.py                # 기본 인증 클래스
├── auth_jwt.py                 # JWT 인증
├── auth_oauth.py               # OAuth2 인증
└── auth_permissions.py         # 권한 관리
```

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 보안 관련 기능
  - 토큰 관리
  - 권한 검증
  - 외부 서비스 통합

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 인증** (`auth_base.py`)
   - 인증 초기화
   - 기본 동작
   - 공통 기능

2. **JWT 인증** (`auth_jwt.py`)
   - 토큰 생성
   - 토큰 검증
   - 토큰 갱신

3. **OAuth2 인증** (`auth_oauth.py`)
   - OAuth2 흐름
   - 토큰 교환
   - 사용자 정보

4. **권한 관리** (`auth_permissions.py`)
   - 권한 정의
   - 권한 검사
   - 역할 관리

## 테스트 접근법

Auth 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 인증 기능 테스트
2. **통합 테스트**: 인증 흐름 테스트
3. **보안 테스트**: 보안 취약점 테스트

## 구현된 테스트 코드

각 인증 유형별 테스트 코드:

### 기본 인증 테스트

- [기본 인증 테스트 코드](/fastapi_template/tests/test_auth/test_auth_base.py)

### JWT 인증 테스트

- [JWT 인증 테스트 코드](/fastapi_template/tests/test_auth/test_auth_jwt.py)

### OAuth2 인증 테스트

- [OAuth2 인증 테스트 코드](/fastapi_template/tests/test_auth/test_auth_oauth.py)

### 권한 관리 테스트

- [권한 관리 테스트 코드](/fastapi_template/tests/test_auth/test_auth_permissions.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_auth/
    ├── __init__.py
    ├── test_auth_base.py
    ├── test_auth_jwt.py
    ├── test_auth_oauth.py
    └── test_auth_permissions.py
```

## 테스트 커버리지 확인

Auth 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.auth tests/test_auth/ -v
```

## 모범 사례

1. 모든 인증 방식의 성공/실패를 테스트합니다.
2. 토큰의 유효성과 만료를 검증합니다.
3. 권한 검사의 정확성을 확인합니다.
4. 보안 취약점을 테스트합니다.

## 주의사항

1. 실제 인증 서버에 영향을 주지 않도록 합니다.
2. 테스트용 토큰과 키를 사용합니다.
3. 비동기 작업의 완료를 적절히 대기합니다.
4. 보안 관련 설정을 테스트 환경에 맞게 조정합니다.
