from fastapi import APIRouter, Depends, status, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy.orm import Session

from config.db import get_db
from schema.manga import MangaBase, MangaDetailResponse
from services.manga import get_manga_listing, get_manga_by_id

router = APIRouter(tags=["Manga"], prefix="/api/manga")


@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[MangaBase])
async def manga_list(
    database: Session = Depends(get_db),
    size: int = Query(20, ge=1, le=50, description="Items per page (max 50)"),
    page: int = Query(1, ge=1, description="Page number"),
    search: str | None = Query(None, description="Search query for title, genre, author, or serialization"),
):
    """
    Get paginated list of manga with optional search filtering.
    """
    manga_query = await get_manga_listing(database, search=search)
    return sqlalchemy_paginate(database, manga_query)


@router.get("/{mal_id}", status_code=status.HTTP_200_OK, response_model=MangaDetailResponse)
async def get_manga_detail(
    mal_id: int,
    database: Session = Depends(get_db),
):
    """
    Get complete details of a specific manga along with its precomputed top-10 similar manga.
    """
    return await get_manga_by_id(mal_id, database)