# app/core/pubsub.py

import json 
from collections.abc import AsyncGenerator

from app.core.redis import redis_client


def _channel_name(movie_id: str) -> str:
    return f"movie:{movie_id}:events"


async def publish_event(movie_id: str, event: str, data: dict) -> None:
    channel = _channel_name(movie_id)
    payload = json.dumps({"event": event, "data": data})
    await redis_client.publish(channel, payload)
    
    
async def subscribe(movie_id: str) -> AsyncGenerator[dict | None, None]:
    channel = _channel_name(movie_id)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=15,
            )
            if message is None:
                yield None  
                continue
            yield json.loads(message["data"])
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()