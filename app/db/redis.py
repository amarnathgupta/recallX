import redis.asyncio as aioredis
from app.core.config import settings

_client = None

async def get_client() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _client

async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None