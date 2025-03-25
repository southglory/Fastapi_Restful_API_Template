# 테스트 가이드

이 문서는 FastAPI 템플릿의 테스트 방법과 테스트 코드 작성 가이드라인을 제공합니다.

## 목차

### 기본 가이드

- [테스트 개요 및 구조](testing/01-test_overview.md) - 프로젝트의 테스트 철학과 접근 방식
- [테스트 시작 및 실행 가이드](testing/02-test_guide.md) - 테스트 시작 방법과 다양한 실행 옵션
- [테스트 모범 사례 및 패턴](testing/03-test_practices.md) - 효과적인 테스트 작성 방법과 공통 패턴
- [모듈별 테스트 가이드](testing/04-test_modules.md) - 각 모듈의 테스트 방법에 대한 개요
- [테스트 도구 가이드](testing/05-test_tools.md) - 사용되는 테스트 도구와 라이브러리 소개

### 모듈별 테스트 가이드

- [모듈별 테스트 가이드 개요](testing/04-test_modules.md) - 각 모듈의 테스트 방법에 대한 개요
- **모듈별 상세 가이드** - 각 모듈의 상세 테스트 방법은 `testing/modules/` 디렉토리 내 문서 참조

## 테스트 용이성 순위

아래는 모듈별 테스트 난이도를 쉬운 순서대로 정리한 것입니다. 테스트 코드 작성 시 이 순서를 따라 진행하는 것을 권장합니다.

| 순위 | 모듈 | 난이도 | 문서 링크 |
|-----|-----|-------|----------|
| 1 | Validators | 쉬움 | [가이드](testing/modules/testing_modules_validators.md) |
| 2 | Security | 쉬움-중간 | [가이드](testing/modules/testing_modules_security.md) |
| 3 | Config | 쉬움-중간 | [가이드](testing/modules/testing_modules_config.md) |
| 4 | Schemas | 쉬움-중간 | [가이드](testing/modules/testing_modules_schemas.md) |
| 5 | Utils | 중간 | [가이드](testing/modules/testing_modules_utils.md) |
| 6 | Exceptions | 중간 | [가이드](testing/modules/testing_modules_exceptions.md) |
| 7 | Repositories | 중간 | [가이드](testing/modules/testing_modules_repositories.md) |
| 8 | Services | 중간 | [가이드](testing/modules/testing_modules_services.md) |
| 9 | Middleware | 중간-어려움 | [가이드](testing/modules/testing_modules_middleware.md) |
| 10 | Dependency | 중간-어려움 | [가이드](testing/modules/testing_modules_dependency.md) |
| 11 | Auth | 중간-어려움 | [가이드](testing/modules/testing_modules_auth.md) |
| 12 | Cache | 어려움 | [가이드](testing/modules/testing_modules_cache.md) |
| 13 | Database | 어려움 | [가이드](testing/modules/testing_modules_database.md) |
| 14 | Monitoring | 어려움 | [가이드](testing/modules/testing_modules_monitoring.md) |
| 15 | API | 가장 어려움 | [가이드](testing/modules/testing_modules_api.md) |

## 모듈 의존성 순위

아래는 모듈 간 의존성을 고려한 구현 순서입니다. 가장 독립적인 모듈부터 시작하여 점차 다른 모듈에 의존하는 구성 요소로 진행하는 것이 효율적입니다.

| 순위 | 모듈 | 의존성 수준 | 이유 |
|-----|-----|-----------|------|
| 1 | Validators | 매우 낮음 | 순수 함수로 구성되어 외부 의존성이 거의 없음 |
| 2 | Utils | 매우 낮음 | 기본 유틸리티 함수로 독립적으로 작동 |
| 3 | Config | 낮음 | 환경 설정 관리, 외부 의존성이 적음 |
| 4 | Schemas | 낮음 | 데이터 모델 정의, 일부 validators에 의존 |
| 5 | Exceptions | 낮음 | 예외 정의 및 처리, 기본 구성 요소에 의존 |
| 6 | Security | 중간 | 기본 보안 기능, config와 일부 utils에 의존 |
| 7 | Database | 중간 | 데이터베이스 연결 및 모델, config에 의존 |
| 8 | Cache | 중간 | 캐싱 시스템, config와 utils에 의존 |
| 9 | Repositories | 중간-높음 | 데이터 액세스 계층, database와 schemas에 의존 |
| 10 | Services | 높음 | 비즈니스 로직, repositories와 여러 모듈에 의존 |
| 11 | Auth | 높음 | 인증 및 권한 관리, security, database, config 등에 의존 |
| 12 | Middleware | 높음 | 요청/응답 처리, 여러 모듈에 걸쳐 의존성 있음 |
| 13 | Dependency | 높음 | 종속성 주입 시스템, 거의 모든 모듈에 의존 |
| 14 | Monitoring | 높음 | 시스템 모니터링, 다양한 모듈에 통합 필요 |
| 15 | API | 매우 높음 | 최종 엔드포인트, 모든 모듈 통합 필요 |

## 빠른 시작

테스트를 처음 작성할 때 참고할 수 있는 간단한 예시입니다:

```python
# tests/test_validators/test_string_validators.py
import pytest
from app.common.validators.string_validators import validate_email

# 기본 단위 테스트
def test_validate_email():
    # 유효한 이메일 테스트
    assert validate_email("user@example.com") == True
    
    # 유효하지 않은 이메일 테스트
    assert validate_email("invalid_email") == False
    assert validate_email("user@example") == False

# 파라미터화된 테스트
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("user.name@company.co.kr", True),
    ("user+tag@example.com", True),
    ("invalid_email", False),
    ("user@", False),
    ("@domain.com", False),
    ("user@domain", False)
])
def test_validate_email_parametrized(email, expected):
    assert validate_email(email) == expected
```

더 자세한 내용은 [테스트 시작 및 실행 가이드](testing/02-test_guide.md) 문서를 참고하세요.
