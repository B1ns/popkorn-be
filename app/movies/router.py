# app/movies/router.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.movies.schemas import MovieListResponse, MovieResponse
from app.movies.service import MovieService

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=MovieListResponse)
async def get_movies(
  page: int = Query(1, ge=1),
  size: int = Query(20, ge=1, le=100),
  db: AsyncSession = Depends(get_db),  
):
    service = MovieService(db)
    return await service.get_movies(page=page, size=size)


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    service = MovieService(db)
    movie = await service.get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return movie


@router.post("/sync")
async def sync_movies(
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    service = MovieService(db)
    count = await service.sync_popular_movies(page=page)
    return {"synced": count}