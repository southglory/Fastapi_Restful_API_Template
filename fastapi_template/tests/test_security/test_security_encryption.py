"""
암호화/복호화 모듈 테스트
"""

import pytest
from app.common.security.security_encryption import (
    Encryption,
    encrypt_data,
    decrypt_data,
    encrypt_text,
    decrypt_text,
    validate_key
)


def test_encryption_singleton():
    """싱글톤 패턴 테스트"""
    enc1 = Encryption()
    enc2 = Encryption()
    assert enc1 is enc2


def test_encryption_key_derivation():
    """키 유도 테스트"""
    enc = Encryption()
    assert isinstance(enc.key, bytes)
    assert len(enc.key) == 32


def test_encrypt_decrypt_data():
    """암호화/복호화 테스트"""
    # 테스트 데이터
    test_data = "테스트 데이터"
    
    # 암호화
    encrypted_data = encrypt_data(test_data)
    assert encrypted_data != test_data
    assert isinstance(encrypted_data, str)
    
    # 복호화
    decrypted_data = decrypt_data(encrypted_data)
    assert decrypted_data == test_data


def test_encrypt_decrypt_text():
    """텍스트 암호화/복호화 테스트"""
    # 테스트 데이터
    test_data = "테스트 데이터"
    
    # 암호화
    encrypted_data = encrypt_text(test_data)
    assert encrypted_data != test_data
    assert isinstance(encrypted_data, str)
    
    # 복호화
    decrypted_data = decrypt_text(encrypted_data)
    assert decrypted_data == test_data


def test_encryption_with_custom_key():
    """사용자 정의 키로 암호화/복호화 테스트"""
    # 테스트 데이터
    test_data = "테스트 데이터"
    custom_key = b"test_key_32_bytes_long_key_here"
    
    # 사용자 정의 키로 암호화
    enc = Encryption(key=custom_key)
    encrypted_data = enc.encrypt(test_data)
    
    # 동일한 키로 복호화
    dec = Encryption(key=custom_key)
    decrypted_data = dec.decrypt(encrypted_data)
    assert decrypted_data == test_data


def test_encryption_with_different_keys():
    """다른 키로 암호화/복호화 시도 테스트"""
    # 테스트 데이터
    test_data = "테스트 데이터"
    key1 = b"test_key_32_bytes_long_key_here"
    key2 = b"different_key_32_bytes_long_key"
    
    # 첫 번째 키로 암호화
    enc1 = Encryption(key=key1)
    encrypted_data = enc1.encrypt(test_data)
    
    # 다른 키로 복호화 시도
    enc2 = Encryption(key=key2)
    decrypted_data = enc2.decrypt(encrypted_data)
    assert decrypted_data != test_data


def test_validate_key():
    """키 유효성 검사 테스트"""
    # 유효한 키
    valid_key = b"test_key_32_bytes_long_key_here"
    assert validate_key(valid_key)
    
    # 유효하지 않은 키 (길이가 짧음)
    invalid_key = b"short_key"
    assert not validate_key(invalid_key)


def test_encryption_with_empty_data():
    """빈 데이터 암호화/복호화 테스트"""
    # 빈 문자열
    empty_data = ""
    encrypted_data = encrypt_data(empty_data)
    decrypted_data = decrypt_data(encrypted_data)
    assert decrypted_data == empty_data


def test_encryption_with_binary_data():
    """바이너리 데이터 암호화/복호화 테스트"""
    # 바이너리 데이터
    binary_data = b"binary_data"
    encrypted_data = encrypt_data(binary_data)
    decrypted_data = decrypt_data(encrypted_data)
    assert decrypted_data == binary_data.decode()


def test_encryption_with_long_data():
    """긴 데이터 암호화/복호화 테스트"""
    # 긴 문자열
    long_data = "a" * 1000
    encrypted_data = encrypt_data(long_data)
    decrypted_data = decrypt_data(encrypted_data)
    assert decrypted_data == long_data


def test_encryption_with_special_characters():
    """특수 문자 포함 데이터 암호화/복호화 테스트"""
    # 특수 문자 포함
    special_data = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    encrypted_data = encrypt_data(special_data)
    decrypted_data = decrypt_data(encrypted_data)
    assert decrypted_data == special_data 