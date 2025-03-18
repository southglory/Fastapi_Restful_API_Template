# FastAPI 템플릿 공통 모듈 문서

이 문서는 FastAPI 템플릿의 `app/common` 디렉토리에 있는 공통 모듈들에 대한 개요와 상세 정보를 제공합니다.

## 목차

- [모듈 목록](#모듈-목록)
- [인증 모듈](#인증-모듈)
- [캐싱 모듈](#캐싱-모듈)
- [설정 모듈](#설정-모듈)
- [데이터베이스 모듈](#데이터베이스-모듈)
- [의존성 모듈](#의존성-모듈)
- [예외 처리 모듈](#예외-처리-모듈)
- [미들웨어 모듈](#미들웨어-모듈)
- [모니터링 모듈](#모니터링-모듈)
- [스키마 모듈](#스키마-모듈)
- [보안 모듈](#보안-모듈)
- [유틸리티 모듈](#유틸리티-모듈)
- [데이터 검증 모듈](#데이터-검증-모듈)
- [모듈 사용 가이드](#모듈-사용-가이드)
- [모듈 확장](#모듈-확장)

## 모듈 목록

| 모듈 | 경로 | 설명 | 주요 기능 |
|------|------|------|-----------|
| `auth` | `app/common/auth/` | 인증 관련 기능 | JWT 토큰 생성/검증, 비밀번호 해싱 |
| `cache` | `app/common/cache/` | 캐싱 기능 | Redis 기반 캐싱, 데코레이터 |
| `config` | `app/common/config/` | 설정 관리 | 환경 변수, 애플리케이션 설정 |
| `database` | `app/common/database/` | 데이터베이스 연결 | 세션 관리, 모델 기본 클래스 |
| `dependencies` | `app/common/dependencies/` | 의존성 주입 | 인증, 권한, 세션 의존성 함수 |
| `exceptions` | `app/common/exceptions/` | 예외 처리 | 사용자 정의 예외, 예외 핸들러 |
| `middleware` | `app/common/middleware/` | 미들웨어 | CORS, 로깅, 요청 ID |
| `monitoring` | `app/common/monitoring/` | 모니터링 | 상태 확인, 메트릭스 |
| `schemas` | `app/common/schemas/` | 공통 스키마 | 응답 모델, 기본 스키마 |
| `security` | `app/common/security/` | 보안 | 데이터 암호화, CSRF 보호 |
| `utils` | `app/common/utils/` | 유틸리티 | 날짜/시간, 문자열 처리 등 |
| `validators` | `app/common/validators/` | 유효성 검사 | 입력 데이터 검증 |

## 인증 모듈

**경로**: `app/common/auth/`

인증 관련 기능을 제공합니다:

- JWT 토큰 생성 및 검증
- 비밀번호 해싱 및 검증
- 인증 전략 구현

```python
from app.common.auth import create_access_token, verify_token
```

[인증 모듈 상세 문서](common_modules/common_auth.md)

## 캐싱 모듈

**경로**: `app/common/cache/`

캐싱 기능을 제공합니다:

- Redis 기반 캐싱
- 함수 결과 캐싱을 위한 데코레이터
- 캐시 무효화 유틸리티

```python
from app.common.cache import cached, invalidate_cache
```

[캐싱 모듈 상세 문서](common_modules/common_cache.md)

## 설정 모듈

**경로**: `app/common/config/`

애플리케이션 설정을 관리합니다:

- 환경 변수 로드 및 검증
- 환경별 설정 프로필
- 애플리케이션 상수

```python
from app.common.config import settings
```

[설정 모듈 상세 문서](common_modules/common_config.md)

## 데이터베이스 모듈

**경로**: `app/common/database/`

데이터베이스 연결을 관리합니다:

- 데이터베이스 세션 생성 및 관리
- 기본 모델 클래스 제공
- 마이그레이션 유틸리티

```python
from app.common.database import get_db, Base
```

[데이터베이스 상세 문서](common_modules/common_database.md)

## 의존성 모듈

**경로**: `app/common/dependencies/`

재사용 가능한 의존성 주입 함수를 제공합니다:

- 현재 사용자 인증 및 검증
- 권한 확인
- 데이터베이스 세션 의존성
- 기타 공통 의존성 함수

```python
from app.common.dependencies import get_current_user, get_current_active_user
```

[의존성 모듈 상세 문서](common_modules/common_dependencies.md)

## 예외 처리 모듈

**경로**: `app/common/exceptions/`

사용자 정의 예외 및 예외 처리기를 제공합니다:

- API 오류 클래스
- 예외 핸들러
- 에러 응답 형식화

```python
from app.common.exceptions import APIError, NotFoundException
```

[예외 처리 모듈 상세 문서](common_modules/common_exceptions.md)

## 미들웨어 모듈

**경로**: `app/common/middleware/`

FastAPI 미들웨어를 제공합니다:

- CORS 설정
- 요청/응답 로깅
- 요청 ID 생성
- 성능 모니터링

```python
from app.common.middleware import add_process_time_header
```

[미들웨어 모듈 상세 문서](common_modules/common_middleware.md)

## 모니터링 모듈

**경로**: `app/common/monitoring/`

애플리케이션 모니터링 도구를 제공합니다:

- 상태 확인 엔드포인트
- 메트릭스 수집
- 로깅 유틸리티

```python
from app.common.monitoring import check_service_health
```

[모니터링 모듈 상세 문서](common_modules/common_monitoring.md)

## 스키마 모듈

**경로**: `app/common/schemas/`

공통 Pydantic 스키마를 제공합니다:

- 기본 응답 모델
- 페이지네이션 스키마
- 에러 응답 스키마

```python
from app.common.schemas import ResponseSchema, PaginationParams
```

[스키마 모듈 상세 문서](common_modules/common_schemas.md)

## 보안 모듈

**경로**: `app/common/security/`

보안 관련 기능을 제공합니다:

- 데이터 암호화/복호화
- CSRF 토큰 생성 및 검증
- 보안 헤더 관리

```python
from app.common.security import encrypt_data, decrypt_data
```

[보안 모듈 상세 문서](common_modules/common_security.md)

## 유틸리티 모듈

**경로**: `app/common/utils/`

다양한 유틸리티 함수를 제공합니다:

- 날짜/시간 처리
- UUID 생성
- 문자열 변환

```python
from app.common.utils import generate_uuid, format_datetime
```

[유틸리티 모듈 상세 문서](common_modules/common_utils.md)

## 데이터 검증 모듈

**경로**: `app/common/validators/`

입력 데이터 유효성 검증 기능을 제공합니다:

- 이메일 검증
- 비밀번호 강도 검증
- 데이터 형식 검증

```python
from app.common.validators import validate_email, validate_password_strength
```

[데이터 검증 모듈 상세 문서](common_modules/common_validators.md)

## 모듈 사용 가이드

각 모듈은 독립적으로 사용할 수 있으며, 필요에 따라 임포트하여 사용할 수 있습니다.

```python
# 예시: 인증된 사용자가 필요한 엔드포인트
from fastapi import Depends
from app.common.dependencies import get_current_active_user

@app.get("/me")
async def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user
```

## 모듈 확장

새로운 공통 모듈을 추가하려면:

1. `app/common/` 디렉토리에 새 모듈 디렉토리 생성
2. `__init__.py`에 모듈 함수/클래스 정의
3. `app/common/__init__.py`에 새 모듈 추가
4. 문서화 (주석 및 README 업데이트)
