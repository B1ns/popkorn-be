# app/comments/schemas.py

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentAuthor(BaseModel):
    id: uuid.UUID
    username: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    user: CommentAuthor
    content: str
    is_spoiler: bool
    spoiler_score: int
    ai_status: str
    parent_id: uuid.UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    total: int
    items: list[CommentResponse]


class SpoilerRevealResponse(BaseModel):
    id: uuid.UUID
    content: str
    spoiler_score: int
    spoiler_reason: str | None

    model_config = ConfigDict(from_attributes=True)