from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import logging

from models.manga import Manga, MangaSimilarity

logger = logging.getLogger("anime_app")


async def get_manga_listing(database: Session, search: str | None = None):
    try:
        query = database.query(Manga)
        
        # Apply search filter if query string is provided
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Manga.title.ilike(search_pattern)) |
                (Manga.title_english.ilike(search_pattern)) |
                (Manga.genres.ilike(search_pattern)) |
                (Manga.authors.ilike(search_pattern)) |
                (Manga.serializations.ilike(search_pattern))
            )
            
        query = query.order_by(Manga.popularity.asc())
        return query
    except Exception as e:
        logger.error("Error preparing manga listing query: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching manga listings: {str(e)}",
        )


async def get_manga_by_id(mal_id: int, database: Session) -> dict:
    try:
        # Fetch the target manga
        manga = database.query(Manga).filter(Manga.mal_id == mal_id).first()
        if not manga:
            logger.warning("Manga MAL ID %s not found.", mal_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Manga Not Found!"
            )

        # Fetch its precomputed top 10 similar manga using a join
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

        # Construct response payload combining manga details and its recommendations
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