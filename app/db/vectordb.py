from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

COLLECTION_NAME = "memories"
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small

_client = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
    return _client

def init_collection():
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' created")
    else:
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' already exists")