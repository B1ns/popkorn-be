# app/comments/service.py

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.comments.models import Comment
from app.comments.repository import CommentRepository
from app.comments.schemas import CommentCreate, CommentListResponse, CommentResponse
from app.comments.tasks import analyze_spoiler


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CommentRepository(session)

    async def create_comment(
        self, movie_id: uuid.UUID, user_id: uuid.UUID, data: CommentCreate
    ) -> Comment:
        if data.parent_id is not None:
            parent = await self.repo.get_by_id(data.parent_id)
            if parent is None:
                raise ValueError("답글을 달려는 댓글을 찾을 수 없습니다.")
            if parent.movie_id != movie_id:
                raise ValueError("다른 영화의 댓글에는 답글을 달 수 없습니다.")
            if parent.parent_id is not None:
                raise ValueError("답글에는 답글을 달 수 없습니다.")

        comment = Comment(
            movie_id=movie_id,
            user_id=user_id,
            parent_id=data.parent_id,
            content=data.content,
        )

        created = await self.repo.create(comment)
        await self.session.commit()

        analyze_spoiler.delay(str(created.id))

        return await self.repo.get_by_id(created.id)

    async def get_comments(
        self, movie_id: uuid.UUID, page: int, size: int
    ) -> CommentListResponse:
        items, total = await self.repo.list_by_movie(movie_id, page, size)
        reply_counts = await self.repo.count_replies([c.id for c in items])

        responses = [
            CommentResponse.model_validate(c).model_copy(
                update={"reply_count": reply_counts.get(c.id, 0)}
            )
            for c in items
        ]
        return CommentListResponse(total=total, items=responses)

    async def get_replies(
        self, comment_id: uuid.UUID, page: int, size: int
    ) -> CommentListResponse:
        items, total = await self.repo.list_replies(comment_id, page, size)
        responses = [CommentResponse.model_validate(c) for c in items]
        return CommentListResponse(total=total, items=responses)

    async def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        comment = await self.repo.get_by_id(comment_id)
        if comment is None:
            raise LookupError("존재하지 않는 댓글입니다.")
        if comment.user_id != user_id:
            raise PermissionError("본인 댓글만 삭제할 수 있습니다.")

        comment.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def get_comment_for_spoiler(self, comment_id: uuid.UUID) -> Comment:
        comment = await self.repo.get_by_id(comment_id)
        if comment is None:
            raise LookupError("존재하지 않는 댓글입니다.")
        return comment