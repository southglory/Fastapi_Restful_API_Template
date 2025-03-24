"""
# File: fastapi_template/app/common/exceptions/http.py
# Description: HTTP 관련 예외 클래스
"""

from typing import Dict, Optional

from fastapi import status

from app.common.exceptions.base import AppException


class BadRequestError(AppException):
    """
    잘못된 요청 오류 (400)
    """
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "잘못된 요청입니다."


class UnauthorizedError(AppException):
    """
    인증되지 않은 요청 오류 (401)
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "인증이 필요합니다."
    
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


class ForbiddenError(AppException):
    """
    접근 권한 없음 오류 (403)
    """
    status_code = status.HTTP_403_FORBIDDEN
    detail = "접근 권한이 없습니다."


class NotFoundError(AppException):
    """
    리소스를 찾을 수 없음 오류 (404)
    """
    status_code = status.HTTP_404_NOT_FOUND
    detail = "요청한 리소스를 찾을 수 없습니다."


class MethodNotAllowedError(AppException):
    """
    허용되지 않은 메서드 오류 (405)
    """
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    detail = "허용되지 않은 HTTP 메서드입니다."


class ConflictError(AppException):
    """
    리소스 충돌 오류 (409)
    """
    status_code = status.HTTP_409_CONFLICT
    detail = "리소스 충돌이 발생했습니다."


class UnprocessableEntityError(AppException):
    """
    처리할 수 없는 엔티티 오류 (422)
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "요청 데이터를 처리할 수 없습니다."


class TooManyRequestsError(AppException):
    """
    요청 횟수 초과 오류 (429)
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요."


class InternalServerError(AppException):
    """
    서버 내부 오류 (500)
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "서버 내부 오류가 발생했습니다." 