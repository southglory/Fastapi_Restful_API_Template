"""
# File: fastapi_template/tests/test_security/test_hashing.py
# Description: 패스워드 해싱 및 검증 테스트
"""

import os
import tempfile
import pytest
from app.common.security.hashing import (
    hash_password,
    verify_hash,
    generate_hash,
    generate_token,
    hash_file_contents
)


def test_hash_password():
    """패스워드 해싱 테스트"""
    # 기본 해싱 테스트
    password = "my_secure_password"
    hashed = hash_password(password)
    
    # 해시 형식 검증 (salt$hash)
    assert '$' in hashed
    
    # 같은 패스워드, 다른 솔트로 해싱하면 다른 결과가 나와야 함
    hashed2 = hash_password(password)
    assert hashed != hashed2


def test_hash_password_with_salt():
    """지정된 솔트로 패스워드 해싱 테스트"""
    # 지정된 솔트로 해싱
    password = "test_password"
    salt = "fixed_salt_for_testing"
    
    hashed1 = hash_password(password, salt)
    hashed2 = hash_password(password, salt)
    
    # 같은 솔트를 사용하면 같은 결과가 나와야 함
    assert hashed1 == hashed2
    
    # 해시에 솔트가 포함되어 있어야 함
    assert hashed1.startswith(salt)


def test_verify_hash():
    """패스워드 해시 검증 테스트"""
    # 패스워드 해싱 및 검증
    password = "verify_test_password"
    hashed = hash_password(password)
    
    # 올바른 패스워드로 검증
    assert verify_hash(password, hashed) == True
    
    # 잘못된 패스워드로 검증
    assert verify_hash("wrong_password", hashed) == False
    assert verify_hash("", hashed) == False


def test_verify_hash_with_invalid_format():
    """잘못된 형식의 해시 검증 테스트"""
    # $ 구분자가 없는 경우
    assert verify_hash("password", "invalid_hash_format") == False
    
    # 빈 문자열 해시
    assert verify_hash("password", "") == False
    
    # None 값 해시
    assert verify_hash("password", None) == False


@pytest.mark.parametrize("password", [
    "simple",
    "complex_password123!",
    "한글비밀번호123",
    "!@#$%^&*()",
    " ",  # 공백
    ""    # 빈 문자열
])
def test_hash_verify_various_inputs(password):
    """다양한 입력값에 대한 해싱/검증 테스트"""
    hashed = hash_password(password)
    assert verify_hash(password, hashed) == True


def test_generate_hash():
    """데이터 해싱 테스트"""
    # 같은 입력에 대해 같은 해시가 생성되어야 함
    data = "test_data"
    hash1 = generate_hash(data)
    hash2 = generate_hash(data)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 해시는 64자
    
    # 다른 입력에 대해 다른 해시가 생성되어야 함
    hash3 = generate_hash("different_data")
    assert hash1 != hash3


def test_generate_token():
    """토큰 생성 테스트"""
    # 토큰 길이 및 중복 여부 확인
    token1 = generate_token()
    token2 = generate_token()
    
    assert len(token1) == 32  # 16바이트 = 32자 hex
    assert token1 != token2  # 랜덤성 확인


def test_hash_file_contents():
    """파일 내용 해싱 테스트"""
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"test file content")
        temp_path = temp.name
    
    try:
        # 파일 내용 해싱
        md5_hash, sha256_hash = hash_file_contents(temp_path)
        
        # 해시 값이 존재하는지 확인
        assert md5_hash != ''
        assert sha256_hash != ''
        
        # 해시 길이 확인
        assert len(md5_hash) == 32  # MD5는 32자
        assert len(sha256_hash) == 64  # SHA-256은 64자
        
        # 같은 파일에 대해 같은 해시 생성 확인
        md5_hash2, sha256_hash2 = hash_file_contents(temp_path)
        assert md5_hash == md5_hash2
        assert sha256_hash == sha256_hash2
        
    finally:
        # 임시 파일 삭제
        os.unlink(temp_path)


def test_hash_file_contents_nonexistent_file():
    """존재하지 않는 파일 해싱 테스트"""
    # 존재하지 않는 파일 경로
    invalid_path = "/nonexistent/file/path"
    
    # 존재하지 않는 파일에 대해 빈 해시값 반환 확인
    md5_hash, sha256_hash = hash_file_contents(invalid_path)
    assert md5_hash == ''
    assert sha256_hash == '' 