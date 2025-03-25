"""
# File: fastapi_template/app/common/exceptions/__init__.py
# Description: 예외 처리 모듈 초기화
"""

# 기본 예외
from app.common.exceptions.exceptions_base import AppException

# HTTP 예외
from app.common.exceptions.exceptions_http import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError
)

# 인증 관련 예외
from app.common.exceptions.exceptions_auth import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    InvalidCredentialsError,
    PermissionDeniedError,
    InsufficientRoleError,
    AccountDisabledError,
    AccountLockedError
)

# 데이터베이스 관련 예외
from app.common.exceptions.exceptions_database import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    TransactionError
)

# 유효성 검증 관련 예외
from app.common.exceptions.exceptions_validation import (
    ValidationError,
    InvalidParameterError, 
    MissingRequiredFieldError,
    InvalidFormatError,
    ValueOutOfRangeError
)

# 예외 처리기
from app.common.exceptions.exceptions_handlers import add_exception_handlers

__all__ = [
    # 기본 예외
    "AppException",
    
    # HTTP 예외
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "ConflictError",
    "UnprocessableEntityError",
    "TooManyRequestsError",
    "InternalServerError",
    
    # 인증 관련 예외
    "AuthenticationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "InvalidCredentialsError",
    "PermissionDeniedError",
    "InsufficientRoleError",
    "AccountDisabledError",
    "AccountLockedError",
    
    # 데이터베이스 관련 예외
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "EntityNotFoundError",
    "EntityAlreadyExistsError",
    "TransactionError",
    
    # 유효성 검증 관련 예외
    "ValidationError",
    "InvalidParameterError",
    "MissingRequiredFieldError",
    "InvalidFormatError",
    "ValueOutOfRangeError",
    
    # 예외 처리기
    "add_exception_handlers"
] 