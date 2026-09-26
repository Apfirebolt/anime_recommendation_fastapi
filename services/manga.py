from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import cast, Date
from sqlalchemy.orm import Session
import logging

from models.manga import Manga, MangaSimilarity

logger = logging.getLogger("anime_app")


async def get_manga_listing(
    database: Session, 
    search: str | None = None,
    genre: str | None = None,
    published_after: date | None = None,
    published_before: date | None = None,
    sort_by: str | None = "popularity",
    page: int = 1,
    size: int = 20,
):
    try:
        query = database.query(Manga)
        
        # 1. Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Manga.title.ilike(search_pattern)) |
                (Manga.title_english.ilike(search_pattern)) |
                (Manga.genres.ilike(search_pattern)) |
                (Manga.authors.ilike(search_pattern)) |
                (Manga.serializations.ilike(search_pattern))
            )

        # 2. Apply genre filter
        if genre:
            genre_pattern = f"%{genre}%"
            query = query.filter(Manga.genres.ilike(genre_pattern))

        # 3. Apply published date range filters with safe SQL Date casting
        if published_after:
            query = query.filter(cast(Manga.published_from, Date) >= published_after)
        if published_before:
            query = query.filter(cast(Manga.published_from, Date) <= published_before)

        # 4. Apply dynamic sorting criteria
        if sort_by == "highest_voted" or sort_by == "score":
            query = query.order_by(Manga.score.desc().nullslast())
        elif sort_by == "most_chapters":
            query = query.order_by(Manga.chapters.desc().nullslast())
        elif sort_by == "most_volumes":
            query = query.order_by(Manga.volumes.desc().nullslast())
        elif sort_by == "newest":
            query = query.order_by(Manga.published_from.desc().nullslast())
        elif sort_by == "oldest":
            query = query.order_by(Manga.published_from.asc().nullslast())
        elif sort_by == "popularity":
            query = query.order_by(Manga.popularity.asc().nullslast())
        elif sort_by == "favorites":
            query = query.order_by(Manga.favorites.desc().nullslast())
        elif sort_by == "rank":
            query = query.order_by(Manga.rank.asc().nullslast())
        else:
            query = query.order_by(Manga.popularity.asc().nullslast())

        # Apply manual pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        return query

    except Exception as e:
        logger.error("Error preparing manga listing query: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching manga listings: {str(e)}",
        )


async def get_manga_by_id(mal_id: int, database: Session) -> dict:
    try:
        manga = database.query(Manga).filter(Manga.mal_id == mal_id).first()
        if not manga:
            logger.warning("Manga MAL ID %s not found.", mal_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Manga Not Found!"
            )

        similarity_query = (
            database.query(MangaSimilarity, Manga)
            .join(Manga, MangaSimilarity.similar_manga_id == Manga.mal_id)
            .filter(MangaSimilarity.manga_id == mal_id)
            .order_by(MangaSimilarity.rank)
            .all()
        )

        similar_list = []
        for sim, sim_manga in similarity_query:
            similar_list.append({
                "rank": sim.rank,
                "similarity_score": sim.similarity_score,
                "mal_id": sim_manga.mal_id,
                "title": sim_manga.title,
                "genres": sim_manga.genres,
                "synopsis": sim_manga.synopsis,
                "image_url": sim_manga.image_url,
                "score": sim_manga.score
            })

        manga_data = {c.name: getattr(manga, c.name) for c in manga.__table__.columns}
        manga_data["similar_manga"] = similar_list

        return manga_data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error("Error fetching manga ID %s: %s", mal_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching manga details: {str(e)}",
        )