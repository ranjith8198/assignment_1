import pandas as pd

# Load dataset
df = pd.read_csv("traffic_stops.csv")

print("Before cleaning:", df.shape)

# 1. Remove columns with all missing values
df = df.dropna(axis=1, how='all')

# 2. Handle NaN values
df['driver_age'] = df['driver_age'].fillna(df['driver_age'].median())
df['driver_gender'] = df['driver_gender'].fillna('Unknown')
df['driver_race'] = df['driver_race'].fillna('Unknown')
df['search_type'] = df['search_type'].fillna('Not Conducted')

print("After cleaning:", df.shape)
print("\nMissing values after cleaning:")
print(df.isnull().sum())

df.to_csv("traffic_stops_cleaned.csv", index=False)


