"""
# File: tests/test_exceptions/test_exceptions_auth.py
# Description: 인증 관련 예외 클래스 테스트
"""
import pytest
from fastapi import status
from app.common.exceptions.exceptions_auth import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    InvalidCredentialsError,
    PermissionDeniedError,
    InsufficientRoleError,
    AccountDisabledError,
    AccountLockedError,
)


def test_authentication_error():
    """AuthenticationError 테스트"""
    # 기본 헤더
    exc = AuthenticationError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "인증에 실패했습니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}
    
    # 커스텀 헤더
    headers = {"WWW-Authenticate": "Basic"}
    exc = AuthenticationError(headers=headers)
    assert exc.headers == headers
    
    # 커스텀 메시지
    exc = AuthenticationError(detail="커스텀 인증 오류")
    assert exc.detail == "커스텀 인증 오류"


def test_invalid_token_error():
    """InvalidTokenError 테스트"""
    exc = InvalidTokenError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "유효하지 않은 인증 토큰입니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}


def test_token_expired_error():
    """TokenExpiredError 테스트"""
    exc = TokenExpiredError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "인증 토큰이 만료되었습니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}


def test_invalid_credentials_error():
    """InvalidCredentialsError 테스트"""
    exc = InvalidCredentialsError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "잘못된 로그인 정보입니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}


def test_permission_denied_error():
    """PermissionDeniedError 테스트"""
    exc = PermissionDeniedError()
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == "해당 작업에 대한 권한이 없습니다."


def test_insufficient_role_error():
    """InsufficientRoleError 테스트"""
    exc = InsufficientRoleError()
    assert exc.status_code == status.HTTP_403_FORBIDDEN
    assert exc.detail == "작업에 필요한 역할(Role)이 없습니다."


def test_account_disabled_error():
    """AccountDisabledError 테스트"""
    exc = AccountDisabledError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "계정이 비활성화되었습니다. 관리자에게 문의하세요."
    assert exc.headers == {"WWW-Authenticate": "Bearer"}


def test_account_locked_error():
    """AccountLockedError 테스트"""
    exc = AccountLockedError()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.detail == "계정이 잠겼습니다. 비밀번호 재설정이 필요합니다."
    assert exc.headers == {"WWW-Authenticate": "Bearer"} 