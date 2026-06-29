# app/movies/service.py
import uuid
import json
from datetime import date, datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.movies.models import Movie
from app.movies.schemas import MovieResponse
from app.movies.repository import MovieRepository


TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MovieRepository(db)

    
    async def sync_popular_movies(self, page: int = 1) -> int:
        url = f"{settings.TMDB_BASE_URL}/movie/popular"
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "ko-KR",
            "page": page,
        }

        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params)
            res.raise_for_status()
            data = res.json()

        results = data.get("results", [])
        saved = 0
        for item in results:
            movie_data = self._parse_tmdb_movie(item)
            await self.repo.upsert_by_tmdb(movie_data)
            saved += 1

        await self.db.commit()
        return saved
    
    
    async def get_movies(self, page: int = 1, size: int = 20) -> dict:
        cache_key = f"movies:list:page={page}:size={size}"
        
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        offset = (page - 1) * size
        movies = await self.repo.list(offset=offset, limit=size)
        total = await self.repo.count()
        
        items = [
            MovieResponse.model_validate(m).model_dump(mode="json")
            for m in movies
        ]
        
        result = {"total": total, "items": items}
        
        await redis_client.set(cache_key, json.dumps(result), ex=3600)
        
        return result
    
    
    async def getmovie(self, movie_id: uuid.UUID) -> Movie | None:
        return await self.repo.get_by_id(movie_id)

    
    def _parse_tmdb_movie(self, item: dict) -> dict:
        poster = item.get("poster_path")
        backdrop = item.get("backdrop_path")
        release_str = item.get("release_data")
        release = date.fromisoformat(release_str) if release_str else None

        return {
            "tmdb_id": item["id"],
            "title": item.get("title") or item.get("original_title", ""),
            "overview": item.get("overview") or None,
            "poster_url": f"{TMDB_IMAGE_BASE}/w500{poster}" if poster else None,
            "backdrop_url": f"{TMDB_IMAGE_BASE}/w1280{backdrop}" if backdrop else None,
            "release_date": release if release else None,
            "genres": item.get("genre_ids", []),
            "vote_average": item.get("vote_average"),
            "cached_at": datetime.now(timezone.utc),
        }