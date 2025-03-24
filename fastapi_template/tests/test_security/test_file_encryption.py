"""
# File: fastapi_template/tests/test_security/test_file_encryption.py
# Description: 파일 암호화/복호화 테스트
"""

import os
import tempfile
from pathlib import Path

import pytest
import nacl.secret
import nacl.utils

from app.common.security.file_encryption import (
    FileEncryption,
    encrypt_data_to_file,
    decrypt_file_to_data,
    encrypt_with_nacl,
    decrypt_with_nacl
)


def test_file_encryption_init():
    """FileEncryption 클래스 초기화 테스트"""
    # 기본 초기화
    encryptor = FileEncryption()
    assert encryptor.box is not None
    assert isinstance(encryptor.box, nacl.secret.SecretBox)
    
    # 문자열 키로 초기화
    test_key = "test_encryption_key_string"
    encryptor = FileEncryption(test_key)
    assert encryptor.box is not None
    
    # 바이트 키로 초기화
    test_bytes_key = b"test_encryption_key_bytes_12345"
    encryptor = FileEncryption(test_bytes_key)
    assert encryptor.box is not None
    
    # 정확한 길이의 키로 초기화
    exact_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    encryptor = FileEncryption(exact_key)
    assert encryptor.box is not None
    
    # b'...' 문자열 형식의 키로 초기화
    string_byte_key = str(exact_key)
    encryptor = FileEncryption(string_byte_key)
    assert encryptor.box is not None


def test_key_preparation():
    """키 변환 테스트"""
    encryptor = FileEncryption()
    
    # 문자열 키 변환
    string_key = "test_key"
    key_bytes = encryptor._prepare_key(string_key)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32  # NaCl SecretBox는 32바이트 키 필요
    
    # 짧은 바이트 키 변환
    short_bytes = b"short"
    key_bytes = encryptor._prepare_key(short_bytes)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 정확한 길이의 키
    exact_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key_bytes = encryptor._prepare_key(exact_key)
    assert key_bytes == exact_key


def test_generate_key():
    """키 생성 테스트"""
    key = FileEncryption.generate_key()
    assert isinstance(key, bytes)
    assert len(key) == nacl.secret.SecretBox.KEY_SIZE


def test_encrypt_decrypt_small_file():
    """작은 파일 암호화/복호화 테스트"""
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"Test content for encryption")
        input_path = tmp_file.name
    
    try:
        # 출력 파일 경로
        output_path = input_path + ".encrypted"
        decrypted_path = input_path + ".decrypted"
        
        # 암호화 객체 생성
        encryptor = FileEncryption()
        
        # 파일 암호화
        encryptor.encrypt_file(input_path, output_path)
        assert os.path.exists(output_path)
        
        # 파일 복호화
        encryptor.decrypt_file(output_path, decrypted_path)
        assert os.path.exists(decrypted_path)
        
        # 원본과 복호화된 파일 비교
        with open(input_path, 'rb') as f1, open(decrypted_path, 'rb') as f2:
            assert f1.read() == f2.read()
            
    finally:
        # 임시 파일 삭제
        for file_path in [input_path, output_path, decrypted_path]:
            if os.path.exists(file_path):
                os.unlink(file_path)


def test_encrypt_decrypt_memory():
    """메모리에서 암호화/복호화 테스트"""
    # 테스트 데이터
    test_data = b"Test data for in-memory encryption and decryption"
    
    # 암호화 객체 생성
    encryptor = FileEncryption()
    
    # 메모리에서 암호화
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(test_data)
        tmp_file.flush()
        tmp_file.seek(0)
        
        # 파일 객체로 암호화
        encrypted_data = encryptor.encrypt_file(tmp_file)
        
    # 암호화된 데이터 검증
    assert encrypted_data is not None
    assert len(encrypted_data) > len(test_data)
    
    # 메모리에서 복호화
    import io
    input_stream = io.BytesIO(encrypted_data)
    decrypted_data, success = encryptor.decrypt_file(input_stream)
    
    # 복호화 결과 검증
    assert success is True
    assert decrypted_data == test_data


def test_chunk_encryption():
    """청크 단위 암호화 테스트"""
    # 큰 데이터 생성 (5MB)
    large_data = b"0" * (5 * 1024 * 1024)
    
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(large_data)
        input_path = tmp_file.name
    
    try:
        # 출력 파일 경로
        output_path = input_path + ".encrypted"
        decrypted_path = input_path + ".decrypted"
        
        # 암호화 객체 생성 (작은 청크 사이즈로 설정)
        encryptor = FileEncryption()
        
        # 작은 청크 사이즈로 파일 암호화 (100KB)
        encryptor.encrypt_file(input_path, output_path, chunk_size=100 * 1024)
        assert os.path.exists(output_path)
        
        # 작은 청크 사이즈로 파일 복호화 (100KB)
        encryptor.decrypt_file(output_path, decrypted_path, chunk_size=100 * 1024)
        assert os.path.exists(decrypted_path)
        
        # 원본과 복호화된 파일 비교
        with open(input_path, 'rb') as f1, open(decrypted_path, 'rb') as f2:
            assert f1.read() == f2.read()
            
    finally:
        # 임시 파일 삭제
        for file_path in [input_path, output_path, decrypted_path]:
            if os.path.exists(file_path):
                os.unlink(file_path)


def test_encrypt_data_to_file_util():
    """데이터를 파일로 암호화하는 유틸리티 함수 테스트"""
    # 테스트 데이터
    test_data = "Test string data for encryption"
    
    try:
        # 임시 파일 경로
        output_path = tempfile.gettempdir() + "/encrypted_data.bin"
        
        # 데이터 암호화하여 파일로 저장
        result = encrypt_data_to_file(test_data, output_path)
        assert result is True
        assert os.path.exists(output_path)
        
        # 파일 크기 확인 (최소한 데이터 크기 + 논스 크기보다 커야 함)
        assert os.path.getsize(output_path) > len(test_data) + nacl.secret.SecretBox.NONCE_SIZE
        
        # 파일에서 데이터 복호화
        decrypted = decrypt_file_to_data(output_path)
        assert decrypted == test_data
        
        # 바이트 데이터로 반환
        decrypted_bytes = decrypt_file_to_data(output_path, as_string=False)
        assert decrypted_bytes == test_data.encode('utf-8')
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_encrypt_decrypt_with_nacl():
    """NaCl을 사용한 암호화/복호화 유틸리티 함수 테스트"""
    # 테스트 데이터
    test_data = "Test string data for NaCl encryption"
    
    # 데이터 암호화
    encrypted = encrypt_with_nacl(test_data)
    assert isinstance(encrypted, str)
    
    # 암호화된 데이터 복호화
    decrypted = decrypt_with_nacl(encrypted)
    assert decrypted == test_data
    
    # 바이트 데이터 암호화/복호화
    test_bytes = b"Test bytes data for NaCl encryption"
    encrypted = encrypt_with_nacl(test_bytes)
    decrypted = decrypt_with_nacl(encrypted)
    assert decrypted == test_bytes.decode('utf-8')


def test_encryption_with_invalid_data():
    """잘못된 데이터로 암호화/복호화 실패 테스트"""
    # 잘못된 암호화된 데이터 복호화
    result = decrypt_with_nacl("invalid_encrypted_data")
    assert result is None
    
    # 존재하지 않는 파일 복호화
    non_existent_file = "/non_existent_file.encrypted"
    result = decrypt_file_to_data(non_existent_file)
    assert result is None
    
    # 잘못된 형식의 암호화된 파일 복호화
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"Not an encrypted file")
        invalid_file = tmp_file.name
    
    try:
        result = decrypt_file_to_data(invalid_file)
        assert result is None
    finally:
        if os.path.exists(invalid_file):
            os.unlink(invalid_file)


def test_different_keys():
    """다른 키로 암호화/복호화 테스트"""
    # 테스트 데이터
    test_data = "Test data for different keys"
    
    # 두 개의 다른 키 생성
    key1 = FileEncryption.generate_key()
    key2 = FileEncryption.generate_key()
    
    # 첫 번째 키로 암호화
    encryptor1 = FileEncryption(key1)
    encrypted = encrypt_with_nacl(test_data)
    
    # 두 번째 키로 복호화 시도 (실패해야 함)
    encryptor2 = FileEncryption(key2)
    
    # 임시 파일에 암호화된 데이터 저장
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        # 첫 번째 키로 암호화
        with open(output_path, 'wb') as f:
            nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
            f.write(nonce)
            encrypted = encryptor1.box.encrypt(test_data.encode('utf-8'), nonce=nonce)
            f.write(encrypted.ciphertext)
        
        # 두 번째 키의 객체로 복호화 시도
        decrypted = decrypt_file_to_data(output_path)
        # 두 번째 키로는 복호화되지 않음
        assert decrypted is None
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_environment_key():
    """환경 변수 키 테스트"""
    # 환경 변수에 키 설정
    test_key = "env_test_key"
    os.environ["FILE_ENCRYPTION_KEY"] = test_key
    
    try:
        # 환경 변수 키로 암호화 객체 생성
        encryptor = FileEncryption()
        
        # 테스트 데이터
        test_data = "Test with environment key"
        
        # 암호화 및 복호화
        encrypted = encrypt_with_nacl(test_data)
        decrypted = decrypt_with_nacl(encrypted)
        
        assert decrypted == test_data
        
    finally:
        # 환경 변수 삭제
        if "FILE_ENCRYPTION_KEY" in os.environ:
            del os.environ["FILE_ENCRYPTION_KEY"] 