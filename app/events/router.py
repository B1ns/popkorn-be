# app/events/router.py

import json
from contextlib import aclosing

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.auth.router import get_current_user
from app.auth.schemas import UserResponse
from app.core.pubsub import subscribe
from app.events.schemas import TicketResponse
from app.events.service import issue_ticket, redeem_ticket

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


@router.post("/{movie_id}/events/ticket", response_model=TicketResponse)
async def create_events_ticket(
    movie_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    ticket = await issue_ticket(str(current_user.id), movie_id)
    return TicketResponse(ticket=ticket)


@router.get("/{movie_id}/events")
async def movie_events(request: Request, movie_id: str, ticket: str):
    user_id = await redeem_ticket(ticket, movie_id)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 티켓입니다.",
        )

    return StreamingResponse(
        event_stream(request, movie_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )