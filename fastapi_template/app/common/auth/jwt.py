"""
# File: fastapi_template/app/common/auth/jwt.py
# Description: JWT 인증 관련 유틸리티 함수
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt, JWTError
from pydantic import ValidationError

from app.common.config import settings
from app.common.exceptions import AuthenticationError
from app.db.schemas.token import TokenPayload


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰 생성
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰 검증 및 디코딩
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if (
            token_data.exp is not None
            and datetime.fromtimestamp(float(token_data.exp)) < datetime.utcnow()
        ):
            raise ValidationError("Token expired")

        return payload
    except (JWTError, ValidationError):
        raise ValidationError("Could not validate credentials")
