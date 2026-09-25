import pandas as pd

# 1. Load your dataset
df = pd.read_csv("data/manga_dataset.csv")

print(f"Original shape: {df.shape}")

df_sorted = df.sort_values(by="popularity", ascending=True)

# 3. Take the top 15,000 rows
df_top_15k = df_sorted.head(15000)

print(f"Filtered shape: {df_top_15k.shape}")

# 4. Save the pruned dataset to a new CSV file
df_top_15k.to_csv("data/manga_filtered.csv", index=False)