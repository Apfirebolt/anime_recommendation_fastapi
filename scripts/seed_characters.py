import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.anime import Character

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

    # 2. Load and Filter Dataset
    csv_path = 'data/characters.csv'
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    initial_count = len(df)
    
    # Drop duplicate character_ids if any exist
    df = df.drop_duplicates(subset=['character_id']).reset_index(drop=True)
    
    # Skip/drop entries where the description column is missing or NaN
    df = df.dropna(subset=['description']).reset_index(drop=True)
    
    print(f"Loaded {initial_count} rows. After deduplication and removing missing descriptions: {len(df)} rows.")

    try:
        # 3. Clear existing data to allow safe re-runs
        print("Clearing existing database tables for a fresh seed...")
        db.execute(text("TRUNCATE TABLE characters RESTART IDENTITY CASCADE;"))
        db.commit()

        # 4. Insert Character Records in Batches of 5,000
        print("Inserting character records into the database...")
        batch_size = 5000
        character_objects = []
        inserted_count = 0

        for _, row in df.iterrows():
            # do not insert characters with missing descriptions (already filtered out)
            if pd.isna(row.get('description')):
                continue
            character = Character(
                character_id=int(row['character_id']),
                name=str(row['name']),
                full_name=str(row['full_name']) if pd.notna(row.get('full_name')) else None,
                alternate_name=str(row['alternate_name']) if pd.notna(row.get('alternate_name')) else None,
                url=str(row['url']) if pd.notna(row.get('url')) else None,
                attributes=str(row['attributes']) if pd.notna(row.get('attributes')) else None,
                description=str(row['description'])
            )
            character_objects.append(character)

            # Once the batch hits 5,000, insert, commit, and print message
            if len(character_objects) >= batch_size:
                db.bulk_save_objects(character_objects)
                db.commit()
                inserted_count += len(character_objects)
                print(f"Successfully inserted {inserted_count} character records...")
                character_objects = []  # Reset the batch list


        if character_objects:
            db.bulk_save_objects(character_objects)
            db.commit()
            inserted_count += len(character_objects)

        print(f"Successfully inserted all character records! Total inserted: {inserted_count}")
        print(f"Database fully seeded in {time.time() - start_time:.2f} seconds!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()