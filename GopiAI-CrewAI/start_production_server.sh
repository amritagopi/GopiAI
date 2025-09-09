#!/bin/bash
"""
Production startup script for CrewAI API server with Gunicorn
"""

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting CrewAI API server in production mode..."

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment  
source venv/bin/activate

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "❌ Gunicorn not installed. Installing..."
    pip install gunicorn
fi

# Create log directory if it doesn't exist
mkdir -p /home/amritagopi/.gopiai/logs

# Check environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set!"
fi

# Export PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"

echo "📊 Starting with Gunicorn production server..."

# Stop any existing instances
pkill -f "gunicorn.*crewai_api_server" || true
sleep 2

# Start Gunicorn server
exec ./venv/bin/gunicorn \
    --config gunicorn_config.py \
    --chdir "$SCRIPT_DIR" \
    crewai_api_server:app