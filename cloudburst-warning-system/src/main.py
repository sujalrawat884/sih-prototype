"""
Cloudburst Early Warning System - FastAPI Backend

This module implements a FastAPI backend for a cloudburst early warning system
that processes sensor data and provides anomaly detection.
"""

from collections import deque
from datetime import datetime
from typing import Dict, List
import logging
from dotenv import load_dotenv
import os
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from twilio.rest import Client  # Add Twilio Client import

load_dotenv()  # Load environment variables from .env file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Twilio client (with error handling)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")  # Your Twilio phone number

# Check if Twilio credentials are available
TWILIO_ENABLED = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_NUMBER)

if TWILIO_ENABLED:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        logger.info("✅ Twilio SMS service initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Twilio initialization failed: {e}")
        TWILIO_ENABLED = False
        twilio_client = None
else:
    twilio_client = None
    logger.info("📱 Twilio SMS service disabled (credentials not found) - using mock SMS")

# Initialize FastAPI app
app = FastAPI(
    title="Cloudburst Early Warning System",
    description="A system for detecting cloudburst conditions using sensor data",
    version="1.0.0"
)

# In-memory storage for sensor readings (last 50 readings)
sensor_readings: deque = deque(maxlen=50)


class SensorData(BaseModel):
    """
    Pydantic model for sensor data input.
    
    Attributes:
        rainfall: Rainfall measurement in mm/hr
        humidity: Humidity percentage (0-100)
        temperature: Temperature in Celsius
        pressure: Atmospheric pressure in hPa
    """
    rainfall: float
    humidity: float
    temperature: float
    pressure: float


class SensorResponse(BaseModel):
    """
    Pydantic model for sensor data response.
    
    Attributes:
        status: Detection status ("safe", "warning", "cloudburst_detected")
        timestamp: ISO timestamp of the reading
        data: Original sensor data
    """
    status: str
    timestamp: str
    data: SensorData


def anomaly_detection(data: Dict[str, float]) -> str:
    """
    Analyze sensor data to detect cloudburst conditions.
    
    Args:
        data: Dictionary containing sensor readings
        
    Returns:
        str: Detection status - "safe", "warning", or "cloudburst_detected"
        
    Detection Logic:
        - Cloudburst: rainfall > 50 OR (humidity > 85 AND pressure < 1000)
        - Warning: rainfall between 20-50
        - Safe: all other conditions
    """
    rainfall = data.get("rainfall", 0)
    humidity = data.get("humidity", 0)
    pressure = data.get("pressure", 1013.25)  # Standard atmospheric pressure
    
    # Check for cloudburst conditions
    if rainfall > 50 or (humidity > 85 and pressure < 1000):
        return "cloudburst_detected"
    
    # Check for warning conditions
    if 20 <= rainfall <= 50:
        return "warning"
    
    # Safe conditions
    return "safe"

def send_alert_sms(message: str, numbers: list):
    """
    Send SMS alert using Twilio to a list of phone numbers.
    Falls back to mock SMS if Twilio is not configured or fails.
    
    Args:
        message: SMS message content
        numbers: List of phone numbers to send to
        
    Returns:
        list: List of response objects with SMS status
    """
    responses = []
    
    if not TWILIO_ENABLED or not twilio_client:
        # Mock SMS functionality for testing/demo
        for number in numbers:
            mock_response = {
                "number": number,
                "sid": f"mock_sms_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "mock_sent",
                "message": "SMS service in demo mode"
            }
            responses.append(mock_response)
            logger.info(f"📱 MOCK SMS sent to {number}: {message}")
            print(f"📱 MOCK SMS ALERT → {number}: {message}")
        return responses
    
    # Real SMS sending with error handling
    for number in numbers:
        try:
            sms = twilio_client.messages.create(
                body=message,
                from_=TWILIO_NUMBER,
                to=f"+91{number}"  # Add country code if needed
            )
            logger.info(f"✅ Real SMS sent to {number}. SID: {sms.sid}, Status: {sms.status}")
            responses.append({
                "number": number, 
                "sid": sms.sid, 
                "status": sms.status,
                "message": "SMS sent successfully"
            })
        except Exception as e:
            logger.error(f"❌ Failed to send SMS to {number}: {str(e)}")
            # Fallback to mock SMS on failure
            mock_response = {
                "number": number,
                "sid": f"fallback_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "mock_fallback",
                "message": f"SMS failed, using mock: {str(e)}"
            }
            responses.append(mock_response)
            print(f"📱 FALLBACK MOCK SMS → {number}: {message}")
    
    return responses

def trigger_alert(status: str, sensor_data: SensorData) -> None:
    """
    Trigger appropriate alerts based on detection status.
    
    Args:
        status: Detection status from anomaly detection
        sensor_data: The sensor data that triggered the alert
    """
    if status == "cloudburst_detected":
        alert_message = f"🚨 ALERT: Cloudburst detected! Rainfall: {sensor_data.rainfall}mm/hr, " \
                   f"Humidity: {sensor_data.humidity}%, Pressure: {sensor_data.pressure}hPa. " \
                   f"Stay safe and avoid low-lying regions."
        logger.critical(alert_message)
        send_alert_sms(alert_message, ["9937424848"])
    elif status == "warning":
        warning_message = f"⚠️ WARNING: High rainfall detected. Rainfall: {sensor_data.rainfall}mm/hr"
        logger.warning(warning_message)
        print(warning_message)


@app.get("/")
async def root():
    """Root endpoint providing system information."""
    return {
        "message": "Cloudburst Early Warning System API",
        "version": "1.0.0",
        "endpoints": {
            "POST /sensor-data": "Submit sensor readings",
            "GET /latest-readings": "Get last 50 sensor readings",
            "POST /trigger-cloudburst": "Manually trigger cloudburst alert (for testing)",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with SMS service status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "readings_count": len(sensor_readings),
        "sms_service": {
            "enabled": TWILIO_ENABLED,
            "status": "active" if TWILIO_ENABLED else "mock_mode",
            "message": "Real SMS service" if TWILIO_ENABLED else "Using mock SMS for demo"
        }
    }


@app.post("/sensor-data", response_model=SensorResponse)
async def process_sensor_data(sensor_data: SensorData):
    """
    Process incoming sensor data and perform anomaly detection.
    
    Args:
        sensor_data: Sensor readings from weather station
        
    Returns:
        SensorResponse: Detection status and timestamp
        
    Raises:
        HTTPException: If sensor data is invalid
    """
    try:
        # Convert sensor data to dictionary for anomaly detection
        data_dict = sensor_data.dict()
        
        # Perform anomaly detection
        status = anomaly_detection(data_dict)
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Store reading with timestamp and status
        reading_record = {
            "timestamp": timestamp,
            "status": status,
            "data": data_dict
        }
        sensor_readings.append(reading_record)
        
        # Trigger alerts if necessary
        trigger_alert(status, sensor_data)
        
        # Create response
        response = SensorResponse(
            status=status,
            timestamp=timestamp,
            data=sensor_data
        )
        
        logger.info(f"Processed sensor data: {status} - {timestamp}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing sensor data: {str(e)}")


@app.post("/trigger-cloudburst")
async def trigger_manual_cloudburst():
    """
    Manually trigger a cloudburst alert for testing/demo purposes.
    
    This endpoint creates a fake cloudburst scenario with extreme sensor values
    and triggers all the alert mechanisms including SMS alerts.
    
    Returns:
        Dict: Response with cloudburst status and timestamp
    """
    try:
        # Create fake extreme sensor data that would trigger cloudburst
        fake_sensor_data = SensorData(
            rainfall=75.5,    # High rainfall > 50
            humidity=95.2,    # High humidity > 85
            temperature=18.5, # Low temperature (storm conditions)
            pressure=985.3    # Low pressure < 1000
        )
        
        # Force cloudburst detection
        status = "cloudburst_detected"
        timestamp = datetime.now().isoformat()
        
        # Store the fake reading
        reading_record = {
            "timestamp": timestamp,
            "status": status,
            "data": fake_sensor_data.dict()
        }
        sensor_readings.append(reading_record)
        
        # Trigger all alerts (SMS, logging, etc.)
        trigger_alert(status, fake_sensor_data)
        
        # Create response
        response = {
            "status": status,
            "timestamp": timestamp,
            "message": "Manual cloudburst alert triggered successfully!",
            "data": fake_sensor_data.dict(),
            "alert_sent": True
        }
        
        logger.critical(f"Manual cloudburst triggered: {timestamp}")
        return response
        
    except Exception as e:
        logger.error(f"Error triggering manual cloudburst: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering cloudburst: {str(e)}")


@app.get("/latest-readings")
async def get_latest_readings() -> List[Dict]:
    """
    Retrieve the last 50 sensor readings for dashboard visualization.
    
    Returns:
        List[Dict]: List of sensor readings with timestamps and status
    """
    try:
        readings_list = list(sensor_readings)
        logger.info(f"Retrieved {len(readings_list)} latest readings")
        return readings_list
        
    except Exception as e:
        logger.error(f"Error retrieving readings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving readings: {str(e)}")


if __name__ == "__main__":
    # Run the application
    print("🌧️ Starting Cloudburst Early Warning System...")
    print("📊 API documentation available at: http://localhost:8000/docs")
    print("🔍 Alternative docs at: http://localhost:8000/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )