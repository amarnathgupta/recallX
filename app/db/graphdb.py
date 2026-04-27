from neo4j import AsyncGraphDatabase
from app.core.config import settings

_driver = None

async def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver

async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None

async def init_constraints():
    driver = await get_driver()
    async with driver.session() as session:
        # Unique constraints — idempotent banate hai
        await session.run(
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS "
            "FOR (u:User) REQUIRE u.id IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS "
            "FOR (t:Topic) REQUIRE t.name IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS "
            "FOR (e:Entity) REQUIRE e.name IS UNIQUE"
        )
    print("✅ Neo4j constraints initialized")