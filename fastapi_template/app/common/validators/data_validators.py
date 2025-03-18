"""
# File: fastapi_template/app/common/validators/data_validators.py
# Description: 데이터 검증 유틸리티 함수
"""

from typing import Any, Dict, List, Optional, Union
import re


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
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
) -> tuple[bool, Optional[str]]:
    """
    숫자 값이 지정된 범위 내에 있는지 검증합니다.

    Args:
        value: 검증할 숫자 값
        min_value: 최소값 (None이면 하한 없음)
        max_value: 최대값 (None이면 상한 없음)

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    if min_value is not None and value < min_value:
        return False, f"값({value})이 최소값({min_value})보다 작습니다."

    if max_value is not None and value > max_value:
        return False, f"값({value})이 최대값({max_value})보다 큽니다."

    return True, None


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
    ]
    for char in sql_chars:
        value = value.replace(char, "")

    return value
