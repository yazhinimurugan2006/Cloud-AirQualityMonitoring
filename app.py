import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Air Quality Monitoring — Kaggle Dataset", layout="wide")
st.title("🌏 Cloud-Powered Real-Time Air Quality Monitoring")
st.caption("Sustainable Development Goal 13 — Climate Action")

@st.cache_data
def load_data():
    # Load dataset
    df = pd.read_csv("air_quality_data.csv")

    # Normalize column names (lowercase, remove spaces, replace dots with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace('.', '_')

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop rows without PM2.5 readings
    if 'pm2_5' not in df.columns:
        st.error("❌ The dataset does not contain a PM2.5 column.")
        st.stop()

    df = df.dropna(subset=['pm2_5'])
    return df

# Load data
data = load_data()

# Sidebar city selection
cities = st.sidebar.multiselect("Select Cities", data["city"].unique(), default=data["city"].unique()[:3])
mask = data["city"].isin(cities)
filtered = data.loc[mask]

# AQI level function
def aqi_level(pm):
    if pm <= 30: return "Good"
    elif pm <= 60: return "Moderate"
    elif pm <= 90: return "Poor"
    elif pm <= 120: return "Very Poor"
    else: return "Severe"

filtered["AQI_Level"] = filtered["pm2_5"].apply(aqi_level)

# Line chart for PM2.5 over time
st.markdown("### PM2.5 Levels Over Time")
st.plotly_chart(
    px.line(filtered, x="date", y="pm2_5", color="city", title="PM2.5 Concentration Over Time"),
    use_container_width=True
)

# Average pollutant levels
pollutants = ["pm2_5", "pm10", "no2", "so2", "co", "o3"]
available = [p for p in pollutants if p in filtered.columns]

st.markdown("### Average Pollutant Levels by City")
avg = filtered.groupby("city")[available].mean().reset_index()
st.plotly_chart(
    px.bar(avg, x="city", y=available, barmode="group", title="Average Pollutant Concentrations"),
    use_container_width=True
)

# Correlation heatmap
st.markdown("### Pollutant Correlation Heatmap")
corr = filtered[available].corr()
st.plotly_chart(px.imshow(corr, text_auto=True, title="Pollutant Correlation Matrix"), use_container_width=True)

# AQI category table
st.markdown("### AQI Category Table (Last 10 Entries)")
st.dataframe(filtered[["date", "city", "pm2_5", "AQI_Level"]].tail(10))
