"""
# File: fastapi_template/app/common/exceptions/exceptions_base.py
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