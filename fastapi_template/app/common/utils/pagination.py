"""
# File: fastapi_template/app/common/utils/pagination.py
# Description: 페이지네이션 관련 유틸리티
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams:
    """
    API 요청의 페이지네이션 파라미터
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="페이지 번호"),
        page_size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


class PageInfo(BaseModel):
    """
    페이지 정보 모델
    """
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


class PaginatedResponse(GenericModel, Generic[T]):
    """
    페이지네이션 결과 응답 모델
    """
    items: List[T]
    page_info: PageInfo

    @classmethod
    def create(
        cls, items: List[T], total_items: int, params: PaginationParams
    ) -> "PaginatedResponse[T]":
        """
        페이지네이션 응답 객체 생성
        """
        total_pages = (total_items + params.page_size - 1) // params.page_size
        
        page_info = PageInfo(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=params.page > 1,
            has_next=params.page < total_pages
        )
        
        return cls(items=items, page_info=page_info) 