"""
# File: tests/test_config/test_settings_file.py
# Description: settings 모듈의 파일 로드 기능 테스트
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from app.common.config.settings import load_config_from_file


def test_load_config_file_read_exception():
    """설정 파일 읽기 중 예외 발생 테스트"""
    # 파일이 존재하지만 읽기 중 예외 발생하는 상황
    with patch('os.path.exists', return_value=True):
        # 파일을 열 때는 성공하지만 읽는 중 예외 발생
        with patch('builtins.open', side_effect=Exception("파일 읽기 오류")):
            # 파일 로드 시도
            result = load_config_from_file("/path/to/existing/but/unreadable/file")
            
            # 오류 발생 시 빈 딕셔너리 반환 확인
            assert result == {} 