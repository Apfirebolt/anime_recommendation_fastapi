from fastapi import HTTPException, status, types
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select
import logging
from sqlalchemy import cast, Date
from typing import List
from datetime import date

from models.anime import Anime, AnimeSimilarity

logger = logging.getLogger("anime_app")


async def get_anime_listing(
    database: Session, 
    search: str | None = None,
    genre: str | None = None,
    aired_after: date | None = None,
    aired_before: date | None = None,
    sort_by: str | None = "popularity",
    page: int = 1,
    size: int = 20,
):
    try:
        query = database.query(Anime)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Anime.title.ilike(search_pattern)) |
                (Anime.title_english.ilike(search_pattern)) |
                (Anime.genres.ilike(search_pattern)) |
                (Anime.studios.ilike(search_pattern))
            )

        # Apply genre filter (since genres are stored as pipe-separated strings like "Action|Comedy")
        if genre:
            genre_pattern = f"%{genre}%"
            query = query.filter(Anime.genres.ilike(genre_pattern))

        if aired_after:
            query = query.filter(cast(Anime.aired_from, Date) >= aired_after)
        if aired_before:
            query = query.filter(cast(Anime.aired_from, Date) <= aired_before)

        # dynamic sorting criteria
        if sort_by == "highest_voted" or sort_by == "score":
            query = query.order_by(Anime.score.desc().nullslast())
        elif sort_by == "most_episodes":
            query = query.order_by(Anime.episodes.desc().nullslast())
        elif sort_by == "newest":
            query = query.order_by(Anime.aired_from.desc().nullslast())
        elif sort_by == "oldest":
            query = query.order_by(Anime.aired_from.asc().nullslast())
        elif sort_by == "popularity":
            query = query.order_by(Anime.popularity.asc().nullslast())
        elif sort_by == "favorites":
            query = query.order_by(Anime.favorites.desc().nullslast())
        elif sort_by == "rank":
            query = query.order_by(Anime.rank.asc().nullslast())
        else:
            # Fallback default
            query = query.order_by(Anime.popularity.asc().nullslast())

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        return query
    except Exception as e:
        logger.error("Error preparing anime listing query: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching anime listings: {str(e)}",
        )


async def get_anime_by_id(mal_id: int, database: Session) -> dict:
    try:
        # Fetch the target anime
        anime = database.query(Anime).filter(Anime.mal_id == mal_id).first()
        if not anime:
            logger.warning("Anime MAL ID %s not found.", mal_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Anime Not Found!"
            )

        # Fetch its precomputed top 10 similar anime using a join
        similarity_query = (
            database.query(AnimeSimilarity, Anime)
            .join(Anime, AnimeSimilarity.similar_anime_id == Anime.mal_id)
            .filter(AnimeSimilarity.anime_id == mal_id)
            .order_by(AnimeSimilarity.rank)
            .all()
        )

        similar_list = []
        for sim, sim_anime in similarity_query:
            similar_list.append({
                "rank": sim.rank,
                "similarity_score": sim.similarity_score,
                "mal_id": sim_anime.mal_id,
                "title": sim_anime.title,
                "genres": sim_anime.genres,
                "synopsis": sim_anime.synopsis,
                "image_url": sim_anime.image_url,
                "score": sim_anime.score
            })

        # Construct response payload combining anime details and its recommendations
        anime_data = {c.name: getattr(anime, c.name) for c in anime.__table__.columns}
        anime_data["similar_anime"] = similar_list

        return anime_data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error("Error fetching anime ID %s: %s", mal_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching anime details: {str(e)}",
        )