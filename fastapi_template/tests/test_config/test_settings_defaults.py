"""
# File: tests/test_config/test_settings_defaults.py
# Description: 설정 기본값 테스트
"""

import os
import pytest
from app.common.config.settings import Settings


@pytest.fixture
def clear_env_vars():
    """테스트에 관련된 환경 변수 제거"""
    env_vars = ["PROJECT_NAME", "DEBUG", "API_V1_STR", "LOG_LEVEL", "SECRET_KEY", "DATABASE_URL"]
    original_values = {}
    
    # 기존 값 저장 및 제거
    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # 원래 값 복원
    for var, value in original_values.items():
        os.environ[var] = value


def test_settings_default_values(clear_env_vars):
    """환경 변수 없이 기본값 테스트"""
    # 환경 변수 없이 기본값 테스트
    settings = Settings()
    
    # 설정 출력
    print(f"설정 확인: {settings}")
    
    # 타입 검증 (값 자체는 환경에 따라 다를 수 있음)
    assert isinstance(settings.PROJECT_NAME, str)
    assert isinstance(settings.DEBUG, bool)
    assert isinstance(settings.API_V1_STR, str)
    assert isinstance(settings.LOG_LEVEL, str)
    assert isinstance(settings.SECRET_KEY, str)
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(settings.REFRESH_TOKEN_EXPIRE_DAYS, int)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7


def test_settings_override_default(clear_env_vars):
    """기본값 일부만 오버라이드하는 테스트"""
    # 일부 설정만 환경 변수로 설정
    os.environ["PROJECT_NAME"] = "오버라이드 테스트"
    os.environ["DEBUG"] = "True"
    
    settings = Settings()
    
    # 오버라이드된 값과 기본값 검증
    assert settings.PROJECT_NAME == "오버라이드 테스트"  # 오버라이드됨
    assert settings.DEBUG is True  # 오버라이드됨
    assert isinstance(settings.API_V1_STR, str)  # 값은 환경에 따라 다를 수 있음
    assert isinstance(settings.LOG_LEVEL, str)  # 값은 환경에 따라 다를 수 있음
    

def test_settings_boolean_conversion(clear_env_vars):
    """불리언 값 변환 테스트"""
    # 다양한 불리언 값 테스트
    test_cases = [
        ("True", True),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("False", False),
        ("false", False),
        ("0", False),
        ("no", False),
    ]
    
    for env_value, expected_value in test_cases:
        os.environ["DEBUG"] = env_value
        settings = Settings()
        assert settings.DEBUG is expected_value, f"환경 변수 DEBUG={env_value}일 때 settings.DEBUG가 {expected_value}여야 함" 