import pytest
from datetime import datetime, timedelta
from app.common.validators.data_validators import (
    validate_numeric_range,
    validate_age,
    validate_date,
    validate_future_date,
    validate_enum_value,
    validate_required_fields,
    validate_string_length,
    sanitize_input,
)


def test_validate_numeric_range():
    # 범위 내 값 테스트
    assert validate_numeric_range(5, 0, 10) == True

    # 경계값 테스트
    assert validate_numeric_range(0, 0, 10) == True  # 최소값
    assert validate_numeric_range(10, 0, 10) == True  # 최대값

    # 범위 밖 값 테스트
    assert validate_numeric_range(-1, 0, 10) == False  # 최소값 미만
    assert validate_numeric_range(11, 0, 10) == False  # 최대값 초과

    # 제한 없는 경우 테스트
    assert validate_numeric_range(5, None, 10) == True  # 최소값 없음
    assert validate_numeric_range(5, 0, None) == True  # 최대값 없음
    assert validate_numeric_range(5, None, None) == True  # 제한 없음


def test_validate_age():
    # 기본 범위 테스트 (18~100)
    assert validate_age(18) == True
    assert validate_age(65) == True
    assert validate_age(100) == True

    # 범위 밖 값 테스트
    assert validate_age(17) == False
    assert validate_age(101) == False

    # 커스텀 범위 테스트
    assert validate_age(16, min_age=16, max_age=80) == True
    assert validate_age(80, min_age=16, max_age=80) == True
    assert validate_age(15, min_age=16, max_age=80) == False
    assert validate_age(81, min_age=16, max_age=80) == False


@pytest.mark.parametrize(
    "date_str,format_str,expected",
    [
        ("2023-01-01", "%Y-%m-%d", True),
        ("01/01/2023", "%m/%d/%Y", True),
        ("2023.01.01", "%Y.%m.%d", True),
        ("invalid-date", "%Y-%m-%d", False),
        ("2023-13-01", "%Y-%m-%d", False),  # 존재하지 않는 월
        ("2023-01-32", "%Y-%m-%d", False),  # 존재하지 않는 일
    ],
)
def test_validate_date(date_str, format_str, expected):
    assert validate_date(date_str, format_str) == expected


def test_validate_future_date():
    # 현재 날짜 구하기
    now = datetime.now()

    # 미래 날짜 테스트
    future = now + timedelta(days=1)
    future_str = future.strftime("%Y-%m-%d")
    assert validate_future_date(future_str) == True

    # 과거 날짜 테스트
    past = now - timedelta(days=1)
    past_str = past.strftime("%Y-%m-%d")
    assert validate_future_date(past_str) == False

    # 잘못된 형식 테스트
    assert validate_future_date("invalid-date") == False


def test_validate_enum_value():
    # 문자열 열거형 테스트
    status_values = ["PENDING", "ACTIVE", "COMPLETED", "CANCELLED"]
    assert validate_enum_value("ACTIVE", status_values) == True
    assert validate_enum_value("UNKNOWN", status_values) == False

    # 숫자 열거형 테스트
    priority_values = [1, 2, 3, 5, 8]
    assert validate_enum_value(3, priority_values) == True
    assert validate_enum_value(4, priority_values) == False


def test_validate_required_fields():
    # 모든 필드가 존재하는 테스트
    data = {"id": 1, "name": "John", "email": "john@example.com"}
    required_fields = ["id", "name", "email"]
    result, error_msg = validate_required_fields(data, required_fields)
    assert result == True
    assert error_msg is None

    # 일부 필드가 누락된 테스트
    data = {"id": 1, "name": "John"}
    result, error_msg = validate_required_fields(data, required_fields)
    assert result == False
    assert error_msg is not None
    assert "누락" in str(error_msg)
    assert "email" in str(error_msg)

    # 필드 값이 None인 경우 테스트
    data = {"id": 1, "name": "John", "email": None}
    result, error_msg = validate_required_fields(data, required_fields)
    assert result == False
    assert error_msg is not None
    assert "email" in str(error_msg)

    # 빈 데이터 테스트
    data = {}
    result, error_msg = validate_required_fields(data, required_fields)
    assert result == False
    assert error_msg is not None
    assert all(field in str(error_msg) for field in required_fields)


def test_validate_string_length():
    # 유효한 문자열 길이 테스트
    result, error_msg = validate_string_length("Hello", min_length=3, max_length=10)
    assert result == True
    assert error_msg is None

    # 최소 길이 위반 테스트
    result, error_msg = validate_string_length("Hi", min_length=3)
    assert result == False
    assert error_msg is not None
    assert "짧습니다" in str(error_msg)

    # 최대 길이 위반 테스트
    result, error_msg = validate_string_length("Hello World", max_length=10)
    assert result == False
    assert error_msg is not None
    assert "깁니다" in str(error_msg)

    # 최소/최대 길이 모두 None인 테스트
    result, error_msg = validate_string_length("Any length string")
    assert result == True
    assert error_msg is None


def test_sanitize_input():
    # HTML 태그 제거 테스트
    input_text = "<script>alert('XSS')</script>Hello"
    sanitized = sanitize_input(input_text)
    assert "<script>" not in sanitized
    assert "Hello" in sanitized

    # SQL 인젝션 문자 제거 테스트
    input_text = "name'; DROP TABLE users; --"
    sanitized = sanitize_input(input_text)
    assert "'" not in sanitized
    assert ";" not in sanitized
    assert "--" not in sanitized
    assert "DROP" not in sanitized

    # SQL 키워드 제거 테스트
    input_text = "SELECT * FROM users WHERE id=1"
    sanitized = sanitize_input(input_text)
    assert "SELECT" not in sanitized
    assert "FROM" not in sanitized
    assert "WHERE" not in sanitized
    assert "id=1" not in sanitized
