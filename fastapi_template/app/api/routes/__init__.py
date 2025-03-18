"""
# File: fastapi_template/app/api/routes/__init__.py
# Description: API 라우트 패키지 초기화
# - 라우터 모듈 export
"""

from app.api.routes.users import router as users_router
from app.api.routes.items import router as items_router
from app.api.routes.auth import router as auth_router

__all__ = ["users_router", "items_router", "auth_router"]
