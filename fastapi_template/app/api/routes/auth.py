"""
# File: fastapi_template/app/api/routes/auth.py
# Description: 인증 관련 API 엔드포인트 정의
# - JWT 토큰 발급 및 갱신
# - 로그인/로그아웃 처리
# - 인증 상태 확인
"""

from fastapi import APIRouter, Depends

router = APIRouter()


