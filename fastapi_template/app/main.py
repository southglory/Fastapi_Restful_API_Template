"""
# File: fastapi_template/app/main.py
# Description: FastAPI 애플리케이션의 진입점
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.common.database import Base, engine
from app.common.exceptions import add_exception_handlers
from app.common.utils.cache import get_redis_connection
from app.common.config import settings

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트 처리
    """
    # 애플리케이션 시작 시 수행할 작업
    logger.info("애플리케이션 시작 중...")

    # Redis 연결 초기화
    try:
        redis = await get_redis_connection()
        await redis.ping()
        logger.info("Redis 연결 성공")
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")

    yield

    # 애플리케이션 종료 시 수행할 작업
    logger.info("애플리케이션 종료 중...")


# 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI RESTful API 템플릿",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 전역 예외 핸들러 추가
add_exception_handlers(app)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    루트 엔드포인트 - 애플리케이션 상태 확인
    """
    return {
        "app_name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "status": "healthy",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    상태 확인 엔드포인트 - 컨테이너 헬스체크용
    """
    return {"status": "ok"}
