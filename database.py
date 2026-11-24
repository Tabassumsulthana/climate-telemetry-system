import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "weather_telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            city TEXT,
            country TEXT,
            temperature REAL,
            humidity INTEGER,
            us_aqi INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_weather_query(city: str, country: str, temp: float, humidity: int, aqi: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_logs (timestamp, city, country, temperature, humidity, us_aqi) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), city, country, temp, humidity, aqi),
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 15) -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        f"SELECT timestamp AS 'Logged At', city AS 'City', country AS 'Country', temperature AS 'Temp', humidity AS 'Humidity (%)', us_aqi AS 'US AQI' FROM search_logs ORDER BY id DESC LIMIT {limit}",
        conn,
    )
    conn.close()
    return df