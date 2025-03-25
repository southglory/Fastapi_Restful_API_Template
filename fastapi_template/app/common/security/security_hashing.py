"""
# File: fastapi_template/app/common/security/hashing.py
# Description: 패스워드 해싱 및 검증 유틸리티
"""

import hashlib
import secrets
import base64
from typing import Tuple


def hash_password(password: str, salt: str = None) -> str:
    """
    패스워드를 해싱합니다.
    
    Args:
        password: 해싱할 패스워드
        salt: 사용할 솔트 (None인 경우 랜덤 생성)
        
    Returns:
        솔트와 해시를 포함한 해시된 패스워드 문자열
    """
    if salt is None:
        salt = secrets.token_hex(16)  # 32자 길이의 랜덤 솔트 생성
        
    # 패스워드와 솔트를 합쳐서 해싱
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'), 
        salt.encode('utf-8'),
        100000  # 반복 횟수
    )
    
    # base64로 인코딩
    b64_hash = base64.b64encode(pw_hash).decode('utf-8')
    
    # 솔트와 해시를 함께 저장 (형식: salt$hash)
    return f"{salt}${b64_hash}"


def verify_hash(password: str, hashed_password: str) -> bool:
    """
    패스워드가 해시와 일치하는지 검증합니다.
    
    Args:
        password: 검증할 패스워드
        hashed_password: 저장된 해시 문자열 (hash_password 반환값)
        
    Returns:
        패스워드가 해시와 일치하면 True, 아니면 False
    """
    # None 또는 빈 문자열 검증
    if not hashed_password:
        return False
        
    # 솔트와 해시 분리
    try:
        salt, stored_hash = hashed_password.split('$')
        
        # 동일한 방식으로 해싱하여 비교
        pw_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 동일한 반복 횟수
        )
        
        # base64로 인코딩하여 비교
        computed_hash = base64.b64encode(pw_hash).decode('utf-8')
        
        return computed_hash == stored_hash
    except (ValueError, TypeError, AttributeError):
        # 형식이 잘못되었거나 예외 발생 시 검증 실패
        return False


def generate_hash(data: str) -> str:
    """
    주어진 데이터의 SHA-256 해시를 생성합니다.
    
    Args:
        data: 해싱할 데이터 문자열
        
    Returns:
        16진수 형식의 해시 문자열
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_token() -> str:
    """
    랜덤 토큰을 생성합니다. (32자 길이)
    
    Returns:
        16진수 형식의 랜덤 토큰
    """
    return secrets.token_hex(16)


def hash_file_contents(file_path: str) -> Tuple[str, str]:
    """
    파일 내용의 해시를 계산합니다.
    
    Args:
        file_path: 해싱할 파일 경로
        
    Returns:
        (md5_hash, sha256_hash) 튜플
    """
    md5_hasher = hashlib.md5()
    sha256_hasher = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            # 파일을 청크 단위로 읽어 해싱
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hasher.update(chunk)
                sha256_hasher.update(chunk)
                
        return md5_hasher.hexdigest(), sha256_hasher.hexdigest()
    except (IOError, OSError):
        # 파일을 열 수 없는 경우
        return '', ''


# 표준 인터페이스 함수 추가 (다른 모듈과의 일관성)
def get_password_hash(password: str) -> str:
    """
    패스워드를 해싱합니다. (표준 인터페이스 - hash_password의 별칭)
    
    Args:
        password: 해싱할 패스워드
        
    Returns:
        해싱된 패스워드
    """
    return hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    패스워드를 검증합니다. (표준 인터페이스 - verify_hash의 별칭)
    
    Args:
        plain_password: 평문 패스워드
        hashed_password: 해시된 패스워드
        
    Returns:
        일치 여부
    """
    return verify_hash(plain_password, hashed_password) 