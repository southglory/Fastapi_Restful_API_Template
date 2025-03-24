"""
# File: tests/test_config/test_environment_settings.py
# Description: 환경별 설정 테스트
"""

import os
import pytest
import json
from unittest import mock
from functools import lru_cache

# ValidationError 예외 임포트
from app.common.config import ValidationError, EnvironmentType
from app.common.config.settings import (
    Settings, DevSettings, TstSettings, ProdSettings, get_settings
)


# @pytest.fixture 데코레이터를 통해 테스트 전후 환경을 설정하고 정리합니다.
@pytest.fixture
def env_setup():
    """테스트 실행 전후에 환경 변수 상태를 저장하고 복원합니다."""
    # 기존 환경 변수 백업
    original_env = os.environ.copy()
    
    # 테스트에 영향을 줄 수 있는 환경 변수 제거
    for key in list(os.environ.keys()):
        if key.startswith(("REDIS_", "DATABASE_", "ENVIRONMENT")):
            os.environ.pop(key, None)
    
    yield  # 테스트 실행
    
    # 테스트 후 원래 환경 변수로 복원
    os.environ.clear()
    os.environ.update(original_env)


def test_environment_mocking():
    """환경 변수를 통한 환경 설정 클래스 테스트"""
    # 개발 환경 테스트
    settings_dev = DevSettings()
    assert settings_dev.ENVIRONMENT == EnvironmentType.DEVELOPMENT
    assert settings_dev.DEBUG is True
    
    # 테스트 환경 테스트
    settings_test = TstSettings()
    assert settings_test.ENVIRONMENT == EnvironmentType.TESTING
    assert isinstance(settings_test.DATABASE_URL, str)
    
    # 프로덕션 환경 테스트 (필수 값 제공)
    settings_prod = ProdSettings(
        SECRET_KEY="테스트용_프로덕션_시크릿키",
        DATABASE_URL="postgresql://user:pass@localhost/db",
        CORS_ORIGINS="https://example.com"
    )
    assert settings_prod.ENVIRONMENT == EnvironmentType.PRODUCTION
    assert settings_prod.DEBUG is False


def test_settings_get_mock():
    """get_settings 함수 테스트"""
    # 캐시 초기화
    get_settings.cache_clear()
    
    # 개발 환경 테스트
    with mock.patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        settings = get_settings()
        assert settings.ENVIRONMENT == EnvironmentType.DEVELOPMENT
        assert isinstance(settings, DevSettings)
    
    # 캐시 초기화
    get_settings.cache_clear()
    
    # 테스트 환경 테스트
    with mock.patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
        settings = get_settings()
        assert settings.ENVIRONMENT == EnvironmentType.TESTING
        assert isinstance(settings, TstSettings)
    
    # 캐시 초기화
    get_settings.cache_clear()
    
    # 프로덕션 환경 테스트
    with mock.patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "test_secure_key",
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
        "CORS_ORIGINS": "https://example.com"
    }):
        settings = get_settings()
        assert settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        assert isinstance(settings, ProdSettings)


def test_environment_types():
    """환경 타입 열거형 테스트"""
    # 환경 타입 값 검증
    assert EnvironmentType.DEVELOPMENT == "development"
    assert EnvironmentType.TESTING == "testing"
    assert EnvironmentType.PRODUCTION == "production"
    
    # 문자열에서 환경 타입으로 변환
    assert EnvironmentType("development") == EnvironmentType.DEVELOPMENT
    assert EnvironmentType("testing") == EnvironmentType.TESTING
    assert EnvironmentType("production") == EnvironmentType.PRODUCTION 