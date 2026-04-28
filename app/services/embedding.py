from openai import AsyncOpenAI
from app.core.config import settings

_client = None

def get_openai():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client

async def embed(text: str) -> list[float]:
    client = get_openai()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding