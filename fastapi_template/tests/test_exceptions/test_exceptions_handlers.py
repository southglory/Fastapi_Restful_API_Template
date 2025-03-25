"""
# File: tests/test_exceptions/test_exceptions_handlers.py
# Description: 예외 핸들러 테스트
"""
import json
import pytest
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.common.exceptions.exceptions_base import AppException
from app.common.exceptions.exceptions_validation import ValidationError
from app.common.exceptions.exceptions_database import DatabaseError
from app.common.exceptions.exceptions_handlers import add_exception_handlers


@pytest.fixture
def app():
    """테스트용 FastAPI 앱 생성"""
    app = FastAPI()
    add_exception_handlers(app)
    return app


@pytest.fixture
def mock_request():
    """테스트용 Request 객체 생성"""
    return Request(scope={
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": []
    })


async def test_handle_app_exception(app, mock_request):
    """AppException 핸들러 테스트"""
    # 기본 예외
    exc = AppException()
    handler = app.exception_handlers[AppException]
    response = await handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "서버 오류가 발생했습니다."}
    
    # 커스텀 상태 코드와 메시지
    exc = AppException(status_code=400, detail="잘못된 요청")
    response = await handler(mock_request, exc)
    assert response.status_code == 400
    assert json.loads(response.body) == {"detail": "잘못된 요청"}
    
    # 헤더 포함
    exc = AppException(headers={"X-Custom": "value"})
    response = await handler(mock_request, exc)
    assert response.headers["x-custom"] == "value"


async def test_handle_validation_error(app, mock_request):
    """ValidationException 핸들러 테스트"""
    # 기본 검증 오류
    exc = RequestValidationError(errors=[])
    handler = app.exception_handlers[PydanticValidationError]
    response = await handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    
    # 상세 오류 정보 포함
    errors = [
        {"loc": ("query", "page"), "msg": "field required", "type": "missing"}
    ]
    exc = RequestValidationError(errors=errors)
    response = await handler(mock_request, exc)
    assert response.status_code == 422
    assert "field required" in json.loads(response.body)["detail"][0]["msg"]


async def test_handle_sql_error(app, mock_request):
    """SQLAlchemy 예외 핸들러 테스트"""
    # 기본 SQL 예외
    exc = SQLAlchemyError("데이터베이스 오류")
    handler = app.exception_handlers[SQLAlchemyError]
    response = await handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "데이터베이스 오류가 발생했습니다."}


async def test_handle_general_exception(app, mock_request):
    """일반 예외 핸들러 테스트"""
    # 기본 예외
    exc = Exception("일반 오류")
    handler = app.exception_handlers[Exception]
    response = await handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "서버 내부 오류가 발생했습니다."} 