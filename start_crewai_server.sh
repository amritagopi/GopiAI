#!/bin/bash

# Check if port is already in use and kill existing processes
echo "Checking for existing CrewAI processes..."
if pgrep -f "crewai_api_server.py" > /dev/null; then
    echo "Killing existing CrewAI server processes..."
    pkill -f "crewai_api_server.py"
    sleep 2
fi

# Check if port 5052 is still in use
if netstat -tln 2>/dev/null | grep -q ":5052 "; then
    echo "Port 5052 is still in use, attempting to kill process..."
    fuser -k 5052/tcp 2>/dev/null || true
    sleep 2
fi

# Set up environment variables
export FLASK_APP=crewai_api_server.py
export FLASK_ENV=development
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create necessary directories
mkdir -p ~/.gopiai/logs

# Start the server
echo "Starting CrewAI API server..."
cd GopiAI-CrewAI
source ../.venv/bin/activate
python -u crewai_api_server.py
