"""
# File: fastapi_template/app/common/exceptions/validation.py
# Description: 유효성 검증 관련 예외 클래스
"""

from typing import Optional, Dict, Any, List, Union

from fastapi import status

from app.common.exceptions.base import AppException


class ValidationError(AppException):
    """
    데이터 유효성 검증 실패 예외
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "데이터 검증에 실패했습니다."


class InvalidParameterError(ValidationError):
    """
    잘못된 파라미터 예외
    """
    detail = "잘못된 파라미터가 제공되었습니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        param_name: Optional[str] = None,
        param_value: Optional[Any] = None,
        reason: Optional[str] = None,
        **kwargs
    ) -> None:
        self.param_name = param_name
        self.param_value = param_value
        self.reason = reason
        
        message = detail or self.detail
        if param_name:
            message = f"파라미터 '{param_name}'"
            if param_value is not None:
                message += f"의 값 '{param_value}'"
            if reason:
                message += f"이(가) 유효하지 않습니다: {reason}"
            else:
                message += "이(가) 유효하지 않습니다."
                
        super().__init__(detail=message, status_code=self.status_code, **kwargs)


class MissingRequiredFieldError(ValidationError):
    """
    필수 필드 누락 예외
    """
    detail = "필수 필드가 누락되었습니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        field_names: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> None:
        self.field_names = field_names
        
        message = detail or self.detail
        if field_names:
            if isinstance(field_names, str):
                message = f"필수 필드 '{field_names}'이(가) 누락되었습니다."
            else:
                fields_str = "', '".join(field_names)
                message = f"필수 필드 '{fields_str}'이(가) 누락되었습니다."
                
        super().__init__(detail=message, status_code=self.status_code, **kwargs)


class InvalidFormatError(ValidationError):
    """
    잘못된 형식 예외
    """
    detail = "데이터가 올바른 형식이 아닙니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        field_name: Optional[str] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ) -> None:
        self.field_name = field_name
        self.expected_format = expected_format
        
        message = detail or self.detail
        if field_name:
            message = f"필드 '{field_name}'의 형식이 올바르지 않습니다"
            if expected_format:
                message += f". 예상 형식: {expected_format}"
            message += "."
                
        super().__init__(detail=message, status_code=self.status_code, **kwargs)


class ValueOutOfRangeError(ValidationError):
    """
    값 범위 초과 예외
    """
    detail = "값이 허용된 범위를 벗어났습니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        field_name: Optional[str] = None,
        value: Optional[Any] = None,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        **kwargs
    ) -> None:
        self.field_name = field_name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        
        message = detail or self.detail
        if field_name:
            message = f"필드 '{field_name}'"
            if value is not None:
                message += f"의 값 '{value}'"
            message += "이(가) 범위를 벗어났습니다"
            
            if min_value is not None and max_value is not None:
                message += f". 허용 범위: {min_value} ~ {max_value}"
            elif min_value is not None:
                message += f". 최소값: {min_value}"
            elif max_value is not None:
                message += f". 최대값: {max_value}"
            message += "."
                
        super().__init__(detail=message, status_code=self.status_code, **kwargs) 