# app/events/router.py
import json
from contextlib import aclosing

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.pubsub import subscribe

router = APIRouter(prefix="/movies", tags=["events"])


async def event_stream(request: Request, movie_id: str):
    async with aclosing(subscribe(movie_id)) as events:
        async for message in events:
            if await request.is_disconnected():
                break

            if message is None:
                yield ": heartbeat\n\n"
                continue

            yield f"event: {message['event']}\ndata: {json.dumps(message['data'])}\n\n"


@router.get("/{movie_id}/events")
async def movie_events(request: Request, movie_id: str):
    return StreamingResponse(
        event_stream(request, movie_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )