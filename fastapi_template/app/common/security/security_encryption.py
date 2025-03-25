"""
# File: fastapi_template/app/common/security/encryption.py
# Description: 데이터 암호화/복호화 유틸리티 (표준 라이브러리 사용 버전)
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Union, Any, cast, TypeVar

from fastapi_template.app.common.config import config_settings


class Encryption:
    """
    암호화/복호화 유틸리티 클래스 (표준 라이브러리 사용 버전)

    다양한 방식으로 키를 생성할 수 있습니다:
    1. 직접 키를 제공 (init)
    2. 환경 변수 사용 (ENCRYPTION_KEY)
    3. settings.SECRET_KEY에서 키 유도 (기본 동작)
    4. 랜덤 키 생성 (마지막 대안)
    """

    _instance = None  # 싱글톤 패턴을 위한 클래스 변수

    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(Encryption, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self, key: Optional[Union[str, bytes]] = None, salt: Optional[bytes] = None
    ):
        """
        암호화/복호화 유틸리티 초기화

        Args:
            key: 직접 제공하는 암호화 키 (문자열 또는 바이트)
            salt: 키 유도에 사용할 솔트
        """
        # 이미 초기화되었으면 스킵
        if getattr(self, "_initialized", False):
            return

        # 키 설정 우선순위:
        # 1. 직접 전달된 키
        # 2. 환경 변수 ENCRYPTION_KEY
        # 3. settings.SECRET_KEY에서 유도
        # 4. 랜덤 생성
        if key:
            # 직접 전달된 키 사용
            self.key = self._convert_key_to_bytes(key)
        elif os.getenv("ENCRYPTION_KEY"):
            # 환경 변수에서 키 사용
            env_key = os.getenv("ENCRYPTION_KEY")
            if env_key:
                self.key = self._convert_key_to_bytes(env_key)
            else:
                self.key = self._derive_key_from_secret(salt)
        else:
            # settings.SECRET_KEY에서 키 유도 또는 랜덤 생성
            self.key = self._derive_key_from_secret(salt)
            
        # 솔트 저장
        self.salt = salt or b"default_salt_for_encryption"
        
        self._initialized = True
    
    def _convert_key_to_bytes(self, key: Union[str, bytes]) -> bytes:
        """키를 바이트로 변환"""
        if isinstance(key, str):
            # 문자열을 바이트로 변환
            if key.startswith("b'") and key.endswith("'"):
                try:
                    return eval(key)  # b'...' 형식의 문자열을 바이트로 변환
                except (SyntaxError, ValueError):
                    pass
            return key.encode('utf-8')
        return key

    def _derive_key_from_secret(self, salt: Optional[bytes] = None) -> bytes:
        """설정의 SECRET_KEY에서 암호화 키 유도"""
        # 비밀 키가 없으면 랜덤 생성
        if not config_settings.SECRET_KEY:
            return self.generate_key()

        # 비밀 키를 바이트로 변환
        secret_key = config_settings.SECRET_KEY.encode()

        # 솔트 설정
        if salt is None:
            salt = b"fastapi_template_salt"

        # PBKDF2를 사용해 키 유도
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            secret_key,
            salt,
            iterations=100000,
            dklen=32
        )
        
        return dk

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        데이터 암호화

        Args:
            data: 암호화할 문자열 또는 바이트

        Returns:
            암호화된 데이터 (base64 인코딩된 문자열)
        """
        if isinstance(data, str):
            data = data.encode()

        # 랜덤 초기화 벡터 생성 (16바이트)
        iv = secrets.token_bytes(16)
        
        # 키에서 암호화 키 유도
        cipher_key = hashlib.pbkdf2_hmac(
            'sha256',
            self.key,
            iv,
            iterations=1000,
            dklen=32
        )
        
        # XOR 기반 암호화
        xored = bytearray()
        for i, byte in enumerate(data):
            key_byte = cipher_key[i % len(cipher_key)]
            xored.append(byte ^ key_byte)
        
        # IV와 암호화된 데이터 결합
        encrypted = iv + bytes(xored)
        
        # Base64 인코딩
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        암호화된 데이터 복호화

        Args:
            encrypted_data: 암호화된 데이터 (base64 인코딩된 문자열)

        Returns:
            복호화된 문자열
        """
        try:
            # Base64 디코딩
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # IV 추출 (처음 16바이트)
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # 키에서 암호화 키 유도
            cipher_key = hashlib.pbkdf2_hmac(
                'sha256',
                self.key,
                iv,
                iterations=1000,
                dklen=32
            )
            
            # XOR 기반 복호화
            decrypted = bytearray()
            for i, byte in enumerate(ciphertext):
                key_byte = cipher_key[i % len(cipher_key)]
                decrypted.append(byte ^ key_byte)
            
            return bytes(decrypted).decode()
        except Exception as e:
            # 복호화 실패 시
            raise ValueError(f"복호화 실패: {str(e)}")

    @staticmethod
    def generate_key() -> bytes:
        """암호화에 사용할 랜덤 키 생성 (32바이트)"""
        return secrets.token_bytes(32)


# 모듈 레벨에서 사용할 수 있는 싱글톤 인스턴스
_encryption = None


def get_encryption() -> Encryption:
    """암호화 유틸리티 싱글톤 인스턴스 반환"""
    global _encryption
    if _encryption is None:
        _encryption = Encryption()
    return _encryption


# 간편한 함수 인터페이스 제공
def encrypt_data(data: Union[str, bytes]) -> str:
    """문자열 또는 바이트 데이터 암호화"""
    return get_encryption().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """암호화된 문자열 데이터 복호화"""
    return get_encryption().decrypt(encrypted_data)


# 새로운 함수 인터페이스 (이름 변경 버전)
def encrypt_text(data: Union[str, bytes]) -> str:
    """
    문자열 또는 바이트 데이터 암호화 (encrypt_data의 별칭)
    
    Args:
        data: 암호화할 문자열 또는 바이트
        
    Returns:
        암호화된 데이터 (base64 인코딩된 문자열)
    """
    return encrypt_data(data)


def decrypt_text(encrypted_data: str) -> str:
    """
    암호화된 문자열 데이터 복호화 (decrypt_data의 별칭)
    
    Args:
        encrypted_data: 암호화된 데이터 (base64 인코딩된 문자열)
        
    Returns:
        복호화된 문자열
    """
    return decrypt_data(encrypted_data)


def validate_key(key: Union[str, bytes]) -> bool:
    """
    암호화 키의 유효성 검사
    
    Args:
        key: 검사할 암호화 키 (문자열 또는 바이트)
        
    Returns:
        유효한 키인지 여부
    """
    try:
        # 키 변환 시도
        key_bytes = Encryption()._convert_key_to_bytes(key)
        return len(key_bytes) >= 16  # 최소 16바이트 이상이어야 함
    except Exception:
        return False
