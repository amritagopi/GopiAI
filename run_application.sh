#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Function to start a component
start_component() {
    local name=$1
    local cmd=$2
    local log_file=$3
    
    if is_running "$cmd"; then
        echo -e "${GREEN}${name} is already running${NC}"
    else
        echo -e "${GREEN}Starting ${name}...${NC}"
        nohup bash -c "source ${name}_env/bin/activate && ${cmd} > ${log_file} 2>&1 &" > /dev/null 2>&1
        sleep 2
        if is_running "$cmd"; then
            echo -e "${GREEN}${name} started successfully!${NC}"
        else
            echo -e "${RED}Failed to start ${name}. Check ${log_file} for details.${NC}"
            return 1
        fi
    fi
}

# Main script
echo -e "${GREEN}Starting GopiAI Application...${NC}"

# Start CrewAI API server
start_component "crewai" "python -m gunicorn -w 4 -b 0.0.0.0:5051 crewai_api_server:app" "crewai_server.log"

# Start UI
start_component "ui" "python -m gopiai.ui.main" "ui.log"

echo -e "${GREEN}\nGopiAI is now running!${NC}"
echo -e "- CrewAI API: http://localhost:5051"
echo -e "- UI: Check your desktop environment for the GopiAI window"
echo -e "\nTo stop the application, run: pkill -f 'gunicorn|python -m gopiai.ui.main'"
