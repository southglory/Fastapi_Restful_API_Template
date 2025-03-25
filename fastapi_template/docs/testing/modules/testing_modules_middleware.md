# Middleware 모듈 테스트 가이드

[@middleware](/fastapi_template/app/common/middleware)

## 개요

`middleware` 모듈은 FastAPI 애플리케이션의 미들웨어 기능을 구현하는 모듈입니다. 인증, CORS, 로깅, 보안 등의 미들웨어를 제공하며, 요청/응답 파이프라인을 처리합니다.

## 현재 모듈 구조

```
app/common/middleware/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── middleware_base.py          # 기본 미들웨어 클래스
├── middleware_auth.py          # 인증 미들웨어
├── middleware_cors.py          # CORS 미들웨어
├── middleware_logging.py       # 로깅 미들웨어
└── middleware_security.py      # 보안 미들웨어
```

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 요청/응답 파이프라인 처리
  - 비동기 미들웨어 실행
  - 미들웨어 체인 순서
  - 상태 관리

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 미들웨어** (`middleware_base.py`)
   - 미들웨어 초기화
   - 기본 동작
   - 공통 기능

2. **인증 미들웨어** (`middleware_auth.py`)
   - 토큰 검증
   - 권한 확인
   - 인증 실패 처리

3. **CORS 미들웨어** (`middleware_cors.py`)
   - CORS 설정
   - 프리플라이트 요청
   - 헤더 처리

4. **로깅 미들웨어** (`middleware_logging.py`)
   - 요청 로깅
   - 응답 로깅
   - 성능 측정

5. **보안 미들웨어** (`middleware_security.py`)
   - 보안 헤더
   - XSS 방지
   - CSRF 보호

## 테스트 접근법

Middleware 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 미들웨어 기능 테스트
2. **통합 테스트**: 미들웨어 체인 테스트
3. **엔드투엔드 테스트**: 전체 요청/응답 흐름 테스트

## 구현된 테스트 코드

각 미들웨어 유형별 테스트 코드:

### 기본 미들웨어 테스트

- [기본 미들웨어 테스트 코드](/fastapi_template/tests/test_middleware/test_middleware_base.py)

### 인증 미들웨어 테스트

- [인증 미들웨어 테스트 코드](/fastapi_template/tests/test_middleware/test_middleware_auth.py)

### CORS 미들웨어 테스트

- [CORS 미들웨어 테스트 코드](/fastapi_template/tests/test_middleware/test_middleware_cors.py)

### 로깅 미들웨어 테스트

- [로깅 미들웨어 테스트 코드](/fastapi_template/tests/test_middleware/test_middleware_logging.py)

### 보안 미들웨어 테스트

- [보안 미들웨어 테스트 코드](/fastapi_template/tests/test_middleware/test_middleware_security.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_middleware/
    ├── __init__.py
    ├── test_middleware_base.py
    ├── test_middleware_auth.py
    ├── test_middleware_cors.py
    ├── test_middleware_logging.py
    └── test_middleware_security.py
```

## 테스트 커버리지 확인

Middleware 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.middleware tests/test_middleware/ -v
```

## 모범 사례

1. 모든 미들웨어의 요청/응답 처리를 테스트합니다.
2. 미들웨어 체인의 순서를 검증합니다.
3. 에러 처리와 예외 상황을 테스트합니다.
4. 성능 영향을 모니터링합니다.

## 주의사항

1. 실제 외부 서비스에 영향을 주지 않도록 합니다.
2. 미들웨어 순서를 테스트 시 고려합니다.
3. 비동기 작업의 완료를 적절히 대기합니다.
4. 테스트 환경의 보안 설정을 조정합니다.
