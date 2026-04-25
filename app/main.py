from fastapi import FastAPI
from app.db.test_connections import wait_for_services

app = FastAPI(title="RecallX", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}