"""
# File: fastapi_template/app/db/schemas/token.py
# Description: JWT 토큰 관련 Pydantic 스키마 정의
"""

from pydantic import BaseModel
from typing import Optional, List


class Token(BaseModel):
    """
    JWT 액세스 토큰 응답 스키마
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    JWT 토큰 페이로드 스키마
    """
    sub: Optional[int] = None
    exp: Optional[int] = None
    scopes: List[str] = [] 