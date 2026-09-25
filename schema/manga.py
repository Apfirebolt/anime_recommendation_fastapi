from typing import Optional, List
from pydantic import BaseModel

class MangaBase(BaseModel):
    mal_id: int
    title: str
    title_english: Optional[str] = None
    type: Optional[str] = None
    chapters: Optional[int] = None
    volumes: Optional[int] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    genres: Optional[str] = None
    synopsis: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class SimilarMangaResponse(BaseModel):
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


class MangaDetailResponse(MangaBase):
    title_japanese: Optional[str] = None
    status: Optional[str] = None
    publishing: Optional[bool] = None
    published_from: Optional[str] = None
    published_to: Optional[str] = None
    authors: Optional[str] = None
    serializations: Optional[str] = None
    themes: Optional[str] = None
    demographics: Optional[str] = None
    similar_manga: List[SimilarMangaResponse] = []

    class Config:
        from_attributes = True