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


class FileEncryption:
    """
    PyNaCl을 사용한 파일 암호화 클래스
    
    NACL의 SecretBox를 사용하여 파일을 암호화/복호화합니다.
    """
    
    def __init__(self, key: Union[str, bytes, None] = None):
        """
        FileEncryption 클래스 초기화
        
        Args:
            key: 암호화 키 (문자열 또는 바이트)
                None인 경우 환경 변수에서 키를 가져옴
        """
        if key is None:
            key = os.environ.get("FILE_ENCRYPTION_KEY", "default_encryption_key")
        
        self.box = nacl.secret.SecretBox(self._prepare_key(key))
    
    def _prepare_key(self, key: Union[str, bytes, None]) -> bytes:
        """
        암호화 키를 적절한 형식으로 변환
        
        Args:
            key: 변환할 키
            
        Returns:
            bytes: 32바이트 키
        """
        try:
            if key is None:
                key = "default_encryption_key"
            
            if isinstance(key, str):
                # 문자열이 b'...' 형식인 경우
                if key.startswith("b'") and key.endswith("'"):
                    try:
                        key = eval(key)  # 안전한 환경에서만 사용
                    except:
                        key = key.encode('utf-8')
                else:
                    key = key.encode('utf-8')
            
            # 바이트로 변환 시도
            if not isinstance(key, bytes):
                try:
                    key = bytes(key)
                except (TypeError, ValueError):
                    try:
                        key = str(key).encode('utf-8')
                    except:
                        key = b"default_encryption_key"
            
            # 키 길이가 32바이트가 아닌 경우 해시로 변환
            if len(key) != nacl.secret.SecretBox.KEY_SIZE:
                key = hashlib.sha256(key).digest()
            
            return key
        except:
            return hashlib.sha256(b"default_encryption_key").digest()
    
    @staticmethod
    def generate_key() -> bytes:
        """
        새로운 암호화 키 생성
        
        Returns:
            bytes: 생성된 키
        """
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    
    def encrypt_file(self, input_file: Union[str, BinaryIO], output_file: Optional[Union[str, BinaryIO]] = None, chunk_size: int = 8192) -> Optional[bytes]:
        """
        파일 또는 데이터를 암호화
        
        Args:
            input_file: 입력 파일 경로 또는 파일 객체
            output_file: 출력 파일 경로 또는 파일 객체 (선택 사항)
            chunk_size: 청크 크기 (바이트)
            
        Returns:
            Optional[bytes]: 암호화된 데이터 (output_file이 None인 경우)
        """
        try:
            # 입력 파일 처리
            if isinstance(input_file, (str, bytes)):
                with open(input_file, 'rb') as f:
                    data = f.read()
            else:
                data = input_file.read()
                try:
                    input_file.close()
                except IOError:
                    pass

            # 데이터 암호화
            encrypted_data = self.box.encrypt(data)
            if encrypted_data is None:
                return None

            # 출력 파일이 지정된 경우 파일로 저장
            if output_file:
                try:
                    with open(output_file, 'wb') as f:
                        f.write(encrypted_data)
                    return True
                except IOError:
                    return None
            return encrypted_data
        except Exception:
            return None
    
    def decrypt_file(self, input_file: Union[str, BinaryIO], output_file: Optional[Union[str, BinaryIO]] = None, chunk_size: int = 8192) -> Union[Tuple[Optional[bytes], bool], Tuple[None, bool]]:
        """
        파일 또는 데이터를 복호화
        
        Args:
            input_file: 입력 파일 경로 또는 파일 객체
            output_file: 출력 파일 경로 또는 파일 객체 (선택 사항)
            chunk_size: 청크 크기 (바이트)
            
        Returns:
            Union[Tuple[Optional[bytes], bool], Tuple[None, bool]]: (복호화된 데이터, 성공 여부)
        """
        try:
            # 입력 파일 처리
            if isinstance(input_file, (str, bytes)):
                with open(input_file, 'rb') as f:
                    data = f.read()
            else:
                data = input_file.read()
                try:
                    input_file.close()
                except IOError:
                    pass

            # 데이터 복호화
            try:
                decrypted_data = self.box.decrypt(data)
            except Exception:
                return None, False

            # 출력 파일이 지정된 경우 파일로 저장
            if output_file:
                try:
                    with open(output_file, 'wb') as f:
                        f.write(decrypted_data)
                    return True, True
                except IOError:
                    return None, False
            return decrypted_data, True
        except Exception:
            return None, False


def encrypt_data_to_file(data: Union[str, bytes],
                        output_path: Union[str, bytes, os.PathLike]) -> bool:
    """
    데이터를 암호화하여 파일로 저장
    
    Args:
        data: 암호화할 데이터
        output_path: 출력 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    try:
        if data is None:
            return False
            
        if isinstance(data, str):
            try:
                data = data.encode('utf-8')
            except:
                return False
        
        encryptor = FileEncryption()
        try:
            encrypted = encryptor.box.encrypt(data)
        except:
            return False
        
        try:
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            return True
        except:
            return False
        
    except:
        return False


def decrypt_file_to_data(input_path: Union[str, bytes, os.PathLike],
                        as_string: bool = True) -> Optional[Union[str, bytes]]:
    """
    암호화된 파일에서 데이터 복호화
    
    Args:
        input_path: 입력 파일 경로
        as_string: 문자열로 반환 여부
        
    Returns:
        Optional[Union[str, bytes]]: 복호화된 데이터
    """
    try:
        encryptor = FileEncryption()
        
        with open(input_path, 'rb') as f:
            data = f.read()
            try:
                decrypted = encryptor.box.decrypt(data)
            except:
                return None
            
            if as_string:
                try:
                    return decrypted.decode('utf-8')
                except:
                    return None
            return decrypted
            
    except:
        return None


def encrypt_with_nacl(data: Union[str, bytes]) -> Optional[str]:
    """
    NaCl을 사용하여 데이터 암호화
    
    Args:
        data: 암호화할 데이터
        
    Returns:
        Optional[str]: Base64로 인코딩된 암호화 데이터
    """
    try:
        if data is None:
            return None
            
        if isinstance(data, str):
            try:
                data = data.encode('utf-8')
            except:
                return None
        
        encryptor = FileEncryption()
        try:
            encrypted = encryptor.box.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        except:
            return None
        
    except:
        return None


def decrypt_with_nacl(encrypted_data: str) -> Optional[str]:
    """
    NaCl을 사용하여 데이터 복호화
    
    Args:
        encrypted_data: Base64로 인코딩된 암호화 데이터
        
    Returns:
        Optional[str]: 복호화된 데이터
    """
    try:
        encryptor = FileEncryption()
        try:
            encrypted = base64.b64decode(encrypted_data)
        except:
            return None
            
        try:
            decrypted = encryptor.box.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except:
            return None
        
    except:
        return None 