"""
# File: tests/test_config/test_loader.py
# Description: 환경 변수 로더 테스트
"""

import os
import json
import tempfile
import pytest
from app.common.config.loader import (
    load_env_vars,
    load_env_file,
    load_json_config,
    merge_configs,
)


def test_load_env_vars():
    """환경 변수 로드 테스트"""
    # 환경 변수 설정
    os.environ["TEST_VAR1"] = "value1"
    os.environ["TEST_VAR2"] = "value2"
    
    # 환경 변수 로드
    env_vars = load_env_vars(["TEST_VAR1", "TEST_VAR2"])
    
    # 환경 변수 검증
    assert env_vars["TEST_VAR1"] == "value1"
    assert env_vars["TEST_VAR2"] == "value2"
    
    # 삭제
    del os.environ["TEST_VAR1"]
    del os.environ["TEST_VAR2"]


def test_load_env_vars_none_existing():
    """존재하지 않는 환경 변수 로드 테스트"""
    # 존재하지 않는 환경 변수 로드
    env_vars = load_env_vars(["NON_EXISTENT_VAR"])
    
    # 존재하지 않는 변수는 결과에 포함되지 않음
    assert "NON_EXISTENT_VAR" not in env_vars


def test_load_env_file():
    """환경 변수 파일 로드 테스트"""
    # 임시 환경 변수 파일 생성
    env_content = """
APP_NAME=TestApp
DEBUG=true
API_PREFIX=/api/v1
"""
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(env_content)
        temp_name = temp.name
    
    try:
        # 환경 변수 파일 로드
        env_vars = load_env_file(temp_name)
        
        # 환경 변수 검증
        assert env_vars["APP_NAME"] == "TestApp"
        assert env_vars["DEBUG"] == "true"
        assert env_vars["API_PREFIX"] == "/api/v1"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_env_file_nonexistent():
    """존재하지 않는 환경 변수 파일 로드 테스트"""
    # 존재하지 않는 파일 경로
    file_path = "/path/to/nonexistent/.env"
    
    # 환경 변수 파일 로드 시도
    env_vars = load_env_file(file_path)
    
    # 존재하지 않는 파일일 경우 빈 딕셔너리 반환 확인
    assert env_vars == {}


def test_load_env_file_corrupted():
    """손상된 환경 변수 파일 로드 테스트"""
    # 손상된 환경 변수 파일 생성 (python-dotenv 형식에 맞지 않는 내용)
    env_content = """
APP_NAME TestApp  # 등호 없음
DEBUG=true
잘못된 형식의 줄
API_PREFIX=/api/v1
"""
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(env_content)
        temp_name = temp.name
    
    try:
        # 환경 변수 파일 로드 시도
        env_vars = load_env_file(temp_name)
        
        # dotenv는 잘못된 형식의 줄은 무시하고 올바른 형식만 로드
        assert "APP_NAME" not in env_vars
        assert env_vars["DEBUG"] == "true"
        assert env_vars["API_PREFIX"] == "/api/v1"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_json_config():
    """JSON 설정 파일 로드 테스트"""
    # 임시 JSON 설정 파일 생성
    json_content = {
        "app_name": "TestApp",
        "debug": True,
        "api_prefix": "/api/v1",
        "nested": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as temp:
        json.dump(json_content, temp)
        temp_name = temp.name
    
    try:
        # JSON 설정 파일 로드
        config = load_json_config(temp_name)
        
        # 설정 검증
        assert config["app_name"] == "TestApp"
        assert config["debug"] is True
        assert config["api_prefix"] == "/api/v1"
        assert config["nested"]["key1"] == "value1"
        assert config["nested"]["key2"] == "value2"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_json_config_nonexistent():
    """존재하지 않는 JSON 설정 파일 로드 테스트"""
    # 존재하지 않는 파일 경로
    file_path = "/path/to/nonexistent/config.json"
    
    # JSON 설정 파일 로드 시도
    config = load_json_config(file_path)
    
    # 존재하지 않는 파일일 경우 빈 딕셔너리 반환 확인
    assert config == {}


def test_load_json_config_malformed():
    """잘못된 형식의 JSON 설정 파일 로드 테스트"""
    # 잘못된 형식의 JSON 설정 파일 생성
    json_content = """
    {
        "app_name": "TestApp",
        "debug": true,
        이것은 잘못된 JSON 형식입니다
        "api_prefix": "/api/v1"
    }
    """
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as temp:
        temp.write(json_content)
        temp_name = temp.name
    
    try:
        # JSON 설정 파일 로드 시도
        config = load_json_config(temp_name)
        
        # 잘못된 형식일 경우 빈 딕셔너리 반환 확인
        assert config == {}
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_merge_configs():
    """설정 병합 테스트"""
    # 기본 설정
    base_config = {
        "app_name": "BaseApp",
        "debug": False,
        "api_prefix": "/api/v1",
        "nested": {
            "key1": "base_value1",
            "key2": "base_value2"
        }
    }
    
    # 추가 설정
    additional_config = {
        "app_name": "TestApp",
        "nested": {
            "key1": "new_value1"
        },
        "new_key": "new_value"
    }
    
    # 설정 병합
    merged_config = merge_configs(base_config, additional_config)
    
    # 병합 결과 검증
    assert merged_config["app_name"] == "TestApp"  # 추가 설정 우선
    assert merged_config["debug"] is False  # 기본 설정 유지
    assert merged_config["api_prefix"] == "/api/v1"  # 기본 설정 유지
    assert merged_config["nested"]["key1"] == "new_value1"  # 추가 설정 우선
    assert merged_config["nested"]["key2"] == "base_value2"  # 기본 설정 유지
    assert merged_config["new_key"] == "new_value"  # 새 키 추가 