import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import time

start_time = time.time()

# 1. Load data
df = pd.read_csv('data/anime_filtered.csv')

# 2. Build feature soup
critical_cols = ['genres', 'themes', 'studios', 'synopsis', 'type', 'source']
for col in critical_cols:
    df[col] = df[col].fillna('')

df['feature_soup'] = (
    df['genres'] + ' ' + df['genres'] + ' ' + 
    df['themes'] + ' ' + df['themes'] + ' ' + 
    df['studios'] + ' ' + df['source'] + ' ' + 
    df['synopsis']
)

# 3. Vectorize
print("Vectorizing text...")
tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
tfidf_matrix = tfidf.fit_transform(df['feature_soup'])

# 4. Compute similarity matrix
print("Computing similarity matrix...")
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
print(f"Matrix computed in {time.time() - start_time:.2f} seconds!")

# 5. Extract top 10 for EVERY anime and store in a list for bulk insertion
print("Extracting top 10 matches for all entries...")
bulk_similarity_records = []

for idx, row in df.iterrows():
    # Get similarity scores for this specific anime
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Skip index 0 (itself) and take top 10
    top_10 = sim_scores[1:11]
    
    for rank, (sim_idx, score) in enumerate(top_10, start=1):
        bulk_similarity_records.append({
            "anime_mal_id": row['mal_id'],
            "similar_anime_mal_id": df.iloc[sim_idx]['mal_id'],
            "rank": rank,
            "similarity_score": float(score)
        })

# Convert to a DataFrame for easy inspection or database insertion
similarity_df = pd.DataFrame(bulk_similarity_records)
print(f"Generated {len(similarity_df)} total relationship rows!")
print(similarity_df.head(10))