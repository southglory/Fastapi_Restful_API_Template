"""
# File: fastapi_template/app/core/config.py
# Description: 애플리케이션 환경 설정 관리
# - 환경 변수 로드 및 검증
# - 데이터베이스 연결 설정
# - JWT 설정
# - 기타 앱 설정 값
"""

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    Field,
    PostgresDsn,
    field_validator
)
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    API_V1_STR: str = Field("/api/v1", description="API 접두사")
    PROJECT_NAME: str = Field("FastAPI RESTful API Template", description="프로젝트 이름")
    
    # CORS 설정
    CORS_ORIGINS: Union[str, List[str]] = Field(
        ["http://localhost:3000", "http://localhost:8000"],
        description="CORS 허용 출처 (문자열 또는 목록)"
    )
    
    # 데이터베이스 설정
    DATABASE_URL: str = Field(..., description="데이터베이스 연결 문자열")
    DB_ECHO_LOG: bool = Field(False, description="SQL 쿼리 로깅 활성화 여부")
    
    # JWT 설정
    SECRET_KEY: str = Field(..., description="JWT 서명 키")
    ALGORITHM: str = Field("HS256", description="JWT 알고리즘")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="액세스 토큰 만료 시간(분)")
    
    # Redis 설정
    REDIS_HOST: str = Field("redis", description="Redis 호스트")
    REDIS_PORT: int = Field(6379, description="Redis 포트")
    REDIS_DB: int = Field(0, description="Redis DB 번호")
    REDIS_TTL: int = Field(3600, description="기본 캐시 만료 시간(초)")
    
    # 기타 설정
    DEBUG: bool = Field(False, description="디버그 모드 활성화 여부")
    
    # 환경 변수 파일 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """CORS_ORIGINS가 문자열인 경우 JSON 목록으로 파싱"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except ValueError:
                # 단일 문자열인 경우 1개 항목 목록으로 반환
                return [v]
        return v


# 설정 인스턴스 생성
settings = Settings()

