"""
# File: tests/test_config/test_additional_coverage.py
# Description: 추가 코드 커버리지를 위한 테스트
"""

import os
import tempfile
import pytest
from app.common.config.loader import (
    load_env_vars,
    merge_configs,
    get_env_setting
)


def test_load_env_vars_with_prefix():
    """환경 변수 접두사로 필터링하는 테스트"""
    # 테스트 환경 변수 설정
    os.environ["TEST_PREFIX_VAR1"] = "value1"
    os.environ["TEST_PREFIX_VAR2"] = "value2"
    os.environ["OTHER_VAR"] = "value3"
    
    try:
        # 접두사로 필터링
        env_vars = load_env_vars(prefix="TEST_PREFIX_")
        
        # 접두사가 있는 변수만 로드되고, 접두사는 제거됨
        assert "VAR1" in env_vars
        assert "VAR2" in env_vars
        assert "OTHER_VAR" not in env_vars
        assert env_vars["VAR1"] == "value1"
        assert env_vars["VAR2"] == "value2"
    finally:
        # 테스트 환경 변수 삭제
        del os.environ["TEST_PREFIX_VAR1"]
        del os.environ["TEST_PREFIX_VAR2"]
        del os.environ["OTHER_VAR"]


def test_load_env_vars_empty():
    """환경 변수가 없는 경우 테스트"""
    # 특정 환경 변수를 로드 시도 (존재하지 않는 변수)
    result = load_env_vars(var_names=["NON_EXISTENT_VAR1", "NON_EXISTENT_VAR2"])
    
    # 빈 딕셔너리 반환 확인
    assert result == {}


def test_get_env_setting_with_prefix():
    """접두사가 있는 환경 변수 설정 가져오기 테스트"""
    # 테스트 환경 변수 설정
    os.environ["TEST_PREFIX_SETTING"] = "test_value"
    
    try:
        # 접두사와 함께 설정 가져오기
        value = get_env_setting("SETTING", prefix="TEST_PREFIX_")
        
        # 값 검증
        assert value == "test_value"
    finally:
        # 테스트 환경 변수 삭제
        del os.environ["TEST_PREFIX_SETTING"]


def test_get_env_setting_required_error():
    """필수 환경 변수가 없는 경우 테스트"""
    # 존재하지 않는 필수 환경 변수 가져오기 시도
    with pytest.raises(ValueError) as exc:
        get_env_setting("NON_EXISTENT_REQUIRED_VAR", required=True)
    
    # 오류 메시지 검증
    assert "필수 환경 변수가 없습니다" in str(exc.value)


def test_merge_configs_empty():
    """빈 설정 병합 테스트"""
    # 빈 설정 목록으로 병합
    result = merge_configs()
    
    # 빈 딕셔너리 반환 확인
    assert result == {}


def test_merge_configs_single():
    """단일 설정 병합 테스트"""
    # 단일 설정
    config = {"key1": "value1", "key2": "value2"}
    
    # 단일 설정으로 병합
    result = merge_configs(config)
    
    # 원본 설정과 동일 확인 (복사본이므로 동일 객체가 아님)
    assert result == config
    assert result is not config


def test_merge_configs_nested_complex():
    """복잡한 중첩 설정 병합 테스트"""
    # 기본 설정
    base_config = {
        "app": {
            "name": "BaseApp",
            "version": "1.0.0",
            "settings": {
                "debug": True,
                "log_level": "INFO"
            }
        },
        "db": {
            "url": "sqlite:///base.db",
            "options": {
                "echo": False,
                "pool_size": 5
            }
        }
    }
    
    # 오버라이드 설정
    override_config = {
        "app": {
            "name": "OverrideApp",
            "settings": {
                "log_level": "DEBUG",
                "new_setting": "value"
            }
        },
        "db": {
            "options": {
                "pool_size": 10
            }
        },
        "new_section": {
            "key": "value"
        }
    }
    
    # 설정 병합
    result = merge_configs(base_config, override_config)
    
    # 병합 결과 검증
    assert result["app"]["name"] == "OverrideApp"  # 덮어씌워짐
    assert result["app"]["version"] == "1.0.0"  # 유지됨
    assert result["app"]["settings"]["debug"] is True  # 유지됨
    assert result["app"]["settings"]["log_level"] == "DEBUG"  # 덮어씌워짐
    assert result["app"]["settings"]["new_setting"] == "value"  # 추가됨
    assert result["db"]["url"] == "sqlite:///base.db"  # 유지됨
    assert result["db"]["options"]["echo"] is False  # 유지됨
    assert result["db"]["options"]["pool_size"] == 10  # 덮어씌워짐
    assert result["new_section"]["key"] == "value"  # 추가됨 