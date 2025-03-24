"""
# File: fastapi_template/tests/test_security/test_encryption.py
# Description: 암호화/복호화 기능 테스트
"""

import os
import base64
import pytest
from unittest.mock import patch, MagicMock

from app.common.security.encryption import (
    Encryption,
    encrypt_data,
    decrypt_data,
    get_encryption
)


def test_encryption_with_provided_key():
    """직접 키를 제공한 경우 암호화/복호화 테스트"""
    # 테스트용 키 생성
    test_key = Encryption.generate_key()
    
    # 테스트용 암호화 인스턴스 생성
    encryption = Encryption(key=test_key)
    
    # 암호화 및 복호화 테스트
    original_text = "민감한 정보"
    encrypted = encryption.encrypt(original_text)
    decrypted = encryption.decrypt(encrypted)
    
    # 검증
    assert encrypted != original_text
    assert decrypted == original_text


def test_encryption_with_string_data():
    """문자열 데이터 암호화/복호화 테스트"""
    encryption = Encryption()
    
    # 한글 문자열 테스트
    original_text = "안녕하세요 테스트입니다."
    encrypted = encryption.encrypt(original_text)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == original_text


def test_encryption_with_bytes_data():
    """바이트 데이터 암호화/복호화 테스트"""
    encryption = Encryption()
    
    # 바이트 데이터 테스트
    original_bytes = b"binary data test"
    encrypted = encryption.encrypt(original_bytes)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == original_bytes.decode()


def test_get_encryption_singleton():
    """암호화 싱글톤 인스턴스 테스트"""
    # 두 번 호출해도 같은 인스턴스 반환 확인
    encryption1 = get_encryption()
    encryption2 = get_encryption()
    
    assert encryption1 is encryption2


def test_helper_functions():
    """암호화/복호화 헬퍼 함수 테스트"""
    # 헬퍼 함수 테스트
    data = "헬퍼 함수 테스트"
    encrypted = encrypt_data(data)
    decrypted = decrypt_data(encrypted)
    
    assert encrypted != data
    assert decrypted == data


@patch('os.getenv')
def test_encryption_with_env_key(mock_getenv):
    """환경 변수 암호화 키 사용 테스트"""
    # 환경 변수에서 키를 가져오도록 모킹
    test_key = Encryption.generate_key()
    mock_getenv.return_value = test_key
    
    # Encryption 클래스를 새로 초기화하기 위해 싱글톤 인스턴스를 리셋
    Encryption._instance = None
    
    # 테스트용 암호화 인스턴스 생성 (환경 변수에서 키 사용)
    encryption = Encryption()
    
    # 암호화 및 복호화 테스트
    original_text = "환경 변수 키 테스트"
    encrypted = encryption.encrypt(original_text)
    decrypted = encryption.decrypt(encrypted)
    
    # 검증
    assert decrypted == original_text
    # 실제 호출 확인 (실제 구현에 맞게 수정)
    mock_getenv.assert_any_call("ENCRYPTION_KEY")


def test_key_generation():
    """키 생성 테스트"""
    # 키 생성
    key = Encryption.generate_key()
    
    # 키가 올바른 형식인지 확인
    assert isinstance(key, bytes)
    assert len(key) == 32  # 표준 AES 키는 32바이트
    
    # base64로 디코딩 가능한지 확인
    try:
        base64.urlsafe_b64decode(key)
    except Exception:
        pytest.fail("키가 올바른 base64 형식이 아닙니다.")


def test_encryption_with_invalid_key_handling():
    """잘못된 형식의 키 처리 테스트"""
    # 잘못된 형식의 키
    invalid_key = b"invalid_key_format_not_base64"
    
    # 기존 인스턴스 리셋
    Encryption._instance = None
    
    # 예외가 발생하지 않고 내부적으로 처리되어야 함
    encryption = Encryption(key=invalid_key)
    
    # 정상 작동 확인
    test_data = "테스트 데이터"
    encrypted = encryption.encrypt(test_data)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == test_data


def test_encryption_with_string_key():
    """문자열 키로 암호화 객체 생성 테스트"""
    # 키를 직접 생성 (문자열로)
    test_key = "test_encryption_key_string"
    
    # 키로 객체 생성
    encryption = Encryption(test_key)
    assert encryption.key is not None
    
    # 암호화/복호화 기능 테스트
    plaintext = "String key test data"
    encrypted = encryption.encrypt(plaintext)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == plaintext


def test_encryption_with_no_key():
    """키 없이 암호화 객체 생성 테스트 (SECRET_KEY 사용)"""
    # 기존 인스턴스 리셋
    Encryption._instance = None
    
    # 키 없이 암호화 객체 생성 (settings.SECRET_KEY 사용)
    encryption = Encryption()
    
    # 암호화 기능 테스트
    test_data = "기본 키 테스트"
    encrypted = encryption.encrypt(test_data)
    decrypted = encryption.decrypt(encrypted)
    
    assert decrypted == test_data 