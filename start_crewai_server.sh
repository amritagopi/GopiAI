#!/bin/bash

# Set up environment variables
export FLASK_APP=crewai_api_server.py
export FLASK_ENV=development
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create necessary directories
mkdir -p ~/.gopiai/logs

# Start the server
echo "Starting CrewAI API server..."
cd GopiAI-CrewAI
source ../venv/bin/activate
python -u crewai_api_server.py
