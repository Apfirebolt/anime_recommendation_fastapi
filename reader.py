import pandas as pd

df = pd.read_csv("data/anime_filtered.csv")

print(df.head())

print(df.columns)

print(df.isnull().sum())