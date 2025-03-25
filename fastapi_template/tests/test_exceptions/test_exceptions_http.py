"""
# File: tests/test_exceptions/test_exceptions_http.py
# Description: HTTP 관련 예외 클래스 테스트
"""
import pytest
from fastapi import status

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


def test_bad_request_error():
    """BadRequestError 테스트"""
    exc = BadRequestError()
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.detail == "잘못된 요청입니다."


def test_unauthorized_error():
    """UnauthorizedError 테스트"""
    # 기본 헤더
    exc = UnauthorizedError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "인증이 필요합니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}

    # 커스텀 헤더
    headers = {"WWW-Authenticate": "Basic"}
    exc = UnauthorizedError(headers=headers)
    assert exc.headers == headers

    # 커스텀 메시지
    exc = UnauthorizedError(detail="커스텀 인증 오류")
    assert exc.detail == "커스텀 인증 오류"


def test_forbidden_error():
    """ForbiddenError 테스트"""
    exc = ForbiddenError()
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == "접근 권한이 없습니다."


def test_not_found_error():
    """NotFoundError 테스트"""
    exc = NotFoundError()
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "요청한 리소스를 찾을 수 없습니다."


def test_method_not_allowed_error():
    """MethodNotAllowedError 테스트"""
    exc = MethodNotAllowedError()
    assert exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert exc.detail == "허용되지 않은 HTTP 메서드입니다."


def test_conflict_error():
    """ConflictError 테스트"""
    exc = ConflictError()
    assert exc.status_code == status.HTTP_409_CONFLICT
    assert exc.detail == "리소스 충돌이 발생했습니다."


def test_unprocessable_entity_error():
    """UnprocessableEntityError 테스트"""
    exc = UnprocessableEntityError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "요청 데이터를 처리할 수 없습니다."


def test_too_many_requests_error():
    """TooManyRequestsError 테스트"""
    exc = TooManyRequestsError()
    assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exc.detail == "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요."


def test_internal_server_error():
    """InternalServerError 테스트"""
    exc = InternalServerError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "서버 내부 오류가 발생했습니다." 