from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger("anime_app")

async def search_anime_by_vibe(query_text: str, top_k: int = 10):
    try:
        # Import ml_cache dynamically or at the top to avoid circular imports
        from main import ml_cache

        model = ml_cache.get("model")
        records = ml_cache.get("records")
        vectors = ml_cache.get("vectors")

        # Verify cache is properly populated from lifespan startup
        if not model or not records or vectors is None or len(records) == 0:
            logger.error("Vibe search cache is empty or model failed to initialize in memory.")
            return []

        # 1. Encode ONLY the user's incoming search query
        query_vector = model.encode([query_text])

        # 2. Compute Cosine Similarity against the precomputed memory vectors
        similarities = cosine_similarity(query_vector, vectors)[0]

        # 3. Get top_k indices sorted by highest similarity score
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            # Since pickle records are already serialized dictionaries, copy them directly
            anime_dict = dict(records[idx])
            score = float(similarities[idx])
            
            anime_dict["vibe_match_score"] = round(score * 100, 1)
            results.append(anime_dict)

        return results

    except Exception as e:
        logger.error("Error executing vibe search: %s", str(e), exc_info=True)
        return []