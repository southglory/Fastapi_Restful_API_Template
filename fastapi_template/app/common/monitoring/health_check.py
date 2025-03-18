from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict

from ..database.session import get_db
from ..cache.redis_client import get_redis_connection, RedisCacheBackend

router = APIRouter()


async def check_database(db: AsyncSession) -> Dict[str, bool]:
    try:
        await db.execute(text("SELECT 1"))
        return {"database": True}
    except Exception:
        return {"database": False}


async def check_redis() -> Dict[str, bool]:
    try:
        redis_conn = await get_redis_connection()
        cache = RedisCacheBackend(redis_conn)
        await cache.set("health_check", "ok", 1)
        return {"redis": True}
    except Exception:
        return {"redis": False}


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    db_status = await check_database(db)
    redis_status = await check_redis()

    return {**db_status, **redis_status, "api": True}
