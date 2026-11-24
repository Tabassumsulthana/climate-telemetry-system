import time
import pandas as pd
import streamlit as st
from analytics import generate_weather_alerts
from config import DEFAULT_CITY, DEFAULT_COMPARE_CITIES, get_weather_info, get_aqi_category
from weather_api import get_city_coordinates, get_weather_data, get_aqi_data
from data_processor import process_hourly_data, process_daily_data
from database import init_db, log_weather_query, get_recent_logs
from analytics import detect_weather_anomalies, get_5year_climate_baseline
from visualizer import (
    plot_hourly_temp, plot_daily_range, plot_precipitation_humidity,
    plot_city_map, plot_aqi_gauge, plot_pollutants, plot_5year_baseline
)

st.set_page_config(page_title="Real-Time Weather & Climate Telemetry", page_icon="🌦️", layout="wide")
init_db()

# Sidebar Controls
st.sidebar.title("🌍 Telemetry Control Panel")
city_input = st.sidebar.text_input("Search City", value=DEFAULT_CITY)
temp_choice = st.sidebar.radio("Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True)
wind_choice = st.sidebar.radio("Wind Speed Unit", ["km/h", "mph"], horizontal=True)
auto_refresh = st.sidebar.checkbox("Auto-Refresh every 60s", value=False)

if st.sidebar.button("🔄 Refresh Live Data"):
    st.cache_data.clear()

temp_param = "celsius" if "Celsius" in temp_choice else "fahrenheit"
temp_symbol = "°C" if temp_param == "celsius" else "°F"

# Fetch Primary City Data
city_info = get_city_coordinates(city_input)
if not city_info:
    st.error(f"Could not find city '{city_input}'. Please check spelling and try again.")
    st.stop()

weather_json = get_weather_data(city_info["lat"], city_info["lon"], temp_param, wind_choice)
aqi_json = get_aqi_data(city_info["lat"], city_info["lon"])

current = weather_json["current"]
aqi_current = aqi_json["current"]
hourly_df = process_hourly_data(weather_json)
daily_df = process_daily_data(weather_json)
icon, condition_text = get_weather_info(current["weather_code"])


# Header
st.title(f"{icon} {city_info['name']}, {city_info['country']} — Climate Telemetry System")
st.caption(f"Condition: **{condition_text}** | Timezone: `{city_info['timezone']}` | Coordinates: `{city_info['lat']:.2f}, {city_info['lon']:.2f}`")

# Automated Anomaly Banner
for insight in detect_weather_anomalies(hourly_df, aqi_current["us_aqi"]):
    st.info(insight)

# 5 Dashboard Tabs
tab1, tab2, tab3, tab4, = st.tabs([
    "📍 Live Overview",
    "📅 7-Day Forecast & Rain",
    "😷 Air Quality (AQI)",
    "⚖️ Multi-City Compare",
])
with tab1:
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Temperature", f"{current['temperature_2m']}{temp_symbol}")
    c2.metric("Feels Like", f"{current['apparent_temperature']}{temp_symbol}")
    c3.metric("Humidity", f"{current['relative_humidity_2m']}%")
    c4.metric("Wind Speed", f"{current['wind_speed_10m']} {wind_choice}")
    c5.metric("UV Index", f"{current['uv_index']}")
    c6.metric("Pressure", f"{current['surface_pressure']} hPa")

    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        with st.container(border=True):
            st.plotly_chart(plot_hourly_temp(hourly_df, temp_symbol), use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.subheader("🔔 Live Telemetry Alerts")
            temp_c = current["temperature_2m"] if temp_param == "celsius" else (current["temperature_2m"] - 32) * 5 / 9
            wind_kmh = current["wind_speed_10m"] if wind_choice == "km/h" else current["wind_speed_10m"] * 1.60934
            aqi_val = aqi_current.get("us_aqi") or aqi_current.get("european_aqi")

            for level, message in generate_weather_alerts(temp_c=temp_c, wind_kmh=wind_kmh, aqi=aqi_val):
                if level == "error":
                    st.error(message)
                elif level == "warning":
                    st.warning(message)
                elif level == "info":
                    st.info(message)
                else:
                    st.success(message)

        with st.container(border=True):
            st.subheader(f"📍 {city_info['name']} Location")
            map_df = pd.DataFrame([{"lat": city_info["lat"], "lon": city_info["lon"]}])
            st.map(map_df, zoom=10, height=200)
        

with tab2:
    st.plotly_chart(plot_daily_range(daily_df, temp_symbol), use_container_width=True)
    st.plotly_chart(plot_precipitation_humidity(hourly_df), use_container_width=True)
    st.subheader("7-Day Summary Table")
    st.dataframe(daily_df, use_container_width=True, hide_index=True)

with tab3:
    us_aqi = aqi_current["us_aqi"]
    aqi_label, _ = get_aqi_category(us_aqi)
    st.subheader(f"Live Air Quality Status: **{aqi_label}** (US AQI: {us_aqi} | EU AQI: {aqi_current['european_aqi']})")

    g_col, p_col = st.columns(2)
    with g_col:
        st.plotly_chart(plot_aqi_gauge(us_aqi), use_container_width=True)
    with p_col:
        st.plotly_chart(plot_pollutants(aqi_current), use_container_width=True)

with tab4:
    st.subheader("Compare Multiple Cities Side-by-Side")
    city_list = st.multiselect(
        "Select or type any city in the world to compare:",
        options=[
            # Andhra Pradesh & Telangana
            "Hyderabad", "Visakhapatnam", "Vijayawada", "Guntur", "Nellore",
            "Kurnool", "Rajahmundry", "Tirupati", "Kakinada", "Pedana",
            "Machilipatnam", "Warangal", "Nizamabad", "Karimnagar",
            # Major Indian Cities
            "Mumbai", "New Delhi", "Bengaluru", "Chennai", "Kolkata",
            "Pune", "Ahmedabad", "Jaipur", "Surat", "Lucknow",
            "Kanpur", "Nagpur", "Indore", "Bhopal", "Patna",
            "Vadodara", "Coimbatore", "Kochi", "Chandigarh", "Guwahati",
            "Bhubaneswar", "Dehradun", "Jammu", "Srinagar", "Shimla",
            # Major World Cities
            "London", "New York", "Tokyo", "Dubai", "Singapore",
            "Paris", "Sydney", "Toronto", "Berlin", "Seoul",
            "Bangkok", "Riyadh", "Doha", "Moscow", "Los Angeles"
        ],
        default=["Hyderabad", "New Delhi", "Mumbai"],
        accept_new_options=True
    )

    comp_rows = []
    for c_name in city_list:
        loc = get_city_coordinates(c_name)
        if loc:
            w = get_weather_data(loc["lat"], loc["lon"], temp_param, wind_choice)["current"]
            a = get_aqi_data(loc["lat"], loc["lon"])["current"]
            _, cond = get_weather_info(w["weather_code"])
            comp_rows.append({
                "City": f"{loc['name']}, {loc['country']}",
                "Condition": cond,
                f"Temp ({temp_symbol})": w["temperature_2m"],
                f"Feels Like ({temp_symbol})": w["apparent_temperature"],
                "Humidity (%)": w["relative_humidity_2m"],
                f"Wind ({wind_choice})": w["wind_speed_10m"],
                "US AQI": a["us_aqi"],
            })

    if comp_rows:
        comp_df = pd.DataFrame(comp_rows)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        st.bar_chart(comp_df.set_index("City")[f"Temp ({temp_symbol})"])

    st.divider()
    st.subheader(f"Export {city_info['name']} 48-Hour Forecast Data")
    csv_data = hourly_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv_data,
        file_name=f"{city_info['name'].lower()}_weather_forecast.csv",
        mime="text/csv",
    )


if auto_refresh:
    time.sleep(60)
    st.rerun()
