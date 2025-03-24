"""
# File: tests/test_config/test_exception_coverage.py
# Description: 예외 처리 라인 테스트를 위한 추가 테스트 파일
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock
from app.common.config.loader import load_env_file, load_json_config, get_env_setting
from app.common.config.settings import load_config_from_file, ValidationError, Settings
from app.common.config.dev_settings import DevSettings


def test_load_env_file_exception_handling():
    """load_env_file 함수의 예외 처리 테스트"""
    # OS 동작을 모킹하여 파일은 존재하지만 파일 로드 시 예외 발생하도록 설정
    with patch('os.path.exists', return_value=True):
        with patch('dotenv.dotenv_values', side_effect=Exception("예상된 dotenv 오류")):
            # 예외 발생 시에도 빈 딕셔너리 반환하는지 확인
            result = load_env_file("/path/to/test.env")
            assert result == {}


def test_load_env_file_explicit_exception():
    """load_env_file 함수의 구체적인 예외 처리 테스트 (60-62라인 커버)"""
    # 파일은 존재하지만 파일 열기 시 예외 발생하는 시나리오
    with patch('os.path.exists', return_value=True):
        # dotenv_values 함수 자체를 모킹하여 실제 Exception이 발생하도록 처리
        mock_dotenv = MagicMock(side_effect=Exception("예외 발생"))
        
        # 패치 적용 - 정확한 임포트 경로 사용
        with patch('app.common.config.loader.dotenv_values', mock_dotenv):
            result = load_env_file("/path/to/test.env")
            assert result == {}
            # 모의 함수가 호출되었는지 확인
            mock_dotenv.assert_called_once()


def test_load_json_config_exception_handling():
    """load_json_config 함수의 예외 처리 테스트"""
    # 실제 파일을 생성하고 손상된 JSON 작성
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as temp:
        temp.write("{이것은: 유효하지 않은 JSON 형식입니다}")
        temp_name = temp.name
    
    try:
        # JSON 파싱 오류 발생 확인
        result = load_json_config(temp_name)
        # 예외가 발생해도 빈 딕셔너리 반환
        assert result == {}
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)


def test_load_config_from_file_exception_handling():
    """settings.py의 load_config_from_file 함수 예외 처리 테스트"""
    # 파일 존재 여부 체크는 통과하지만 dotenv_values에서 예외 발생
    with patch('os.path.exists', return_value=True):
        with patch('dotenv.dotenv_values', side_effect=Exception("의도적인 dotenv 오류")):
            # 예외 발생 시에도 빈 딕셔너리 반환하는지 확인
            result = load_config_from_file("/path/to/test.env")
            assert result == {}


def test_settings_validate_database_url_exception():
    """Settings 클래스의 validate_database_url 예외 처리 테스트"""
    # 유효하지 않은 데이터베이스 URL 설정
    invalid_db_url = "invalid://localhost/db"
    
    # Pydantic field_validator로 정의된 메서드 호출
    with pytest.raises(ValidationError) as exc:
        Settings().validate_database_url(invalid_db_url)
    
    # 예외 메시지 검증
    assert "지원하지 않는 데이터베이스 URL 형식" in str(exc.value)


def test_settings_validate_required_exception():
    """Settings 클래스의 validate_required 메서드 예외 처리 테스트"""
    # 기본 시크릿 키를 가진 설정 생성
    settings = Settings()
    
    # database_url이 None이고 secret_key가 기본값이므로 예외 발생
    with pytest.raises(ValidationError) as exc:
        settings.validate_required()
    
    # 예외 메시지 검증
    assert "SECRET_KEY is required" in str(exc.value) or "DATABASE_URL is required" in str(exc.value)


def test_settings_validate_empty_secret_key():
    """Settings 클래스의 validate_required 메서드에서 빈 시크릿 키 검증 테스트"""
    # 빈 시크릿 키를 가진 설정 생성
    settings = Settings(secret_key="")
    
    # 빈 시크릿 키로 예외 발생 확인
    with pytest.raises(ValidationError) as exc:
        settings.validate_required()
    
    # 예외 메시지 검증
    assert "SECRET_KEY is required" in str(exc.value)


def test_get_env_setting_default_value():
    """get_env_setting 함수의 기본값 반환 테스트 (113라인 커버)"""
    # 기존 환경 변수 백업
    original_env = os.environ.copy()
    
    try:
        # 테스트 환경 변수가 없는 상황 시뮬레이션
        if "TEST_NON_EXISTENT_VAR" in os.environ:
            del os.environ["TEST_NON_EXISTENT_VAR"]
        
        # 존재하지 않는 환경 변수에 대해 기본값 반환 확인 (필수 아님)
        default_value = "기본값"
        result = get_env_setting("TEST_NON_EXISTENT_VAR", default=default_value, required=False)
        
        # 결과가 기본값과 일치하는지 확인 (113라인 커버)
        assert result == default_value
    finally:
        # 환경 변수 복원
        os.environ.clear()
        os.environ.update(original_env)


def test_dev_settings_dict_config():
    """DevSettings 클래스의 dict_config 메서드 테스트"""
    # DevSettings 객체 생성
    dev_settings = DevSettings()
    
    # __dict__ 속성을 목킹하여 조건 분기 테스트를 보장
    with patch.object(dev_settings, '__dict__', {
        "_private_attr": "이 값은 무시되어야 함",
        "PROJECT_NAME": "테스트 앱",
        "DEBUG": True
    }):
        config = dev_settings.dict_config()
        
        # 언더스코어로 시작하는 속성이 제외되었는지 확인
        assert "_private_attr" not in config
        assert "PROJECT_NAME" in config
        assert config["PROJECT_NAME"] == "테스트 앱"
        assert config["DEBUG"] is True 