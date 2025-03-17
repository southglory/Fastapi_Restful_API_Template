"""
# File: fastapi_template/app/db/session.py
# Description: 호환성을 위한 세션 관리 함수 리다이렉트
"""

# common 모듈로 리다이렉트
from app.common.database.session import (
    get_db,
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    ASYNC_SQLALCHEMY_DATABASE_URL,
)

# 이 파일은 이전 import 경로와의 호환성을 위해 유지됩니다.
# 새로운 코드에서는 app.common.database.session을 직접 사용하는 것을 권장합니다. 