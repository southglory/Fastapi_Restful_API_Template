# Security 모듈 테스트 가이드

[@security](/fastapi_template/app/common/security)

## 개요

`security` 모듈은 애플리케이션의 보안 관련 기능을 구현하는 모듈입니다. JWT 토큰 생성/검증, 비밀번호 해싱, 암호화, 보안 헤더 설정 등을 담당하며, 애플리케이션의 전반적인 보안을 담당합니다.

## 현재 모듈 구조

```
app/common/security/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── security_base.py            # 기본 보안 클래스
├── security_jwt.py             # JWT 토큰 처리
├── security_password.py        # 비밀번호 해싱
└── security_headers.py         # 보안 헤더 설정
```

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 암호화/복호화 로직
  - JWT 토큰 처리
  - 비밀번호 해싱
  - 보안 헤더 설정

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 보안** (`security_base.py`)
   - 보안 설정
   - 암호화 키 관리
   - 기본 보안 기능

2. **JWT 보안** (`security_jwt.py`)
   - 토큰 생성
   - 토큰 검증
   - 토큰 갱신

3. **비밀번호 보안** (`security_password.py`)
   - 비밀번호 해싱
   - 비밀번호 검증
   - 솔트 생성

4. **헤더 보안** (`security_headers.py`)
   - CORS 설정
   - CSP 설정
   - HSTS 설정

## 테스트 접근법

Security 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 보안 함수 테스트
2. **통합 테스트**: 전체 보안 흐름 테스트
3. **보안 테스트**: 취약점 및 보안 위험 테스트

## 구현된 테스트 코드

Security 모듈의 테스트 코드:

- [토큰 보안 테스트](/fastapi_template/tests/test_security/test_security_token.py)
- [해싱 테스트](/fastapi_template/tests/test_security/test_security_hashing.py)
- [암호화 테스트](/fastapi_template/tests/test_security/test_security_encryption.py)
- [파일 암호화 테스트](/fastapi_template/tests/test_security/test_security_file_encryption.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_security/
    ├── __init__.py
    ├── test_security_token.py
    ├── test_security_hashing.py
    ├── test_security_encryption.py
    └── test_security_file_encryption.py
```

## 테스트 커버리지 확인

Security 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.security tests/test_security/ -v
```

## 모범 사례

1. 모든 보안 함수의 성공/실패 케이스를 테스트합니다.
2. 암호화/복호화 결과의 정확성을 검증합니다.
3. JWT 토큰의 유효성과 만료를 테스트합니다.
4. 비밀번호 해싱의 안전성을 확인합니다.

## 주의사항

1. 테스트 환경에서 실제 암호화 키를 사용하지 않습니다.
2. 민감한 데이터를 안전하게 처리합니다.
3. 보안 설정의 기본값을 검증합니다.
4. 취약점 테스트 시 주의를 기울입니다.
