"""
# File: fastapi_template/app/common/exceptions/handlers.py
# Description: 글로벌 예외 처리 핸들러
"""

import logging
from typing import Any, Dict, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.common.exceptions.base import AppException, DatabaseError

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """
    FastAPI 앱에 전역 예외 핸들러 추가
    """
    
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        """
        애플리케이션 예외 처리
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
    
    @app.exception_handler(PydanticValidationError)
    async def handle_validation_error(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Pydantic 검증 오류 처리
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def handle_sql_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """
        데이터베이스 예외 처리
        """
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "데이터베이스 오류가 발생했습니다."}
        )
    
    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        처리되지 않은 모든 예외를 잡는 핸들러
        """
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "서버 내부 오류가 발생했습니다."}
        ) 