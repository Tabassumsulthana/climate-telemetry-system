import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import get_aqi_category

def plot_hourly_temp(df: pd.DataFrame, unit_symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["Temperature"], mode="lines+markers",
        name=f"Temperature ({unit_symbol})", line=dict(color="#ff6b6b", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["Feels Like"], mode="lines",
        name=f"Feels Like ({unit_symbol})", line=dict(color="#feca57", width=2, dash="dash")
    ))
    fig.update_layout(
        title="48-Hour Temperature & Feels-Like Trend",
        xaxis_title="Time", yaxis_title=f"Temperature ({unit_symbol})",
        hovermode="x unified", template="plotly_dark", height=380
    )
    return fig

def plot_daily_range(df: pd.DataFrame, unit_symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Date"], y=df["Max Temp"], name="Max Temp", marker_color="#ff7675"))
    fig.add_trace(go.Bar(x=df["Date"], y=df["Min Temp"], name="Min Temp", marker_color="#74b9ff"))
    fig.update_layout(
        title="7-Day High vs. Low Temperature",
        barmode="group", yaxis_title=f"Temperature ({unit_symbol})",
        template="plotly_dark", height=360
    )
    return fig

def plot_precipitation_humidity(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Time"], y=df["Precipitation Prob (%)"],
        name="Rain Probability (%)", marker_color="#0984e3", opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["Humidity (%)"],
        name="Humidity (%)", line=dict(color="#00cec9", width=2)
    ))
    fig.update_layout(
        title="48-Hour Humidity & Precipitation Probability",
        yaxis_title="Percentage (%)", hovermode="x unified",
        template="plotly_dark", height=360
    )
    return fig

def plot_city_map(city_info: dict):
    fig = go.Figure(go.Scattergeo(
        lat=[city_info["lat"]],
        lon=[city_info["lon"]],
        text=[f"{city_info['name']}, {city_info['country']}"],
        mode="markers+text",
        textposition="top center",
        marker=dict(size=14, color="#ff6b6b", symbol="circle")
    ))
    fig.update_geos(
        projection_type="natural earth", showcountries=True,
        center=dict(lat=city_info["lat"], lon=city_info["lon"]),
        projection_scale=4
    )
    fig.update_layout(
        title="Live Station Coordinates", template="plotly_dark",
        height=320, margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def plot_aqi_gauge(us_aqi: float):
    label, color = get_aqi_category(us_aqi)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=us_aqi,
        title={"text": f"US AQI ({label})"},
        gauge={
            "axis": {"range": [0, 300]},
            "bar": {"color": color},
            "steps": [
                {"range": list((0, 50)), "color": "rgba(46, 204, 113, 0.25)"},
                {"range": list((50, 100)), "color": "rgba(241, 196, 15, 0.25)"},
                {"range": list((100, 150)), "color": "rgba(230, 126, 34, 0.25)"},
                {"range": list((150, 200)), "color": "rgba(231, 76, 60, 0.25)"},
                {"range": list((200, 300)), "color": "rgba(155, 89, 182, 0.25)"},
            ],
        }
    ))
    fig.update_layout(template="plotly_dark", height=300)
    return fig

def plot_pollutants(aqi_current: dict):
    pollutants = {
        "PM2.5 (µg/m³)": aqi_current.get("pm2_5", 0),
        "PM10 (µg/m³)": aqi_current.get("pm10", 0),
        "NO₂ (µg/m³)": aqi_current.get("nitrogen_dioxide", 0),
        "Ozone O₃ (µg/m³)": aqi_current.get("ozone", 0),
    }
    fig = px.bar(
        x=list(pollutants.keys()), y=list(pollutants.values()),
        labels={"x": "Pollutant", "y": "Concentration (µg/m³)"},
        title="Air Pollutant Breakdown", color=list(pollutants.keys()),
        template="plotly_dark", height=300
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_5year_baseline(baseline_df: pd.DataFrame, unit_symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=baseline_df["Year"], y=baseline_df["Historical Max"],
        mode="lines+markers", name=f"Max Temp ({unit_symbol})", line=dict(color="#ff7675", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=baseline_df["Year"], y=baseline_df["Historical Min"],
        mode="lines+markers", name=f"Min Temp ({unit_symbol})", line=dict(color="#74b9ff", width=3)
    ))
    fig.update_layout(
        title="5-Year Historical Temperature Baseline (Same Date)",
        xaxis_title="Year", yaxis_title=f"Temperature ({unit_symbol})",
        template="plotly_dark", height=360
    )
    return fig