"""
Test Script for Cloudburst Early Warning System

This script runs basic tests to verify the system components work correctly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from main import anomaly_detection, SensorData
import httpx


def test_anomaly_detection():
    """Test the anomaly detection function with various scenarios."""
    print("🧪 Testing anomaly detection function...")
    
    test_cases = [
        # Test case: (data, expected_status, description)
        ({"rainfall": 10, "humidity": 60, "temperature": 25, "pressure": 1015}, "safe", "Normal conditions"),
        ({"rainfall": 30, "humidity": 70, "temperature": 22, "pressure": 1010}, "warning", "Moderate rainfall"),
        ({"rainfall": 60, "humidity": 80, "temperature": 20, "pressure": 1005}, "cloudburst_detected", "High rainfall"),
        ({"rainfall": 15, "humidity": 90, "temperature": 18, "pressure": 995}, "cloudburst_detected", "High humidity + low pressure"),
        ({"rainfall": 25, "humidity": 85, "temperature": 20, "pressure": 1005}, "warning", "Moderate rainfall, normal pressure"),
        ({"rainfall": 0, "humidity": 50, "temperature": 30, "pressure": 1020}, "safe", "Clear weather"),
    ]
    
    for data, expected, description in test_cases:
        result = anomaly_detection(data)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {status} {description}: {result} (expected: {expected})")
        
        if result != expected:
            print(f"    Data: {data}")
    
    print()


def test_pydantic_model():
    """Test the SensorData Pydantic model."""
    print("🧪 Testing SensorData Pydantic model...")
    
    try:
        # Valid data
        valid_data = SensorData(rainfall=25.5, humidity=75.2, temperature=22.1, pressure=1008.3)
        print("  ✅ PASS Valid data accepted")
        
        # Test data access
        assert valid_data.rainfall == 25.5
        assert valid_data.humidity == 75.2
        print("  ✅ PASS Data access works correctly")
        
        # Test JSON serialization
        json_data = valid_data.model_dump()
        assert isinstance(json_data, dict)
        print("  ✅ PASS JSON serialization works")
        
    except Exception as e:
        print(f"  ❌ FAIL Model test failed: {e}")
    
    print()


async def test_api_endpoints():
    """Test API endpoints if the server is running."""
    print("🧪 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_response = await client.get(f"{base_url}/health", timeout=5.0)
            if health_response.status_code == 200:
                print("  ✅ PASS Health endpoint accessible")
                
                # Test sensor data endpoint
                test_data = {
                    "rainfall": 25.0,
                    "humidity": 80.0,
                    "temperature": 22.0,
                    "pressure": 1005.0
                }
                
                sensor_response = await client.post(
                    f"{base_url}/sensor-data",
                    json=test_data,
                    timeout=10.0
                )
                
                if sensor_response.status_code == 200:
                    result = sensor_response.json()
                    print(f"  ✅ PASS Sensor data endpoint works - Status: {result.get('status')}")
                    
                    # Test latest readings endpoint
                    readings_response = await client.get(f"{base_url}/latest-readings", timeout=5.0)
                    if readings_response.status_code == 200:
                        readings = readings_response.json()
                        print(f"  ✅ PASS Latest readings endpoint works - Count: {len(readings)}")
                    else:
                        print(f"  ❌ FAIL Latest readings endpoint error: {readings_response.status_code}")
                        
                else:
                    print(f"  ❌ FAIL Sensor data endpoint error: {sensor_response.status_code}")
                    
            else:
                print(f"  ❌ FAIL Health endpoint error: {health_response.status_code}")
                
    except httpx.ConnectError:
        print("  ⚠️ SKIP API tests - Server not running")
        print("    Start the server with: python src/main.py")
    except Exception as e:
        print(f"  ❌ FAIL API test error: {e}")
    
    print()


def main():
    """Run all tests."""
    print("🚀 Cloudburst Early Warning System - Test Suite")
    print("=" * 60)
    
    # Unit tests (don't require server)
    test_anomaly_detection()
    test_pydantic_model()
    
    # Integration tests (require server)
    print("Note: API tests require the FastAPI server to be running")
    try:
        asyncio.run(test_api_endpoints())
    except Exception as e:
        print(f"API test setup failed: {e}")
    
    print("=" * 60)
    print("✨ Test suite completed!")
    print("\nTo run the full system:")
    print("1. python src/main.py          # Start API server")
    print("2. python src/sensor_generator.py  # Start sensor generator")


if __name__ == "__main__":
    main()