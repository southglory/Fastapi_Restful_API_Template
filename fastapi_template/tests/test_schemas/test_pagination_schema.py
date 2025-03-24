"""
# File: tests/test_schemas/test_pagination_schema.py
# Description: 페이지네이션 스키마 테스트
"""

import pytest
from typing import List, Dict, Any
from pydantic import BaseModel

from app.common.schemas.pagination_schema import (
    PaginationParams,
    PageInfo,
    PaginatedResponse
)


class SampleItem(BaseModel):
    """테스트용 샘플 데이터 모델"""
    id: int
    name: str


class TestPaginationParams:
    """페이지네이션 파라미터 테스트"""
    
    def test_pagination_params_init(self):
        """PaginationParams 초기화 테스트"""
        # 기본값 테스트
        params1 = PaginationParams()
        assert params1.page == 1
        assert params1.page_size == 10
        assert params1.skip == 0
        
        # 사용자 정의값 테스트
        params2 = PaginationParams(page=3, page_size=15)
        assert params2.page == 3
        assert params2.page_size == 15
        assert params2.skip == 30  # (3-1) * 15 = 30


class TestPageInfo:
    """페이지 정보 모델 테스트"""
    
    def test_page_info_model(self):
        """PageInfo 모델 검증"""
        page_info = PageInfo(
            page=2,
            page_size=10,
            total_items=25,
            total_pages=3,
            has_previous=True,
            has_next=True
        )
        
        # 값 검증
        assert page_info.page == 2
        assert page_info.page_size == 10
        assert page_info.total_items == 25
        assert page_info.total_pages == 3
        assert page_info.has_previous is True
        assert page_info.has_next is True
        
        # 직렬화 검증
        page_info_dict = page_info.model_dump()
        assert page_info_dict["page"] == 2
        assert page_info_dict["total_pages"] == 3


class TestPaginatedResponse:
    """페이지네이션 응답 테스트"""
    
    def setup_method(self):
        """테스트 데이터 준비"""
        self.items: List[SampleItem] = [
            SampleItem(id=i, name=f"Item {i}")
            for i in range(1, 31)  # 1부터 30까지 아이템 생성
        ]
    
    def test_paginated_response_model(self):
        """PaginatedResponse 모델 검증"""
        # 페이지 정보 생성
        page_info = PageInfo(
            page=1,
            page_size=10,
            total_items=30,
            total_pages=3,
            has_previous=False,
            has_next=True
        )
        
        # 페이지네이션 응답 생성
        response = PaginatedResponse(
            items=self.items[:10],
            page_info=page_info
        )
        
        # 값 검증
        assert len(response.items) == 10
        assert response.page_info.page == 1
        assert response.page_info.total_pages == 3
        assert response.page_info.has_next is True
        
        # 직렬화 검증
        response_dict = response.model_dump()
        assert len(response_dict["items"]) == 10
        assert response_dict["page_info"]["page"] == 1
    
    def test_paginated_response_create_method(self):
        """PaginatedResponse.create 메서드 테스트"""
        params = PaginationParams(page=2, page_size=10)
        response = PaginatedResponse.create(
            items=self.items[10:20],
            total_items=len(self.items),
            params=params
        )
        
        # 값 검증
        assert len(response.items) == 10
        assert response.items[0].id == 11
        assert response.items[9].id == 20
        
        # 페이지 정보 검증
        assert response.page_info.page == 2
        assert response.page_info.page_size == 10
        assert response.page_info.total_items == 30
        assert response.page_info.total_pages == 3
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is True

    def test_paginated_response_zero_total_items(self):
        """총 아이템 수가 0인 경우 테스트"""
        params = PaginationParams(page=1, page_size=10)
        response = PaginatedResponse.create(
            items=[],
            total_items=0,
            params=params
        )
        
        # 페이지 정보 검증
        assert response.page_info.total_items == 0
        assert response.page_info.total_pages == 0
        assert response.page_info.has_previous is False
        assert response.page_info.has_next is False

    def test_paginated_response_exact_page_size(self):
        """정확히 페이지 크기만큼 아이템이 있는 경우 테스트"""
        total_items = 20
        params = PaginationParams(page=2, page_size=10)
        response = PaginatedResponse.create(
            items=self.items[10:20],
            total_items=total_items,
            params=params
        )
        
        # 페이지 정보 검증
        assert response.page_info.total_items == 20
        assert response.page_info.total_pages == 2
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is False  # 마지막 페이지 