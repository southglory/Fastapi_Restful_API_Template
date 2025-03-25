"""
# File: tests/test_exceptions/test_exceptions_base.py
# Description: 기본 예외 클래스 테스트
"""

import pytest
from fastapi import status

from app.common.exceptions.exceptions_base import AppException


def test_app_exception_default():
    """기본 파라미터로 AppException 초기화 테스트"""
    exc = AppException()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "서버 오류가 발생했습니다."
    assert exc.headers is None


def test_app_exception_custom():
    """커스텀 파라미터로 AppException 초기화 테스트"""
    detail = "테스트 오류"
    status_code = 501
    headers = {"X-Custom-Header": "test"}
    
    exc = AppException(detail=detail, status_code=status_code, headers=headers)
    assert exc.status_code == status_code
    assert exc.detail == detail
    assert exc.headers == headers


def test_app_exception_partial_custom():
    """일부 파라미터만 커스텀하여 AppException 초기화 테스트"""
    # detail만 커스텀
    exc = AppException(detail="테스트 오류")
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "테스트 오류"
    
    # status_code만 커스텀
    exc = AppException(status_code=501)
    assert exc.status_code == 501
    assert exc.detail == "서버 오류가 발생했습니다."
    
    # headers만 커스텀
    headers = {"X-Custom-Header": "test"}
    exc = AppException(headers=headers)
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "서버 오류가 발생했습니다."
    assert exc.headers == headers 