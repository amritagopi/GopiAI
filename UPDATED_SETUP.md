# GopiAI - Updated Setup Guide

## Overview
This document provides instructions for setting up GopiAI with separate virtual environments for the UI and CrewAI components to prevent dependency conflicts.

## Prerequisites
- Python 3.12 or later
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository (if not already done)
```bash
git clone <repository-url>
cd GopiAI
```

### 2. Make Setup Scripts Executable
```bash
chmod +x setup_environments.sh run_application.sh stop_application.sh
```

### 3. Set Up Virtual Environments
Run the setup script to create and configure the virtual environments:
```bash
./setup_environments.sh
```

This will create two virtual environments:
- `crewai_env/` - For the CrewAI backend
- `ui_env/` - For the GopiAI UI

### 4. Start the Application
```bash
./run_application.sh
```

This will start:
- CrewAI API server on http://localhost:5051
- GopiAI UI (check your desktop environment for the application window)

### 5. Stop the Application
```bash
./stop_application.sh
```

## Troubleshooting

### Dependency Issues
If you encounter dependency conflicts:
1. Delete the virtual environments:
   ```bash
   rm -rf crewai_env/ ui_env/
   ```
2. Run the setup script again:
   ```bash
   ./setup_environments.sh
   ```

### Log Files
- CrewAI server logs: `crewai_server.log`
- UI logs: `ui.log`

## Virtual Environment Management

### Activate CrewAI Environment
```bash
source crewai_env/bin/activate
```

### Activate UI Environment
```bash
source ui_env/bin/activate
```

### Deactivate Current Environment
```bash
deactivate
```

## Updating Dependencies
To update dependencies:
1. Update the appropriate `requirements.txt` file
2. Delete and recreate the virtual environment
3. Rerun the setup script
