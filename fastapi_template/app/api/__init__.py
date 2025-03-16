"""
# File: fastapi_template/app/api/__init__.py
# Description: API 패키지 초기화
# - API 버전 관리
# - 라우터 통합
"""

from fastapi import APIRouter
from app.api.routes import users, items, auth

api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"]) 