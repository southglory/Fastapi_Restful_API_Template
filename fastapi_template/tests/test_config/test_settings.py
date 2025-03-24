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
    os.environ["PROJECT_NAME"] = "테스트앱"
    os.environ["DEBUG"] = "True"
    os.environ["API_V1_STR"] = "/api/v2"
    
    # 설정 로드
    settings = Settings()
    
    # 설정값 검증
    assert settings.PROJECT_NAME == "테스트앱"
    assert settings.DEBUG is True
    assert settings.API_V1_STR == "/api/v2"


def test_settings_default_values():
    """기존 설정값 확인"""
    # 현재 설정 로드
    settings = Settings()
    
    # 현재 설정 출력
    print(f"현재 설정값: {settings}")
    
    # 설정값이 유효한지 확인
    assert isinstance(settings.PROJECT_NAME, str)
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.API_V1_STR, str)
    assert isinstance(settings.LOG_LEVEL, str)
    assert isinstance(settings.SECRET_KEY, str)
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(settings.REFRESH_TOKEN_EXPIRE_DAYS, int)


def test_settings_case_sensitivity(env_vars_setup):
    """대소문자 구분 테스트"""
    # 대문자 환경 변수 설정
    os.environ["PROJECT_NAME"] = "대문자 테스트"
    
    settings = Settings()
    assert settings.PROJECT_NAME == "대문자 테스트"
    
    # 소문자 환경 변수 설정
    os.environ.clear()
    os.environ["project_name"] = "소문자 테스트"
    
    settings = Settings()
    # 환경 변수 대소문자를 구분하지 않고 인식하는지 확인
    assert settings.PROJECT_NAME == "소문자 테스트"  # Pydantic이 기본적으로 대소문자 구분 없이 환경 변수를 인식함 