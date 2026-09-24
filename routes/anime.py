from fastapi import APIRouter, Depends, status, Query
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy.orm import Session

from config.db import get_db  # Adjust import based on your project db session setup
from . import schema
from . import services

router = APIRouter(tags=["Anime"], prefix="/api/anime")


@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[schema.AnimeBase])
async def anime_list(
    database: Session = Depends(get_db),
    size: int = Query(20, ge=1, le=50, description="Items per page (max 50)"),
    page: int = Query(1, ge=1, description="Page number"),
):
    """
    Get paginated list of anime. Supports custom page sizes (10, 20, max 50).
    """
    anime_query = await services.get_anime_listing(database)
    return sqlalchemy_paginate(database, anime_query)


@router.get("/{mal_id}", status_code=status.HTTP_200_OK, response_model=schema.AnimeDetailResponse)
async def get_anime_detail(
    mal_id: int,
    database: Session = Depends(get_db),
):
    """
    Get complete details of a specific anime along with its precomputed top-10 similar anime.
    """
    return await services.get_anime_by_id(mal_id, database)