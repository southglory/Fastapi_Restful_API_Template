"""
# File: fastapi_template/app/common/auth/password.py
# Description: 비밀번호 해싱 및 검증 유틸리티
"""

from passlib.context import CryptContext

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