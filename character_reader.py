import pandas as pd

df = pd.read_csv("data/characters.csv")

# print null values
print(df.isnull().sum())

# print not null column values for column named 'attributes'

print(df[df['name'].notnull()])
