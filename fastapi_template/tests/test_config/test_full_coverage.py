"""
# File: tests/test_config/test_full_coverage.py
# Description: 설정 모듈 전체 커버리지를 위한 추가 테스트
"""

import os
import pytest
import logging
from unittest import mock
from fastapi_template.app.common.config.config_settings import (
    Settings, DevSettings, ProdSettings, TstSettings,
    EnvironmentType, ValidationError, load_config_from_file, get_settings
)

# 로그 핸들러 설정
logger = logging.getLogger()
handler = logging.StreamHandler()
logger.addHandler(handler)


def test_dotenv_import_error():
    """python-dotenv 가져오기 오류 처리 테스트"""
    # ImportError 시뮬레이션
    def import_error(*args, **kwargs):
        raise ImportError("모의 ImportError")
    
    # dotenv 모듈 가져오기 실패 테스트
    with mock.patch('builtins.__import__', side_effect=import_error):
        with mock.patch('os.path.exists', return_value=True):
            # 파일은 존재하지만 dotenv를 가져올 수 없음
            result = load_config_from_file(".env.test")
            assert result == {}


def test_dotenv_exception():
    """dotenv 파일 로드 중 예외 처리 테스트"""
    # dotenv가 존재하지만 예외 발생 시뮬레이션
    with mock.patch('dotenv.dotenv_values', side_effect=Exception("모의 예외")):
        with mock.patch('os.path.exists', return_value=True):
            with mock.patch('app.common.config.settings.logging.error') as mock_log:
                result = load_config_from_file(".env.test")
                assert result == {}
                assert mock_log.called


def test_settings_utility_methods():
    """설정 유틸리티 메서드 테스트"""
    settings = Settings()
    
    # 로깅 호출 확인을 위한 패치
    with mock.patch('app.common.config.settings.logging.debug') as mock_log:
        # 데이터베이스 설정 반환 테스트
        db_settings = settings.get_db_settings()
        assert "url" in db_settings
        assert "echo" in db_settings
        mock_log.assert_called_once()
        
        # Redis 설정 반환 테스트
        mock_log.reset_mock()
        redis_settings = settings.get_redis_settings()
        assert "host" in redis_settings
        assert "port" in redis_settings
        mock_log.assert_called_once()
        
        # 설정 딕셔너리 반환 테스트
        mock_log.reset_mock()
        config_dict = settings.dict_config()
        assert "PROJECT_NAME" in config_dict
        assert "DATABASE_URL" in config_dict
        mock_log.assert_called_once()


def test_prod_settings_validation_all():
    """프로덕션 설정 유효성 검사 통합 테스트"""
    original_env = os.environ.copy()
    
    try:
        # 환경 변수 초기화
        os.environ.clear()
        os.environ["ENVIRONMENT"] = "production"
        
        # SECRET_KEY 검증
        with pytest.raises(ValidationError) as exc_info:
            ProdSettings()
        assert "프로덕션 환경에서는 안전한 SECRET_KEY가 필요합니다" in str(exc_info.value)
        
        # 안전한 SECRET_KEY 설정
        os.environ["SECRET_KEY"] = "안전한_프로덕션_키"
        
        # DATABASE_URL 검증
        with pytest.raises(ValidationError) as exc_info:
            ProdSettings()
        assert "프로덕션 환경에서는 DATABASE_URL이 필요합니다" in str(exc_info.value)
        
        # DATABASE_URL 설정
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
        
        # CORS_ORIGINS 검증
        with pytest.raises(ValidationError) as exc_info:
            ProdSettings()
        assert "프로덕션 환경에서는 CORS_ORIGINS에 구체적인 출처를 지정해야 합니다" in str(exc_info.value)
        
        # CORS_ORIGINS 설정
        os.environ["CORS_ORIGINS"] = "https://example.com"
        
        # 이제 성공적으로 생성되어야 함
        settings = ProdSettings()
        assert settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        assert settings.DEBUG is False
        assert settings.RELOAD is False
        assert settings.ENABLE_PROFILER is False
        
    finally:
        # 테스트 후 환경 변수 복원
        os.environ.clear()
        os.environ.update(original_env)


def test_get_settings_testing_environment():
    """테스트 환경 설정 가져오기 테스트"""
    original_env = os.environ.copy()
    
    try:
        # 환경 변수 설정
        os.environ.clear()
        os.environ["ENVIRONMENT"] = "testing"
        
        # 함수 캐시 초기화
        get_settings.cache_clear()
        
        # 설정 가져오기
        settings = get_settings()
        
        # 테스트 환경 설정 확인
        assert settings.ENVIRONMENT == EnvironmentType.TESTING
        assert isinstance(settings, TstSettings)
        
    finally:
        # 테스트 후 환경 변수 복원
        os.environ.clear()
        os.environ.update(original_env)


def test_get_settings_production_environment():
    """프로덕션 환경 설정 가져오기 테스트"""
    original_env = os.environ.copy()
    
    try:
        # 환경 변수 설정
        os.environ.clear()
        os.environ["ENVIRONMENT"] = "production"
        os.environ["SECRET_KEY"] = "안전한_키"
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
        os.environ["CORS_ORIGINS"] = "https://example.com"
        
        # 함수 캐시 초기화
        get_settings.cache_clear()
        
        # 설정 가져오기
        settings = get_settings()
        
        # 프로덕션 환경 설정 확인
        assert settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        assert isinstance(settings, ProdSettings)
        
    finally:
        # 테스트 후 환경 변수 복원
        os.environ.clear()
        os.environ.update(original_env)


def test_get_settings_default_environment():
    """기본(개발) 환경 설정 가져오기 테스트"""
    original_env = os.environ.copy()
    
    try:
        # 환경 변수 초기화
        os.environ.clear()
        
        # 함수 캐시 초기화 (lru_cache로 캐시된 함수 초기화)
        get_settings.cache_clear()
        
        # 설정 가져오기
        settings = get_settings()
        
        # 개발 환경 설정 확인
        assert settings.ENVIRONMENT == EnvironmentType.DEVELOPMENT
        assert isinstance(settings, DevSettings)
        
    finally:
        # 테스트 후 환경 변수 복원
        os.environ.clear()
        os.environ.update(original_env)


def test_testing_database_url_none():
    """테스트 환경에서 DATABASE_URL이 None인 경우 테스트"""
    # Settings 객체를 직접 생성
    settings = Settings()
    
    # DATABASE_URL을 명시적으로 None으로 설정
    settings.DATABASE_URL = None
    
    # ENVIRONMENT를 TESTING으로 설정
    settings.ENVIRONMENT = EnvironmentType.TESTING
    
    # validate_settings_by_environment 메서드를 직접 호출
    settings = settings.validate_settings_by_environment()
    
    # 기본값이 올바르게 설정되었는지 확인
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    
    # 로깅 확인
    with mock.patch('app.common.config.settings.logging.info') as mock_log:
        # 다시 초기화하고 검증
        settings = Settings()
        settings.DATABASE_URL = None
        settings.ENVIRONMENT = EnvironmentType.TESTING
        settings = settings.validate_settings_by_environment()
        
        assert settings.DATABASE_URL == "sqlite:///./test.db"
        mock_log.assert_called_with("테스트 환경에서 기본 데이터베이스로 SQLite를 사용합니다: sqlite:///./test.db")