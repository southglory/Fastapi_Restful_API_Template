"""
# File: fastapi_template/app/common/utils/orm_utils.py
# Description: SQLAlchemy ORM 관련 유틸리티 함수
# - SQLAlchemy Column과 Python 타입 간 변환 기능
# - ORM 모델 조작 도우미 함수
"""

from typing import Any, TypeVar, cast
from sqlalchemy.sql.schema import Column

T = TypeVar("T")


def get_python_value(column_value: Any, default_value: T = 0) -> T:
    """
    SQLAlchemy 컬럼 값을 Python 기본 타입으로 변환

    Args:
        column_value: 변환할 SQLAlchemy Column 또는 일반 값
        default_value: 변환 실패 시 반환할 기본값

    Returns:
        변환된 Python 기본 타입 값

    Example:
        ```python
        user_id = get_python_value(user.id)
        ```
    """
    if isinstance(column_value, Column):
        return cast(T, column_value._annotations.get("value", default_value))
    return column_value
