"""
# File: fastapi_template/app/common/auth/password.py
# Description: 비밀번호 해싱 및 검증 유틸리티
"""

from typing import Tuple

from passlib.context import CryptContext
from app.common.validators.string_validators import validate_password_strength as validator_password_strength

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 텍스트 비밀번호와 해시된 비밀번호를 비교하여 일치 여부 확인
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호를 안전한 해시로 변환
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    비밀번호 강도를 검증하는 함수
    
    이 함수는 validators 모듈의 함수를 래핑합니다.
    
    Args:
        password: 검증할 비밀번호
        
    Returns:
        tuple[bool, str]: (검증 결과, 실패 시 오류 메시지)
    """
    return validator_password_strength(password)

