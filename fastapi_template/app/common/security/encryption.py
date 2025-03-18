"""
# File: fastapi_template/app/common/security/encryption.py
# Description: 데이터 암호화/복호화 유틸리티
"""

import os
import base64
from typing import Optional, Union, Any, cast, TypeVar

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.common.config import settings


class Encryption:
    """
    암호화/복호화 유틸리티 클래스

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
            key: 직접 제공하는 암호화 키 (base64 인코딩된 문자열 또는 바이트)
            salt: PBKDF2 키 유도에 사용할 솔트
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
            self.key: Union[str, bytes] = key
        elif os.getenv("ENCRYPTION_KEY"):
            # 환경 변수에서 키 사용
            env_key = os.getenv("ENCRYPTION_KEY")
            self.key = (
                env_key if env_key is not None else self._derive_key_from_secret(salt)
            )
        else:
            # settings.SECRET_KEY에서 키 유도 또는 랜덤 생성
            self.key = self._derive_key_from_secret(salt)

        # Fernet 암호화 객체 생성
        try:
            # 문자열인 경우 바이트로 변환
            if isinstance(self.key, str):
                key_bytes = (
                    self.key.encode()
                    if not self.key.startswith("b'")
                    else eval(self.key)
                )
                self.fernet = Fernet(key_bytes)
            # 바이트인 경우 직접 사용
            elif isinstance(self.key, bytes):
                self.fernet = Fernet(self.key)
            # 다른 타입이거나 None인 경우 새 키 생성
            else:
                self.key = Fernet.generate_key()
                self.fernet = Fernet(self.key)
        except (TypeError, ValueError):
            # 키 변환 시도
            try:
                # 키가 바이트 배열이지만 base64 인코딩이 아닌 경우
                if isinstance(self.key, bytes):
                    encoded_key = base64.urlsafe_b64encode(self.key)
                    self.fernet = Fernet(encoded_key)
                else:
                    # 변환 불가능한 키이므로 새 키 생성
                    self.key = Fernet.generate_key()
                    self.fernet = Fernet(self.key)
            except Exception:
                # 최종적으로 새 키 생성
                self.key = Fernet.generate_key()
                self.fernet = Fernet(self.key)

        self._initialized = True

    def _derive_key_from_secret(self, salt: Optional[bytes] = None) -> bytes:
        """설정의 SECRET_KEY에서 암호화 키 유도"""
        # 비밀 키가 없으면 랜덤 생성
        if not settings.SECRET_KEY:
            return self.generate_key()

        # 비밀 키를 바이트로 변환
        secret_key = settings.SECRET_KEY.encode()

        # 솔트 설정
        if salt is None:
            salt = b"fastapi_template_salt"

        # PBKDF2를 사용해 키 유도
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
        return key

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

        encrypted = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        암호화된 데이터 복호화

        Args:
            encrypted_data: 암호화된 데이터 (base64 인코딩된 문자열)

        Returns:
            복호화된 문자열
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()

    @staticmethod
    def generate_key() -> bytes:
        """암호화에 사용할 랜덤 키 생성"""
        return Fernet.generate_key()


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
