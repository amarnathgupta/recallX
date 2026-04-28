import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.embedding import get_openai

EXTRACTION_PROMPT = """You are a memory extraction engine.
Given a user message, extract meaningful memories worth remembering.

Return a JSON array. Each item must have:
- "content": string — the memory in one clear sentence
- "memory_type": one of "fact", "preference", "episode"
- "importance_score": float between 0.0 and 1.0
- "topics": list of short topic strings (e.g. ["python", "programming"])
- "entities": list of objects with "name" and "type" (e.g. [{"name": "VSCode", "type": "tool"}])

Return ONLY valid JSON. No explanation, no markdown.

Examples:
- "I love using Python" → fact, topics: ["python"], importance: 0.7
- "I hate dark mode" → preference, topics: ["ui"], importance: 0.6
- "Today I deployed my first app" → episode, importance: 0.8

If nothing memorable, return an empty array [].
"""

async def extract_memories(message: str) -> list[dict]:
    client = get_openai()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )


    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    # GPT sometimes wraps in {"memories": [...]}
    if isinstance(parsed, dict):
        for key in ("memories", "items", "results"):
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
        return []

    return parsed if isinstance(parsed, list) else []