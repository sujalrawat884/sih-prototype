"""
Quick Start Script for Cloudburst Early Warning System

This script helps you quickly start the system components.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        print("  ✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"  ❌ Missing dependency: {e}")
        print("  📦 Please run: pip install -r requirements.txt")
        return False


def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    
    src_path = Path(__file__).parent / "src"
    main_script = src_path / "main.py"
    
    if not main_script.exists():
        print(f"❌ Error: {main_script} not found")
        return None
    
    try:
        # Start the server in a new process
        process = subprocess.Popen(
            [sys.executable, str(main_script)],
            cwd=str(src_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print(f"  ✅ Server started with PID: {process.pid}")
        print("  🌐 API will be available at: http://localhost:8000")
        return process
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return None


def start_sensor_generator():
    """Start the sensor data generator."""
    print("📡 Starting sensor data generator...")
    
    src_path = Path(__file__).parent / "src"
    generator_script = src_path / "sensor_generator.py"
    
    if not generator_script.exists():
        print(f"❌ Error: {generator_script} not found")
        return None
    
    try:
        # Start the generator in a new process
        process = subprocess.Popen(
            [sys.executable, str(generator_script)],
            cwd=str(src_path),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print(f"  ✅ Sensor generator started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"  ❌ Failed to start sensor generator: {e}")
        return None


def wait_for_server(max_attempts=10):
    """Wait for the server to be ready."""
    import httpx
    
    print("⏳ Waiting for server to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = httpx.get("http://localhost:8000/health", timeout=2.0)
            if response.status_code == 200:
                print("  ✅ Server is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"  ⏳ Attempt {attempt + 1}/{max_attempts}...")
    
    print("  ⚠️ Server may not be ready yet, but continuing...")
    return False


def open_documentation():
    """Open API documentation in browser."""
    try:
        webbrowser.open("http://localhost:8000/docs")
        print("  📚 API documentation opened in browser")
    except Exception as e:
        print(f"  ⚠️ Could not open browser: {e}")
        print("  📚 Manual link: http://localhost:8000/docs")


def main():
    """Main function to start the system."""
    print("🌧️ Cloudburst Early Warning System - Quick Start")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print()
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server. Exiting.")
        return
    
    print()
    
    # Wait for server to be ready
    server_ready = wait_for_server()
    
    print()
    
    # Start sensor generator
    sensor_process = start_sensor_generator()
    
    print()
    print("=" * 60)
    print("✨ System Started Successfully!")
    print()
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📈 Latest Readings: http://localhost:8000/latest-readings")
    print()
    print("🎯 What's happening:")
    print("  • FastAPI server is running and accepting sensor data")
    print("  • Sensor data generator is sending realistic weather data every 5 seconds")
    print("  • System will detect and alert on cloudburst conditions")
    print()
    print("⚠️ To stop the system:")
    print("  • Close the console windows that opened")
    print("  • Or press Ctrl+C in each window")
    print()
    
    # Optionally open documentation
    try:
        user_input = input("📚 Open API documentation in browser? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '']:
            open_documentation()
    except KeyboardInterrupt:
        print("\n👋 Setup complete!")
    
    print("=" * 60)
    print("🚀 System is now running! Check the console windows for real-time data.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Quick start interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Quick start failed: {e}")
        print("Try running the components manually:")
        print("1. python src/main.py")
        print("2. python src/sensor_generator.py")