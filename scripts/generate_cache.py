# generate_cache.py
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from config.db import SessionLocal
from models.anime import Anime

def build_cache():
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Fetching anime records from database...")
    db = SessionLocal()
    records = db.query(Anime).filter(Anime.synopsis.isnot(None)).all()
    db.close()

    if not records:
        print("No records found!")
        return

    print(f"Preparing text documents for {len(records)} anime entries...")
    documents = [
        f"Title: {a.title}. Genres: {a.genres}. Synopsis: {a.synopsis}" 
        for a in records
    ]

    print("Encoding documents into vectors (this may take a minute)...")
    vectors = model.encode(documents, show_progress_bar=True, batch_size=64)

    # Convert SQLAlchemy objects to clean dictionaries so we don't need live DB sessions in memory
    serialized_records = []
    for a in records:
        anime_dict = {c.name: getattr(a, c.name) for c in a.__table__.columns}
        serialized_records.append(anime_dict)

    cache_data = {
        "records": serialized_records,
        "vectors": vectors
    }

    print("Saving to anime_cache.pkl...")
    with open("anime_cache.pkl", "wb") as f:
        pickle.dump(cache_data, f)

    print("Cache successfully built and saved to anime_cache.pkl!")

if __name__ == "__main__":
    build_cache()