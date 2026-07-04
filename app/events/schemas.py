# app/events/schemas.py

from pydantic import BaseModel


class TicketResponse(BaseModel):
    ticket: str
    

class SSEEventPayload(BaseModel):
    event: str
    data: dict