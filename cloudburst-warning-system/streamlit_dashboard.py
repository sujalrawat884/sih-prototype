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

# Custom CSS styling
st.markdown("""
    <style>
      [data-testid="stAppViewContainer"] 
      [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);  
      }
      [data-testid="stToolbar"] {
        right: 2rem;
      }
      .st-emotion-cache-czk5ss.e16jpq800 {
        visibility: hidden;
      }
      .st-emotion-cache-mnu3yk.ef3psqc5 {
        visibility: hidden;
      }
      .st-emotion-cache-15ecox0.ezrtsby0 {
        visibility: hidden;
      }
      .st-emotion-cache-fm8pe0.e1nzilvr4 {
        color: black;
      }
      .st-emotion-cache-fm8pe0.e1nzilvr4{
        color: white;
      }
    </style>
    """, unsafe_allow_html=True)

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

# Count recent cloudburst alerts (last 10 readings)
recent_alerts = df.tail(10)["status"].value_counts().get("cloudburst_detected", 0)

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
    
    # Show SMS alert notification for cloudburst detection
    if status == "cloudburst_detected":
        st.markdown("""
        <div style='background-color:#ffebee;border:2px solid #f44336;border-radius:10px;padding:15px;margin:10px 0;text-align:center'>
            <h3 style='color:#d32f2f;margin:0;font-weight:bold'>📱 SMS ALERT SENT</h3>
            <p style='color:#d32f2f;margin:5px 0;font-weight:bold'>Emergency SMS notifications have been sent to registered numbers</p>
            <p style='color:#333;font-size:0.9em;margin:0;font-weight:normal'>Stay safe and avoid low-lying regions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show alert details
        st.markdown(f"""
        <div style='background-color:#fff3e0;border:1px solid #ff9800;border-radius:5px;padding:10px;margin:5px 0'>
            <strong style='color:#333'>📊 Alert Details:</strong><br>
            <span style='color:#333'>Rainfall: {latest['rainfall']:.1f} mm/hr</span><br>
            <span style='color:#333'>Humidity: {latest['humidity']:.1f}%</span><br>
            <span style='color:#333'>Pressure: {latest['pressure']:.1f} hPa</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Show recent alert count
    if recent_alerts > 0:
        st.markdown(f"""
        <div style='background-color:#e3f2fd;border:1px solid #2196f3;border-radius:5px;padding:8px;margin:5px 0;text-align:center'>
            <strong style='color:#333'>🔔 Recent Alerts: {recent_alerts}</strong> <span style='color:#666'>(last 10 readings)</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>")
    st.markdown("<div style='font-size:1.1em'>System auto-refreshes every 5 seconds.</div>", unsafe_allow_html=True)

with right:
    st.subheader("Live Sensor Data (Last 50 Readings)")
    
    # Create a 2x2 grid for all 4 charts in one compact view
    chart_row1 = st.columns(2)
    chart_row2 = st.columns(2)
    
    # Row 1: Rainfall and Humidity
    with chart_row1[0]:
        st.markdown("**Rainfall (mm/hr)**")
        st.line_chart(df.set_index("timestamp")["rainfall"], use_container_width=True, height=200)
    
    with chart_row1[1]:
        st.markdown("**Humidity (%)**")
        st.line_chart(df.set_index("timestamp")["humidity"], use_container_width=True, height=200)
    
    # Row 2: Temperature and Pressure
    with chart_row2[0]:
        st.markdown("**Temperature (°C)**")
        st.line_chart(df.set_index("timestamp")["temperature"], use_container_width=True, height=200)
    
    with chart_row2[1]:
        st.markdown("**Pressure (hPa)**")
        st.line_chart(df.set_index("timestamp")["pressure"], use_container_width=True, height=200)

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
