"""
🌧️ Cloudburst Early Warning Dashboard

Streamlit dashboard for real-time monitoring of cloudburst conditions.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =============================
# CONFIGURATION
# =============================
API_URL = "http://localhost:8000/latest-readings"  # Change this to connect to another API URL
REFRESH_INTERVAL_MS = 5000  # Auto-refresh every 5 seconds

# =============================
# PAGE SETUP
# =============================
st.set_page_config(
    page_title="Cloudburst Early Warning Dashboard",
    page_icon="🌧️",
    layout="wide"
)

st.title("🌧️ Cloudburst Early Warning Dashboard")

# Status color legend
with st.expander("Status Legend", expanded=True):
    st.markdown("""
    <span style='font-size:1.2em'>
    <span style='color:green'>✅ Safe</span> &nbsp; 
    <span style='color:orange'>⚠️ Warning</span> &nbsp; 
    <span style='color:red'>🚨 Cloudburst Detected</span>
    </span>
    """, unsafe_allow_html=True)

# =============================
# AUTO-REFRESH
# =============================
st_autorefresh(interval=REFRESH_INTERVAL_MS, key="dashboard_autorefresh")

# =============================
# FETCH DATA FROM BACKEND
# =============================
def fetch_latest_readings(api_url: str) -> pd.DataFrame:
    """
    Fetch latest sensor readings from backend API and return as DataFrame.
    Args:
        api_url: URL to fetch readings from
    Returns:
        pd.DataFrame: DataFrame of readings
    Raises:
        Exception: If backend is unreachable or response is invalid
    """
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame()
        # Each reading: {timestamp, status, data: {rainfall, humidity, temperature, pressure}}
        df = pd.DataFrame([
            {
                "timestamp": r["timestamp"],
                "status": r["status"],
                "rainfall": r["data"].get("rainfall"),
                "humidity": r["data"].get("humidity"),
                "temperature": r["data"].get("temperature"),
                "pressure": r["data"].get("pressure"),
            }
            for r in data
        ])
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        raise Exception(f"Could not fetch data from backend: {e}")

# =============================
# MAIN DASHBOARD LOGIC
# =============================
try:
    df = fetch_latest_readings(API_URL)
    if df.empty:
        st.warning("No sensor data available yet. Waiting for readings...")
        st.stop()
except Exception as e:
    st.error(f"Backend unreachable: {e}")
    st.stop()

# Get latest status and timestamp
latest = df.iloc[-1]
status = latest["status"]
timestamp = latest["timestamp"]

# Status color mapping
status_colors = {
    "safe": ("✅", "green"),
    "warning": ("⚠️", "orange"),
    "cloudburst_detected": ("🚨", "red")
}
icon, color = status_colors.get(status, ("❔", "gray"))

# =============================
# LAYOUT
# =============================
left, right = st.columns([1, 3])

with left:
    st.markdown(f"<h2 style='color:{color};font-size:3em;text-align:center'>{icon} {status.replace('_', ' ').title()}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;font-size:1.1em'>Last alert: <b>{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</b></div>", unsafe_allow_html=True)
    st.markdown("<br>")
    st.markdown("<div style='font-size:1.1em'>System auto-refreshes every 5 seconds.</div>", unsafe_allow_html=True)

with right:
    st.subheader("Live Sensor Data (Last 50 Readings)")
    chart_cols = st.columns(2)
    # Rainfall
    with chart_cols[0]:
        st.markdown("**Rainfall (mm/hr)**")
        st.line_chart(df.set_index("timestamp")["rainfall"], use_container_width=True)
    # Humidity
    with chart_cols[1]:
        st.markdown("**Humidity (%)**")
        st.line_chart(df.set_index("timestamp")["humidity"], use_container_width=True)
    # Temperature
    with chart_cols[0]:
        st.markdown("**Temperature (°C)**")
        st.line_chart(df.set_index("timestamp")["temperature"], use_container_width=True)
    # Pressure
    with chart_cols[1]:
        st.markdown("**Pressure (hPa)**")
        st.line_chart(df.set_index("timestamp")["pressure"], use_container_width=True)

# =============================
# FOOTER
# =============================
st.markdown("---")
st.markdown("<div style='font-size:0.9em'>Backend API: <b>{API_URL}</b></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:0.9em'>To connect to another API, change <code>API_URL</code> at the top of this script.</div>", unsafe_allow_html=True)

# =============================
# END OF SCRIPT
# =============================
# To run: streamlit run streamlit_dashboard.py
# Make sure backend is running and accessible at API_URL.
