"""
페이지네이션 유틸리티 테스트
"""
import pytest
from typing import List
from pydantic import BaseModel
from unittest.mock import MagicMock

from app.common.utils.pagination import (
    PaginationParams,
    PageInfo,
    PaginatedResponse,
    apply_pagination
)


class SampleItem(BaseModel):
    """테스트용 샘플 데이터 모델"""
    id: int
    name: str


class TestPaginationParams:
    """페이지네이션 파라미터 테스트"""
    
    def test_pagination_params_defaults(self):
        """PaginationParams 기본값 테스트"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 10
        assert params.skip == 0
    
    def test_pagination_params_custom(self):
        """PaginationParams 사용자 정의 값 테스트"""
        params = PaginationParams(page=3, page_size=20)
        assert params.page == 3
        assert params.page_size == 20
        assert params.skip == 40  # (3-1) * 20 = 40


class TestApplyPagination:
    """apply_pagination 함수 테스트"""
    
    def test_apply_pagination_to_query(self):
        """쿼리 객체에 페이지네이션 적용 테스트"""
        # 모의 쿼리 객체 생성
        mock_query = MagicMock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # 페이지네이션 파라미터
        params = PaginationParams(page=2, page_size=15)
        
        # apply_pagination 함수 호출
        result = apply_pagination(mock_query, params)
        
        # 함수 호출 검증
        mock_query.offset.assert_called_once_with(params.skip)  # offset(15)
        mock_query.limit.assert_called_once_with(params.page_size)  # limit(15)
        assert result == mock_query


class TestPaginatedResponse:
    """페이지네이션 응답 테스트"""
    
    def setup_method(self):
        """테스트 데이터 준비"""
        self.items: List[SampleItem] = [
            SampleItem(id=i, name=f"Item {i}")
            for i in range(1, 101)  # 1부터 100까지 아이템 생성
        ]
    
    def test_paginated_response_first_page(self):
        """첫 페이지 응답 테스트"""
        params = PaginationParams(page=1, page_size=10)
        response = PaginatedResponse.create(
            items=self.items[:10],
            total_items=len(self.items),
            params=params
        )
        
        # items 검증
        assert len(response.items) == 10
        assert response.items[0].id == 1
        assert response.items[9].id == 10
        
        # page_info 검증
        assert response.page_info.page == 1
        assert response.page_info.page_size == 10
        assert response.page_info.total_items == 100
        assert response.page_info.total_pages == 10
        assert response.page_info.has_previous is False
        assert response.page_info.has_next is True
    
    def test_paginated_response_middle_page(self):
        """중간 페이지 응답 테스트"""
        params = PaginationParams(page=5, page_size=10)
        # 5페이지에 해당하는 아이템: 41-50
        start_idx = (params.page - 1) * params.page_size
        end_idx = start_idx + params.page_size
        page_items = self.items[start_idx:end_idx]
        
        response = PaginatedResponse.create(
            items=page_items,
            total_items=len(self.items),
            params=params
        )
        
        # items 검증
        assert len(response.items) == 10
        assert response.items[0].id == 41
        assert response.items[9].id == 50
        
        # page_info 검증
        assert response.page_info.page == 5
        assert response.page_info.total_pages == 10
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is True
    
    def test_paginated_response_last_page(self):
        """마지막 페이지 응답 테스트"""
        params = PaginationParams(page=10, page_size=10)
        # 10페이지에 해당하는 아이템: 91-100
        start_idx = (params.page - 1) * params.page_size
        end_idx = start_idx + params.page_size
        page_items = self.items[start_idx:end_idx]
        
        response = PaginatedResponse.create(
            items=page_items,
            total_items=len(self.items),
            params=params
        )
        
        # items 검증
        assert len(response.items) == 10
        assert response.items[0].id == 91
        assert response.items[9].id == 100
        
        # page_info 검증
        assert response.page_info.page == 10
        assert response.page_info.total_pages == 10
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is False
    
    def test_paginated_response_partial_page(self):
        """마지막 페이지가 부분적으로 채워진 경우 테스트"""
        # 103개 아이템 생성 (10페이지 + 나머지 3개)
        items = self.items + [
            SampleItem(id=101, name="Item 101"),
            SampleItem(id=102, name="Item 102"),
            SampleItem(id=103, name="Item 103")
        ]
        
        params = PaginationParams(page=11, page_size=10)
        # 11페이지에 해당하는 아이템: 101-103 (3개)
        start_idx = (params.page - 1) * params.page_size
        end_idx = start_idx + params.page_size
        page_items = items[start_idx:end_idx]
        
        response = PaginatedResponse.create(
            items=page_items,
            total_items=len(items),
            params=params
        )
        
        # items 검증
        assert len(response.items) == 3
        assert response.items[0].id == 101
        assert response.items[2].id == 103
        
        # page_info 검증
        assert response.page_info.page == 11
        assert response.page_info.total_items == 103
        assert response.page_info.total_pages == 11
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is False
    
    def test_paginated_response_empty_page(self):
        """빈 페이지 응답 테스트"""
        params = PaginationParams(page=20, page_size=10)  # 존재하지 않는 페이지
        
        response = PaginatedResponse.create(
            items=[],  # 빈 아이템 목록
            total_items=len(self.items),
            params=params
        )
        
        # items 검증
        assert len(response.items) == 0
        
        # page_info 검증
        assert response.page_info.page == 20
        assert response.page_info.total_items == 100
        assert response.page_info.total_pages == 10
        assert response.page_info.has_previous is True
        assert response.page_info.has_next is False
    
    def test_paginated_response_empty_total(self):
        """총 아이템이 0개인 경우 테스트"""
        params = PaginationParams(page=1, page_size=10)
        
        response = PaginatedResponse.create(
            items=[],
            total_items=0,
            params=params
        )
        
        # page_info 검증
        assert response.page_info.page == 1
        assert response.page_info.total_items == 0
        assert response.page_info.total_pages == 0
        assert response.page_info.has_previous is False
        assert response.page_info.has_next is False 