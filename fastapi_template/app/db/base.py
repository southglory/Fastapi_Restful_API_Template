"""
# File: fastapi_template/app/db/base.py
# Description: SQLAlchemy 데이터베이스 기본 설정
# - Base 클래스 정의
# - 데이터베이스 엔진 설정
# - 모델 메타데이터 관리
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
