"""
# File: fastapi_template/app/common/dependencies/__init__.py
# Description: 의존성 주입 모듈 패키지
# - 재사용 가능한 의존성 함수 export
"""

from app.common.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    oauth2_scheme,
)

# 다른 의존성 타입들이 추가될 수 있음
# 예: from app.common.dependencies.rate_limit import rate_limiter

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "oauth2_scheme",
]
