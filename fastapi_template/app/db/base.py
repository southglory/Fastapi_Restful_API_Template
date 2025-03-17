"""
# File: fastapi_template/app/db/base.py
# Description: 호환성을 위한 Base 클래스 리다이렉트
"""

# common 모듈로 리다이렉트
from app.common.database.base import Base, BaseModel, TimeStampMixin

# 이 파일은 이전 import 경로와의 호환성을 위해 유지됩니다.
# 새로운 코드에서는 app.common.database.base를 직접 사용하는 것을 권장합니다.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
