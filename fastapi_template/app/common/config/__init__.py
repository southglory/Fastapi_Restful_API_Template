"""
# File: fastapi_template/app/common/config/__init__.py
# Description: 설정 모듈 초기화
"""

from app.common.config.settings import settings
from app.common.config.dev_settings import dev_settings

__all__ = ["settings", "dev_settings"]
