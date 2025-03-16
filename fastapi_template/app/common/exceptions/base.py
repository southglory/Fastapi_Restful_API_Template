"""
# File: fastapi_template/app/common/exceptions/base.py
# Description: 커스텀 예외 기본 클래스
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    애플리케이션 공통 예외 기본 클래스
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "서버 오류가 발생했습니다."
    
    def __init__(
        self, 
        detail: Optional[str] = None, 
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        self.status_code = status_code or self.status_code
        self.detail = detail or self.detail
        self.headers = headers
        
        super().__init__(status_code=self.status_code, detail=self.detail, headers=headers)


class NotFoundError(AppException):
    """
    리소스를 찾을 수 없을 때 발생하는 예외
    """
    status_code = status.HTTP_404_NOT_FOUND
    detail = "요청한 리소스를 찾을 수 없습니다."


class AuthenticationError(AppException):
    """
    인증 오류 발생 시 사용되는 예외
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
            headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedError(AppException):
    """
    권한 부족 시 발생하는 예외
    """
    status_code = status.HTTP_403_FORBIDDEN
    detail = "해당 작업에 대한 권한이 없습니다."


class ValidationError(AppException):
    """
    데이터 검증 실패 시 발생하는 예외
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "데이터 검증에 실패했습니다."


class DatabaseError(AppException):
    """
    데이터베이스 관련 예외
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "데이터베이스 오류가 발생했습니다." 