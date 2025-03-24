"""
# File: tests/test_config/test_config_file.py
# Description: 설정 파일 로드 테스트
"""

import os
import tempfile
import pytest
from app.common.config.settings import load_config_from_file


def test_load_config_from_file():
    """설정 파일에서 설정을 로드하는 테스트"""
    # 임시 설정 파일 생성 (python-dotenv 형식)
    config_content = """# 기본 설정
APP_NAME=TestApp
DEBUG=true
API_PREFIX=/api/v3
"""
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(config_content)
        temp_name = temp.name
    
    try:
        # 설정 파일 로드
        config = load_config_from_file(temp_name)
        
        # 설정값 검증
        assert config["APP_NAME"] == "TestApp"
        assert config["DEBUG"] == "true"
        assert config["API_PREFIX"] == "/api/v3"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_nonexistent_config_file():
    """존재하지 않는 설정 파일 로드 테스트"""
    # 존재하지 않는 파일 경로
    file_path = "/path/to/nonexistent/config.env"
    
    # 설정 파일 로드 시도
    config = load_config_from_file(file_path)
    
    # 존재하지 않는 파일일 경우 빈 딕셔너리 반환 확인
    assert config == {}


def test_load_malformed_config_file():
    """잘못된 형식의 설정 파일 로드 테스트"""
    # 잘못된 형식의 설정 파일 생성
    config_content = """# 이것은 주석입니다
APP_NAME 잘못된 형식 # 등호가 없음
DEBUG=true
이것은 잘못된 형식입니다
API_PREFIX=/api/v3
"""
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(config_content)
        temp_name = temp.name
    
    try:
        # 설정 파일 로드
        config = load_config_from_file(temp_name)
        
        # dotenv는 잘못된 형식의 줄은 무시하고 올바른 형식만 로드
        assert "APP_NAME" not in config  # 등호가 없어서 무시됨
        assert config["DEBUG"] == "true"
        assert config["API_PREFIX"] == "/api/v3"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_empty_config_file():
    """빈 설정 파일 로드 테스트"""
    # 빈 설정 파일 생성
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp_name = temp.name
    
    try:
        # 설정 파일 로드
        config = load_config_from_file(temp_name)
        
        # 빈 파일일 경우 빈 딕셔너리 반환 확인
        assert config == {}
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_commented_config_file():
    """주석이 있는 설정 파일 로드 테스트"""
    # 주석이 있는 설정 파일 생성
    config_content = """# 이것은 주석입니다
APP_NAME=TestApp
# 이것도 주석입니다
DEBUG=true
# API 접두사 설정
API_PREFIX=/api/v3
"""
    
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(config_content)
        temp_name = temp.name
    
    try:
        # 설정 파일 로드
        config = load_config_from_file(temp_name)
        
        # 주석이 무시되고 올바른 설정만 로드되는지 검증
        assert config["APP_NAME"] == "TestApp"
        assert config["DEBUG"] == "true"
        assert config["API_PREFIX"] == "/api/v3"
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name) 