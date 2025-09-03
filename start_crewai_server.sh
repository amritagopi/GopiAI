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

# Check system resources before starting
echo "Checking system resources..."
echo "Memory usage: $(free -h | grep '^Mem:' | awk '{print $3"/"$2" ("$3/$2*100"%)"}')"
echo "Swap usage: $(free -h | grep '^Swap:' | awk '{print $3"/"$2}')"

# Check if swap is available
echo "WARNING: No swap space detected! This may cause OOM kills during heavy processing."
echo "Consider adding swap space: sudo fallocate -l 8G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile"

# Set memory optimization environment variables
export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=4

# Start the server with resource monitoring
echo "Starting CrewAI API server with enhanced monitoring..."
cd GopiAI-CrewAI
source ../.venv/bin/activate

# Install psutil if not available
python -c "import psutil" 2>/dev/null || pip install psutil

# Start server with restart on failure
MAX_RESTARTS=3
RESTART_COUNT=0

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    echo "Starting server (attempt $((RESTART_COUNT + 1))/$MAX_RESTARTS)..."
    python -u crewai_api_server.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 137 ]; then
        echo "Server killed with SIGKILL (exit code 137) - likely OOM. Restarting..."
        RESTART_COUNT=$((RESTART_COUNT + 1))
        sleep 5
    else
        echo "Server exited with code $EXIT_CODE"
        break
    fi
done

if [ $RESTART_COUNT -eq $MAX_RESTARTS ]; then
    echo "Server failed to start after $MAX_RESTARTS attempts. Check logs for details."
    exit 1
fi
