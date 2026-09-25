from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Float, Boolean

from config.db import Base


class Manga(Base):
    __tablename__ = "manga"

    mal_id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False, index=True)             
    title_english = Column(Text, nullable=True)             
    title_japanese = Column(Text, nullable=True)
    type = Column(String(50), nullable=True)
    chapters = Column(Integer, nullable=True)
    volumes = Column(Integer, nullable=True)
    status = Column(String(100), nullable=True)
    publishing = Column(Boolean, nullable=True)
    published_from = Column(String(100), nullable=True)
    published_to = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)
    scored_by = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    members = Column(Integer, nullable=True)
    favorites = Column(Integer, nullable=True)
    authors = Column(Text, nullable=True)                      
    serializations = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)
    themes = Column(Text, nullable=True)
    demographics = Column(Text, nullable=True)
    synopsis = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    similar_entries = relationship(
        "MangaSimilarity", 
        foreign_keys="[MangaSimilarity.manga_id]", 
        cascade="all, delete-orphan",
        overlaps="manga"                                     
    )


class MangaSimilarity(Base):
    __tablename__ = "manga_similarity"

    id = Column(Integer, primary_key=True, index=True)
    manga_id = Column(Integer, ForeignKey("manga.mal_id"), nullable=False, index=True)
    similar_manga_id = Column(Integer, ForeignKey("manga.mal_id"), nullable=False)
    rank = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)

    manga = relationship("Manga", foreign_keys=[manga_id], overlaps="similar_entries")
    similar_manga = relationship("Manga", foreign_keys=[similar_manga_id])