"""
# File: fastapi_template/app/db/models/__init__.py
# Description: 데이터베이스 모델 패키지 초기화
# - 모든 모델 import
# - Base 클래스 export
"""

from app.db.models.user import User
from app.db.models.item import Item
from app.common.database import Base

# 모든 모델을 여기서 import하여 Alembic이 자동으로 감지할 수 있게 함

__all__ = ["User", "Item", "Base"]
