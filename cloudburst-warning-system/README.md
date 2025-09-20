# 🌧️ Cloudburst Early Warning System

A prototype system for detecting cloudburst conditions using real-time sensor data analysis. This system uses machine learning-inspired anomaly detection to identify dangerous weather patterns and trigger alerts.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sensor Data   │───▶│   FastAPI       │───▶│   Alert System  │
│   Generator     │    │   Backend       │    │   (SMS/Logging) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Data Storage   │
                       │  (In-Memory)    │
                       └─────────────────┘
```

## 📋 Features

- **Real-time Sensor Data Processing**: Handles rainfall, humidity, temperature, and pressure data
- **Anomaly Detection**: Three-tier alert system (Safe, Warning, Cloudburst Detected)
- **Data Storage**: In-memory storage of last 50 readings for dashboard integration
- **Alert System**: Automated logging and SMS alerts for dangerous conditions
- **REST API**: RESTful endpoints for easy integration with dashboards
- **Realistic Data Simulation**: Weather pattern-based sensor data generator

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or Download the Project**
   ```powershell
   cd "C:\Users\Shruti\Downloads\SIH\cloudburst-warning-system"
   ```

2. **Create Virtual Environment (Recommended)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

## 🚀 Running the System

### Step 1: Start the FastAPI Backend

Open a terminal/PowerShell and run:

```powershell
cd "C:\Users\Shruti\Downloads\SIH\cloudburst-warning-system\src"
python main.py
```

You should see:
```
🌧️ Starting Cloudburst Early Warning System...
📊 API documentation available at: http://localhost:8000/docs
🔍 Alternative docs at: http://localhost:8000/redoc
```

### Step 2: Start the Sensor Data Generator

Open a **new** terminal/PowerShell window and run:

```powershell
cd "C:\Users\Shruti\Downloads\SIH\cloudburst-warning-system\src"
python sensor_generator.py
```

You should see real-time sensor data being generated and sent to the API:
```
🚀 Cloudburst Early Warning System - Sensor Data Generator
📡 Sending data to: http://localhost:8000/sensor-data
⏱️ Interval: 5 seconds
📊 Data mode: Realistic patterns

🟢 Status: SAFE | Rainfall: 2.34mm/hr | Humidity: 65.12% | Pressure: 1015.67hPa
```

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sensor-data` | Submit sensor readings for analysis |
| `GET` | `/latest-readings` | Retrieve last 50 sensor readings |
| `GET` | `/health` | Health check and system status |
| `GET` | `/` | API information and documentation |

### API Documentation

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc

### Example API Usage

#### Submit Sensor Data
```bash
curl -X POST "http://localhost:8000/sensor-data" \
-H "Content-Type: application/json" \
-d '{
  "rainfall": 45.5,
  "humidity": 88.2,
  "temperature": 22.1,
  "pressure": 995.5
}'
```

#### Get Latest Readings
```bash
curl -X GET "http://localhost:8000/latest-readings"
```

## 🎯 Detection Logic

### Alert Levels

1. **🟢 Safe**: Normal weather conditions
   - Rainfall ≤ 20 mm/hr
   - Standard humidity and pressure

2. **🟡 Warning**: Elevated conditions requiring monitoring
   - Rainfall between 20-50 mm/hr

3. **🔴 Cloudburst Detected**: Dangerous conditions requiring immediate action
   - Rainfall > 50 mm/hr **OR**
   - (Humidity > 85% **AND** Pressure < 1000 hPa)

### Example Scenarios

| Rainfall | Humidity | Pressure | Status | Reason |
|----------|----------|----------|--------|---------|
| 15.0 | 65.0 | 1015.0 | 🟢 Safe | Normal conditions |
| 35.0 | 70.0 | 1010.0 | 🟡 Warning | Moderate rainfall |
| 55.0 | 80.0 | 1005.0 | 🔴 Cloudburst | High rainfall |
| 25.0 | 90.0 | 995.0 | 🔴 Cloudburst | High humidity + low pressure |

## 📁 Project Structure

```
cloudburst-warning-system/
│
├── src/
│   ├── main.py              # FastAPI backend application
│   └── sensor_generator.py  # Dummy sensor data generator
│
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables (Optional)

You can customize the system behavior by setting these environment variables:

- `API_HOST`: API server host (default: "0.0.0.0")
- `API_PORT`: API server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: "info")

### Sensor Generator Configuration

Edit `sensor_generator.py` to modify:

- `INTERVAL`: Time between readings (default: 5 seconds)
- `API_URL`: Backend API URL (default: "http://localhost:8000")
- `USE_REALISTIC_DATA`: Use weather patterns vs random data

## 🎯 Integration with Streamlit Dashboard

The system is designed for easy integration with a Streamlit dashboard:

1. **Data Access**: Use the `/latest-readings` endpoint to fetch data
2. **Real-time Updates**: Poll the API every few seconds for live updates
3. **Visualization**: Plot rainfall, humidity, pressure trends over time
4. **Alert Display**: Show current status and recent alerts

### Example Streamlit Integration

```python
import streamlit as st
import requests
import pandas as pd

# Fetch latest readings
response = requests.get("http://localhost:8000/latest-readings")
data = response.json()

# Convert to DataFrame
df = pd.DataFrame([reading['data'] for reading in data])
df['timestamp'] = [reading['timestamp'] for reading in data]
df['status'] = [reading['status'] for reading in data]

# Display charts
st.line_chart(df.set_index('timestamp')[['rainfall', 'humidity', 'pressure']])
```

## 🧪 Testing

### Manual Testing

1. **Start the system** as described above
2. **Monitor the console output** for different weather patterns
3. **Check API responses** using the interactive documentation at http://localhost:8000/docs
4. **Verify alerts** are triggered when cloudburst conditions are detected

### API Testing with curl

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test with safe conditions
curl -X POST "http://localhost:8000/sensor-data" -H "Content-Type: application/json" -d '{"rainfall": 5, "humidity": 60, "temperature": 25, "pressure": 1015}'

# Test with warning conditions
curl -X POST "http://localhost:8000/sensor-data" -H "Content-Type: application/json" -d '{"rainfall": 30, "humidity": 70, "temperature": 22, "pressure": 1010}'

# Test with cloudburst conditions
curl -X POST "http://localhost:8000/sensor-data" -H "Content-Type: application/json" -d '{"rainfall": 60, "humidity": 95, "temperature": 20, "pressure": 985}'
```

## 🚨 Troubleshooting

### Common Issues

1. **"Connection Error" in sensor generator**
   - Ensure the FastAPI backend is running first
   - Check that port 8000 is not blocked by firewall

2. **"Module not found" errors**
   - Activate your virtual environment
   - Run `pip install -r requirements.txt`

3. **Port already in use**
   - Change the port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`
   - Update the API_URL in `sensor_generator.py` accordingly

### Logs and Debugging

- Check console output for detailed error messages
- API logs show all incoming requests and responses
- Sensor generator displays connection status and response codes

## 🔮 Future Enhancements

- **Database Integration**: Replace in-memory storage with persistent database
- **Authentication**: Add API key authentication for production use
- **Geographic Data**: Include GPS coordinates for location-based alerts
- **Historical Analysis**: Implement trend analysis and prediction models
- **Multiple Sensors**: Support for multiple weather stations
- **Real SMS Integration**: Connect with actual SMS service providers
- **Web Dashboard**: Built-in web interface for monitoring

## 📄 License

This project is created for educational and demonstration purposes. Feel free to modify and extend it for your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built for SIH (Smart India Hackathon) - Cloudburst Early Warning System Prototype** 🇮🇳