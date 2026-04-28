import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct

from app.db.postgres import AsyncSessionLocal
from app.db.vectordb import get_client as get_qdrant, COLLECTION_NAME
from app.db.graphdb import get_driver
from app.db.redis import get_client as get_redis
from app.services.embedding import embed
from app.models.memory import Memory, MemoryTypeEnum


async def _save_postgres(
    session: AsyncSession,
    user_id: str,
    content: str,
    memory_type: str,
    importance_score: float,
    vector_id: str,
) -> Memory:
    memory = Memory(
        user_id=uuid.UUID(user_id),
        content=content,
        memory_type=MemoryTypeEnum(memory_type),
        importance_score=importance_score,
        vector_id=vector_id,
    )
    session.add(memory)
    await session.flush()   # id generate ho jaaye
    return memory


async def _save_qdrant(
    vector_id: str,
    user_id: str,
    content: str,
    memory_type: str,
    importance_score: float,
):
    vector = await embed(content)
    client = get_qdrant()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=vector_id,
                vector=vector,
                payload={
                    "user_id": user_id,
                    "content": content,
                    "memory_type": memory_type,
                    "importance_score": importance_score,
                },
            )
        ],
    )


async def _save_neo4j(
    user_id: str,
    memory_id: str,
    topics: list[str],
    entities: list[dict],
    memory_type: str,
):
    driver = await get_driver()
    async with driver.session() as session:
        # User node ensure karo
        await session.run(
            "MERGE (u:User {id: $user_id})",
            user_id=user_id,
        )
        # Topics
        for topic in topics:
            if memory_type == "preference":
                rel = "PREFERS"
            else:
                rel = "KNOWS_ABOUT"
            await session.run(
                f"""
                MERGE (t:Topic {{name: $name}})
                MERGE (u:User {{id: $user_id}})
                MERGE (u)-[:{rel}]->(t)
                """,
                name=topic.lower(),
                user_id=user_id,
            )
        # Entities
        for entity in entities:
            await session.run(
                """
                MERGE (e:Entity {name: $name, type: $type})
                MERGE (u:User {id: $user_id})
                MERGE (u)-[:KNOWS]->(e)
                """,
                name=entity.get("name", ""),
                type=entity.get("type", "unknown"),
                user_id=user_id,
            )


async def _invalidate_cache(user_id: str):
    redis = await get_redis()
    await redis.delete(f"context:{user_id}")


async def write_memories(user_id: str, extracted: list[dict]) -> list[Memory]:
    if not extracted:
        return []

    saved = []
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for item in extracted:
                content = item.get("content", "").strip()
                if not content:
                    continue

                memory_type = item.get("memory_type", "fact")
                importance = float(item.get("importance_score", 0.5))
                topics = item.get("topics", [])
                entities = item.get("entities", [])
                vector_id = str(uuid.uuid4())

                # Postgres + Qdrant + Neo4j parallel
                memory, _, _ = await asyncio.gather(
                    _save_postgres(
                        session, user_id, content,
                        memory_type, importance, vector_id
                    ),
                    _save_qdrant(
                        vector_id, user_id, content,
                        memory_type, importance
                    ),
                    _save_neo4j(
                        user_id, vector_id,
                        topics, entities, memory_type
                    ),
                )
                saved.append(memory)

    await _invalidate_cache(user_id)
    return saved