"""
# File: fastapi_template/app/common/security/token.py
# Description: 보안 토큰 생성 및 관리 유틸리티 (PyJWT 사용)
"""

import time
import uuid
import secrets
import base64
import hmac
import hashlib
import jwt
from typing import Dict, Union, Optional, Tuple, Any
from datetime import datetime, timedelta, UTC

from app.common.config import settings


def generate_secure_token(length: int = 32) -> str:
    """
    안전한 랜덤 토큰을 생성합니다.
    
    Args:
        length: 생성할 토큰의 길이 (바이트 수 아님)
        
    Returns:
        지정된 길이의 랜덤 토큰 (16진수 문자열)
    """
    # length를 바이트 수로 변환 (2글자 = 1바이트)
    byte_length = length // 2
    # 나머지가 있으면 1 추가
    if length % 2 == 1:
        byte_length += 1
        
    # 랜덤 바이트 생성
    token = secrets.token_hex(byte_length)
    return token[:length]  # 길이가 홀수인 경우 맞춰서 반환


def generate_uuid() -> str:
    """
    UUID를 생성합니다.
    
    Returns:
        UUID 문자열
    """
    return str(uuid.uuid4())


def sign_data(data: str, secret: Optional[str] = None) -> str:
    """
    데이터에 서명을 추가합니다.
    
    Args:
        data: 서명할 데이터 문자열
        secret: 서명에 사용할 비밀키 (None인 경우 설정값 사용)
        
    Returns:
        서명된 데이터 (데이터.서명 형식)
    """
    if secret is None:
        secret = settings.SECRET_KEY
        
    # 데이터에 HMAC-SHA256 서명 생성
    signature = hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 원본 데이터.서명 형식으로 반환
    return f"{data}.{signature}"


def verify_signature(signed_data: str, secret: Optional[str] = None) -> Tuple[bool, str]:
    """
    서명된 데이터를 검증합니다.
    
    Args:
        signed_data: 검증할 서명된 데이터 (데이터.서명 형식)
        secret: 서명에 사용된 비밀키 (None인 경우 설정값 사용)
        
    Returns:
        (검증 결과, 원본 데이터) 튜플
    """
    try:
        # 데이터와 서명 분리
        data, signature = signed_data.rsplit('.', 1)
        
        # 같은 방식으로 서명을 생성하여 비교
        verified_data = sign_data(data, secret)
        _, verified_signature = verified_data.rsplit('.', 1)
        
        # 서명 일치 여부 확인
        if signature == verified_signature:
            return True, data
        else:
            return False, ""
    except (ValueError, AttributeError):
        # 형식이 잘못된 경우
        return False, ""


def generate_timed_token(user_id: Union[str, int], expires_in: int = 3600) -> str:
    """
    만료 시간이 포함된 토큰을 생성합니다.
    
    Args:
        user_id: 사용자 ID
        expires_in: 토큰 만료 시간 (초)
        
    Returns:
        서명된 토큰 문자열
    """
    # 현재 시간 + 만료 시간
    expiry = int(time.time()) + expires_in
    
    # 토큰 데이터 생성
    token_data = f"{user_id}:{expiry}"
    
    # 서명 추가
    return sign_data(token_data)


def validate_token(token: str) -> Dict[str, Union[bool, str, int]]:
    """
    토큰을 검증합니다.
    
    Args:
        token: 검증할 토큰
        
    Returns:
        검증 결과 정보가 담긴 딕셔너리
    """
    # 서명 검증
    is_valid, data = verify_signature(token)
    
    if not is_valid:
        return {
            "valid": False,
            "error": "Invalid signature"
        }
    
    try:
        # 토큰 데이터 파싱
        user_id, expiry_str = data.split(':')
        expiry = int(expiry_str)
        
        # 만료 시간 검증 (여기서 time.time() 함수를 직접 호출해야 모킹 가능)
        current_time = int(time.time())
        if current_time > expiry:
            return {
                "valid": False,
                "error": "Token expired",
                "user_id": user_id,
                "expiry": expiry
            }
        
        # 유효한 토큰
        return {
            "valid": True,
            "user_id": user_id,
            "expiry": expiry,
            "expires_in": expiry - current_time  # 남은 시간 (초)
        }
    except (ValueError, IndexError):
        # 형식이 잘못된 경우
        return {
            "valid": False,
            "error": "Malformed token"
        }


# PyJWT를 사용한 JWT 토큰 함수 추가
def create_jwt_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None
) -> str:
    """
    JWT 토큰을 생성합니다.
    
    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (None인 경우 기본값 15분)
        secret_key: 서명에 사용할 비밀키 (None인 경우 설정값 사용)
        
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 비밀키 설정
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode, 
        secret_key, 
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_jwt_token(
    token: str, 
    secret_key: Optional[str] = None, 
    verify_expiration: bool = True
) -> Dict[str, Any]:
    """
    JWT 토큰을 디코딩합니다.
    
    Args:
        token: 디코딩할 JWT 토큰
        secret_key: 서명 검증에 사용할 비밀키 (None인 경우 설정값 사용)
        verify_expiration: 만료 시간 검증 여부
        
    Returns:
        디코딩된 토큰 데이터
        
    Raises:
        jwt.InvalidTokenError: 토큰이 유효하지 않을 경우
        jwt.ExpiredSignatureError: 토큰이 만료된 경우
    """
    # 비밀키 설정
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    # JWT 토큰 디코딩
    return jwt.decode(
        token, 
        secret_key, 
        algorithms=["HS256"],
        options={"verify_exp": verify_expiration}
    )


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    사용자 액세스 토큰을 생성합니다.
    
    Args:
        subject: 토큰 주체 (일반적으로 사용자 ID)
        expires_delta: 만료 시간 (None인 경우 기본값 사용)
        secret_key: 서명에 사용할 비밀키 (None인 경우 설정값 사용)
        extra_data: 토큰에 추가할 데이터
        
    Returns:
        JWT 액세스 토큰
    """
    # 기본 만료 시간이 설정되지 않은 경우 기본값 사용
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 기본 클레임 설정
    to_encode = {
        "sub": str(subject),
        "iat": datetime.now(UTC),
        "type": "access"
    }
    
    # 추가 데이터가 있으면 병합
    if extra_data:
        to_encode.update(extra_data)
    
    # JWT 토큰 생성
    return create_jwt_token(to_encode, expires_delta, secret_key)


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None
) -> str:
    """
    사용자 리프레시 토큰을 생성합니다.
    
    Args:
        subject: 토큰 주체 (일반적으로 사용자 ID)
        expires_delta: 만료 시간 (None인 경우 기본값 사용)
        secret_key: 서명에 사용할 비밀키 (None인 경우 설정값 사용)
        
    Returns:
        JWT 리프레시 토큰
    """
    # 기본 만료 시간이 설정되지 않은 경우 기본값 사용
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # 기본 클레임 설정
    to_encode = {
        "sub": str(subject),
        "iat": datetime.now(UTC),
        "type": "refresh"
    }
    
    # JWT 토큰 생성
    return create_jwt_token(to_encode, expires_delta, secret_key) 