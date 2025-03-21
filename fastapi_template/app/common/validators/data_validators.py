"""
# File: fastapi_template/app/common/validators/data_validators.py
# Description: 데이터 검증 유틸리티 함수
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> tuple[bool, Optional[str]]:
    """
    데이터 딕셔너리에 필수 필드가 모두 있는지 검증합니다.

    Args:
        data: 검증할 데이터 딕셔너리
        required_fields: 필수 필드 목록

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    missing_fields = [
        field for field in required_fields if field not in data or data[field] is None
    ]

    if missing_fields:
        return False, f"다음 필드가 누락되었습니다: {', '.join(missing_fields)}"

    return True, None


def validate_numeric_range(
    value: Union[int, float],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
) -> bool:
    """
    숫자 값이 지정된 범위 내에 있는지 검증합니다.

    Args:
        value: 검증할 숫자 값
        min_val: 최소값 (None인 경우 최소값 검사 안함)
        max_val: 최대값 (None인 경우 최대값 검사 안함)

    Returns:
        bool: 범위 내에 있으면 True, 아니면 False
    """
    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True


def validate_age(age: int, min_age: int = 18, max_age: int = 100) -> bool:
    """
    나이가 유효한 범위 내에 있는지 검증합니다.

    Args:
        age: 검증할 나이
        min_age: 최소 나이 (기본값: 18)
        max_age: 최대 나이 (기본값: 100)

    Returns:
        bool: 유효한 나이 범위 내에 있으면 True, 아니면 False
    """
    return validate_numeric_range(age, min_age, max_age)


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    날짜 문자열이 유효한 형식인지 검증합니다.

    Args:
        date_str: 검증할 날짜 문자열
        format_str: 날짜 형식 (기본값: '%Y-%m-%d')

    Returns:
        bool: 유효한 날짜 형식이면 True, 아니면 False
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_future_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    날짜가 현재보다 미래인지 검증합니다.

    Args:
        date_str: 검증할 날짜 문자열
        format_str: 날짜 형식 (기본값: '%Y-%m-%d')

    Returns:
        bool: 미래 날짜이면 True, 아니면 False
    """
    if not validate_date(date_str, format_str):
        return False

    date = datetime.strptime(date_str, format_str)
    return date > datetime.now()


def validate_enum_value(value: Any, valid_values: List[Any]) -> bool:
    """
    값이 유효한 열거형 값 목록에 있는지 검증합니다.

    Args:
        value: 검증할 값
        valid_values: 유효한 값 목록

    Returns:
        bool: 유효한 값 목록에 포함되어 있으면 True, 아니면 False
    """
    return value in valid_values


def validate_string_length(
    value: str, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> tuple[bool, Optional[str]]:
    """
    문자열 길이가 지정된 범위 내에 있는지 검증합니다.

    Args:
        value: 검증할 문자열
        min_length: 최소 길이 (None이면 하한 없음)
        max_length: 최대 길이 (None이면 상한 없음)

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    if min_length is not None and len(value) < min_length:
        return (
            False,
            f"문자열 길이({len(value)})가 최소 길이({min_length})보다 짧습니다.",
        )

    if max_length is not None and len(value) > max_length:
        return False, f"문자열 길이({len(value)})가 최대 길이({max_length})보다 깁니다."

    return True, None


def sanitize_input(value: str) -> str:
    """
    사용자 입력에서 잠재적으로 위험한 문자를 제거합니다.

    Args:
        value: 정제할 문자열

    Returns:
        str: 정제된 문자열
    """
    # HTML 태그 제거
    value = re.sub(r"<[^>]*>", "", value)

    # SQL 인젝션 방지를 위한 특수 문자 이스케이프
    sql_chars = [
        "'",
        '"',
        ";",
        "--",
        "/*",
        "*/",
        "=",
        "DROP",
        "DELETE",
        "INSERT",
        "SELECT",
        "UPDATE",
        "FROM",
        "WHERE",
    ]
    for char in sql_chars:
        value = value.replace(char, "")

    return value
