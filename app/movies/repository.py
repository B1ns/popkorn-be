# app/movies/repository.py
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.models import Movie

class MovieRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    
    async def get_by_id(self, movie_id: uuid.UUID) -> Movie | None:
        result = await self.db.execute(
            select(Movie).where(Movie.id == movie_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_tmdb_id(self, tmdb_id: int) -> Movie | None:
        result = await self.db.execute(
            select(Movie).where(Movie.tmdb_id == tmdb_id)
        )
        return result.scalar_one_or_none()
    
    
    async def list(self, offset: int = 0, limit: int = 20) -> list[Movie]:
        result = await self.db.execute(
            select(Movie)
            .order_by(Movie.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Movie.id)))
        return result.scalar_one()
    
    
    async def create(self, movie: Movie) -> Movie:
        self.db.add(movie)
        await self.db.flush()
        await self.db.refresh(movie)
        return movie
    
    async def upsert_by_tmdb(self, data: dict) -> Movie:
        existing = await self.get_by_tmdb_id(data["tmdb_id"])
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            await self.db.flush()
            return existing
        movie = Movie(**data)
        return await self.create(movie)