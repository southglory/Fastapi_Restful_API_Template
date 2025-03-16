"""
# File: fastapi_template/app/main.py
# Description: FastAPI 애플리케이션의 진입점
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="FastAPI RESTful API 템플릿",
    version="0.1.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    """애플리케이션 시작 시 실행되는 이벤트 핸들러"""
    # 데이터베이스 연결 테스트 등의 작업 수행
    pass

@app.on_event("shutdown")
async def shutdown_db_client():
    """애플리케이션 종료 시 실행되는 이벤트 핸들러"""
    # 리소스 정리 작업 수행
    pass

@app.get("/")
def root():
    """루트 엔드포인트"""
    return {"message": "Welcome to FastAPI RESTful API Template"}
