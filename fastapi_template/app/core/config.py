"""
# File: fastapi_template/app/core/config.py
# Description: 애플리케이션 환경 설정 관리
# - 환경 변수 로드 및 검증
# - 데이터베이스 연결 설정
# - JWT 설정
# - 기타 앱 설정 값
"""

import os
from typing import List, Union, Dict, Any

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI RESTful API Template"
    
    # CORS 설정
    CORS_ORIGINS: List[str] = []
    
    # 데이터베이스 설정
    DATABASE_URL: str
    DB_ECHO_LOG: bool = False
    
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 기타 설정
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 설정 인스턴스 생성
settings = Settings()

# CORS_ORIGINS를 문자열에서 리스트로 변환
if settings.CORS_ORIGINS and isinstance(settings.CORS_ORIGINS, str):
    import json
    settings.CORS_ORIGINS = json.loads(settings.CORS_ORIGINS)

