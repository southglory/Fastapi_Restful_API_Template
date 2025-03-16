"""
# File: fastapi_template/app/api/routes/users.py
# Description: 사용자 관련 CRUD API 엔드포인트 정의
# - 사용자 생성, 조회, 수정, 삭제 기능
# - 사용자 인증 및 권한 검증
"""

from fastapi import APIRouter, Depends

router = APIRouter()


