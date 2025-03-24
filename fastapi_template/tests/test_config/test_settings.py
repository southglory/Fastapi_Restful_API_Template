"""
# File: tests/test_config/test_settings.py
# Description: Settings 클래스 테스트
"""

import os
import pytest
from app.common.config.settings import Settings


@pytest.fixture
def env_vars_setup():
    """테스트 전후로 환경 변수 백업 및 복원"""
    # 기존 환경 변수 백업
    original_env = os.environ.copy()
    yield
    # 테스트 후 환경 변수 복원
    os.environ.clear()
    os.environ.update(original_env)


def test_settings_load_from_env(env_vars_setup):
    """환경 변수에서 설정이 로드되는지 테스트"""
    # 환경 변수 설정
    os.environ["APP_NAME"] = "테스트앱"
    os.environ["DEBUG"] = "True"
    os.environ["API_PREFIX"] = "/api/v2"
    
    # 설정 로드
    settings = Settings()
    
    # 설정값 검증
    assert settings.app_name == "테스트앱"
    assert settings.debug is True
    assert settings.api_prefix == "/api/v2"


def test_settings_default_values():
    """기존 설정값 확인"""
    # 현재 설정 로드
    settings = Settings()
    
    # 현재 설정 출력
    print(f"현재 설정값: {settings}")
    
    # 설정값이 유효한지 확인
    assert isinstance(settings.app_name, str)
    assert isinstance(settings.debug, bool)
    assert isinstance(settings.api_prefix, str)
    assert isinstance(settings.log_level, str)
    assert isinstance(settings.secret_key, str)
    assert isinstance(settings.access_token_expire_minutes, int)
    assert isinstance(settings.refresh_token_expire_days, int)


def test_settings_case_insensitive(env_vars_setup):
    """대소문자 구분 없이 환경 변수가 로드되는지 테스트"""
    # 대문자 환경 변수 설정
    os.environ["APP_NAME"] = "대문자 테스트"
    
    settings = Settings()
    assert settings.app_name == "대문자 테스트"
    
    # 소문자 환경 변수도 인식되는지 확인
    os.environ.clear()
    os.environ["app_name"] = "소문자 테스트"
    
    settings = Settings()
    assert settings.app_name == "소문자 테스트" 