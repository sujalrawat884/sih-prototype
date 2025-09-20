"""
Dummy Sensor Data Generator

This script simulates weather sensor data and sends it to the 
Cloudburst Early Warning System API every 5 seconds.
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict

import httpx


class SensorDataGenerator:
    """
    A class to generate realistic sensor data and send it to the API.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the sensor data generator.
        
        Args:
            api_base_url: Base URL of the FastAPI server
        """
        self.api_base_url = api_base_url
        self.endpoint = f"{api_base_url}/sensor-data"
        
        # Weather patterns for more realistic data generation
        self.weather_patterns = {
            "clear": {"rainfall_range": (0, 5), "humidity_range": (50, 70), "pressure_range": (1010, 1025)},
            "cloudy": {"rainfall_range": (0, 10), "humidity_range": (65, 80), "pressure_range": (1005, 1015)},
            "rainy": {"rainfall_range": (5, 30), "humidity_range": (75, 90), "pressure_range": (995, 1010)},
            "storm": {"rainfall_range": (25, 60), "humidity_range": (85, 95), "pressure_range": (980, 1000)},
            "cloudburst": {"rainfall_range": (50, 100), "humidity_range": (90, 100), "pressure_range": (980, 995)}
        }
        
        # Current weather state (for pattern continuity)
        self.current_pattern = "clear"
        self.pattern_duration = 0
        self.max_pattern_duration = random.randint(5, 15)  # 5-15 readings per pattern
    
    def generate_realistic_data(self) -> Dict[str, float]:
        """
        Generate realistic sensor data based on current weather pattern.
        
        Returns:
            Dict[str, float]: Dictionary containing sensor readings
        """
        # Change weather pattern occasionally for variety
        self.pattern_duration += 1
        if self.pattern_duration >= self.max_pattern_duration:
            self.pattern_duration = 0
            self.max_pattern_duration = random.randint(5, 15)
            
            # Choose new weather pattern with realistic probabilities
            pattern_weights = {
                "clear": 0.3,
                "cloudy": 0.3,
                "rainy": 0.25,
                "storm": 0.1,
                "cloudburst": 0.05  # Rare but possible
            }
            
            patterns = list(pattern_weights.keys())
            weights = list(pattern_weights.values())
            self.current_pattern = random.choices(patterns, weights=weights)[0]
            
            print(f"🌤️ Weather pattern changed to: {self.current_pattern}")
        
        # Get current pattern parameters
        pattern = self.weather_patterns[self.current_pattern]
        
        # Generate data within pattern ranges with some randomness
        rainfall = round(random.uniform(*pattern["rainfall_range"]), 2)
        humidity = round(random.uniform(*pattern["humidity_range"]), 2)
        pressure = round(random.uniform(*pattern["pressure_range"]), 2)
        
        # Temperature is somewhat independent but influenced by weather
        if self.current_pattern in ["storm", "cloudburst"]:
            temperature = round(random.uniform(15, 22), 2)  # Cooler during storms
        elif self.current_pattern == "clear":
            temperature = round(random.uniform(22, 30), 2)  # Warmer when clear
        else:
            temperature = round(random.uniform(18, 26), 2)  # Moderate
        
        return {
            "rainfall": rainfall,
            "humidity": humidity,
            "temperature": temperature,
            "pressure": pressure
        }
    
    def generate_random_data(self) -> Dict[str, float]:
        """
        Generate completely random sensor data within realistic ranges.
        
        Returns:
            Dict[str, float]: Dictionary containing sensor readings
        """
        return {
            "rainfall": round(random.uniform(0, 100), 2),      # 0-100 mm/hr
            "humidity": round(random.uniform(50, 100), 2),     # 50-100%
            "temperature": round(random.uniform(15, 30), 2),   # 15-30°C
            "pressure": round(random.uniform(980, 1020), 2)    # 980-1020 hPa
        }
    
    async def send_data(self, data: Dict[str, float]) -> None:
        """
        Send sensor data to the API endpoint.
        
        Args:
            data: Sensor data dictionary to send
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json=data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", "unknown")
                    timestamp = result.get("timestamp", "unknown")
                    
                    # Color-coded status display
                    status_colors = {
                        "safe": "🟢",
                        "warning": "🟡",
                        "cloudburst_detected": "🔴"
                    }
                    
                    color = status_colors.get(status, "⚪")
                    print(f"{color} Status: {status.upper()} | "
                          f"Rainfall: {data['rainfall']}mm/hr | "
                          f"Humidity: {data['humidity']}% | "
                          f"Pressure: {data['pressure']}hPa | "
                          f"Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Show additional info for warnings and alerts
                    if status == "warning":
                        print("   ⚠️ Elevated rainfall levels detected")
                    elif status == "cloudburst_detected":
                        print("   🚨 CLOUDBURST CONDITION DETECTED!")
                        
                else:
                    print(f"❌ Error: HTTP {response.status_code} - {response.text}")
                    
        except httpx.ConnectError:
            print("❌ Connection Error: Could not connect to the API server.")
            print("   Make sure the FastAPI server is running on http://localhost:8000")
        except httpx.TimeoutException:
            print("❌ Timeout Error: Request timed out")
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
    
    async def run_simulation(self, interval: int = 5, use_realistic_data: bool = True) -> None:
        """
        Run the sensor data simulation.
        
        Args:
            interval: Time interval between data transmissions (seconds)
            use_realistic_data: Whether to use realistic weather patterns
        """
        print("🌧️ Starting Sensor Data Generator...")
        print(f"📡 Sending data to: {self.endpoint}")
        print(f"⏱️ Interval: {interval} seconds")
        print(f"📊 Data mode: {'Realistic patterns' if use_realistic_data else 'Random'}")
        print("=" * 70)
        
        # Test connection first
        try:
            async with httpx.AsyncClient() as client:
                health_response = await client.get(f"{self.api_base_url}/health", timeout=5.0)
                if health_response.status_code == 200:
                    print("✅ Successfully connected to API server")
                else:
                    print("⚠️ API server responded but may have issues")
        except Exception:
            print("⚠️ Warning: Could not verify API server connection")
        
        print("=" * 70)
        
        try:
            reading_count = 0
            while True:
                reading_count += 1
                print(f"\n📊 Reading #{reading_count}")
                
                # Generate sensor data
                if use_realistic_data:
                    data = self.generate_realistic_data()
                else:
                    data = self.generate_random_data()
                
                # Send data to API
                await self.send_data(data)
                
                # Wait for next reading
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Simulation stopped by user after {reading_count} readings")
        except Exception as e:
            print(f"\n❌ Simulation error: {str(e)}")


async def main():
    """Main function to run the sensor data generator."""
    # Configuration
    API_URL = "http://localhost:8000"
    INTERVAL = 5  # seconds
    USE_REALISTIC_DATA = True
    
    # Create and run generator
    generator = SensorDataGenerator(api_base_url=API_URL)
    await generator.run_simulation(interval=INTERVAL, use_realistic_data=USE_REALISTIC_DATA)


if __name__ == "__main__":
    # Run the sensor data generator
    print("🚀 Cloudburst Early Warning System - Sensor Data Generator")
    print("Press Ctrl+C to stop the simulation\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")