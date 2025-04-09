import pandas as pd


def load_flights():
    url = "https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_flights_export_2025-03-31_134734.csv"
    return pd.read_csv(url)


def load_hotels():
    url = "https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_hotels_export_2025-03-31_171805.csv"
    return pd.read_csv(url)


def load_sessions():
    url = "https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_sessions_export_2025-03-31_221253.csv"
    return pd.read_csv(url)


def load_users():
    url = "https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_users_export_2025-04-01_101058.csv"
    return pd.read_csv(url)
