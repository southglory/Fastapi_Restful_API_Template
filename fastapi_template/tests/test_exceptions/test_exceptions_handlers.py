"""
# File: tests/test_exceptions/test_exceptions_handlers.py
# Description: 예외 핸들러 테스트
"""
import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import json

from app.common.exceptions.exceptions_base import AppException
from app.common.exceptions.exceptions_handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)


@pytest.fixture
def mock_request():
    """테스트용 Request 객체 생성"""
    return Request(scope={
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": []
    })


def test_app_exception_handler(mock_request):
    """AppException 핸들러 테스트"""
    # 기본 예외
    exc = AppException()
    response = app_exception_handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == json.dumps({"detail": "알 수 없는 오류가 발생했습니다."}).encode()
    
    # 커스텀 상태 코드와 메시지
    exc = AppException(status_code=400, detail="잘못된 요청")
    response = app_exception_handler(mock_request, exc)
    assert response.status_code == 400
    assert response.body == json.dumps({"detail": "잘못된 요청"}).encode()
    
    # 헤더 포함
    exc = AppException(headers={"X-Custom": "value"})
    response = app_exception_handler(mock_request, exc)
    assert response.headers["x-custom"] == "value"


def test_validation_exception_handler(mock_request):
    """ValidationException 핸들러 테스트"""
    # 기본 검증 오류
    exc = RequestValidationError(errors=[])
    response = validation_exception_handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    assert response.body == json.dumps({"detail": "입력 데이터 검증에 실패했습니다."}).encode()
    
    # 상세 오류 정보 포함
    errors = [
        {"loc": ("query", "page"), "msg": "field required", "type": "missing"}
    ]
    exc = RequestValidationError(errors=errors)
    response = validation_exception_handler(mock_request, exc)
    assert response.status_code == 422
    assert "field required" in response.body.decode()


def test_http_exception_handler(mock_request):
    """HTTPException 핸들러 테스트"""
    # 기본 HTTP 예외
    exc = HTTPException(status_code=404)
    response = http_exception_handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    assert response.body == json.dumps({"detail": "Not Found"}).encode()
    
    # 커스텀 메시지
    exc = HTTPException(status_code=404, detail="리소스를 찾을 수 없습니다")
    response = http_exception_handler(mock_request, exc)
    assert response.status_code == 404
    assert response.body == json.dumps({"detail": "리소스를 찾을 수 없습니다"}).encode()
    
    # 헤더 포함
    exc = HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"})
    response = http_exception_handler(mock_request, exc)
    assert response.headers["www-authenticate"] == "Bearer"


def test_generic_exception_handler(mock_request):
    """GenericException 핸들러 테스트"""
    # 기본 예외
    exc = Exception("일반 오류")
    response = generic_exception_handler(mock_request, exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == json.dumps({"detail": "알 수 없는 오류가 발생했습니다."}).encode()
    
    # 커스텀 메시지
    exc = Exception("커스텀 오류")
    response = generic_exception_handler(mock_request, exc)
    assert response.status_code == 500
    assert response.body == json.dumps({"detail": "알 수 없는 오류가 발생했습니다."}).encode() 