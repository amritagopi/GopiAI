#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Reproduce and Log Hang Script
================================

This script reproduces the hang issue where messages freeze in "⏳ Обрабатываю запрос..." state
when RAG service (port 5051) is stopped, and captures detailed DEBUG logs.

Steps:
1. Ensures RAG service (port 5051) is STOPPED
2. Enables DEBUG logging in both UI and CrewAI modules
3. Launches GopiAI-UI with detailed logging
4. Guides user to reproduce the hang
5. Captures all debug output to log files
"""

import os
import sys
import time
import subprocess
import logging
import psutil
import requests
from datetime import datetime
from pathlib import Path

def setup_debug_logging():
    """Configure DEBUG level logging for comprehensive debug output"""
    log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"gopiai_hang_debug_{log_timestamp}.log"
    
    # Configure root logger for DEBUG level
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s.%(msecs)03d] %(name)-20s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"📁 Debug logs will be saved to: {log_file}")
    return log_file, logger

def check_port_status(port, service_name):
    """Check if a specific port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True, conn.pid
    return False, None

def stop_rag_service():
    """Stop RAG service running on port 5051"""
    print("\n🔍 Checking RAG service status (port 5051)...")
    
    # Check if port 5051 is in use
    in_use, pid = check_port_status(5051, "RAG service")
    
    if in_use:
        print(f"⚠️ RAG service is running on port 5051 (PID: {pid})")
        print("🛑 Stopping RAG service...")
        
        try:
            if pid:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=10)
                print(f"✅ RAG service stopped (PID: {pid})")
            else:
                print("⚠️ Could not determine PID, trying alternative methods...")
                # Try to kill any python processes using port 5051
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
        except Exception as e:
            print(f"❌ Error stopping RAG service: {e}")
            print("💡 You may need to manually stop the RAG service")
    else:
        print("✅ RAG service is not running (port 5051 is free)")
    
    # Double-check by trying to connect
    try:
        response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
        if response.status_code == 200:
            print("⚠️ WARNING: RAG service still responds! Manual intervention needed.")
            return False
    except requests.exceptions.RequestException:
        print("✅ Confirmed: RAG service is not accessible")
        return True
    
    return True

def setup_environment_for_debug():
    """Set up environment variables for maximum debug output"""
    env = os.environ.copy()
    env.update({
        'PYTHONUNBUFFERED': '1',           # Disable output buffering
        'PYTHONASYNCIODEBUG': '1',         # AsyncIO debug
        'PYTHONVERBOSE': '1',              # Verbose Python output
        'PYTHONDEBUG': '1',                # Python debug mode
        'QT_LOGGING_RULES': '*=true',      # Enable all Qt logging
        'QT_DEBUG_PLUGINS': '1',           # Qt plugin debug
        'GOPIAI_DEBUG': 'true',            # GopiAI debug flag
        'GOPIAI_LOG_LEVEL': 'DEBUG',       # GopiAI log level
        'PYTHONIOENCODING': 'utf-8',       # Encoding
        'PYTHONUTF8': '1',                 # UTF-8 mode
    })
    return env

def patch_ui_for_debug_logging():
    """Create a patched version of the UI main file with DEBUG logging enabled"""
    
    ui_main_path = Path("GopiAI-UI/gopiai/ui/main.py")
    ui_main_debug_path = Path("GopiAI-UI/gopiai/ui/main_debug.py")
    
    if not ui_main_path.exists():
        print(f"❌ UI main file not found: {ui_main_path}")
        return None
    
    # Read original file
    with open(ui_main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add DEBUG logging setup at the beginning
    debug_setup = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG VERSION: GopiAI UI with extensive logging enabled
"""

import logging
import sys
import os

# FORCE DEBUG LOGGING SETUP
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s.%(msecs)03d] %(name)-20s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s',
    datefmt='%H:%M:%S'
)

# Set DEBUG level for all GopiAI modules
for name in sys.modules:
    if 'gopiai' in name or 'crewai' in name:
        logging.getLogger(name).setLevel(logging.DEBUG)

print("🔧 DEBUG LOGGING ENABLED FOR ALL MODULES")
print("="*60)

'''
    
    # Insert debug setup after the shebang but before imports
    lines = content.split('\n')
    new_lines = [lines[0]]  # Keep shebang
    new_lines.extend(debug_setup.split('\n'))
    new_lines.extend(lines[1:])  # Add rest of content
    
    # Write debug version
    debug_content = '\n'.join(new_lines)
    with open(ui_main_debug_path, 'w', encoding='utf-8') as f:
        f.write(debug_content)
    
    print(f"✅ Debug UI created: {ui_main_debug_path}")
    return ui_main_debug_path

def launch_ui_with_debug(debug_ui_path, log_file, logger):
    """Launch the UI with maximum debug output"""
    
    print("\n🚀 Launching GopiAI-UI with DEBUG logging...")
    print("="*60)
    
    env = setup_environment_for_debug()
    
    cmd = [
        sys.executable,
        '-u',              # Unbuffered output
        '-X', 'dev',       # Development mode
        '-X', 'utf8',      # UTF-8 mode
        str(debug_ui_path)
    ]
    
    print(f"📋 Command: {' '.join(cmd)}")
    print(f"📁 Log file: {log_file}")
    print("="*60)
    
    try:
        # Start UI process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )
        
        # Monitor output in real-time
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"UI LAUNCH LOG - {datetime.now()}\n")
            f.write(f"{'='*60}\n")
            
            if process.stdout:
                for line in process.stdout:
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    log_line = f"[{timestamp}] UI: {line.rstrip()}"
                    print(log_line)
                    f.write(log_line + '\n')
                    f.flush()
        
        return process.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️ UI stopped by user")
        if process:
            process.terminate()
        return 0
    except Exception as e:
        logger.error(f"❌ Error launching UI: {e}")
        return 1

def print_instructions():
    """Print instructions for reproducing the hang"""
    print("\n" + "="*60)
    print("📋 INSTRUCTIONS TO REPRODUCE HANG")
    print("="*60)
    print("1. Wait for the GopiAI-UI to fully load")
    print("2. Go to the Chat widget/panel")
    print("3. Send several test messages, such as:")
    print("   - 'Hello, how are you?'")
    print("   - 'What can you help me with?'")
    print("   - 'Tell me about Python programming'")
    print("4. Observe that messages should freeze in '⏳ Обрабатываю запрос...' state")
    print("5. Check the console and log file for timeout errors and stack traces")
    print("6. When done testing, close the UI application")
    print("="*60)
    print("💡 Expected behavior: Messages will hang due to RAG service unavailability")
    print("📝 All debug output is being captured to the log file")
    print("="*60)

def main():
    """Main function to reproduce and log the hang"""
    
    print("🔍 GopiAI Hang Reproduction Script")
    print("="*60)
    print("This script will:")
    print("1. Stop RAG service (port 5051)")
    print("2. Enable DEBUG logging")
    print("3. Launch GopiAI-UI")
    print("4. Guide you to reproduce the hang")
    print("5. Capture all debug logs")
    print("="*60)
    
    # Setup debug logging
    log_file, logger = setup_debug_logging()
    
    # Step 1: Stop RAG service
    if not stop_rag_service():
        print("⚠️ WARNING: RAG service may still be running. Continuing anyway...")
        logger.warning("RAG service stop verification failed")
    
    # Step 2: Create debug version of UI
    debug_ui_path = patch_ui_for_debug_logging()
    if not debug_ui_path:
        return 1
    
    # Step 3: Print instructions
    print_instructions()
    
    # Step 4: Wait for user confirmation
    input("\n📋 Press ENTER when ready to launch UI and start testing...")
    
    # Step 5: Launch UI with debug logging
    try:
        return_code = launch_ui_with_debug(debug_ui_path, log_file, logger)
        
        print(f"\n✅ UI session completed with return code: {return_code}")
        print(f"📁 Complete debug log saved to: {log_file}")
        
        # Clean up debug file
        try:
            debug_ui_path.unlink()
            print(f"🧹 Cleaned up debug file: {debug_ui_path}")
        except:
            pass
        
        return return_code
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
