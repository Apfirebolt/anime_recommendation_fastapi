import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# 1. Load the filtered dataset
df = pd.read_csv('data/anime_filtered.csv')

# 2. Fill missing values for critical columns
critical_cols = ['genres', 'themes', 'studios', 'synopsis', 'type', 'source']
for col in critical_cols:
    df[col] = df[col].fillna('')

df['feature_soup'] = (
    df['genres'] + ' ' + 
    df['genres'] + ' ' +  
    df['themes'] + ' ' + 
    df['themes'] + ' ' +  
    df['studios'] + ' ' + 
    df['source'] + ' ' + 
    df['synopsis']
)

# 4. Vectorize text data using TF-IDF
tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
tfidf_matrix = tfidf.fit_transform(df['feature_soup'])

print(f"TF-IDF Matrix shape: {tfidf_matrix.shape}")

# 5. Compute Cosine Similarity using linear_kernel (optimized for sparse matrices)
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# 6. Create a mapping of anime title to its dataframe index
# (We handle case-insensitivity to easily match "Pokemon" or "Pokémon")
df['title_lower'] = df['title'].str.lower()
indices = pd.Series(df.index, index=df['title_lower']).drop_duplicates()

def get_recommendations(title, cosine_sim=cosine_sim):
    query_title = title.lower()
    if query_title not in indices:
        return f"'{title}' not found in dataset."
    
    idx = indices[query_title]

    # Get similarity scores for all items with this anime
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort based on similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top 10 most similar (skipping index 0, which is Pokémon itself)
    sim_scores = sim_scores[1:11]

    anime_indices = [i[0] for i in sim_scores]
    similarity_values = [i[1] for i in sim_scores]

    # Return a clean dataframe or list of results with scores
    results = pd.DataFrame({
        'Title': df['title'].iloc[anime_indices],
        'Genres': df['genres'].iloc[anime_indices],
        'Similarity_Score': similarity_values
    })
    
    return results

# 7. Test it for Pokémon
print("\n--- Top 10 Similar Anime to Pokémon ---")
recommendations = get_recommendations("Pokemon")
print(recommendations)