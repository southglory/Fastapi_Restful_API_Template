# Validators 모듈 테스트 가이드

## 개요

`validators` 모듈은 다양한 입력값의 유효성을 검증하는 순수 함수들로 구성되어 있습니다. 외부 의존성이 거의 없고 입출력이 명확하여 테스트하기 가장 쉬운 모듈입니다.

## 테스트 용이성

- **난이도**: 쉬움
- **이유**:
  - 외부 의존성이 거의 없음
  - 순수 함수로 구현되어 있음
  - 입력과 출력이 명확하게 정의됨
  - 상태를 유지하지 않음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **문자열 검증 함수**
   - 이메일 검증
   - URL 검증
   - 문자열 형식 검증

2. **데이터 검증 함수**
   - 숫자 범위 검증
   - 날짜 형식 검증
   - 열거형 값 검증

3. **파일 검증 함수**
   - 파일 형식 검증
   - 파일 크기 검증
   - 파일 내용 검증

## 테스트 접근법

Validators 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **입출력 테스트**: 다양한 입력값에 대한 출력 결과를 검증합니다.
2. **경계값 분석**: 유효/무효의 경계에 있는 값들을 중점적으로 테스트합니다.
3. **파라미터화된 테스트**: 여러 테스트 케이스를 효율적으로 작성합니다.

## 테스트 예시

### 기본 단위 테스트

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

### 파라미터화된 테스트

```python
# tests/test_validators/test_string_validators.py
import pytest
from app.common.validators.string_validators import validate_email

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("user.name@example.co.kr", True),
    ("user+tag@example.com", True),
    ("invalid_email", False),
    ("missing_domain@", False),
    ("@missing_username.com", False),
    ("no_at_sign.com", False),
    ("double@@at.com", False),
])
def test_validate_email_multiple_cases(email, expected):
    assert validate_email(email) == expected
```

### 데이터 검증 테스트

```python
# tests/test_validators/test_data_validators.py
import pytest
from app.common.validators.data_validators import validate_age, validate_date

def test_validate_age():
    assert validate_age(18) == True
    assert validate_age(65) == True
    assert validate_age(17) == False
    assert validate_age(120) == False

@pytest.mark.parametrize("date_str,format_str,expected", [
    ("2023-01-01", "%Y-%m-%d", True),
    ("01/01/2023", "%m/%d/%Y", True),
    ("2023.01.01", "%Y.%m.%d", True),
    ("invalid-date", "%Y-%m-%d", False),
    ("2023-13-01", "%Y-%m-%d", False),
    ("2023-01-32", "%Y-%m-%d", False),
])
def test_validate_date(date_str, format_str, expected):
    assert validate_date(date_str, format_str) == expected
```

### 파일 검증 테스트

```python
# tests/test_validators/test_file_validators.py
import pytest
import tempfile
import os
from app.common.validators.file_validators import validate_file_extension

def test_validate_file_extension():
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        # 유효한 확장자 테스트
        assert validate_file_extension(temp_file.name, [".txt", ".pdf"]) == True
        
        # 유효하지 않은 확장자 테스트
        assert validate_file_extension(temp_file.name, [".pdf", ".docx"]) == False
```

## 테스트 커버리지 확인

Validators 모듈은 100%에 가까운 테스트 커버리지를 목표로 해야 합니다:

```bash
pytest --cov=app.common.validators tests/test_validators/
```

## 모범 사례

1. 모든 함수에 대해 최소한 성공 케이스와 실패 케이스를 테스트해야 합니다.
2. 경계값 테스트를 포함하여 예상치 못한 입력에 대한 처리를 검증합니다.
3. 파라미터화된 테스트를 활용하여 코드 중복을 줄입니다.
4. 테스트 함수 이름은 테스트 대상과 시나리오를 명확히 설명해야 합니다.

## 주의사항

1. 외부 리소스에 의존하는 검증 함수는 모킹을 사용하여 테스트합니다.
2. 시간이나 랜덤 값에 의존하는 검증 함수는 고정된 값으로 대체하여 테스트합니다.
3. 복잡한 정규식 패턴은 다양한 케이스로 철저히 테스트해야 합니다.
