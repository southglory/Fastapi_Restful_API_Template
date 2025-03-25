# API 모듈 테스트 가이드

[@api](/fastapi_template/app/api)

## 개요

`api` 모듈은 FastAPI 애플리케이션의 API 엔드포인트를 구현하는 모듈입니다. RESTful API 엔드포인트, 요청/응답 처리, 라우팅, 의존성 주입 등을 담당하며, 클라이언트와의 통신을 처리합니다.

## 현재 모듈 구조

```
app/api/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── api_base.py                 # 기본 API 클래스
├── api_v1/                     # API v1 버전
│   ├── __init__.py
│   ├── endpoints/              # API 엔드포인트
│   │   ├── auth.py            # 인증 관련 엔드포인트
│   │   ├── users.py           # 사용자 관련 엔드포인트
│   │   └── items.py           # 아이템 관련 엔드포인트
│   └── router.py              # API 라우터
└── deps.py                     # API 의존성
```

## 테스트 용이성

- **난이도**: 중간-어려움
- **이유**:
  - 다양한 엔드포인트와 라우팅
  - 복잡한 요청/응답 처리
  - 의존성 주입 시스템
  - 인증/인가 처리

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 API** (`api_base.py`)
   - API 초기화
   - 라우터 설정
   - 미들웨어 구성

2. **인증 엔드포인트** (`api_v1/endpoints/auth.py`)
   - 로그인/로그아웃
   - 토큰 갱신
   - 비밀번호 재설정

3. **사용자 엔드포인트** (`api_v1/endpoints/users.py`)
   - 사용자 CRUD
   - 프로필 관리
   - 권한 관리

4. **아이템 엔드포인트** (`api_v1/endpoints/items.py`)
   - 아이템 CRUD
   - 검색/필터링
   - 페이지네이션

## 테스트 접근법

API 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 엔드포인트 함수 테스트
2. **통합 테스트**: FastAPI 애플리케이션과의 통합 테스트
3. **엔드투엔드 테스트**: 실제 HTTP 요청을 통한 테스트

## 구현된 테스트 코드

각 API 유형별 테스트 코드:

### 기본 API 테스트

- [기본 API 테스트 코드](/fastapi_template/tests/test_api/test_api_base.py)

### 인증 엔드포인트 테스트

- [인증 엔드포인트 테스트 코드](/fastapi_template/tests/test_api/test_api_auth.py)

### 사용자 엔드포인트 테스트

- [사용자 엔드포인트 테스트 코드](/fastapi_template/tests/test_api/test_api_users.py)

### 아이템 엔드포인트 테스트

- [아이템 엔드포인트 테스트 코드](/fastapi_template/tests/test_api/test_api_items.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_api/
    ├── __init__.py
    ├── test_api_base.py
    ├── test_api_auth.py
    ├── test_api_users.py
    └── test_api_items.py
```

## 테스트 커버리지 확인

API 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.api tests/test_api/ -v
```

## 모범 사례

1. 모든 엔드포인트의 성공/실패 케이스를 테스트합니다.
2. 요청/응답 데이터의 유효성을 검증합니다.
3. 인증/인가 처리를 철저히 테스트합니다.
4. API 버전 호환성을 확인합니다.

## 주의사항

1. 테스트 환경에서 실제 데이터베이스에 영향을 주지 않습니다.
2. 인증 토큰과 민감한 데이터를 안전하게 처리합니다.
3. 비동기 작업의 완료를 적절히 대기합니다.
4. API 버전 변경 시 이전 버전과의 호환성을 유지합니다.
