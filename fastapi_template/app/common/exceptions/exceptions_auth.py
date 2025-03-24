"""
# File: fastapi_template/app/common/exceptions/exceptions_auth.py
# Description: 인증 관련 예외 클래스
"""

from typing import Dict, Optional

from fastapi import status

from app.common.exceptions.exceptions_base import AppException


class AuthenticationError(AppException):
    """
    인증 실패 오류
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "인증에 실패했습니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=self.status_code,
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenError(AuthenticationError):
    """
    유효하지 않은 토큰 오류
    """
    detail = "유효하지 않은 인증 토큰입니다."


class TokenExpiredError(AuthenticationError):
    """
    만료된 토큰 오류
    """
    detail = "인증 토큰이 만료되었습니다."


class InvalidCredentialsError(AuthenticationError):
    """
    잘못된 로그인 정보 오류
    """
    detail = "잘못된 로그인 정보입니다."


class PermissionDeniedError(AppException):
    """
    권한 부족 오류
    """
    status_code = status.HTTP_403_FORBIDDEN
    detail = "해당 작업에 대한 권한이 없습니다."


class InsufficientRoleError(PermissionDeniedError):
    """
    역할 부족 오류
    """
    detail = "작업에 필요한 역할(Role)이 없습니다."


class AccountDisabledError(AuthenticationError):
    """
    비활성화된 계정 오류
    """
    detail = "계정이 비활성화되었습니다. 관리자에게 문의하세요."


class AccountLockedError(AuthenticationError):
    """
    잠긴 계정 오류
    """
    detail = "계정이 잠겼습니다. 비밀번호 재설정이 필요합니다." 