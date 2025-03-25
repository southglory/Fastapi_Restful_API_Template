"""
# File: fastapi_template/app/common/security/__init__.py
# Description: 보안 관련 모듈 (암호화, 해싱, 토큰)
"""

from app.common.security.security_encryption import (
    get_encryption, 
    encrypt_text, 
    decrypt_text,
    validate_key
)
from app.common.security.security_hashing import (
    get_password_hash, 
    verify_password, 
    verify_hash
)
from app.common.security.security_token import (
    generate_secure_token,
    generate_uuid,
    sign_data,
    verify_signature,
    generate_timed_token,
    validate_token,
    create_jwt_token,
    decode_jwt_token,
    create_access_token,
    create_refresh_token
)
from app.common.security.security_file_encryption import (
    FileEncryption,
    encrypt_data_to_file,
    decrypt_file_to_data,
    encrypt_with_nacl,
    decrypt_with_nacl
)

__all__ = [
    # 암호화 모듈
    "get_encryption", 
    "encrypt_text", 
    "decrypt_text",
    "validate_key",
    
    # 해싱 모듈
    "get_password_hash", 
    "verify_password", 
    "verify_hash",
    
    # 토큰 모듈
    "generate_secure_token",
    "generate_uuid",
    "sign_data",
    "verify_signature",
    "generate_timed_token",
    "validate_token",
    "create_jwt_token",
    "decode_jwt_token",
    "create_access_token",
    "create_refresh_token",
    
    # 파일 암호화 모듈
    "FileEncryption",
    "encrypt_data_to_file",
    "decrypt_file_to_data",
    "encrypt_with_nacl",
    "decrypt_with_nacl"
]
