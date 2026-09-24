from typing import Optional, List
from pydantic import BaseModel, Field

class AnimeBase(BaseModel):
    mal_id: int
    title: str
    title_english: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    episodes: Optional[int] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    genres: Optional[str] = None
    synopsis: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True




class SimilarAnimeResponse(BaseModel):
    rank: int
    similarity_score: float
    mal_id: int
    title: str
    genres: Optional[str] = None
    synopsis: Optional[str] = None
    image_url: Optional[str] = None
    score: Optional[float] = None

    class Config:
        from_attributes = True


class AnimeDetailResponse(AnimeBase):
    title_japanese: Optional[str] = None
    status: Optional[str] = None
    aired_from: Optional[str] = None
    aired_to: Optional[str] = None
    rating: Optional[str] = None
    studios: Optional[str] = None
    themes: Optional[str] = None
    similar_anime: List[SimilarAnimeResponse] = []

    class Config:
        from_attributes = True