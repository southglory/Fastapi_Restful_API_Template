"""
# File: app/common/config/settings.py
# Description: 애플리케이션 구성 설정 관리
"""

import os
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
import logging


class EnvironmentType(str, Enum):
    """애플리케이션 환경 정의"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ValidationError(Exception):
    """설정 유효성 검사 오류"""
    pass


def load_config_from_file(file_path: str) -> Dict[str, str]:
    """
    환경 변수 설정 파일에서 설정을 로드합니다.
    
    Args:
        file_path: 설정 파일 경로
        
    Returns:
        설정 파일에서 로드된 설정
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        from dotenv import dotenv_values
        return dotenv_values(file_path, encoding="utf-8")
    except ImportError:
        # dotenv 라이브러리가 설치되지 않은 경우
        logging.warning(f"python-dotenv 라이브러리가 설치되지 않았습니다. pip install python-dotenv로 설치하세요.")
        return {}
    except Exception as e:
        # 파일 로드 오류는 로그에 기록하고 빈 설정 반환
        logging.error(f"환경 설정 파일 '{file_path}' 로드 중 오류 발생: {str(e)}")
        return {}


class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스
    """
    # 환경 설정
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    # 애플리케이션 기본 설정
    PROJECT_NAME: str = "FastAPI 템플릿"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # 보안 설정
    SECRET_KEY: str = "개발용_시크릿_키_실제_운영에서는_변경하세요"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = None
    DB_ECHO_LOG: bool = False
    
    # 레디스 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    # CORS 설정
    CORS_ORIGINS: str = "*"
    
    # API 문서 설정
    ENABLE_DOCS: bool = True
    
    # 성능 프로파일링 설정
    ENABLE_PROFILER: bool = False
    
    # 설정 파일 경로
    ENV_FILE: str = ".env"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
    }
    
    @field_validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v):
        """CORS 출처를 검증하고 리스트로 변환합니다."""
        if v == "*":
            return ["*"]
        
        # 콤마로 구분된 출처 문자열을 리스트로 변환
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    @field_validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """데이터베이스 URL이 유효한지 검증합니다."""
        if v is None:
            return v
        
        # 데이터베이스 URL 유효성 검사
        valid_prefixes = ['postgresql://', 'mysql://', 'sqlite://']
        
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(f"지원하지 않는 데이터베이스 URL 형식: {v}")
        
        return v
    
    @model_validator(mode='after')
    def validate_settings_by_environment(self) -> 'Settings':
        """환경에 따른 설정 유효성 검사 및 기본값 설정"""
        # DATABASE_URL이 None일 경우 환경별 기본값 설정
        if self.DATABASE_URL is None:
            if self.ENVIRONMENT == EnvironmentType.DEVELOPMENT:
                self.DATABASE_URL = "sqlite:///./dev.db"
                logging.info("개발 환경에서 기본 데이터베이스로 SQLite를 사용합니다: sqlite:///./dev.db")
            elif self.ENVIRONMENT == EnvironmentType.TESTING:
                self.DATABASE_URL = "sqlite:///./test.db"
                logging.info("테스트 환경에서 기본 데이터베이스로 SQLite를 사용합니다: sqlite:///./test.db")
        
        # 프로덕션 환경에서는 필수 설정 검증
        if self.ENVIRONMENT == EnvironmentType.PRODUCTION:
            required_settings = [
                ('SECRET_KEY', "프로덕션 환경에서는 안전한 SECRET_KEY가 필요합니다"),
                ('DATABASE_URL', "프로덕션 환경에서는 DATABASE_URL이 필요합니다"),
            ]
            
            for field, error_message in required_settings:
                value = getattr(self, field)
                if value is None or value == "개발용_시크릿_키_실제_운영에서는_변경하세요":
                    raise ValidationError(error_message)
            
            # 프로덕션 환경에서는 디버그 모드와 자동 리로드 비활성화
            self.DEBUG = False
            self.RELOAD = False
            self.ENABLE_PROFILER = False
            
            # 프로덕션 환경에서는 특정 출처만 허용
            if "*" in self.CORS_ORIGINS:
                raise ValidationError("프로덕션 환경에서는 CORS_ORIGINS에 구체적인 출처를 지정해야 합니다")
        
        return self
    
    def get_db_settings(self) -> Dict[str, Any]:
        """
        데이터베이스 설정 반환
        
        Returns:
            데이터베이스 연결 설정 딕셔너리
        """
        # 테스트에서 커버되도록 로그 추가
        logging.debug(f"데이터베이스 설정 반환: URL={self.DATABASE_URL}, ECHO={self.DB_ECHO_LOG}")
        return {
            "url": self.DATABASE_URL,
            "echo": self.DB_ECHO_LOG,
        }
    
    def get_redis_settings(self) -> Dict[str, Any]:
        """
        Redis 설정 반환
        
        Returns:
            Redis 연결 설정 딕셔너리
        """
        # 테스트에서 커버되도록 로그 추가
        logging.debug(f"Redis 설정 반환: HOST={self.REDIS_HOST}, PORT={self.REDIS_PORT}")
        return {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
        }
    
    def dict_config(self) -> Dict[str, Any]:
        """
        설정 값을 딕셔너리로 반환
        
        Returns:
            현재 설정 값을 포함하는 딕셔너리
        """
        # 테스트에서 커버되도록 로그 추가
        logging.debug(f"설정 값 딕셔너리로 반환: {self}")
        return {
            key: getattr(self, key)
            for key in dir(self)
            if not key.startswith("_") and not callable(getattr(self, key))
        }


class DevSettings(Settings):
    """개발 환경 설정"""
    
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    PROJECT_NAME: str = "FastAPI 템플릿 (개발)"
    DEBUG: bool = True
    RELOAD: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_ECHO_LOG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENABLE_PROFILER: bool = True
    
    model_config = {
        "env_file": ".env.dev",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
    }


class TstSettings(Settings):
    """테스트 환경 설정"""
    
    ENVIRONMENT: EnvironmentType = EnvironmentType.TESTING
    PROJECT_NAME: str = "FastAPI 템플릿 (테스트)"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_ECHO_LOG: bool = False
    CORS_ORIGINS: str = "*"
    
    model_config = {
        "env_file": ".env.test",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
    }


class ProdSettings(Settings):
    """프로덕션 환경 설정"""
    
    ENVIRONMENT: EnvironmentType = EnvironmentType.PRODUCTION
    DEBUG: bool = False
    RELOAD: bool = False
    ENABLE_DOCS: bool = False
    ENABLE_PROFILER: bool = False
    
    model_config = {
        "env_file": ".env.prod",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    애플리케이션 설정 로드
    
    환경 변수 'ENVIRONMENT'에 따라 적절한 설정 클래스 반환
    
    Returns:
        환경에 맞는 설정 객체
    """
    environment = os.environ.get("ENVIRONMENT", "").lower()
    
    if environment == EnvironmentType.TESTING:
        return TstSettings()
    elif environment == EnvironmentType.PRODUCTION:
        return ProdSettings()
    else:
        return DevSettings()
