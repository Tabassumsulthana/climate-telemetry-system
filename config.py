GEOCODING_URL = "https://open-meteo.com"
FORECAST_URL = "https://open-meteo.com"
AQI_URL = "https://open-meteo.com"

DEFAULT_CITY = "Hyderabad"
DEFAULT_COMPARE_CITIES = ["Hyderabad", "London", "Tokyo", "New York"]

WMO_CODES = {
    0: ("☀️", "Clear Sky"),
    1: ("🌤️", "Mainly Clear"),
    2: ("⛅", "Partly Cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫️", "Fog"),
    48: ("🌫️", "Depositing Rime Fog"),
    51: ("🌦️", "Light Drizzle"),
    53: ("🌦️", "Moderate Drizzle"),
    55: ("🌧️", "Dense Drizzle"),
    61: ("🌧️", "Slight Rain"),
    63: ("🌧️", "Moderate Rain"),
    65: ("🌧️", "Heavy Rain"),
    71: ("🌨️", "Slight Snow"),
    73: ("🌨️", "Moderate Snow"),
    75: ("❄️", "Heavy Snow"),
    80: ("🌦️", "Slight Rain Showers"),
    81: ("🌧️", "Moderate Rain Showers"),
    82: ("⛈️", "Violent Rain Showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm with Hail"),
    99: ("⛈️", "Heavy Thunderstorm with Hail"),
}

def get_weather_info(code: int):
    return WMO_CODES.get(code, ("🌡️", "Unknown"))

def get_aqi_category(aqi: float):
    if aqi <= 50:
        return "Good", "#2ecc71"
    elif aqi <= 100:
        return "Moderate", "#f1c40f"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#e67e22"
    elif aqi <= 200:
        return "Unhealthy", "#e74c3c"
    elif aqi <= 300:
        return "Very Unhealthy", "#9b59b6"
    return "Hazardous", "#7f0000"