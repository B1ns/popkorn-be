# app/comments/repository.py

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.comments.models import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        

    async def get_by_id(self, comment_id: uuid.UUID) -> Comment | None:
        result = await self.session.execute(
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.id == comment_id, Comment.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    

    async def list_by_movie(
        self, movie_id: uuid.UUID, page: int, size: int
    ) -> tuple[list[Comment], int]:
        base_query = select(Comment).where(
            Comment.movie_id == movie_id, Comment.deleted_at.is_(None)
        )

        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            base_query.options(selectinload(Comment.user))
            .order_by(Comment.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        items = list(result.scalars().all())
        return items, total
    

    async def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        return comment