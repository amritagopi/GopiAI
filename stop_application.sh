#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to stop a component
stop_component() {
    local name=$1
    local pattern=$2
    
    echo -e "${GREEN}Stopping ${name}...${NC}"
    pkill -f "${pattern}" || true
    
    # Verify process has stopped
    if pgrep -f "${pattern}" > /dev/null; then
        echo -e "${RED}Warning: Could not stop ${name}${NC}"
    else
        echo -e "${GREEN}${name} stopped successfully${NC}"
    fi
}

# Main script
echo -e "${GREEN}Stopping GopiAI Application...${NC}"

# Stop UI
stop_component "UI" "python -m gopiai.ui.main"

# Stop CrewAI API server
stop_component "CrewAI API" "gunicorn.*crewai_api_server"

echo -e "${GREEN}\nGopiAI has been stopped.${NC}"
