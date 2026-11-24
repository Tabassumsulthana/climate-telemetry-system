import pandas as pd

def process_hourly_data(weather_json: dict) -> pd.DataFrame:
    hourly = weather_json["hourly"]
    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly["time"]),
        "Temperature": hourly["temperature_2m"],
        "Feels Like": hourly["apparent_temperature"],
        "Humidity (%)": hourly["relative_humidity_2m"],
        "Precipitation Prob (%)": hourly["precipitation_probability"],
        "Precipitation (mm)": hourly["precipitation"],
        "Wind Speed": hourly["wind_speed_10m"],
    })
    return df.head(48)

def process_daily_data(weather_json: dict) -> pd.DataFrame:
    daily = weather_json["daily"]
    df = pd.DataFrame({
        "Date": pd.to_datetime(daily["time"]).strftime("%a, %b %d"),
        "Max Temp": daily["temperature_2m_max"],
        "Min Temp": daily["temperature_2m_min"],
        "UV Max": daily["uv_index_max"],
        "Rain Sum (mm)": daily["precipitation_sum"],
        "Sunrise": pd.to_datetime(daily["sunrise"]).strftime("%I:%M %p"),
        "Sunset": pd.to_datetime(daily["sunset"]).strftime("%I:%M %p"),
    })
    return df