#!/usr/bin/env python3
"""
GopiAI Application Entry Point for Briefcase Packaging

This module serves as the main entry point for the packaged GopiAI application.
It handles startup of both the CrewAI server and the UI components.
"""

import sys
import os
import threading
import time
import subprocess
from pathlib import Path

# Add project paths to Python path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "GopiAI-UI"))
sys.path.insert(0, str(current_dir / "GopiAI-CrewAI"))

def start_crewai_server():
    """Start the CrewAI API server in a separate process"""
    try:
        crewai_dir = current_dir / "GopiAI-CrewAI"
        os.chdir(crewai_dir)
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{crewai_dir}:{env.get('PYTHONPATH', '')}"
        
        print("🚀 Starting CrewAI server...")
        
        # Start the server
        server_process = subprocess.Popen([
            sys.executable, "crewai_api_server.py"
        ], env=env, cwd=crewai_dir)
        
        return server_process
        
    except Exception as e:
        print(f"❌ Failed to start CrewAI server: {e}")
        return None

def wait_for_server(max_attempts=30):
    """Wait for the server to be ready"""
    import requests
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:5052/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ CrewAI server is ready")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print("❌ Server failed to start within timeout")
    return False


def main():
    """Briefcase entry point"""
    return _main()

def _main():
    """Internal main function"""
    print("🚀 GopiAI Application Starting...")
    
    # Start CrewAI server in background
    server_process = start_crewai_server()
    if not server_process:
        print("❌ Failed to start server component")
        return 1
    
    # Wait for server to be ready
    if not wait_for_server():
        print("❌ Server is not responding")
        server_process.terminate()
        return 1
    
    try:
        # Import and start UI
        print("🖥️ Starting UI...")
        
        # Change back to UI directory
        ui_dir = current_dir / "GopiAI-UI"
        os.chdir(ui_dir)
        
        # Import UI main after paths are set
        from gopiai.ui.main import main as ui_main
        
        # Start UI in main thread
        return ui_main()
        
    except KeyboardInterrupt:
        print("\n⚠️ Shutting down...")
        server_process.terminate()
        return 0
    except Exception as e:
        print(f"❌ UI Error: {e}")
        server_process.terminate()
        return 1

if __name__ == "__main__":
    sys.exit(_main())