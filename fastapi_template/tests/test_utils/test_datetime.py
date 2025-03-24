"""
날짜/시간 유틸리티 함수 테스트
"""
import pytest
from datetime import datetime, timezone
from freezegun import freeze_time

from app.common.utils.datetime import (
    get_utc_now,
    format_datetime,
    parse_datetime,
    add_time
)


class TestDatetimeUtils:
    """날짜/시간 유틸리티 함수 테스트"""

    def test_format_datetime(self):
        """datetime 포맷팅 함수 테스트"""
        # 테스트용 날짜 생성
        dt = datetime(2023, 5, 15, 10, 30, 0)
        
        # 기본 포맷 테스트
        assert format_datetime(dt) == "2023-05-15 10:30:00"
        
        # 커스텀 포맷 테스트
        assert format_datetime(dt, "%Y/%m/%d") == "2023/05/15"
        assert format_datetime(dt, "%H:%M") == "10:30"
        assert format_datetime(dt, "%Y년 %m월 %d일") == "2023년 05월 15일"
    
    def test_parse_datetime(self):
        """문자열을 datetime으로 파싱하는 함수 테스트"""
        # 기본 포맷 테스트
        dt_str = "2023-05-15 10:30:00"
        expected = datetime(2023, 5, 15, 10, 30, 0)
        assert parse_datetime(dt_str) == expected
        
        # 커스텀 포맷 테스트
        dt_str_custom = "2023/05/15"
        expected_custom = datetime(2023, 5, 15, 0, 0, 0)
        assert parse_datetime(dt_str_custom, "%Y/%m/%d") == expected_custom
        
        # 유효하지 않은 형식 테스트
        with pytest.raises(ValueError):
            parse_datetime("2023-05-15", "%Y/%m/%d")
    
    @freeze_time("2023-05-15 10:30:00")
    def test_get_utc_now(self):
        """현재 UTC 시간 조회 함수 테스트"""
        # freezegun을 사용하여 시간 고정
        now = get_utc_now()
        
        # 날짜 및 시간 검증
        assert now.year == 2023
        assert now.month == 5
        assert now.day == 15
        assert now.hour == 10
        assert now.minute == 30
        assert now.second == 0
        
        # 타임존 검증
        assert now.tzinfo == timezone.utc
    
    def test_add_time(self):
        """시간 추가 함수 테스트"""
        base_dt = datetime(2023, 5, 15, 10, 30, 0)
        
        # 일 추가 테스트
        result = add_time(base_dt, days=2)
        assert result == datetime(2023, 5, 17, 10, 30, 0)
        
        # 시간 추가 테스트
        result = add_time(base_dt, hours=3)
        assert result == datetime(2023, 5, 15, 13, 30, 0)
        
        # 분 추가 테스트
        result = add_time(base_dt, minutes=45)
        assert result == datetime(2023, 5, 15, 11, 15, 0)
        
        # 초 추가 테스트
        result = add_time(base_dt, seconds=30)
        assert result == datetime(2023, 5, 15, 10, 30, 30)
        
        # 복합 테스트
        result = add_time(base_dt, days=1, hours=2, minutes=15, seconds=10)
        assert result == datetime(2023, 5, 16, 12, 45, 10)
        
        # 음수값 테스트
        result = add_time(base_dt, days=-1, hours=-2)
        assert result == datetime(2023, 5, 14, 8, 30, 0)