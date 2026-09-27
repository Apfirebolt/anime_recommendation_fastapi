# services/vibe_search.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger("anime_app")

async def search_anime_by_vibe(query_text: str, top_k: int = 10):
    try:
        from main import ml_cache

        model = ml_cache.get("model")
        anime_cache = ml_cache.get("anime", {})
        records = anime_cache.get("records")
        vectors = anime_cache.get("vectors")

        # Verify cache is properly populated from lifespan startup
        if not model or not records or vectors is None or len(records) == 0:
            logger.error("Anime vibe search cache is empty or model failed to initialize in memory.")
            return []

        # 1. Encode ONLY the user's incoming search query
        query_vector = model.encode([query_text])

        # 2. Compute Cosine Similarity against the precomputed memory vectors
        similarities = cosine_similarity(query_vector, vectors)[0]

        # 3. Get top_k indices sorted by highest similarity score
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            anime_dict = dict(records[idx])
            score = float(similarities[idx])
            
            anime_dict["vibe_match_score"] = round(score * 100, 1)
            results.append(anime_dict)

        return results

    except Exception as e:
        logger.error("Error executing anime vibe search: %s", str(e), exc_info=True)
        return []


async def search_manga_by_vibe(query_text: str, top_k: int = 10):
    try:
        from main import ml_cache

        model = ml_cache.get("model")
        manga_cache = ml_cache.get("manga", {})
        records = manga_cache.get("records")
        vectors = manga_cache.get("vectors")

        if not model or not records or vectors is None or len(records) == 0:
            logger.error("Manga vibe search cache is empty or model failed to initialize.")
            return []

        # 1. Encode user query
        query_vector = model.encode([query_text])

        # 2. Compute similarity against precomputed manga vectors
        similarities = cosine_similarity(query_vector, vectors)[0]

        # 3. Sort indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            manga_dict = dict(records[idx])
            score = float(similarities[idx])
            
            manga_dict["vibe_match_score"] = round(score * 100, 1)
            results.append(manga_dict)

        return results

    except Exception as e:
        logger.error("Error executing manga vibe search: %s", str(e), exc_info=True)
        return []