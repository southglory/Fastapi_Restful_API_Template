"""
# File: fastapi_template/app/common/monitoring/__init__.py
# Description: 모니터링 관련 모듈 패키지
"""

from app.common.monitoring.health_check import router as health_check_router

__all__ = ["health_check_router"]
