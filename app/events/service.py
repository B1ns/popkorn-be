# app/events/service.py

import json
import secrets

from app.core.redis import redis_client

TICKET_TTL_SECONDS = 30


def _ticket_key(ticket: str) -> str:
    return f"sse_ticket:{ticket}"


async def issue_ticket(user_id: str, movie_id: str) -> str:
    ticket = secrets.token_urlsafe(32)
    payload = json.dumps({"user_id": user_id, "movie_id": movie_id})
    await redis_client.setex(_ticket_key(ticket), TICKET_TTL_SECONDS, payload)
    return ticket


async def redeem_ticket(ticket: str, movie_id: str) -> str | None:
    raw = await redis_client.getdel(_ticket_key(ticket))
    if raw is None:
        return None

    data = json.loads(raw)
    if data["movie_id"] != movie_id:
        return None

    return data["user_id"]