from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.memory import extract_memories, write_memories
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



class TestExtractRequest(BaseModel):
    user_id: str
    message: str

@app.post("/debug/extract")
# docker exec -it pg_db psql -U admin -d recallx_db -c \
# "INSERT INTO users (name, email) VALUES ('Test User', 'test@test.com') RETURNING id;"

async def debug_extract(req: TestExtractRequest):
    extracted = await extract_memories(req.message)
    saved = await write_memories(req.user_id, extracted)
    return {
        "extracted_count": len(extracted),
        "extracted": extracted,
        "saved_ids": [str(m.id) for m in saved],
    }