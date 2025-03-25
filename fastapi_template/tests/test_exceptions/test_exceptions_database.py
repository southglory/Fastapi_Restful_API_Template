"""
# File: tests/test_exceptions/test_exceptions_database.py
# Description: 데이터베이스 관련 예외 클래스 테스트
"""
import pytest
from fastapi import status

from app.common.exceptions.exceptions_database import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    TransactionError
)


def test_database_error():
    """DatabaseError 테스트"""
    exc = DatabaseError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "데이터베이스 오류가 발생했습니다."
    
    # 커스텀 메시지
    exc = DatabaseError(detail="커스텀 DB 오류")
    assert exc.detail == "커스텀 DB 오류"


def test_database_connection_error():
    """DatabaseConnectionError 테스트"""
    exc = DatabaseConnectionError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "데이터베이스 연결에 실패했습니다."
    
    # 커스텀 메시지
    exc = DatabaseConnectionError(detail="커스텀 연결 오류")
    assert exc.detail == "커스텀 연결 오류"


def test_database_query_error():
    """DatabaseQueryError 테스트"""
    exc = DatabaseQueryError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "데이터베이스 쿼리 실행 중 오류가 발생했습니다."
    
    # 커스텀 메시지
    exc = DatabaseQueryError(detail="커스텀 쿼리 오류")
    assert exc.detail == "커스텀 쿼리 오류"


def test_entity_not_found_error():
    """EntityNotFoundError 테스트"""
    # 기본 메시지
    exc = EntityNotFoundError()
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "요청한 엔티티를 찾을 수 없습니다."
    
    # 엔티티 타입과 ID 포함
    exc = EntityNotFoundError(entity_type="User", entity_id=1)
    assert exc.detail == "User (id: 1)을(를) 찾을 수 없습니다."
    
    # 커스텀 메시지
    exc = EntityNotFoundError(detail="커스텀 엔티티 오류")
    assert exc.detail == "커스텀 엔티티 오류"


def test_entity_already_exists_error():
    """EntityAlreadyExistsError 테스트"""
    # 기본 메시지
    exc = EntityAlreadyExistsError()
    assert exc.status_code == status.HTTP_409_CONFLICT
    assert exc.detail == "엔티티가 이미 존재합니다."
    
    # 엔티티 타입과 식별자 포함
    exc = EntityAlreadyExistsError(entity_type="User", identifier="email@example.com")
    assert exc.detail == "User이(가) 이미 존재합니다."
    
    # 커스텀 메시지
    exc = EntityAlreadyExistsError(detail="커스텀 엔티티 오류")
    assert exc.detail == "커스텀 엔티티 오류"


def test_transaction_error():
    """TransactionError 테스트"""
    exc = TransactionError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "트랜잭션 처리 중 오류가 발생했습니다."
    
    # 커스텀 메시지
    exc = TransactionError(detail="커스텀 트랜잭션 오류")
    assert exc.detail == "커스텀 트랜잭션 오류" 