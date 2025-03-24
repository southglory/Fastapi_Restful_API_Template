"""
# File: app/common/config/settings.py
# Description: 애플리케이션 설정을 관리하는 모듈
"""

import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
# 참고: model_validator는 현재 명시적으로 사용되지 않지만, 향후 모델 수준의 유효성 검사를 위해 가져왔습니다.
# 현재는 field_validator와 별도의 validate_required 메서드로 유효성 검사를 수행합니다.
# model_validator를 사용하면 아래 validate_required 메서드를 @model_validator 데코레이터로
# 대체하여 모델 초기화 시 자동으로 검증할 수 있습니다.


class ValidationError(Exception):
    """설정 유효성 검사 오류를 나타내는 예외 클래스"""
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
    except Exception:
        # 파일 로드 오류는 무시하고 빈 설정 반환
        return {}


class Settings(BaseSettings):
    """
    애플리케이션 설정을 관리하는 클래스
    """
    # 애플리케이션 기본 설정
    app_name: str = "FastAPI 템플릿"
    debug: bool = False
    api_prefix: str = "/api"
    log_level: str = "INFO"
    
    # 보안 설정
    secret_key: str = "개발용_시크릿_키_실제_운영에서는_변경하세요"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # 데이터베이스 설정
    database_url: Optional[str] = None
    
    # CORS 설정
    allowed_origins: str = "*"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # 추가 필드 허용
    }
    
    @field_validator('database_url')
    def validate_database_url(cls, v):
        """데이터베이스 URL이 유효한지 검증합니다."""
        if v is None:
            return v
        
        # 데이터베이스 URL 유효성 검사
        # 실제로는 여기서 URL 형식 검사 또는 드라이버 지원 여부 확인 등이 필요
        valid_prefixes = ['postgresql://', 'mysql://', 'sqlite://']
        
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(f"지원하지 않는 데이터베이스 URL 형식: {v}")
        
        return v
        
    # validators 모듈과 통합 예시:
    # @field_validator('app_name')
    # def validate_app_name(cls, v):
    #     """애플리케이션 이름이 유효한지 검증합니다."""
    #     from app.common.validators.string_validators import validate_string_length
    #     
    #     # 문자열 길이 검증
    #     if not validate_string_length(v, min_length=2, max_length=50):
    #         raise ValidationError("애플리케이션 이름은 2-50자 사이여야 합니다")
    #     
    #     # 특수문자 검증 (순수 Python 로직)
    #     if any(char in r'!@#$%^&*()+={}[]|\:;"<>,?/' for char in v):
    #         raise ValidationError("애플리케이션 이름에 특수문자를 포함할 수 없습니다")
    #     
    #     return v
    
    # validators 모듈 활용 예시 (API URL 검증):
    # @field_validator('api_prefix')
    # def validate_api_prefix(cls, v):
    #     """API 접두사가 유효한지 검증합니다."""
    #     if not v.startswith('/'):
    #         v = f"/{v}"  # 슬래시로 시작하지 않으면 추가
    #     
    #     # URL 경로 검증을 위해 validators 모듈 활용
    #     from app.common.validators.string_validators import validate_url
    #     test_url = f"https://example.com{v}"
    #     
    #     if not validate_url(test_url):
    #         raise ValidationError(f"유효하지 않은 API 접두사입니다: {v}")
    #     
    #     return v
    
    def validate_required(self):
        """필수 설정이 존재하는지 검증합니다."""
        required_settings = [
            ('secret_key', "SECRET_KEY is required"),
            ('database_url', "DATABASE_URL is required for production"),
        ]
        
        for field, error_message in required_settings:
            value = getattr(self, field, None)
            if not value or value == getattr(Settings(), field):
                raise ValidationError(error_message)
        
    # 고급 유효성 검사를 위한 validators 모듈 통합 예시:
    # def validate_security_settings(self):
    #     """보안 관련 설정을 종합적으로 검증합니다."""
    #     from app.common.validators.string_validators import validate_password_strength
    #     
    #     # 시크릿 키 강도 검증
    #     valid, message = validate_password_strength(
    #         self.secret_key,
    #         min_length=32,
    #         require_uppercase=True,
    #         require_lowercase=True,
    #         require_digits=True,
    #         require_special_chars=True
    #     )
    #     
    #     if not valid:
    #         raise ValidationError(f"보안 취약한 시크릿 키입니다: {message}")
    
    # model_validator를 사용한 대체 구현 예시:
    # @model_validator(mode='after')
    # def validate_required_settings(self) -> 'Settings':
    #     required_settings = [
    #         ('secret_key', "SECRET_KEY is required"),
    #         ('database_url', "DATABASE_URL is required for production"),
    #     ]
    #     
    #     for field, error_message in required_settings:
    #         value = getattr(self, field, None)
    #         if not value or value == getattr(Settings(), field):
    #             raise ValueError(error_message)
    #     
    #     return self


# 애플리케이션 설정 인스턴스
settings = Settings()
