import pandas as pd

df = pd.read_csv("data/manga_dataset.csv")

print(df.head())

print(df.columns)

print(df.isnull().sum())

# number of rows
print(df.shape[0])

# number of columns
print(df.shape[1])