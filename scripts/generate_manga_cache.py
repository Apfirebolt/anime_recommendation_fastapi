# scripts/generate_manga_cache.py
import pickle
from sentence_transformers import SentenceTransformer
from config.db import SessionLocal
from models.manga import Manga

def generate_manga_cache():
    db = SessionLocal()
    try:
        print("Fetching manga records from database...")
        records = db.query(Manga).filter(Manga.synopsis.isnot(None)).all()
        print(f"Found {len(records)} manga records with a synopsis.")

        if not records:
            print("No records found. Exiting cache generation.")
            return

        # Build descriptive documents for embedding
        documents = [
            f"Title: {m.title}. Genres: {m.genres or ''}. Themes: {m.themes or ''}. Authors: {m.authors or ''}. Synopsis: {m.synopsis}"
            for m in records
        ]

        print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        print("Encoding manga documents into vector embeddings (this may take a minute)...")
        vectors = model.encode(documents, show_progress_bar=True, batch_size=64)

        # Serialize SQLAlchemy model attributes into plain dictionaries
        record_dicts = []
        for m in records:
            m_dict = {c.name: getattr(m, c.name) for c in m.__table__.columns}
            record_dicts.append(m_dict)

        cache_data = {
            "records": record_dicts,
            "vectors": vectors
        }

        print("Saving cache to manga_cache.pkl...")
        with open("manga_cache.pkl", "wb") as f:
            pickle.dump(cache_data, f)
            
        print("Manga cache generated and saved successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    generate_manga_cache()