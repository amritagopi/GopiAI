#!/bin/bash

# Enable error checking
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Server configuration
SERVER_IP="127.0.0.1"  # Change this to your server IP
CREWAI_PORT=5051

# Paths
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$BASE_DIR/GopiAI-CrewAI"
FRONTEND_DIR="$BASE_DIR/GopiAI-UI"

# Virtual environments
BACKEND_VENV="$BACKEND_DIR/backend_env"
FRONTEND_VENV="$FRONTEND_DIR/frontend_env"

# Function to setup and activate virtual environment
setup_environment() {
    local env_name=$1
    local env_path=$2
    local requirements_file=$3
    
    echo -e "\n${BLUE}[SETUP]${NC} Setting up $env_name environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$env_path" ]; then
        echo -e "  - Creating virtual environment at $env_path"
        python3 -m venv "$env_path"
    fi
    
    # Activate environment
    source "$env_path/bin/activate"
    echo -e "  - Activated $env_name environment"
    
    # Install requirements if file exists
    if [ -f "$requirements_file" ]; then
        echo -e "  - Installing requirements from $(basename $requirements_file)"
        pip install -r "$requirements_file"
    fi
    
    deactivate
}

# Create necessary directories
setup_directories() {
    echo -e "\n${BLUE}[SETUP]${NC} Creating required directories..."
    
    # Backend directories
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/memory/vectors"
    
    # Create empty chats.json if it doesn't exist
    if [ ! -f "$BACKEND_DIR/memory/chats.json" ]; then
        echo "{}" > "$BACKEND_DIR/memory/chats.json"
    fi
    
    echo -e "  - Backend directories created"
}

# Start backend server
start_backend() {
    echo -e "\n${GREEN}[BACKEND]${NC} Starting Backend Server..."
    
    # Activate backend environment
    if [ -f "$BACKEND_VENV/bin/activate" ]; then
        source "$BACKEND_VENV/bin/activate"
        echo -e "  - Using backend environment: $BACKEND_VENV"
    else
        echo -e "${YELLOW}[WARNING]${NC} Backend environment not found at $BACKEND_VENV"
        echo -e "  - Setting up backend environment..."
        setup_environment "Backend" "$BACKEND_VENV" "$BACKEND_DIR/requirements.txt"
        source "$BACKEND_VENV/bin/activate"
    fi
    
    # Navigate to backend directory
    cd "$BACKEND_DIR"
    
    # Set environment variables for backend
    export FLASK_APP="crewai_api_server.py"
    export FLASK_ENV="development"
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    
    # Start the backend server in background
    echo -e "  - Starting CrewAI API Server on $SERVER_IP:$CREWAI_PORT"
    nohup python -m flask run --host=$SERVER_IP --port=$CREWAI_PORT > "$BACKEND_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/gopiai_backend.pid
    
    echo -e "${GREEN}[OK]${NC} Backend server started (PID: $BACKEND_PID)"
    echo -e "  - Logs: $BACKEND_DIR/logs/backend.log"
    
    # Wait for server to start
    echo -e "  - Waiting for server to initialize..."
    sleep 5
    
    # Check if server is running
    if ! curl -s "http://$SERVER_IP:$CREWAI_PORT/health" > /dev/null; then
        echo -e "${RED}[ERROR]${NC} Failed to start backend server"
        echo -e "  - Check logs at: $BACKEND_DIR/logs/backend.log"
        exit 1
    fi
    
    deactivate
}

# Start frontend application
start_frontend() {
    echo -e "\n${GREEN}[FRONTEND]${NC} Starting Frontend Application..."
    
    # Activate frontend environment if it exists
    if [ -f "$FRONTEND_VENV/bin/activate" ]; then
        source "$FRONTEND_VENV/bin/activate"
        echo -e "  - Using frontend environment: $FRONTEND_VENV"
    else
        echo -e "${YELLOW}[WARNING]${NC} Frontend environment not found at $FRONTEND_VENV"
        echo -e "  - Setting up frontend environment..."
        setup_environment "Frontend" "$FRONTEND_VENV" "$FRONTEND_DIR/requirements.txt"
        source "$FRONTEND_VENV/bin/activate"
    fi
    
    # Navigate to frontend directory
    cd "$FRONTEND_DIR"
    
    # Set environment variables for frontend
    export MEMORY_ENABLED=1
    export CREWAI_API_URL="http://$SERVER_IP:$CREWAI_PORT"
    
    # Add backend to PYTHONPATH for any required imports
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    
    # Start the frontend application
    echo -e "  - Starting GopiAI-UI Application..."
    python -m gopiai.ui.main
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}[SHUTDOWN]${NC} Stopping all services..."
    
    # Stop backend server if running
    if [ -f "/tmp/gopiai_backend.pid" ]; then
        BACKEND_PID=$(cat /tmp/gopiai_backend.pid)
        echo -e "  - Stopping backend server (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
        rm -f /tmp/gopiai_backend.pid
    fi
    
    echo -e "${GREEN}[OK]${NC} All services have been stopped."
    exit 0
}

# Set up trap to catch Ctrl+C and other termination signals
trap cleanup INT TERM

# Main execution
main() {
    echo -e "\n${GREEN}================================================${NC}"
    echo -e "     ${YELLOW}GOPI_AI System - Starting Components${NC}"
    echo -e "${GREEN}================================================${NC}"
    
    # Setup directories
    setup_directories
    
    # Start backend server
    start_backend
    
    # Start frontend application
    start_frontend
}

# Run main function
main
