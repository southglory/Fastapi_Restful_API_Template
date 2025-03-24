"""
# File: app/common/config/dev_settings.py
# Description: 개발 환경용 애플리케이션 설정
"""

from typing import Dict, Any
from pydantic_settings import BaseSettings


class DevSettings(BaseSettings):
    """
    개발 환경용 애플리케이션 설정을 관리하는 클래스
    """
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "FastAPI 템플릿 (개발)"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # 개발 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_ECHO_LOG: bool = True
    
    # 레디스 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # 보안 설정
    SECRET_KEY: str = "개발용_시크릿_키_실제_운영에서는_변경하세요"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 개발 환경에서는 더 긴 만료 시간
    
    # 로깅 설정
    LOG_LEVEL: str = "DEBUG"
    
    # CORS 설정
    CORS_ORIGINS: list = ["*"]
    
    # 개발 도구 활성화
    ENABLE_DOCS: bool = True
    ENABLE_PROFILER: bool = True
    
    model_config = {
        "env_file": ".env.dev",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
    
    def dict_config(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


# 개발 환경 설정 인스턴스
dev_settings = DevSettings() 