"""
# File: fastapi_template/app/common/exceptions/__init__.py
# Description: 예외 처리 모듈 초기화
"""

from app.common.exceptions.base import (
    AppException,
    NotFoundError,
    AuthenticationError,
    PermissionDeniedError,
    ValidationError,
    DatabaseError
)
from app.common.exceptions.handlers import add_exception_handlers

__all__ = [
    "AppException",
    "NotFoundError",
    "AuthenticationError",
    "PermissionDeniedError",
    "ValidationError",
    "DatabaseError",
    "add_exception_handlers"
] 