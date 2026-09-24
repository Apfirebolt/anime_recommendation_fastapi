from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Float, Boolean

from config.db import Base


class Anime(Base):
    __tablename__ = "anime"

    mal_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    title_english = Column(String(255), nullable=True)
    title_japanese = Column(String(255), nullable=True)
    type = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)
    episodes = Column(Integer, nullable=True)
    status = Column(String(100), nullable=True)
    airing = Column(Boolean, nullable=True)
    aired_from = Column(String(100), nullable=True)
    aired_to = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    rating = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)
    scored_by = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    members = Column(Integer, nullable=True)
    favorites = Column(Integer, nullable=True)
    season = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    studios = Column(String(255), nullable=True)
    producers = Column(Text, nullable=True)
    licensors = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)
    themes = Column(Text, nullable=True)
    demographics = Column(Text, nullable=True)
    synopsis = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    # Relationship to similarity mappings (outgoing recommendations)
    similar_entries = relationship(
        "AnimeSimilarity", 
        foreign_keys="[AnimeSimilarity.anime_id]", 
        cascade="all, delete-orphan"
    )


class AnimeSimilarity(Base):
    __tablename__ = "anime_similarity"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.mal_id"), nullable=False, index=True)
    similar_anime_id = Column(Integer, ForeignKey("anime.mal_id"), nullable=False)
    rank = Column(Integer, nullable=False)  # 1 through 10
    similarity_score = Column(Float, nullable=False)

    # Relationships back to the anime table
    anime = relationship("Anime", foreign_keys=[anime_id])
    similar_anime = relationship("Anime", foreign_keys=[similar_anime_id])