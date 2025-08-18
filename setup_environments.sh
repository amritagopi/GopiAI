#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to create and activate virtual environment
setup_venv() {
    local name=$1
    local req_file=$2
    
    echo -e "${GREEN}Setting up ${name} environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "${name}_env" ]; then
        echo "Creating ${name} virtual environment..."
        python -m venv ${name}_env
    fi
    
    # Activate environment
    echo -e "${GREEN}Activating ${name} environment...${NC}"
    source ${name}_env/bin/activate
    
    # Upgrade pip and install requirements
    echo -e "${GREEN}Installing requirements for ${name}...${NC}"
    pip install --upgrade pip
    
    if [ -f "$req_file" ]; then
        pip install -r "$req_file"
    else
        echo -e "${GREEN}Warning: Requirements file ${req_file} not found${NC}"
    fi
    
    # Deactivate environment
    deactivate
    echo -e "${GREEN}${name} environment setup complete!${NC}\n"
}

# Main script
echo -e "${GREEN}Starting environment setup...${NC}"

# Setup CrewAI environment
setup_venv "crewai" "GopiAI-CrewAI/requirements.txt"

# Setup UI environment
setup_venv "ui" "GopiAI-UI/requirements.txt"

echo -e "${GREEN}All environments have been set up successfully!${NC}"
echo -e "${GREEN}To activate the CrewAI environment, run: source crewai_env/bin/activate${NC}"
echo -e "${GREEN}To activate the UI environment, run: source ui_env/bin/activate${NC}"
