"""
토큰 모듈 테스트
"""


import pytest
import time
from datetime import datetime, timedelta, UTC
from app.common.security.security_token import (
    generate_secure_token,
    generate_uuid,
    sign_data,
    verify_signature,
    generate_timed_token,
    validate_token,
    create_jwt_token,
    verify_jwt_token,
    decode_jwt_token,
    is_token_expired,
    create_access_token,
    create_refresh_token
)


def test_generate_secure_token():
    """안전한 토큰 생성 테스트"""
    token = generate_secure_token()
    assert isinstance(token, str)
    assert len(token) == 32  # 기본 길이
    
    # 다른 길이 테스트
    token = generate_secure_token(length=64)
    assert len(token) == 64


def test_generate_uuid():
    """UUID 생성 테스트"""
    uuid_str = generate_uuid()
    assert isinstance(uuid_str, str)
    # UUID 형식 검증 (8-4-4-4-12 형식)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    import re
    assert re.match(uuid_pattern, uuid_str) is not None


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
    with pytest.raises(Exception):
        # 현재 시간을 2시간 후로 설정
        expired_token = generate_timed_token(user_id, -3600)  # 1시간 전에 만료된 토큰
        result = validate_token(expired_token)
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
    assert "malformed" in result["error"].lower()


def test_create_jwt_token():
    """JWT 토큰 생성 테스트"""
    # 기본 데이터로 토큰 생성
    data = {"user_id": "test_user", "role": "admin"}
    token = create_jwt_token(data)
    
    # 토큰 형식 확인
    assert isinstance(token, str)
    assert "." in token  # JWT 형식 확인 (header.payload.signature)
    
    # 토큰 디코딩하여 검증
    decoded = decode_jwt_token(token)
    assert decoded["user_id"] == "test_user"
    assert decoded["role"] == "admin"
    assert "exp" in decoded
    
    # 만료 시간 지정 테스트
    expires = timedelta(hours=2)
    token = create_jwt_token(data, expires_delta=expires)
    decoded = decode_jwt_token(token)
    exp_time = datetime.fromtimestamp(decoded["exp"], UTC)
    assert (exp_time - datetime.now(UTC)).total_seconds() > 7100  # 약 2시간


def test_verify_jwt_token():
    """JWT 토큰 검증 테스트"""
    payload = {"user_id": 1, "role": "admin"}
    token = create_jwt_token(payload)
    assert verify_jwt_token(token)
    assert not verify_jwt_token("invalid_token")


def test_decode_jwt_token():
    """JWT 토큰 디코딩 테스트"""
    data = {"user_id": "test_user", "role": "admin"}
    token = create_jwt_token(data)
    
    # 토큰 디코딩
    decoded = decode_jwt_token(token)
    assert decoded["user_id"] == data["user_id"]
    assert decoded["role"] == data["role"]
    assert "exp" in decoded
    
    # 만료 시간 검증 비활성화
    decoded = decode_jwt_token(token, verify_expiration=False)
    assert decoded["user_id"] == data["user_id"]
    
    # 잘못된 토큰 디코딩
    with pytest.raises(Exception):
        decode_jwt_token("invalid_token")


def test_is_token_expired():
    """토큰 만료 확인 테스트"""
    # 만료되지 않은 토큰
    payload = {"user_id": 1, "role": "admin"}
    token = create_jwt_token(payload)
    assert not is_token_expired(token)

    # 만료된 토큰
    expired_payload = {
        "user_id": 1,
        "role": "admin",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    expired_token = create_jwt_token(expired_payload)
    assert is_token_expired(expired_token)


def test_token_expiration():
    """토큰 만료 시간 테스트"""
    # 1초 후 만료되는 토큰 생성
    payload = {"user_id": 1, "role": "admin"}
    token = create_jwt_token(payload, expires_delta=timedelta(seconds=1))
    
    # 만료 전 검증
    assert not is_token_expired(token)
    
    # 1초 대기
    time.sleep(1)
    
    # 만료 후 검증
    assert is_token_expired(token)


def test_token_with_custom_claims():
    """사용자 정의 클레임이 포함된 토큰 테스트"""
    payload = {
        "user_id": 1,
        "role": "admin",
        "custom_claim": "test_value"
    }
    token = create_jwt_token(payload)
    decoded = decode_jwt_token(token)
    
    assert decoded["user_id"] == payload["user_id"]
    assert decoded["role"] == payload["role"]
    assert decoded["custom_claim"] == payload["custom_claim"]


def test_token_with_empty_payload():
    """빈 페이로드로 토큰 생성 테스트"""
    token = create_jwt_token({})
    assert isinstance(token, str)
    assert "." in token
    decoded = decode_jwt_token(token)
    assert isinstance(decoded, dict)
    assert "exp" in decoded 


def test_create_access_token():
    """액세스 토큰 생성 테스트"""
    subject = "test_user"
    token = create_access_token(subject)
    assert isinstance(token, str)
    
    # 추가 데이터 포함 테스트
    extra_data = {"role": "admin"}
    token = create_access_token(subject, extra_data=extra_data)
    decoded = decode_jwt_token(token)
    assert decoded["sub"] == subject
    assert decoded["role"] == extra_data["role"]
    
    # 만료 시간 지정 테스트
    expires = timedelta(minutes=30)
    token = create_access_token(subject, expires_delta=expires)
    decoded = decode_jwt_token(token)
    exp_time = datetime.fromtimestamp(decoded["exp"], UTC)
    assert (exp_time - datetime.now(UTC)).total_seconds() > 1700  # 약 30분


def test_create_refresh_token():
    """리프레시 토큰 생성 테스트"""
    subject = "test_user"
    token = create_refresh_token(subject)
    assert isinstance(token, str)
    
    # 토큰 디코딩
    decoded = decode_jwt_token(token)
    assert decoded["sub"] == subject
    assert "exp" in decoded
    
    # 만료 시간 지정 테스트
    expires = timedelta(days=7)
    token = create_refresh_token(subject, expires_delta=expires)
    decoded = decode_jwt_token(token)
    exp_time = datetime.fromtimestamp(decoded["exp"], UTC)
    assert (exp_time - datetime.now(UTC)).total_seconds() > 604000  # 약 7일


def test_token_with_special_characters():
    """특수 문자 포함 토큰 테스트"""
    subject = "test_user!@#$%^&*()"
    token = create_access_token(subject)
    decoded = decode_jwt_token(token)
    assert decoded["sub"] == subject 