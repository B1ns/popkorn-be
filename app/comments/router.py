# app/comments/router.py

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.auth.schemas import UserResponse
from app.comments.schemas import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    SpoilerRevealResponse,
)
from app.comments.service import CommentService
from app.core.database import get_db

movies_router = APIRouter(prefix="/movies", tags=["comments"])
comments_router = APIRouter(prefix="/comments", tags=["comments"])


@movies_router.get("/{movie_id}/comments", response_model=CommentListResponse)
async def list_comments(
    movie_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = CommentService(session)
    return await service.get_comments(movie_id, page, size)


@movies_router.post(
    "/{movie_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    movie_id: uuid.UUID,
    data: CommentCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = CommentService(session)
    try:
        comment = await service.create_comment(movie_id, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return CommentResponse.model_validate(comment)


@comments_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = CommentService(session)
    try:
        await service.delete_comment(comment_id, current_user.id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@comments_router.get("/{comment_id}/spoiler", response_model=SpoilerRevealResponse)
async def reveal_spoiler(
    comment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = CommentService(session)
    try:
        comment = await service.get_comment_for_spoiler(comment_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SpoilerRevealResponse.model_validate(comment)