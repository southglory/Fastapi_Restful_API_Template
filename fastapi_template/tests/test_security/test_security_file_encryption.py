"""
# File: fastapi_template/tests/test_security/test_security_file_encryption.py
# Description: 파일 암호화/복호화 테스트
"""

import os
import tempfile
from pathlib import Path
import io
import base64

import pytest
import nacl.secret
import nacl.utils

from app.common.security.security_file_encryption import (
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
        output_path = os.path.join(tempfile.gettempdir(), "encrypted_data.bin")
        
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


def test_file_encryption_errors():
    """파일 암호화/복호화 오류 테스트"""
    encryptor = FileEncryption()
    
    # 존재하지 않는 입력 파일
    non_existent_file = "/non_existent_input.txt"
    output_path = "/tmp/output.encrypted"
    
    # 암호화 실패
    result = encryptor.encrypt_file(non_existent_file, output_path)
    assert result is None
    
    # 복호화 실패
    result, success = encryptor.decrypt_file(non_existent_file)
    assert result is None
    assert success is False
    
    # 잘못된 파일 객체로 암호화
    class InvalidFile:
        def read(self):
            raise IOError("Failed to read")
    
    invalid_file = InvalidFile()
    result = encryptor.encrypt_file(invalid_file)
    assert result is None
    
    # 잘못된 파일 객체로 복호화
    result, success = encryptor.decrypt_file(invalid_file)
    assert result is None
    assert success is False


def test_encryption_util_errors():
    """암호화 유틸리티 함수 오류 테스트"""
    # 잘못된 출력 경로로 데이터 암호화
    invalid_path = "/invalid/path/file.encrypted"
    result = encrypt_data_to_file("test data", invalid_path)
    assert result is False
    
    # None 데이터로 NaCl 암호화
    result = encrypt_with_nacl(None)
    assert result is None
    
    # 잘못된 형식의 암호화된 데이터로 NaCl 복호화
    result = decrypt_with_nacl("invalid base64 data")
    assert result is None


def test_key_preparation_errors():
    """키 변환 오류 테스트"""
    encryptor = FileEncryption()
    
    # 잘못된 형식의 b'...' 문자열
    invalid_byte_string = "b'invalid byte string"
    key_bytes = encryptor._prepare_key(invalid_byte_string)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # None 키
    key_bytes = encryptor._prepare_key(None)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 잘못된 형식의 바이트 데이터
    invalid_bytes = b"invalid bytes"
    key_bytes = encryptor._prepare_key(invalid_bytes)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 잘못된 형식의 eval 문자열
    invalid_eval_string = "b'\\x00'"
    key_bytes = encryptor._prepare_key(invalid_eval_string)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 잘못된 형식의 eval 문자열 (SyntaxError)
    invalid_eval_string = "b'\\x'"
    key_bytes = encryptor._prepare_key(invalid_eval_string)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32


def test_encrypt_file_errors():
    """파일 암호화 오류 테스트"""
    encryptor = FileEncryption()
    
    # 잘못된 인코딩의 데이터
    class InvalidFile:
        def read(self):
            raise IOError("Failed to read")
    
    invalid_file = InvalidFile()
    result = encryptor.encrypt_file(invalid_file)
    assert result is None
    
    # 파일 쓰기 권한 없음
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        input_path = tmp_file.name
        output_path = "/root/invalid/path.encrypted"  # 권한 없는 경로
    
    try:
        result = encryptor.encrypt_file(input_path, output_path)
        assert result is None
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)
    
    # 잘못된 형식의 데이터
    class InvalidDataFile:
        def read(self):
            return object()  # 문자열이나 바이트로 변환할 수 없는 객체
    
    invalid_data_file = InvalidDataFile()
    result = encryptor.encrypt_file(invalid_data_file)
    assert result is None
    
    # 존재하지 않는 파일
    result = encryptor.encrypt_file("/non/existent/file")
    assert result is None


def test_decrypt_file_errors():
    """파일 복호화 오류 테스트"""
    encryptor = FileEncryption()
    
    # 잘못된 형식의 암호화된 데이터
    invalid_data = b"invalid encrypted data"
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(invalid_data)
        invalid_file = tmp_file.name
    
    try:
        result, success = encryptor.decrypt_file(invalid_file)
        assert result is None
        assert success is False
    finally:
        if os.path.exists(invalid_file):
            os.unlink(invalid_file)
    
    # 잘못된 인코딩의 데이터
    class InvalidFile:
        def read(self):
            raise IOError("Failed to read")
    
    invalid_file = InvalidFile()
    result, success = encryptor.decrypt_file(invalid_file)
    assert result is None
    assert success is False
    
    # 잘못된 형식의 데이터
    class InvalidDataFile:
        def read(self):
            return object()  # 문자열이나 바이트로 변환할 수 없는 객체
    
    invalid_data_file = InvalidDataFile()
    result, success = encryptor.decrypt_file(invalid_data_file)
    assert result is None
    assert success is False
    
    # 존재하지 않는 파일
    result, success = encryptor.decrypt_file("/non/existent/file")
    assert result is None
    assert success is False
    
    # 파일 쓰기 권한 없음
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"test data")
        input_path = tmp_file.name
        output_path = "/root/invalid/path.decrypted"  # 권한 없는 경로
    
    try:
        result, success = encryptor.decrypt_file(input_path, output_path)
        assert result is None
        assert success is False
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)


def test_encrypt_data_to_file_errors():
    """데이터 암호화 파일 저장 오류 테스트"""
    # 잘못된 출력 경로
    invalid_path = "/root/invalid/path.encrypted"
    result = encrypt_data_to_file("test data", invalid_path)
    assert result is False
    
    # None 데이터
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        result = encrypt_data_to_file(None, tmp_file.name)
        assert result is False
    os.unlink(tmp_file.name)
    
    # 잘못된 형식의 데이터
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        result = encrypt_data_to_file(123, tmp_file.name)  # 숫자 데이터
        assert result is False
    os.unlink(tmp_file.name)
    
    # 잘못된 인코딩의 데이터
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        result = encrypt_data_to_file(b"\xff\xff", tmp_file.name)  # 잘못된 UTF-8 바이트
        assert result is True  # 바이트는 그대로 암호화됨
    os.unlink(tmp_file.name)


def test_decrypt_file_to_data_errors():
    """파일에서 데이터 복호화 오류 테스트"""
    # 잘못된 형식의 암호화된 데이터
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"invalid encrypted data")
        invalid_file = tmp_file.name
    
    try:
        result = decrypt_file_to_data(invalid_file)
        assert result is None
    finally:
        if os.path.exists(invalid_file):
            os.unlink(invalid_file)
    
    # 존재하지 않는 파일
    result = decrypt_file_to_data("/non/existent/file")
    assert result is None
    
    # 잘못된 인코딩의 복호화된 데이터
    encryptor = FileEncryption()
    encrypted = encryptor.box.encrypt(b"\xff\xff")  # 잘못된 UTF-8 바이트
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(encrypted)
        invalid_file = tmp_file.name
    
    try:
        result = decrypt_file_to_data(invalid_file)
        assert result is None
    finally:
        if os.path.exists(invalid_file):
            os.unlink(invalid_file)


def test_nacl_encryption_errors():
    """NaCl 암호화/복호화 오류 테스트"""
    # 잘못된 형식의 암호화된 데이터
    result = decrypt_with_nacl("invalid base64 data")
    assert result is None
    
    # 잘못된 형식의 암호화된 데이터 (base64 디코딩 실패)
    result = decrypt_with_nacl("invalid base64 data!")
    assert result is None
    
    # 잘못된 형식의 암호화된 데이터 (NaCl 복호화 실패)
    invalid_encrypted = base64.b64encode(b"invalid encrypted data").decode('utf-8')
    result = decrypt_with_nacl(invalid_encrypted)
    assert result is None
    
    # None 데이터
    result = encrypt_with_nacl(None)
    assert result is None
    
    # 잘못된 형식의 데이터
    result = encrypt_with_nacl(123)  # 숫자 데이터
    assert result is None
    
    # 잘못된 인코딩의 데이터
    result = encrypt_with_nacl(b"\xff\xff")  # 잘못된 UTF-8 바이트
    assert isinstance(result, str)  # 바이트는 그대로 암호화됨


def test_file_io_errors():
    """파일 입출력 오류 테스트"""
    encryptor = FileEncryption()
    
    # 파일 읽기 권한 없음
    class NoReadPermissionFile:
        def read(self):
            raise PermissionError("Permission denied")
    
    no_read_file = NoReadPermissionFile()
    result = encryptor.encrypt_file(no_read_file)
    assert result is None
    
    # 파일 쓰기 권한 없음
    class NoWritePermissionFile:
        def write(self, data):
            raise PermissionError("Permission denied")
    
    no_write_file = NoWritePermissionFile()
    result = encryptor.encrypt_file("test.txt", no_write_file)
    assert result is None
    
    # 파일 닫기 오류
    class CloseErrorFile:
        def close(self):
            raise IOError("Failed to close")
        def write(self, data):
            return len(data)
    
    close_error_file = CloseErrorFile()
    result = encryptor.encrypt_file("test.txt", close_error_file)
    assert result is None


def test_key_preparation_advanced_errors():
    """키 준비 고급 오류 테스트"""
    encryptor = FileEncryption()
    
    # 잘못된 키 길이
    invalid_key = b"short"
    key_bytes = encryptor._prepare_key(invalid_key)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 잘못된 키 형식 (바이트로 변환 불가)
    class UnconvertibleKey:
        def __bytes__(self):
            raise TypeError("Cannot convert to bytes")
    
    invalid_key = UnconvertibleKey()
    key_bytes = encryptor._prepare_key(invalid_key)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32


def test_encryption_advanced_errors():
    """암호화 고급 오류 테스트"""
    encryptor = FileEncryption()
    
    # 암호화 중 메모리 오류
    class MemoryErrorData:
        def __bytes__(self):
            raise MemoryError("Out of memory")
    
    memory_error_data = MemoryErrorData()
    result = encryptor.encrypt_file(memory_error_data)
    assert result is None
    
    # 암호화 중 시스템 오류
    class SystemErrorData:
        def __bytes__(self):
            raise SystemError("System error")
    
    system_error_data = SystemErrorData()
    result = encryptor.encrypt_file(system_error_data)
    assert result is None


def test_decryption_advanced_errors():
    """복호화 고급 오류 테스트"""
    encryptor = FileEncryption()
    
    # 복호화 중 메모리 오류
    class MemoryErrorEncryptedData:
        def read(self):
            raise MemoryError("Out of memory")
    
    memory_error_data = MemoryErrorEncryptedData()
    result, success = encryptor.decrypt_file(memory_error_data)
    assert result is None
    assert success is False
    
    # 복호화 중 시스템 오류
    class SystemErrorEncryptedData:
        def read(self):
            raise SystemError("System error")
    
    system_error_data = SystemErrorEncryptedData()
    result, success = encryptor.decrypt_file(system_error_data)
    assert result is None
    assert success is False


def test_nacl_advanced_errors():
    """NaCl 고급 오류 테스트"""
    # 잘못된 base64 디코딩 (패딩 오류)
    invalid_base64 = "invalid base64 with padding="
    result = decrypt_with_nacl(invalid_base64)
    assert result is None
    
    # 잘못된 base64 디코딩 (문자 오류)
    invalid_base64 = "invalid base64 with invalid chars !@#$%^"
    result = decrypt_with_nacl(invalid_base64)
    assert result is None
    
    # 잘못된 NaCl 복호화 (키 오류)
    encrypted = encrypt_with_nacl("test data")
    box = nacl.secret.SecretBox(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    encrypted_data = base64.b64decode(encrypted)
    try:
        box.decrypt(encrypted_data)
    except:
        pass  # 예상된 오류
    
    # 잘못된 NaCl 복호화 (데이터 오류)
    invalid_encrypted = base64.b64encode(b"invalid encrypted data").decode('utf-8')
    result = decrypt_with_nacl(invalid_encrypted)
    assert result is None


def test_file_io_advanced_errors():
    """파일 입출력 고급 오류 테스트"""
    encryptor = FileEncryption()
    
    # 파일 읽기 중 메모리 오류
    class MemoryErrorReadFile:
        def read(self):
            raise MemoryError("Out of memory during read")
    
    memory_error_read = MemoryErrorReadFile()
    result = encryptor.encrypt_file(memory_error_read)
    assert result is None
    
    # 파일 쓰기 중 메모리 오류
    class MemoryErrorWriteFile:
        def write(self, data):
            raise MemoryError("Out of memory during write")
    
    memory_error_write = MemoryErrorWriteFile()
    result = encryptor.encrypt_file("test.txt", memory_error_write)
    assert result is None
    
    # 파일 읽기 중 시스템 오류
    class SystemErrorReadFile:
        def read(self):
            raise SystemError("System error during read")
    
    system_error_read = SystemErrorReadFile()
    result = encryptor.encrypt_file(system_error_read)
    assert result is None
    
    # 파일 쓰기 중 시스템 오류
    class SystemErrorWriteFile:
        def write(self, data):
            raise SystemError("System error during write")
    
    system_error_write = SystemErrorWriteFile()
    result = encryptor.encrypt_file("test.txt", system_error_write)
    assert result is None


def test_key_preparation_system_errors():
    """키 준비 시스템 오류 테스트"""
    encryptor = FileEncryption()
    
    # 메모리 오류
    class MemoryErrorKey:
        def __str__(self):
            raise MemoryError("Out of memory during key preparation")
    
    memory_error_key = MemoryErrorKey()
    key_bytes = encryptor._prepare_key(memory_error_key)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    
    # 시스템 오류
    class SystemErrorKey:
        def __str__(self):
            raise SystemError("System error during key preparation")
    
    system_error_key = SystemErrorKey()
    key_bytes = encryptor._prepare_key(system_error_key)
    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32


def test_encryption_system_errors():
    """암호화 시스템 오류 테스트"""
    encryptor = FileEncryption()
    
    # 메모리 오류 (암호화 중)
    class MemoryErrorEncryption:
        def read(self):
            return b"test data"
        def write(self, data):
            raise MemoryError("Out of memory during encryption")
    
    memory_error_encryption = MemoryErrorEncryption()
    result = encryptor.encrypt_file(memory_error_encryption)
    assert result is None
    
    # 시스템 오류 (암호화 중)
    class SystemErrorEncryption:
        def read(self):
            return b"test data"
        def write(self, data):
            raise SystemError("System error during encryption")
    
    system_error_encryption = SystemErrorEncryption()
    result = encryptor.encrypt_file(system_error_encryption)
    assert result is None


def test_decryption_system_errors():
    """복호화 시스템 오류 테스트"""
    encryptor = FileEncryption()
    
    # 메모리 오류 (복호화 중)
    class MemoryErrorDecryption:
        def read(self):
            return encryptor.box.encrypt(b"test data")
        def write(self, data):
            raise MemoryError("Out of memory during decryption")
    
    memory_error_decryption = MemoryErrorDecryption()
    result, success = encryptor.decrypt_file(memory_error_decryption)
    assert result is None
    assert success is False
    
    # 시스템 오류 (복호화 중)
    class SystemErrorDecryption:
        def read(self):
            return encryptor.box.encrypt(b"test data")
        def write(self, data):
            raise SystemError("System error during decryption")
    
    system_error_decryption = SystemErrorDecryption()
    result, success = encryptor.decrypt_file(system_error_decryption)
    assert result is None
    assert success is False


def test_nacl_system_errors():
    """NaCl 시스템 오류 테스트"""
    # 메모리 오류 (암호화 중)
    class MemoryErrorNaClEncryption:
        def __bytes__(self):
            raise MemoryError("Out of memory during NaCl encryption")
    
    memory_error_encryption = MemoryErrorNaClEncryption()
    result = encrypt_with_nacl(memory_error_encryption)
    assert result is None
    
    # 시스템 오류 (암호화 중)
    class SystemErrorNaClEncryption:
        def __bytes__(self):
            raise SystemError("System error during NaCl encryption")
    
    system_error_encryption = SystemErrorNaClEncryption()
    result = encrypt_with_nacl(system_error_encryption)
    assert result is None
    
    # 메모리 오류 (복호화 중)
    invalid_encrypted = base64.b64encode(b"invalid data").decode('utf-8')
    result = decrypt_with_nacl(invalid_encrypted)
    assert result is None
    
    # 시스템 오류 (복호화 중)
    invalid_encrypted = base64.b64encode(b"system error data").decode('utf-8')
    result = decrypt_with_nacl(invalid_encrypted)
    assert result is None


def test_chunk_encryption_errors():
    """청크 단위 암호화 오류 테스트"""
    encryptor = FileEncryption()
    
    # 청크 읽기 중 오류
    class ChunkReadErrorFile:
        def __init__(self):
            self.read_count = 0
        
        def read(self, size):
            self.read_count += 1
            if self.read_count > 2:
                raise IOError("Failed to read chunk")
            return b"test data"
    
    chunk_read_error = ChunkReadErrorFile()
    result = encryptor.encrypt_file(chunk_read_error)
    assert result is None
    
    # 청크 쓰기 중 오류
    class ChunkWriteErrorFile:
        def __init__(self):
            self.write_count = 0
        
        def read(self, size):
            return b"test data"
        
        def write(self, data):
            self.write_count += 1
            if self.write_count > 2:
                raise IOError("Failed to write chunk")
            return len(data)
    
    chunk_write_error = ChunkWriteErrorFile()
    result = encryptor.encrypt_file("test.txt", chunk_write_error)
    assert result is None


def test_chunk_decryption_errors():
    """청크 단위 복호화 오류 테스트"""
    encryptor = FileEncryption()
    
    # 청크 읽기 중 오류
    class ChunkReadErrorFile:
        def __init__(self):
            self.read_count = 0
        
        def read(self, size):
            self.read_count += 1
            if self.read_count > 2:
                raise IOError("Failed to read chunk")
            return encryptor.box.encrypt(b"test data")
    
    chunk_read_error = ChunkReadErrorFile()
    result, success = encryptor.decrypt_file(chunk_read_error)
    assert result is None
    assert success is False
    
    # 청크 쓰기 중 오류
    class ChunkWriteErrorFile:
        def __init__(self):
            self.write_count = 0
        
        def read(self, size):
            return encryptor.box.encrypt(b"test data")
        
        def write(self, data):
            self.write_count += 1
            if self.write_count > 2:
                raise IOError("Failed to write chunk")
            return len(data)
    
    chunk_write_error = ChunkWriteErrorFile()
    result, success = encryptor.decrypt_file("test.txt", chunk_write_error)
    assert result is None
    assert success is False


def test_file_close_errors():
    """파일 닫기 오류 테스트"""
    encryptor = FileEncryption()
    
    # 입력 파일 닫기 오류
    class InputCloseErrorFile:
        def read(self):
            return b"test data"
        
        def close(self):
            raise IOError("Failed to close input file")
    
    input_close_error = InputCloseErrorFile()
    result = encryptor.encrypt_file(input_close_error)
    assert isinstance(result, bytes)
    
    # 출력 파일 닫기 오류
    class OutputCloseErrorFile:
        def write(self, data):
            return len(data)
        
        def close(self):
            raise IOError("Failed to close output file")
    
    output_close_error = OutputCloseErrorFile()
    result = encryptor.encrypt_file("test.txt", output_close_error)
    assert result is None


def test_utility_function_errors():
    """유틸리티 함수 오류 테스트"""
    # 암호화 중 메모리 오류
    class MemoryErrorUtilData:
        def __bytes__(self):
            raise MemoryError("Out of memory during encryption")
    
    memory_error_data = MemoryErrorUtilData()
    result = encrypt_data_to_file(memory_error_data, "test.txt")
    assert result is False
    
    # 복호화 중 메모리 오류
    class MemoryErrorUtilFile:
        def read(self):
            raise MemoryError("Out of memory during decryption")
    
    memory_error_file = MemoryErrorUtilFile()
    result = decrypt_file_to_data(memory_error_file)
    assert result is None
    
    # 암호화 중 시스템 오류
    class SystemErrorUtilData:
        def __bytes__(self):
            raise SystemError("System error during encryption")
    
    system_error_data = SystemErrorUtilData()
    result = encrypt_data_to_file(system_error_data, "test.txt")
    assert result is False
    
    # 복호화 중 시스템 오류
    class SystemErrorUtilFile:
        def read(self):
            raise SystemError("System error during decryption")
    
    system_error_file = SystemErrorUtilFile()
    result = decrypt_file_to_data(system_error_file)
    assert result is None 