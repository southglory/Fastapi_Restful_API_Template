"""
해싱 모듈 테스트
"""


import pytest
import os
from app.common.security.security_hashing import (
    hash_password,
    verify_hash,
    generate_hash,
    generate_token,
    hash_file_contents,
    get_password_hash,
    verify_password
)


def test_hash_password():
    """패스워드 해싱 테스트"""
    password = "test_password"
    hashed = hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert "$" in hashed  # 솔트와 해시가 분리되어 있는지 확인


def test_verify_hash():
    """해시 검증 테스트"""
    password = "test_password"
    hashed = hash_password(password)
    assert verify_hash(password, hashed)
    assert not verify_hash("wrong_password", hashed)


def test_generate_hash():
    """일반 해시 생성 테스트"""
    data = "test_data"
    hashed = generate_hash(data)
    assert hashed != data
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA-256 해시 길이


def test_generate_token():
    """토큰 생성 테스트"""
    token = generate_token()
    assert isinstance(token, str)
    assert len(token) == 32  # 16바이트 = 32자 16진수


def test_hash_file_contents():
    """파일 해시 테스트"""
    # 테스트 파일 생성
    test_file = "test_file.txt"
    test_content = "test content"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        # 파일 해시 계산
        md5_hash, sha256_hash = hash_file_contents(test_file)
        assert md5_hash
        assert sha256_hash
        assert len(md5_hash) == 32
        assert len(sha256_hash) == 64
    finally:
        # 테스트 파일 삭제
        if os.path.exists(test_file):
            os.remove(test_file)


def test_hash_file_contents_nonexistent():
    """존재하지 않는 파일 해시 테스트"""
    md5_hash, sha256_hash = hash_file_contents("nonexistent_file.txt")
    assert md5_hash == ""
    assert sha256_hash == ""


def test_get_password_hash():
    """표준 패스워드 해싱 인터페이스 테스트"""
    password = "test_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert "$" in hashed


def test_verify_password():
    """표준 패스워드 검증 인터페이스 테스트"""
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_hash_password_with_custom_salt():
    """사용자 정의 솔트로 패스워드 해싱 테스트"""
    password = "test_password"
    salt = "custom_salt"
    hashed = hash_password(password, salt)
    assert hashed != password
    assert salt in hashed
    assert verify_hash(password, hashed)


def test_hash_password_with_empty_password():
    """빈 패스워드 해싱 테스트"""
    password = ""
    hashed = hash_password(password)
    assert hashed != password
    assert verify_hash(password, hashed)


def test_hash_password_with_long_password():
    """긴 패스워드 해싱 테스트"""
    password = "a" * 1000
    hashed = hash_password(password)
    assert hashed != password
    assert verify_hash(password, hashed)


def test_hash_password_with_special_characters():
    """특수 문자 포함 패스워드 해싱 테스트"""
    password = "!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_hash(password, hashed) 