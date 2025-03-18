# 테스트 가이드

이 문서는 FastAPI 템플릿의 테스트 방법과 테스트 코드 작성 가이드라인을 제공합니다.

## 목차

- [테스트 개요](#테스트-개요)
- [테스트 실행 방법](#테스트-실행-방법)
- [테스트 구조](#테스트-구조)
- [테스트 용이성 분석](#테스트-용이성-분석)
- [모듈별 테스트 가이드](#모듈별-테스트-가이드)
- [테스트 작성 모범 사례](#테스트-작성-모범-사례)

## 테스트 개요

이 프로젝트는 다음과 같은 테스트 유형을 지원합니다:

- **단위 테스트**: 개별 함수나 메서드의 기능 테스트
- **통합 테스트**: 여러 모듈 간의 상호작용 테스트
- **API 테스트**: HTTP 엔드포인트 테스트

테스트 프레임워크로는 `pytest`를 사용하며, 비동기 테스트를 위해 `pytest-asyncio`를 활용합니다.

## 테스트 실행 방법

### 모든 테스트 실행

```bash
cd fastapi_template
pytest
```

### 특정 테스트 파일 실행

```bash
pytest tests/test_common_modules.py
```

### 테스트 커버리지 측정

```bash
pytest --cov=app tests/
```

## 테스트 구조

```
fastapi_template/
├── tests/
│   ├── conftest.py          # 테스트 설정 및 공통 fixture
│   ├── test_main.py         # 메인 애플리케이션 테스트
│   ├── test_common_modules.py # 공통 모듈 테스트
│   ├── test_api/            # API 엔드포인트 테스트
│   ├── test_auth/           # 인증 모듈 테스트
│   ├── test_validators/     # 유효성 검증 모듈 테스트
│   └── test_db/             # 데이터베이스 모듈 테스트
```

## 테스트 용이성 분석

프로젝트의 각 모듈은 테스트 용이성에 차이가 있습니다. 다음은 테스트 용이성 순위와 그 이유입니다:

1. **Validators (가장 쉬움)**
   - 외부 의존성이 거의 없음
   - 순수 함수로 구현되어 있음
   - 입력과 출력이 명확하게 정의됨
   - 상태를 유지하지 않음

2. **Security**
   - 대부분 순수 함수이나 일부 외부 라이브러리에 의존
   - 암호화/복호화 기능은 결정적이며 테스트하기 쉬움
   - 키 생성 등 일부 기능은 랜덤성을 포함해 테스트가 복잡할 수 있음

3. **Schemas**
   - Pydantic 모델 기반으로 검증 로직이 명확함
   - 단순한 데이터 구조 검증은 쉽게 테스트 가능
   - 복잡한 유효성 검증 규칙이 있는 경우 테스트가 복잡할 수 있음

4. **Utils**
   - 기능에 따라 테스트 난이도가 다양함
   - 날짜, 문자열 처리 등 순수 함수는 테스트하기 쉬움
   - 파일 시스템, 네트워크 관련 기능은 모킹이 필요하여 더 복잡함

5. **Cache**
   - Redis 의존성으로 인해 통합 테스트가 필요함
   - 모킹을 통한 단위 테스트도 가능하나 설정이 복잡함
   - 비동기 코드로 인해 테스트 설정이 더 복잡함

6. **Database**
   - 실제 데이터베이스나 테스트용 인메모리 DB 설정 필요
   - 트랜잭션, 롤백 등 복잡한 동작 테스트가 필요함
   - 비동기 ORM 코드로 인해 테스트 복잡도가 높음

7. **API (가장 어려움)**
   - 전체 애플리케이션 스택을 테스트해야 함
   - 인증, 데이터베이스, 캐싱 등 여러 의존성이 결합됨
   - 실제 HTTP 요청/응답 사이클을 시뮬레이션해야 함
   - 다양한 요청 시나리오와 예외 상황 테스트 필요

테스트 구현시, 이 순서를 고려하여 쉬운 모듈부터 테스트를 작성하는 것이 권장됩니다.

## 모듈별 테스트 가이드

### 1. Validators 모듈 테스트

`validators` 모듈은 외부 의존성이 적고 순수 함수로 구성되어 테스트하기 가장 쉬운 모듈입니다.

```python
# tests/test_validators/test_string_validators.py
from app.common.validators.string_validators import validate_email

def test_validate_email():
    # 유효한 이메일 테스트
    assert validate_email("user@example.com") == True
    
    # 유효하지 않은 이메일 테스트
    assert validate_email("invalid_email") == False
    assert validate_email("user@example") == False
```

### 2. Security 모듈 테스트

암호화 기능 테스트:

```python
# tests/test_security/test_encryption.py
import pytest
from app.common.security.encryption import Encryption

def test_encryption():
    # 암호화 객체 생성
    encryption = Encryption()
    
    # 텍스트 암호화 및 복호화 테스트
    text = "민감한 정보"
    encrypted = encryption.encrypt(text)
    decrypted = encryption.decrypt(encrypted)
    
    assert text != encrypted
    assert text == decrypted
```

### 3. Schemas 모듈 테스트

스키마 검증 테스트:

```python
# tests/test_schemas/test_base_schema.py
import pytest
from pydantic import ValidationError
from app.common.schemas.base import BaseSchema

def test_base_schema():
    # 스키마 정의
    class TestSchema(BaseSchema):
        name: str
        age: int
    
    # 유효한 데이터 테스트
    data = TestSchema(name="홍길동", age=30)
    assert data.name == "홍길동"
    assert data.age == 30
    
    # 유효하지 않은 데이터 테스트
    with pytest.raises(ValidationError):
        TestSchema(name="홍길동", age="30")
```

### 4. Utils 모듈 테스트

유틸리티 함수 테스트:

```python
# tests/test_utils/test_date_utils.py
from datetime import datetime, timedelta
from app.common.utils.date import get_current_datetime, add_days

def test_date_utils():
    # 현재 날짜 테스트
    now = get_current_datetime()
    assert isinstance(now, datetime)
    
    # 날짜 추가 테스트
    future_date = add_days(now, 5)
    assert future_date - now == timedelta(days=5)
```

## 테스트 작성 모범 사례

1. **테스트 격리**: 각 테스트는 독립적으로 실행되어야 합니다.
2. **환경 변수 관리**: 테스트 환경에서 사용하는 환경 변수는 `conftest.py`에서 설정하세요.
3. **모킹 활용**: 외부 의존성이 있는 기능을 테스트할 때는 `unittest.mock` 또는 `pytest-mock`을 활용하세요.
4. **Fixture 활용**: 반복적으로 사용되는 설정이나 객체는 pytest fixture로 정의하세요.
5. **테스트 이름 지정**: 테스트 함수의 이름은 `test_기능명_상황`과 같이 명확하게 지정하세요.
6. **Parametrize 활용**: 유사한 테스트 케이스가 여러 개 있을 경우 `@pytest.mark.parametrize`를 활용하세요.

```python
# 파라미터화된 테스트 예시
@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("invalid_email", False),
    ("missing_domain@", False),
])
def test_validate_email_multiple_cases(email, expected):
    assert validate_email(email) == expected
```
