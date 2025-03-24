"""
# File: tests/test_config/test_json_parser.py
# Description: JSON 설정 파서 테스트
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open
from app.common.config.loader import load_json_config


def test_load_json_config_with_parse_error():
    """JSON 파싱 오류 처리 테스트"""
    # 유효한 JSON 형식이지만 파싱 중 예외 발생을 시뮬레이션
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write('{"key": "value"}')
        temp_name = temp.name
    
    try:
        # json.load가 예외를 발생시키도록 모킹
        with patch('json.load', side_effect=Exception("JSON 파싱 오류")):
            # 설정 로드 시도
            result = load_json_config(temp_name)
            
            # 오류 발생 시 빈 딕셔너리 반환 확인
            assert result == {}
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_json_config_with_file_handling_error():
    """파일 처리 오류 테스트"""
    # 파일은 존재하지만 열기가 실패하는 상황 시뮬레이션
    file_path = "/path/to/existing/but/inaccessible.json"
    
    # 경로가 존재하는 것처럼 모킹
    with patch('os.path.exists', return_value=True):
        # 파일을 열 때 예외 발생하도록 모킹
        with patch('builtins.open', side_effect=IOError("파일 열기 오류")):
            # 설정 로드 시도
            result = load_json_config(file_path)
            
            # 오류 발생 시 빈 딕셔너리 반환 확인
            assert result == {} 