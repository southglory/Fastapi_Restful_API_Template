"""
# File: fastapi_template/app/db/base.py
# Description: 호환성을 위한 Base 클래스 리다이렉트
"""

# common 모듈로 리다이렉트
from app.common.database import Base, BaseModel, TimeStampMixin

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
