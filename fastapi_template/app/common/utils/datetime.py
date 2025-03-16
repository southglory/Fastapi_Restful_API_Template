"""
# File: fastapi_template/app/common/utils/datetime.py
# Description: 날짜/시간 관련 유틸리티 함수
"""

from datetime import datetime, timedelta, timezone


def get_utc_now() -> datetime:
    """
    현재 UTC 시간 반환
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    datetime 객체를 포맷에 맞춰 문자열로 변환
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    문자열을 datetime 객체로 파싱
    """
    return datetime.strptime(dt_str, format_str)


def add_time(dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
    """
    주어진 datetime에 시간을 추가
    """
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return dt + delta 