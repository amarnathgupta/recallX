from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.postgres import engine
from app.db.base import Base
from app.db.vectordb import init_collection
from app.db.graphdb import init_constraints, close_driver
from app.db.redis import get_client, close_client


import app.models.user
import app.models.message
import app.models.memory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Postgres tables ready")

    init_collection()
    await init_constraints()
    await get_client()
    print("🚀 RecallX ready")

    yield

    await engine.dispose()
    await close_driver()
    await close_client()

app = FastAPI(title="RecallX", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}