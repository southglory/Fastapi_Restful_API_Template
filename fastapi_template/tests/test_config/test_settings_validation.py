"""
# File: tests/test_config/test_settings_validation.py
# Description: 설정 유효성 검사 테스트
"""

import os
import pytest
from app.common.config.settings import Settings, ValidationError, EnvironmentType, ProdSettings


@pytest.fixture
def env_setup():
    """테스트 전후로 환경 변수 백업 및 복원"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_database_url_validation(env_setup):
    """데이터베이스 URL 유효성 검사 테스트"""
    # 올바른 DB URL 설정
    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/dbname"
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://user:password@localhost:5432/dbname"
    
    # SQLite URL 설정
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    settings = Settings()
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    
    # MySQL URL 설정
    os.environ["DATABASE_URL"] = "mysql://user:password@localhost:3306/dbname"
    settings = Settings()
    assert settings.DATABASE_URL == "mysql://user:password@localhost:3306/dbname"
    
    # 잘못된 DB URL 설정
    os.environ["DATABASE_URL"] = "invalid-url"
    with pytest.raises(ValidationError):
        settings = Settings()


def test_database_url_none(env_setup):
    """데이터베이스 URL이 None인 경우 테스트"""
    # Settings 객체를 직접 생성
    settings = Settings()
    
    # DATABASE_URL을 명시적으로 None으로 설정
    settings.DATABASE_URL = None
    
    # ENVIRONMENT를 DEVELOPMENT로 설정
    settings.ENVIRONMENT = EnvironmentType.DEVELOPMENT
    
    # validate_settings_by_environment 메서드를 직접 호출
    settings = settings.validate_settings_by_environment()
    
    # 개발 환경에서는 DATABASE_URL이 None일 때 SQLite 기본값으로 설정됨
    assert settings.DATABASE_URL is not None
    assert settings.DATABASE_URL == "sqlite:///./dev.db"
    assert settings.DATABASE_URL.startswith("sqlite:///")


def test_production_settings_validation(env_setup):
    """프로덕션 환경 설정 유효성 검사 테스트"""
    # 환경 변수 설정 - 모든 환경 변수를 명확하게 초기화
    os.environ["ENVIRONMENT"] = "production"
    os.environ["SECRET_KEY"] = "개발용_시크릿_키_실제_운영에서는_변경하세요"  # 기본 시크릿 키
    
    # DATABASE_URL 제거 (다른 테스트에서 설정한 값을 제거)
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    # CORS_ORIGINS 초기화
    os.environ["CORS_ORIGINS"] = "*"
    
    # 기본 시크릿 키로 프로덕션 환경 설정 시도 - 실패해야 함
    with pytest.raises(ValidationError) as exc:
        ProdSettings()
    
    error_message = str(exc.value)
    assert "프로덕션 환경에서는 안전한 SECRET_KEY가 필요합니다" in error_message
    
    # 안전한 시크릿 키 설정
    os.environ["SECRET_KEY"] = "custom_test_secret_key_for_production" 
    
    # DATABASE_URL이 없는 경우 검증 - 실패해야 함
    # 확실하게 DATABASE_URL 제거
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
        
    with pytest.raises(ValidationError) as exc:
        ProdSettings()
    
    error_message = str(exc.value)
    assert "프로덕션 환경에서는 DATABASE_URL이 필요합니다" in error_message
    
    # DATABASE_URL 설정
    os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/proddb"
    
    # CORS_ORIGINS가 "*"인 상태로 프로덕션 환경 설정 시도 - 실패해야 함
    with pytest.raises(ValidationError) as exc:
        ProdSettings()
    
    error_message = str(exc.value)
    assert "프로덕션 환경에서는 CORS_ORIGINS에 구체적인 출처를 지정해야 합니다" in error_message
    
    # 올바른 CORS_ORIGINS 설정
    os.environ["CORS_ORIGINS"] = "https://example.com,https://api.example.com"
    
    # 이제 모든 설정이 올바르므로 성공해야 함
    prod_settings = ProdSettings()
    assert prod_settings.ENVIRONMENT == EnvironmentType.PRODUCTION
    assert prod_settings.SECRET_KEY == "custom_test_secret_key_for_production"
    assert prod_settings.DATABASE_URL == "postgresql://user:password@localhost:5432/proddb"
    assert "*" not in prod_settings.CORS_ORIGINS 