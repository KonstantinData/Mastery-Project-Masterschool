import pandas as pd

url = "https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_flights_export_2025-03-31_134734.csv"

df = pd.read_csv(url)
print(df.head())
