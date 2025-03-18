# 테스트 가이드

이 문서는 FastAPI 템플릿의 테스트 방법과 테스트 코드 작성 가이드라인을 제공합니다.

## 목차

### 기본 가이드

- [테스트 개요](testing/overview.md) - 프로젝트의 테스트 철학과 접근 방식
- [테스트 퀵 스타트](testing/quick_start.md) - 빠르게 테스트를 시작하는 방법
- [테스트 실행 방법](testing/running_tests.md) - 다양한 테스트 실행 명령어와 옵션
- [테스트 구조](testing/structure.md) - 테스트 코드의 디렉토리 구조와 조직 방법
- [테스트 도구 가이드](testing/tools.md) - 사용되는 테스트 도구와 라이브러리 소개
- [테스트 작성 모범 사례](testing/best_practices.md) - 효과적인 테스트 작성 방법
- [공통 테스트 패턴](testing/common_test_patterns.md) - 공통 테스트 패턴과 템플릿

### 모듈별 테스트 가이드

- [모듈별 테스트 가이드 개요](testing/module_guides.md) - 각 모듈의 테스트 방법에 대한 개요
- **모듈별 상세 가이드** - 각 모듈의 상세 테스트 방법은 `testing/modules/` 디렉토리 내 문서 참조

## 테스트 용이성 순위

아래는 모듈별 테스트 난이도를 쉬운 순서대로 정리한 것입니다. 테스트 코드 작성 시 이 순서를 따라 진행하는 것을 권장합니다.

| 순위 | 모듈 | 난이도 | 문서 링크 |
|-----|-----|-------|----------|
| 1 | Validators | 쉬움 | [가이드](testing/modules/validators.md) |
| 2 | Security | 쉬움-중간 | [가이드](testing/modules/security.md) |
| 3 | Config | 쉬움-중간 | [가이드](testing/modules/config.md) |
| 4 | Schemas | 쉬움-중간 | [가이드](testing/modules/schemas.md) |
| 5 | Utils | 중간 | [가이드](testing/modules/utils.md) |
| 6 | Exceptions | 중간 | [가이드](testing/modules/exceptions.md) |
| 7 | Repositories | 중간 | [가이드](testing/modules/repositories.md) |
| 8 | Services | 중간 | [가이드](testing/modules/services.md) |
| 9 | Middleware | 중간-어려움 | [가이드](testing/modules/middleware.md) |
| 10 | Dependency | 중간-어려움 | [가이드](testing/modules/dependency.md) |
| 11 | Auth | 중간-어려움 | [가이드](testing/modules/auth.md) |
| 12 | Cache | 어려움 | [가이드](testing/modules/cache.md) |
| 13 | Database | 어려움 | [가이드](testing/modules/database.md) |
| 14 | Monitoring | 어려움 | [가이드](testing/modules/monitoring.md) |
| 15 | API | 가장 어려움 | [가이드](testing/modules/api.md) |

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

더 자세한 내용은 [테스트 퀵 스타트](testing/quick_start.md) 문서를 참고하세요.
