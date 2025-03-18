"""
# File: fastapi_template/app/api/dependencies.py
# Description: FastAPI 의존성 주입 관리
# - 이 파일은 하위 호환성을 위해 유지되며, 실제 구현은 common/dependencies로 이동됨
"""

from app.common.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    oauth2_scheme,
)

# API 고유의 의존성은 여기에 추가할 수 있음

# 하위 호환성을 위해 모든 의존성을 다시 내보냄
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "oauth2_scheme",
]
