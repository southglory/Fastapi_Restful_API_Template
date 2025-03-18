"""
# File: fastapi_template/app/db/schemas/token.py
# Description: JWT 토큰 관련 Pydantic 스키마 정의
"""

from typing import Optional, List
from pydantic import Field

from app.common.schemas.base_schema import OutputSchema, InternalSchema


class Token(OutputSchema):
    """JWT 액세스 토큰 응답 스키마 (시스템 → 외부)"""

    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")


class TokenPayload(InternalSchema):
    """JWT 토큰 페이로드 스키마 (시스템 내부용)"""

    sub: Optional[int] = Field(None, description="토큰 주체(사용자 ID)")
    exp: Optional[int] = Field(None, description="토큰 만료 시간")
    scopes: List[str] = Field(default=[], description="토큰 접근 범위")
