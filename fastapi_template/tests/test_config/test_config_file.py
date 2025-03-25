"""
# File: tests/test_config/test_config_file.py
# Description: 설정 파일 로드 테스트
"""

import os
import pytest
import tempfile
import sys
from unittest import mock

from fastapi_template.app.common.config.config_settings import load_config_from_file


@pytest.fixture
def temp_env_file():
    """임시 환경 설정 파일 생성"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write("TEST_VAR=test_value\n")
        temp.write("ANOTHER_VAR=another_value\n")
        file_path = temp.name
    
    yield file_path
    
    # 테스트 후 파일 삭제
    os.unlink(file_path)


def test_load_config_from_file(temp_env_file):
    """설정 파일 로드 테스트"""
    config = load_config_from_file(temp_env_file)
    
    assert config["TEST_VAR"] == "test_value"
    assert config["ANOTHER_VAR"] == "another_value"


def test_load_nonexistent_config_file():
    """존재하지 않는 설정 파일 로드 테스트"""
    config = load_config_from_file("nonexistent_file.env")
    
    assert config == {}


def test_load_malformed_config_file():
    """잘못된 형식의 설정 파일 로드 테스트"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write("THIS IS NOT A VALID ENV FILE\n")
        file_path = temp.name
    
    try:
        config = load_config_from_file(file_path)
        assert config == {}
    finally:
        os.unlink(file_path)


def test_load_empty_config_file():
    """빈 설정 파일 로드 테스트"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        file_path = temp.name
    
    try:
        config = load_config_from_file(file_path)
        assert config == {}
    finally:
        os.unlink(file_path)


def test_load_commented_config_file():
    """주석이 있는 설정 파일 로드 테스트"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write("# This is a comment\n")
        temp.write("TEST_VAR=test_value\n")
        temp.write("# Another comment\n")
        file_path = temp.name
    
    try:
        config = load_config_from_file(file_path)
        assert config["TEST_VAR"] == "test_value"
        assert "# This is a comment" not in config
    finally:
        os.unlink(file_path)


def test_load_config_with_import_error():
    """dotenv 모듈이 없는 경우 테스트"""
    # dotenv 모듈을 임시로 가리기
    with mock.patch.dict(sys.modules, {'dotenv': None}):
        # ImportError가 발생해야 하지만 처리되어 빈 딕셔너리 반환
        config = load_config_from_file("any_file.env")
        assert config == {} 