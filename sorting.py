import pandas as pd

df = pd.read_csv('data/anime.csv')
print(f"Original dataset size: {len(df)} rows")

# Step 1: Drop rows missing crucial identifiers or core text fields
df = df.dropna(subset=['title', 'genres', 'synopsis'])

# Clean up empty strings or whitespace-only rows in synopsis and genres
df['synopsis'] = df['synopsis'].astype(str).str.strip()
df['genres'] = df['genres'].astype(str).str.strip()

df = df[(df['synopsis'] != '') & (df['synopsis'].str.lower() != 'nan')]
df = df[(df['genres'] != '') & (df['genres'].str.lower() != 'nan')]

if 'members' in df.columns:
    df = df.sort_values(by='members', ascending=False)
elif 'popularity' in df.columns:
    # If popularity rank is available (lower number is better)
    df = df.sort_values(by='popularity', ascending=True)

df_filtered = df.head(15000).reset_index(drop=True)

# save this 
df_filtered.to_csv('data/anime_filtered.csv', index=False)

print(f"Filtered dataset size: {len(df_filtered)} rows")