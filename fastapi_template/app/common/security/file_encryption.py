"""
# File: fastapi_template/app/common/security/file_encryption.py
# Description: PyNaCl을 사용한 파일 암호화/복호화 유틸리티
"""

import os
import base64
import secrets
import hashlib
from typing import Union, Optional, BinaryIO, Tuple
from pathlib import Path

import nacl.secret
import nacl.utils
from nacl.exceptions import CryptoError

from app.common.config import settings
from app.common.security.encryption import get_encryption


class FileEncryption:
    """
    PyNaCl을 사용한 파일 암호화 클래스
    
    NACL의 SecretBox를 사용하여 파일을 암호화/복호화합니다.
    """
    
    def __init__(self, key: Optional[Union[str, bytes]] = None):
        """
        파일 암호화 클래스 초기화
        
        Args:
            key: 암호화에 사용할 키 (32바이트, None인 경우 환경에서 가져오거나 생성)
        """
        if key is None:
            # 환경 변수에서 키 가져오기 시도
            env_key = os.getenv("FILE_ENCRYPTION_KEY")
            if env_key:
                self.key = self._prepare_key(env_key)
            else:
                # 설정 파일의 SECRET_KEY에서 키 유도
                self.key = self._derive_key_from_secret(settings.SECRET_KEY)
        else:
            self.key = self._prepare_key(key)
            
        # SecretBox 초기화
        self.box = nacl.secret.SecretBox(self.key)
        
    def _prepare_key(self, key: Union[str, bytes]) -> bytes:
        """
        키를 NaCl에서 사용할 수 있는 형태로 변환
        
        Args:
            key: 입력 키 (문자열 또는 바이트)
            
        Returns:
            32바이트 키
        """
        if isinstance(key, str):
            # 문자열을 바이트로 변환
            if key.startswith("b'") and key.endswith("'"):
                try:
                    key = eval(key)  # b'...' 형식 문자열을 바이트로 변환
                except (SyntaxError, ValueError):
                    key = key.encode('utf-8')
            else:
                key = key.encode('utf-8')
        
        # 키가 32바이트가 아니면 SHA-256으로 해싱
        if len(key) != 32:
            key = hashlib.sha256(key).digest()
            
        return key
    
    def _derive_key_from_secret(self, secret: str) -> bytes:
        """
        비밀키에서 파일 암호화 키 유도
        
        Args:
            secret: 비밀키 문자열
            
        Returns:
            32바이트 키
        """
        return hashlib.sha256(secret.encode('utf-8')).digest()
    
    def encrypt_file(self, 
                    input_file: Union[str, Path, BinaryIO], 
                    output_file: Optional[Union[str, Path, BinaryIO]] = None,
                    chunk_size: int = 1024 * 1024  # 1MB 단위로 처리
                    ) -> Optional[bytes]:
        """
        파일을 암호화합니다.
        
        Args:
            input_file: 암호화할 파일 경로 또는 파일 객체
            output_file: 암호화된 파일을 저장할 경로 또는 파일 객체 (None이면 암호화된 데이터 반환)
            chunk_size: 한 번에 처리할 청크 크기 (바이트)
            
        Returns:
            output_file이 None이면 암호화된 바이트 데이터 반환, 그렇지 않으면 None
        """
        # 파일 또는 파일 객체 관리
        close_input = False
        close_output = False
        
        # 버퍼링을 위한 바이트 배열
        result_buffer = bytearray() if output_file is None else None
        
        try:
            # 입력 파일 열기
            if isinstance(input_file, (str, Path)):
                input_file = open(input_file, 'rb')
                close_input = True
                
            # 출력 파일 열기 (필요한 경우)
            if output_file is not None and isinstance(output_file, (str, Path)):
                output_file = open(output_file, 'wb')
                close_output = True
                
            # 논스 생성 (24바이트)
            nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
            
            # 논스 먼저 쓰기
            if output_file is not None:
                output_file.write(nonce)
            else:
                result_buffer.extend(nonce)
                
            # 전체 데이터 읽기
            data = input_file.read()
            
            # 데이터 암호화
            encrypted = self.box.encrypt(data, nonce=nonce)
            
            # 암호화된 데이터 쓰기 (논스 제외)
            if output_file is not None:
                output_file.write(encrypted.ciphertext)
            else:
                result_buffer.extend(encrypted.ciphertext)
                
            # 버퍼에 데이터가 있으면 반환
            if result_buffer:
                return bytes(result_buffer)
                
            return None
                
        finally:
            # 열었던 파일 닫기
            if close_input and input_file:
                input_file.close()
            if close_output and output_file:
                output_file.close()
    
    def decrypt_file(self, 
                    input_file: Union[str, Path, BinaryIO], 
                    output_file: Optional[Union[str, Path, BinaryIO]] = None,
                    chunk_size: int = 1024 * 1024  # 1MB 단위로 처리
                    ) -> Optional[Tuple[bytes, bool]]:
        """
        암호화된 파일을 복호화합니다.
        
        Args:
            input_file: 복호화할 파일 경로 또는 파일 객체
            output_file: 복호화된 파일을 저장할 경로 또는 파일 객체 (None이면 복호화된 데이터 반환)
            chunk_size: 한 번에 처리할 청크 크기 (바이트)
            
        Returns:
            output_file이 None이면 (복호화된 바이트 데이터, 성공 여부) 튜플 반환, 그렇지 않으면 None
        """
        # 파일 또는 파일 객체 관리
        close_input = False
        close_output = False
        
        # 버퍼링을 위한 바이트 배열
        result_buffer = bytearray() if output_file is None else None
        
        try:
            # 입력 파일 열기
            if isinstance(input_file, (str, Path)):
                input_file = open(input_file, 'rb')
                close_input = True
                
            # 출력 파일 열기 (필요한 경우)
            if output_file is not None and isinstance(output_file, (str, Path)):
                output_file = open(output_file, 'wb')
                close_output = True
                
            # 논스 읽기 (24바이트)
            nonce = input_file.read(nacl.secret.SecretBox.NONCE_SIZE)
            if len(nonce) != nacl.secret.SecretBox.NONCE_SIZE:
                raise ValueError("Invalid encrypted file format (missing nonce)")
            
            try:
                # 나머지 데이터 모두 읽기
                ciphertext = input_file.read()
                
                # 데이터 복호화
                decrypted = self.box.decrypt(ciphertext, nonce=nonce)
                
                # 복호화된 데이터 쓰기
                if output_file is not None:
                    output_file.write(decrypted)
                    return None
                else:
                    return decrypted, True
                
            except CryptoError:
                # 복호화 실패
                if output_file is not None:
                    return None
                else:
                    return b'', False
                
        finally:
            # 열었던 파일 닫기
            if close_input and input_file:
                input_file.close()
            if close_output and output_file:
                output_file.close()

    @staticmethod
    def generate_key() -> bytes:
        """
        파일 암호화용 랜덤 키 생성
        
        Returns:
            32바이트 랜덤 키
        """
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


# 문자열과 작은 파일을 위한 간단한 유틸리티 함수
def encrypt_data_to_file(data: Union[str, bytes], output_file: Union[str, Path]) -> bool:
    """
    데이터를 암호화하여 파일에 저장합니다.
    
    Args:
        data: 암호화할 데이터 (문자열 또는 바이트)
        output_file: 암호화된 데이터를 저장할 파일 경로
        
    Returns:
        성공 여부
    """
    try:
        # 문자열을 바이트로 변환
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # 암호화 객체 생성
        encryptor = FileEncryption()
        
        # 데이터를 파일로 암호화
        with open(output_file, 'wb') as f:
            nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
            f.write(nonce)
            
            encrypted = encryptor.box.encrypt(data, nonce=nonce)
            f.write(encrypted.ciphertext)
            
        return True
    except Exception:
        return False


def decrypt_file_to_data(input_file: Union[str, Path], as_string: bool = True) -> Union[str, bytes, None]:
    """
    암호화된 파일을 복호화하여 데이터로 반환합니다.
    
    Args:
        input_file: 복호화할 파일 경로
        as_string: True면 문자열로, False면 바이트로 반환
        
    Returns:
        복호화된 데이터 (복호화 실패 시 None)
    """
    try:
        # 암호화 객체 생성
        decryptor = FileEncryption()
        
        # 파일에서 데이터 읽기
        with open(input_file, 'rb') as f:
            nonce = f.read(nacl.secret.SecretBox.NONCE_SIZE)
            if len(nonce) != nacl.secret.SecretBox.NONCE_SIZE:
                return None
                
            encrypted_data = f.read()
            
            # 복호화
            decrypted = decryptor.box.decrypt(encrypted_data, nonce=nonce)
            
            # 요청에 따라 문자열 또는 바이트로 반환
            if as_string:
                return decrypted.decode('utf-8')
            return decrypted
    except Exception:
        return None


# 간단한 데이터 암호화/복호화 유틸리티 함수 (기존 encryption 모듈과의 통합)
def encrypt_with_nacl(data: Union[str, bytes]) -> str:
    """
    데이터를 NaCl로 암호화합니다.
    
    Args:
        data: 암호화할 데이터 (문자열 또는 바이트)
        
    Returns:
        Base64 인코딩된 암호화 데이터
    """
    # 암호화 객체 생성
    encryptor = FileEncryption()
    
    # 문자열을 바이트로 변환
    if isinstance(data, str):
        data = data.encode('utf-8')
        
    # 암호화
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    encrypted = encryptor.box.encrypt(data, nonce=nonce)
    
    # Base64 인코딩하여 반환
    return base64.urlsafe_b64encode(nonce + encrypted.ciphertext).decode('utf-8')


def decrypt_with_nacl(encrypted_data: str) -> Union[str, None]:
    """
    NaCl로 암호화된 데이터를 복호화합니다.
    
    Args:
        encrypted_data: Base64 인코딩된 암호화 데이터
        
    Returns:
        복호화된 문자열 (실패 시 None)
    """
    try:
        # 암호화 객체 생성
        decryptor = FileEncryption()
        
        # Base64 디코딩
        data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        
        # 논스와 암호문 분리
        nonce = data[:nacl.secret.SecretBox.NONCE_SIZE]
        ciphertext = data[nacl.secret.SecretBox.NONCE_SIZE:]
        
        # 복호화
        decrypted = decryptor.box.decrypt(ciphertext, nonce=nonce)
        return decrypted.decode('utf-8')
    except Exception:
        return None 