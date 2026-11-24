from datetime import datetime, timedelta
import requests
import pandas as pd
import streamlit as st

ARCHIVE_URL = "https://open-meteo.com"

def detect_weather_anomalies(hourly_df: pd.DataFrame, aqi_val: int) -> list:
    insights = []
    temp_mean = hourly_df["Temperature"].mean()
    temp_max = hourly_df["Temperature"].max()
    temp_min = hourly_df["Temperature"].min()
    max_rain_prob = hourly_df["Precipitation Prob (%)"].max()

    if (temp_max - temp_min) >= 12:
        insights.append(f"⚠️ **High Thermal Swing:** Temperature will fluctuate by **{temp_max - temp_min:.1f}°** over the next 48 hours.")
    if max_rain_prob >= 70:
        peak_rain_time = hourly_df.loc[hourly_df["Precipitation Prob (%)"].idxmax(), "Time"].strftime("%a %I:%M %p")
        insights.append(f"🌧️ **Precipitation Alert:** High probability of rain (**{max_rain_prob}%**) expected around **{peak_rain_time}**.")
    if aqi_val > 100:
        insights.append(f"😷 **Air Quality Advisory:** US AQI is currently **{aqi_val}** (Above safe threshold). Limit prolonged outdoor exertion.")
    if not insights:
        insights.append(f"✅ **Stable Atmospheric Conditions:** Temperatures remain steady around an average of **{temp_mean:.1f}°** with low severe-weather risk.")
    return insights

@st.cache_data(ttl=3600)
def get_5year_climate_baseline(lat: float, lon: float, temp_unit: str = "celsius") -> pd.DataFrame:
    today = datetime.now().date()
    records = []
    for years_ago in range(1, 6):
        target_date = today - timedelta(days=365 * years_ago)
        date_str = target_date.strftime("%Y-%m-%d")
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date_str,
            "end_date": date_str,
            "daily": "temperature_2m_max,temperature_2m_min",
            "temperature_unit": temp_unit,
            "timezone": "auto",
        }
        try:
            res = requests.get(ARCHIVE_URL, params=params, timeout=8)
            if res.status_code == 200:
                d = res.json().get("daily", {})
                if d.get("temperature_2m_max"):
                    records.append({
                        "Year": str(target_date.year),
                        "Historical Max": d["temperature_2m_max"][0],
                        "Historical Min": d["temperature_2m_min"][0],
                    })
        except requests.RequestException:
            continue
    return pd.DataFrame(records)
def generate_weather_alerts(temp_c: float, wind_kmh: float, aqi: float | None = None) -> list[tuple[str, str]]:
    """
    Returns a list of (level, message) tuples based on live telemetry thresholds.
    Levels: 'error', 'warning', 'info', 'success'
    """
    alerts = []

    # Temperature checks
    if temp_c >= 40:
        alerts.append(("error", f"🔥 Extreme Heat Alert ({temp_c}°C): Stay hydrated and avoid direct afternoon sun."))
    elif temp_c >= 35:
        alerts.append(("warning", f"☀️ High Temperature Advisory ({temp_c}°C): Drink plenty of water outdoors."))
    elif temp_c <= 5:
        alerts.append(("info", f"❄️ Cold Weather Advisory ({temp_c}°C): Dress in warm layers."))

    # Wind speed checks
    if wind_kmh >= 50:
        alerts.append(("error", f"💨 High Wind Warning ({wind_kmh} km/h): Secure loose outdoor items and drive carefully."))
    elif wind_kmh >= 30:
        alerts.append(("warning", f"🌬️ Breezy Conditions ({wind_kmh} km/h): Moderate gusts expected."))

    # Air Quality (AQI) checks
    if aqi is not None:
        if aqi > 200:
            alerts.append(("error", f"😷 Very Unhealthy Air Quality (AQI {int(aqi)}): Avoid outdoor exertion and wear an N95 mask."))
        elif aqi > 150:
            alerts.append(("warning", f"⚠️ Unhealthy Air Quality (AQI {int(aqi)}): Sensitive groups should limit outdoor activity."))
        elif aqi > 100:
            alerts.append(("info", f"🌫️ Moderate Air Quality (AQI {int(aqi)}): Acceptable, though sensitive individuals should take care."))

    # If everything is normal
    if not alerts:
        alerts.append(("success", "✅ Optimal Conditions: Weather and air quality are safe for outdoor activities."))

    return alerts