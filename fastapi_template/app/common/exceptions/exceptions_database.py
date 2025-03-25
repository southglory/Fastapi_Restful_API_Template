"""
# File: fastapi_template/app/common/exceptions/exceptions_database.py
# Description: 데이터베이스 관련 예외 클래스
"""

from typing import Optional, Dict, Any

from fastapi import status

from app.common.exceptions.exceptions_base import AppException


class DatabaseError(AppException):
    """
    데이터베이스 관련 기본 예외
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "데이터베이스 오류가 발생했습니다."


class DatabaseConnectionError(DatabaseError):
    """
    데이터베이스 연결 실패 예외
    """
    detail = "데이터베이스 연결에 실패했습니다."


class DatabaseQueryError(DatabaseError):
    """
    데이터베이스 쿼리 실행 오류
    """
    detail = "데이터베이스 쿼리 실행 중 오류가 발생했습니다."


class EntityNotFoundError(AppException):
    """
    엔티티를 찾을 수 없을 때 발생하는 예외
    """
    status_code = status.HTTP_404_NOT_FOUND
    detail = "요청한 엔티티를 찾을 수 없습니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[Any] = None,
        **kwargs
    ) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        
        message = detail or self.detail
        if entity_type:
            message = f"{entity_type}"
            if entity_id:
                message += f" (id: {entity_id})"
            message += "을(를) 찾을 수 없습니다."
            
        super().__init__(detail=message, status_code=self.status_code, **kwargs)


class EntityAlreadyExistsError(AppException):
    """
    엔티티가 이미 존재할 때 발생하는 예외
    """
    status_code = status.HTTP_409_CONFLICT
    detail = "엔티티가 이미 존재합니다."
    
    def __init__(
        self,
        detail: Optional[str] = None,
        entity_type: Optional[str] = None,
        identifier: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        self.entity_type = entity_type
        self.identifier = identifier
        
        message = detail or self.detail
        if entity_type:
            message = f"{entity_type}이(가) 이미 존재합니다."
            
        super().__init__(detail=message, status_code=self.status_code, **kwargs)


class TransactionError(DatabaseError):
    """
    트랜잭션 처리 중 발생하는 예외
    """
    detail = "트랜잭션 처리 중 오류가 발생했습니다." 