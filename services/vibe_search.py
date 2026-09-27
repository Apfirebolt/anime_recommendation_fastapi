from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger("anime_app")

model = SentenceTransformer('all-MiniLM-L6-v2')

# Global cache variables
_CACHED_ANIME_RECORDS = None
_CACHED_ANIME_VECTORS = None

def _initialize_cache(database):
    """Loads records and computes embeddings once and stores them in memory safely."""
    global _CACHED_ANIME_RECORDS, _CACHED_ANIME_VECTORS
    
    # If already successfully cached with actual data, return immediately
    if _CACHED_ANIME_RECORDS is not None and len(_CACHED_ANIME_RECORDS) > 0:
        return

    logger.info("Initializing Vibe Search cache: encoding anime catalog...")
    from models.anime import Anime
    
    records = database.query(Anime).filter(Anime.synopsis.isnot(None)).all()
    
    if not records:
        logger.warning("No anime records found with a synopsis!")
        return

    documents = [
        f"Title: {a.title}. Genres: {a.genres}. Synopsis: {a.synopsis}" 
        for a in records
    ]
    
    vectors = model.encode(documents, show_progress_bar=False, batch_size=64)
    
    # Assign to global variables *only* after full success
    _CACHED_ANIME_RECORDS = records
    _CACHED_ANIME_VECTORS = vectors
    
    logger.info("Vibe Search cache successfully built with %d anime entries.", len(_CACHED_ANIME_RECORDS))


async def search_anime_by_vibe(database, query_text: str, top_k: int = 10):
    try:
        # 1. Ensure cache is loaded
        _initialize_cache(database)

        if not _CACHED_ANIME_RECORDS or _CACHED_ANIME_VECTORS is None or len(_CACHED_ANIME_RECORDS) == 0:
            return []

        # 2. Encode ONLY the user's incoming search query
        query_vector = model.encode([query_text])

        # 3. Compute Cosine Similarity against the precomputed vectors in memory
        similarities = cosine_similarity(query_vector, _CACHED_ANIME_VECTORS)[0]

        # 4. Get top_k indices sorted by highest similarity score
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            anime = _CACHED_ANIME_RECORDS[idx]
            score = float(similarities[idx])
            
            anime_dict = {c.name: getattr(anime, c.name) for c in anime.__table__.columns}
            anime_dict["vibe_match_score"] = round(score * 100, 1)
            results.append(anime_dict)

        return results

    except Exception as e:
        logger.error("Error executing vibe search: %s", str(e), exc_info=True)
        return []