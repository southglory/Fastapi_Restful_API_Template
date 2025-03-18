"""
# File: fastapi_template/app/common/config/settings.py
# Description: 애플리케이션 설정 관리
"""

import json
from typing import List, Union
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 앱 설정
    PROJECT_NAME: str = "FastAPI Template"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # CORS 설정
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_ECHO_LOG: bool = False

    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL: int = 3600  # 기본 캐시 만료 시간(초)

    # JWT 설정
    SECRET_KEY: str = "dev-secret-key-for-testing"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    @property
    def redis_url(self) -> str:
        """Redis 연결 URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def database_url_async(self) -> str:
        """비동기 데이터베이스 URL"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


# 기본 설정 인스턴스 생성
settings = Settings()


# 개발 환경 설정
class DevSettings(Settings):
    """개발 환경 설정"""

    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"

    model_config = SettingsConfigDict(
        env_file=".env.dev", env_file_encoding="utf-8", case_sensitive=True
    )


# 개발 환경 설정 인스턴스
dev_settings = DevSettings()
