# app/movies/schemas.py
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

class MovieResponse(BaseModel):
    id: uuid.UUID
    tmdb_id: int
    title: str
    overview: str | None
    poster_url: str | None
    backdrop_url: str | None
    release_date: date | None
    genres: list
    vote_average: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class MovieListResponse(BaseModel):
    total: int
    items: list[MovieResponse]