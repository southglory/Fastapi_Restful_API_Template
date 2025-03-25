"""
# File: tests/test_exceptions/test_exceptions_validation.py
# Description: 검증 관련 예외 클래스 테스트
"""
import pytest
from fastapi import status

from app.common.exceptions.exceptions_validation import (
    ValidationError,
    InvalidParameterError,
    MissingRequiredFieldError,
    InvalidFormatError,
    ValueOutOfRangeError
)


def test_validation_error():
    """ValidationError 테스트"""
    exc = ValidationError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "데이터 검증에 실패했습니다."
    
    # 커스텀 메시지
    exc = ValidationError(detail="커스텀 검증 오류")
    assert exc.detail == "커스텀 검증 오류"


def test_invalid_parameter_error():
    """InvalidParameterError 테스트"""
    # 기본 메시지
    exc = InvalidParameterError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "잘못된 파라미터입니다."
    
    # 파라미터 정보 포함
    exc = InvalidParameterError(
        param_name="age",
        param_value="invalid",
        reason="숫자여야 합니다"
    )
    assert exc.detail == "파라미터 'age'가 잘못되었습니다: 'invalid' (숫자여야 합니다)"
    
    # 커스텀 메시지
    exc = InvalidParameterError(detail="커스텀 파라미터 오류")
    assert exc.detail == "커스텀 파라미터 오류"


def test_missing_required_field_error():
    """MissingRequiredFieldError 테스트"""
    # 기본 메시지
    exc = MissingRequiredFieldError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "필수 필드가 누락되었습니다."
    
    # 필드 목록 포함
    exc = MissingRequiredFieldError(field_names=["name", "email"])
    assert exc.detail == "다음 필드가 필요합니다: name, email"
    
    # 커스텀 메시지
    exc = MissingRequiredFieldError(detail="커스텀 필드 오류")
    assert exc.detail == "커스텀 필드 오류"


def test_invalid_format_error():
    """InvalidFormatError 테스트"""
    # 기본 메시지
    exc = InvalidFormatError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "잘못된 데이터 형식입니다."
    
    # 필드와 형식 정보 포함
    exc = InvalidFormatError(
        field_name="email",
        expected_format="이메일 주소"
    )
    assert exc.detail == "필드 'email'의 형식이 잘못되었습니다. 예상 형식: 이메일 주소"
    
    # 커스텀 메시지
    exc = InvalidFormatError(detail="커스텀 형식 오류")
    assert exc.detail == "커스텀 형식 오류"


def test_value_out_of_range_error():
    """ValueOutOfRangeError 테스트"""
    # 기본 메시지
    exc = ValueOutOfRangeError()
    assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.detail == "값이 허용 범위를 벗어났습니다."
    
    # 범위 정보 포함
    exc = ValueOutOfRangeError(
        field_name="age",
        value=150,
        min_value=0,
        max_value=120
    )
    assert exc.detail == "필드 'age'의 값(150)이 허용 범위(0~120)를 벗어났습니다."
    
    # 커스텀 메시지
    exc = ValueOutOfRangeError(detail="커스텀 범위 오류")
    assert exc.detail == "커스텀 범위 오류" 