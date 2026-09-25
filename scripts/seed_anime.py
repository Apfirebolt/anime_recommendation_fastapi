import os
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.anime import Anime, AnimeSimilarity

def get_database_url():
    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")
    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_NAME")
    db_port = os.getenv("DATABASE_PORT")
    return f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def seed_data():
    start_time = time.time()
    
    # 1. Setup Database Connection
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # 2. Load and Deduplicate Filtered Dataset
    csv_path = 'data/anime_filtered.csv'
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Drop duplicate mal_ids if any exist in the CSV
    initial_count = len(df)
    df = df.drop_duplicates(subset=['mal_id']).reset_index(drop=True)
    print(f"Loaded {initial_count} rows. After deduplication: {len(df)} rows.")

    try:
        # 3. Clear existing data to allow safe re-runs (handle foreign keys with cascade/delete)
        print("Clearing existing database tables for a fresh seed...")
        db.execute(text("TRUNCATE TABLE anime_similarity RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE anime RESTART IDENTITY CASCADE;"))
        db.commit()

        # 4. Insert Anime Records
        print("Inserting anime records into the database...")
        anime_objects = []
        for _, row in df.iterrows():
            anime = Anime(
                mal_id=int(row['mal_id']),
                title=str(row['title']),
                title_english=str(row['title_english']) if pd.notna(row.get('title_english')) else None,
                title_japanese=str(row['title_japanese']) if pd.notna(row.get('title_japanese')) else None,
                type=str(row['type']) if pd.notna(row.get('type')) else None,
                source=str(row['source']),
                episodes=int(row['episodes']) if pd.notna(row.get('episodes')) else None,
                status=str(row['status']),
                airing=bool(row.get('airing', False)),
                aired_from=str(row['aired_from']) if pd.notna(row.get('aired_from')) else None,
                aired_to=str(row['aired_to']) if pd.notna(row.get('aired_to')) else None,
                duration=str(row.get('duration', '')),
                rating=str(row['rating']) if pd.notna(row.get('rating')) else None,
                score=float(row['score']) if pd.notna(row.get('score')) else None,
                scored_by=int(row['scored_by']) if pd.notna(row.get('scored_by')) else None,
                rank=int(row['rank']) if pd.notna(row.get('rank')) else None,
                popularity=int(row['popularity']),
                members=int(row['members']),
                favorites=int(row['favorites']),
                season=str(row['season']) if pd.notna(row.get('season')) else None,
                year=int(row['year']) if pd.notna(row.get('year')) else None,
                studios=str(row['studios']) if pd.notna(row.get('studios')) else None,
                producers=str(row['producers']) if pd.notna(row.get('producers')) else None,
                licensors=str(row['licensors']) if pd.notna(row.get('licensors')) else None,
                genres=str(row['genres']),
                themes=str(row['themes']) if pd.notna(row.get('themes')) else None,
                demographics=str(row['demographics']) if pd.notna(row.get('demographics')) else None,
                synopsis=str(row['synopsis']),
                image_url=str(row['image_url'])
            )
            anime_objects.append(anime)

        db.bulk_save_objects(anime_objects)
        db.commit()
        print("Successfully inserted all anime records!")

        # 5. Build Feature Soup & Compute Cosine Similarity
        print("Computing TF-IDF and similarity matrix...")
        critical_cols = ['genres', 'themes', 'studios', 'source', 'synopsis']
        for col in critical_cols:
            df[col] = df[col].fillna('')

        df['feature_soup'] = (
            df['genres'] + ' ' + df['genres'] + ' ' + 
            df['themes'] + ' ' + df['themes'] + ' ' + 
            df['studios'] + ' ' + 
            df['source'] + ' ' + 
            df['synopsis']
        )

        tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
        tfidf_matrix = tfidf.fit_transform(df['feature_soup'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        # 6. Extract Top 10 and Insert Similarities
        print("Extracting top 10 similar anime and preparing relations...")
        similarity_objects = []

        for idx, row in df.iterrows():
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Skip index 0 (itself) and take top 10
            top_10 = sim_scores[1:11]
            
            for rank, (sim_idx, score) in enumerate(top_10, start=1):
                similarity_objects.append(
                    AnimeSimilarity(
                        anime_id=int(row['mal_id']),
                        similar_anime_id=int(df.iloc[sim_idx]['mal_id']),
                        rank=rank,
                        similarity_score=float(score)
                    )
                )

        print(f"Inserting {len(similarity_objects)} similarity mappings...")
        db.bulk_save_objects(similarity_objects)
        db.commit()

        print(f"Database fully seeded in {time.time() - start_time:.2f} seconds!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()