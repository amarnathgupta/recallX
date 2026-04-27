import asyncio
from sqlalchemy import create_engine, text
# import asyncpg
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
import redis
from app.core.config import settings


# 🔁 retry helper
async def retry_async(func, retries=10, delay=2):
    for i in range(retries):
        try:
            await func()
            return True
        except Exception as e:
            print(f"Retry {i+1} failed:", e)
            await asyncio.sleep(delay)
    raise Exception("Service not available after retries")


def retry_sync(func, retries=10, delay=2):
    import time
    for i in range(retries):
        try:
            func()
            return True
        except Exception as e:
            print(f"Retry {i+1} failed:", e)
            time.sleep(delay)
    raise Exception("Service not available after retries")


# 🔌 checks
# async def check_postgres():
def check_postgres():
    engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    print("✅ PostgreSQL ready")
    # conn = await asyncpg.connect(
    #     user=settings.POSTGRES_USER,
    #     password=settings.POSTGRES_PASSWORD,
    #     database=settings.POSTGRES_DB,
    #     host=settings.POSTGRES_HOST,
    #     port=settings.POSTGRES_PORT,
    # )
    # await conn.close()
    # print("✅ PostgreSQL ready")


def check_qdrant():
    client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )
    client.get_collections()
    print("✅ Qdrant ready")


def check_neo4j():
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )
    with driver.session() as session:
        session.run("RETURN 1").consume()
    driver.close()
    print("✅ Neo4j ready")


def check_redis():
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        socket_timeout=5,
    )
    r.ping()
    print("✅ Redis ready")


# 🚀 main wait function
async def wait_for_services():
    print("⏳ Waiting for services...")

    # await retry_async(check_postgres)

    await asyncio.gather(
        asyncio.to_thread(retry_sync, check_postgres),
        asyncio.to_thread(retry_sync, check_qdrant),
        asyncio.to_thread(retry_sync, check_neo4j),
        asyncio.to_thread(retry_sync, check_redis),
    )

    print("🚀 All services are ready!")

if __name__ == "__main__":
    asyncio.run(wait_for_services())