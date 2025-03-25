"""
# File: fastapi_template/app/common/utils/pagination.py
# Description: 페이지네이션 관련 유틸리티
"""

from typing import List, TypeVar, Any, Dict

from app.common.schemas.pagination_schema import (
    PaginationParams,
)

T = TypeVar("T")

# 페이지네이션 스키마 관련 코드는 app.common.schemas.pagination_schema 모듈로 이동됨
# 여기서는 필요한 기능을 import하여 사용

# 추가 유틸리티 함수가 필요한 경우 이곳에 구현

def apply_pagination(query: Any, params: PaginationParams) -> Any:
    """
    쿼리에 페이지네이션 적용
    
    Args:
        query: 데이터베이스 쿼리 객체
        params: 페이지네이션 파라미터
        
    Returns:
        페이지네이션이 적용된 쿼리 객체
    """
    return query.offset(params.skip).limit(params.page_size)
