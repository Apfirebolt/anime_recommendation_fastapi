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

from models.manga import Manga, MangaSimilarity

def get_database_url():
    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")
    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_NAME")
    db_port = os.getenv("DATABASE_PORT")
    return f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def seed_manga_data():
    start_time = time.time()
    
    # 1. Setup Database Connection
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # 2. Load and Deduplicate Filtered Dataset (Top 15K manga)
    csv_path = 'data/manga_filtered.csv'
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    print(f"Loading manga dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    initial_count = len(df)
    df = df.drop_duplicates(subset=['mal_id']).reset_index(drop=True)
    print(f"Loaded {initial_count} rows. After deduplication: {len(df)} rows.")

    try:
        # 3. Clear existing manga data safely
        print("Clearing existing manga database tables for a fresh seed...")
        db.execute(text("TRUNCATE TABLE manga_similarity RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE manga RESTART IDENTITY CASCADE;"))
        db.commit()

        # 4. Insert Manga Records
        print("Inserting manga records into the database...")
        manga_objects = []
        for _, row in df.iterrows():
            manga = Manga(
                mal_id=int(row['mal_id']),
                title=str(row['title']),
                title_english=str(row['title_english']) if pd.notna(row.get('title_english')) else None,
                title_japanese=str(row['title_japanese']) if pd.notna(row.get('title_japanese')) else None,
                type=str(row['type']) if pd.notna(row.get('type')) else None,
                chapters=int(row['chapters']) if pd.notna(row.get('chapters')) else None,
                volumes=int(row['volumes']) if pd.notna(row.get('volumes')) else None,
                status=str(row['status']),
                publishing=bool(row.get('publishing', False)),
                published_from=str(row['published_from']) if pd.notna(row.get('published_from')) else None,
                published_to=str(row['published_to']) if pd.notna(row.get('published_to')) else None,
                score=float(row['score']) if pd.notna(row.get('score')) else None,
                scored_by=int(row['scored_by']) if pd.notna(row.get('scored_by')) else None,
                rank=int(row['rank']) if pd.notna(row.get('rank')) else None,
                popularity=int(row['popularity']),
                members=int(row['members']),
                favorites=int(row['favorites']),
                authors=str(row['authors']) if pd.notna(row.get('authors')) else None,
                serializations=str(row['serializations']) if pd.notna(row.get('serializations')) else None,
                genres=str(row['genres']) if pd.notna(row.get('genres')) else '',
                themes=str(row['themes']) if pd.notna(row.get('themes')) else '',
                demographics=str(row['demographics']) if pd.notna(row.get('demographics')) else '',
                synopsis=str(row['synopsis']) if pd.notna(row.get('synopsis')) else '',
                image_url=str(row['image_url']) if pd.notna(row.get('image_url')) else None
            )
            manga_objects.append(manga)

        db.bulk_save_objects(manga_objects)
        db.commit()
        print("Successfully inserted all manga records!")

        # 5. Build Feature Soup & Compute Cosine Similarity
        print("Computing TF-IDF and similarity matrix for manga...")
        critical_cols = ['genres', 'themes', 'authors', 'serializations', 'synopsis']
        for col in critical_cols:
            df[col] = df[col].fillna('')

        # Give higher weight to genres, authors, and themes by repeating them
        df['feature_soup'] = (
            df['genres'] + ' ' + df['genres'] + ' ' + 
            df['themes'] + ' ' + 
            df['authors'] + ' ' + df['authors'] + ' ' + 
            df['serializations'] + ' ' + 
            df['synopsis']
        )

        tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
        tfidf_matrix = tfidf.fit_transform(df['feature_soup'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        # 6. Extract Top 10 and Insert Similarities
        print("Extracting top 10 similar manga and preparing relations...")
        similarity_objects = []

        for idx, row in df.iterrows():
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Skip index 0 (itself) and take top 10
            top_10 = sim_scores[1:11]
            
            for rank, (sim_idx, score) in enumerate(top_10, start=1):
                similarity_objects.append(
                    MangaSimilarity(
                        manga_id=int(row['mal_id']),
                        similar_manga_id=int(df.iloc[sim_idx]['mal_id']),
                        rank=rank,
                        similarity_score=float(score)
                    )
                )

        print(f"Inserting {len(similarity_objects)} manga similarity mappings...")
        db.bulk_save_objects(similarity_objects)
        db.commit()

        print(f"Manga database fully seeded in {time.time() - start_time:.2f} seconds!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during manga seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_manga_data()