import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Define 3 mini movie summaries
movies = [
    "action hero fight battle",
    "action chase car speed",
    "romantic love story date"
]

print("--- 1. RAW TEXT DATA ---")
for i, m in enumerate(movies):
    print(f"Movie {i+1}: {m}")
print()

# 2. Convert text to a word count matrix (X)
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(movies).toarray()

print("--- 2. FEATURE MATRIX (X) ---")
print("Vocabulary:", vectorizer.get_feature_names_out())
print(X)
print(f"Shape of X: {X.shape} (3 movies, {X.shape[1]} unique words)\n")

# --- MANUAL MATH BEHIND COSINE SIMILARITY ---

# 3. Calculate the Dot Product Numerator (X * X^T)
# This measures raw word overlap between every pair of movies
dot_product = np.dot(X, X.T)
print("--- 3. NUMERATOR: DOT PRODUCT MATRIX (X @ X.T) ---")
print(dot_product)
print("(Shows how many words each movie shares with every other movie)\n")

# 4. Calculate the L2 Norm (Magnitude) of each movie vector
# Formula: sqrt(sum of squared features for each row)
l2_norms = np.linalg.norm(X, axis=1, keepdims=True)
print("--- 4. DENOMINATOR: L2 NORMS (Magnitudes) ---")
print(l2_norms)
print("(Measures the length/verbosity of each movie's vector)\n")

# 5. Calculate Outer Product of Norms
# This creates a matrix where entry (i, j) is norm(movie_i) * norm(movie_j)
norm_matrix = np.dot(l2_norms, l2_norms.T)
print("--- 5. DENOMINATOR: NORM PRODUCT MATRIX ---")
print(norm_matrix)
print()

# 6. Final Division: Dot Product / Norm Product
manual_cosine = dot_product / norm_matrix
print("--- 6. FINAL MANUAL COSINE SIMILARITY MATRIX ---")
print(manual_cosine)
print()

# 7. Compare with Scikit-Learn's built-in function
sklearn_cosine = cosine_similarity(X, X)
print("--- 7. SCIKIT-LEARN VERIFICATION ---")
print(sklearn_cosine)
print("\nAre manual and sklearn results identical?", np.allclose(manual_cosine, sklearn_cosine))