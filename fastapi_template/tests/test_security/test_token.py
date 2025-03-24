"""
# File: fastapi_template/tests/test_security/test_token.py
# Description: 보안 토큰 생성 및 관리 테스트
"""

import time
import re
import unittest.mock
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest
import jwt

from app.common.security.token import (
    generate_secure_token,
    generate_uuid,
    sign_data,
    verify_signature,
    generate_timed_token,
    validate_token,
    create_jwt_token,
    decode_jwt_token,
    create_access_token,
    create_refresh_token,
)

from app.common.config import settings


def test_generate_secure_token():
    """랜덤 토큰 생성 테스트"""
    # 기본 길이 토큰
    token = generate_secure_token()
    assert isinstance(token, str)
    assert len(token) == 32
    
    # 짝수 길이
    token = generate_secure_token(40)
    assert isinstance(token, str)
    assert len(token) == 40
    
    # 홀수 길이
    token = generate_secure_token(15)
    assert isinstance(token, str)
    assert len(token) == 15


def test_generate_uuid():
    """UUID 생성 테스트"""
    uuid = generate_uuid()
    assert isinstance(uuid, str)
    # UUID 형식 검증 (8-4-4-4-12 형식)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    assert re.match(uuid_pattern, uuid) is not None


def test_sign_data():
    """데이터 서명 테스트"""
    data = "test_data"
    signed = sign_data(data)
    
    # 형식 검증 (원본.서명)
    assert '.' in signed
    parts = signed.split('.')
    assert len(parts) == 2
    assert parts[0] == data
    # 서명은 SHA256 해시 결과값이어야 함 (64자)
    assert len(parts[1]) == 64
    
    # 다른 비밀키로 서명
    custom_secret = "custom_secret"
    signed_custom = sign_data(data, custom_secret)
    assert signed != signed_custom


def test_verify_signature():
    """서명 검증 테스트"""
    data = "test_data"
    signed = sign_data(data)
    
    # 유효한 서명 검증
    is_valid, original = verify_signature(signed)
    assert is_valid == True
    assert original == data
    
    # 유효하지 않은 서명 검증
    invalid_signed = f"{data}.invalid_signature"
    is_valid, original = verify_signature(invalid_signed)
    assert is_valid == False
    assert original == ""
    
    # 형식이 잘못된 서명 검증
    is_valid, original = verify_signature("invalid_format")
    assert is_valid == False
    assert original == ""
    
    # 다른 비밀키로 서명한 데이터 검증
    custom_secret = "custom_secret"
    signed_custom = sign_data(data, custom_secret)
    is_valid, original = verify_signature(signed_custom)
    assert is_valid == False
    
    # 같은 비밀키로 검증
    is_valid, original = verify_signature(signed_custom, custom_secret)
    assert is_valid == True
    assert original == data


def test_generate_timed_token():
    """시간 제한 토큰 생성 테스트"""
    user_id = "test_user"
    token = generate_timed_token(user_id)
    
    # 형식 검증
    assert isinstance(token, str)
    assert '.' in token
    
    # 유효성 검증
    is_valid, data = verify_signature(token)
    assert is_valid == True
    
    # 데이터 형식 검증 (user_id:expiry)
    parts = data.split(':')
    assert len(parts) == 2
    assert parts[0] == user_id
    expiry = int(parts[1])
    assert expiry > int(time.time())


def test_validate_token():
    """토큰 검증 테스트"""
    # 유효한 토큰
    user_id = "validate_test_user"
    token = generate_timed_token(user_id, 3600)
    
    result = validate_token(token)
    assert result["valid"] == True
    assert result["user_id"] == user_id
    
    # 만료된 토큰
    with patch('time.time', return_value=int(time.time()) + 7200):
        # 현재 시간을 2시간 후로 설정
        
        result = validate_token(token)
        assert result["valid"] == False
        assert "expired" in result["error"].lower()
    
    # 잘못된 서명의 토큰
    parts = token.split('.')
    invalid_token = f"{parts[0]}.invalid_signature"
    result = validate_token(invalid_token)
    assert result["valid"] == False
    assert "signature" in result["error"].lower()
    
    # 형식이 잘못된 토큰
    result = validate_token("invalid_format")
    assert result["valid"] == False
    assert "signature" in result["error"].lower()


def test_token_with_different_expiry():
    """다양한 만료 시간 테스트"""
    user_id = "expiry_test_user"
    
    # 짧은 만료 시간
    token_short = generate_timed_token(user_id, 10)
    result = validate_token(token_short)
    assert result["valid"] == True
    assert result["expires_in"] <= 10
    
    # 긴 만료 시간
    token_long = generate_timed_token(user_id, 86400)
    result = validate_token(token_long)
    assert result["valid"] == True
    assert result["expires_in"] <= 86400


def test_token_with_mocked_time():
    """시간 모킹을 통한 토큰 테스트"""
    user_id = "mock_time_test_user"
    
    # 현재 시간 모킹 (고정된 시간으로 설정)
    with patch('time.time') as mock_time:
        fixed_time = 1600000000
        mock_time.return_value = fixed_time
        
        # 토큰 생성
        token = generate_timed_token(user_id, 3600)
        
        # 같은 시간에 검증
        result = validate_token(token)
        assert result["valid"] == True
        assert result["expires_in"] == 3600
        
        # 1시간 후 검증 (만료 직전)
        mock_time.return_value = fixed_time + 3599
        result = validate_token(token)
        assert result["valid"] == True
        assert result["expires_in"] == 1
        
        # 1시간 1초 후 검증 (만료됨)
        mock_time.return_value = fixed_time + 3601
        result = validate_token(token)
        assert result["valid"] == False


def test_malformed_token_data():
    """형식이 잘못된 토큰 데이터 테스트"""
    # 서명은 유효하지만 데이터 형식이 잘못된 경우
    malformed_data = "no_expiry_data"
    signed_token = sign_data(malformed_data)
    
    result = validate_token(signed_token)
    assert result["valid"] == False
    assert "malformed" in result["error"].lower()


# PyJWT 테스트 함수 추가
def test_create_jwt_token():
    """JWT 토큰 생성 테스트"""
    # 기본 데이터로 토큰 생성
    data = {"user_id": "test_user", "role": "admin"}
    token = create_jwt_token(data)
    
    # 토큰 형식 확인
    assert isinstance(token, str)
    
    # 토큰 디코딩하여 검증
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert "exp" in decoded
    assert decoded["user_id"] == "test_user"
    assert decoded["role"] == "admin"
    
    # 만료 시간 검증 (정확한 값 비교 대신 존재 여부만 확인)
    assert isinstance(decoded["exp"], int)
    assert decoded["exp"] > int(time.time())


def test_jwt_token_with_custom_expiry():
    """사용자 지정 만료 시간이 있는 JWT 토큰 테스트"""
    data = {"user_id": "test_user"}
    expires = timedelta(hours=2)
    token = create_jwt_token(data, expires)
    
    # 토큰 디코딩하여 만료 시간 검증
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    
    # 현재 시간 기준으로 만료까지 남은 시간이 약 2시간인지 확인 (정확한 값보다 범위로 검증)
    time_to_expire = decoded["exp"] - int(time.time())
    assert 7100 < time_to_expire < 7300  # 대략 2시간(7200초) 근처


def test_decode_jwt_token():
    """JWT 토큰 디코딩 테스트"""
    # 토큰 생성
    data = {"user_id": "test_user", "scope": "read:profile"}
    token = create_jwt_token(data)
    
    # 토큰 디코딩
    decoded = decode_jwt_token(token)
    assert decoded["user_id"] == "test_user"
    assert decoded["scope"] == "read:profile"
    
    # 만료된 토큰 테스트
    expired_data = {"user_id": "expired_user"}
    # 이미 만료된 토큰 생성
    expires_delta = timedelta(seconds=-1)
    expired_token = create_jwt_token(expired_data, expires_delta)
    
    # 만료 검증 활성화된 경우 예외 발생
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_jwt_token(expired_token)
    
    # 만료 검증 비활성화된 경우 정상 디코딩
    decoded = decode_jwt_token(expired_token, verify_expiration=False)
    assert decoded["user_id"] == "expired_user"
    
    # 잘못된 서명의 토큰 테스트
    with pytest.raises(jwt.InvalidTokenError):
        decode_jwt_token(token + "invalid")


def test_create_access_token():
    """액세스 토큰 생성 테스트"""
    # 기본 액세스 토큰 생성
    user_id = "test_user"
    token = create_access_token(user_id)
    
    # 토큰 디코딩하여 검증
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    assert decoded["type"] == "access"
    assert "iat" in decoded  # 발급 시간
    
    # 추가 데이터로 토큰 생성
    extra_data = {"role": "admin", "permissions": ["read", "write"]}
    token = create_access_token(user_id, extra_data=extra_data)
    
    # 토큰에 추가 데이터가 포함되어 있는지 확인
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded["role"] == "admin"
    assert decoded["permissions"] == ["read", "write"]


def test_create_refresh_token():
    """리프레시 토큰 생성 테스트"""
    # 기본 리프레시 토큰 생성
    user_id = "test_user"
    token = create_refresh_token(user_id)
    
    # 토큰 디코딩하여 검증
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == user_id
    assert decoded["type"] == "refresh"
    
    # 만료 시간이 settings의 값에 맞게 설정되었는지 확인 (대략적인 범위로 검증)
    days_in_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    time_to_expire = decoded["exp"] - int(time.time())
    # 설정된 일수에 해당하는 초 범위 내에 있는지 확인 (오차 허용)
    assert days_in_seconds - 3600 < time_to_expire < days_in_seconds + 3600


def test_token_types_compatibility():
    """액세스 토큰과 리프레시 토큰의 호환성 테스트"""
    user_id = "test_user"
    
    # 액세스 토큰과 리프레시 토큰 생성
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    # 두 토큰 모두 디코딩 가능
    access_decoded = decode_jwt_token(access_token)
    refresh_decoded = decode_jwt_token(refresh_token)
    
    # 토큰 타입 확인
    assert access_decoded["type"] == "access"
    assert refresh_decoded["type"] == "refresh"
    
    # 동일한 사용자 ID 확인
    assert access_decoded["sub"] == user_id
    assert refresh_decoded["sub"] == user_id 