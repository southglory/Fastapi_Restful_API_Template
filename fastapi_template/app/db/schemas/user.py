"""
# File: fastapi_template/app/db/schemas/user.py
# Description: 사용자 관련 Pydantic 스키마 정의
# - 요청/응답 데이터 검증
# - API 문서화를 위한 스키마
# - 데이터 직렬화/역직렬화
"""

from pydantic import BaseModel, EmailStr


