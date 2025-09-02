# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Во время работы используй все доступные тебе инструменты, включая MCP.

## Project Overview

GopiAI is a comprehensive AI platform with modular architecture that includes agent coordination, modern UI, and advanced language model capabilities. The system consists of three main components:

- **GopiAI-CrewAI**: CrewAI server backend with agent orchestration
- **GopiAI-UI**: Qt-based user interface 
- **GopiAI-Assets**: Shared assets and utilities

## Architecture

The project uses dual virtual environment architecture:
- **Primary environment (`.venv`)**: Main environment for UI and non-CrewAI components
- **CrewAI environment**: Separate environment in `GopiAI-CrewAI/venv/` for CrewAI server

Communication between UI and CrewAI server happens via REST API (port 5052), ensuring loose coupling.

## Common Commands

### Project Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r GopiAI-UI/requirements_ui.txt
```

### Running the Application
```bash
# Start both CrewAI server and UI
./start_linux.sh

# Start only CrewAI server
./start_crewai_server.sh

# Run UI standalone (assumes CrewAI server is running)
.venv/bin/python -m gopiai.ui.main
```

### Development Commands
```bash
# Run tests for specific component
cd GopiAI-Assets && pytest tests/
cd GopiAI-CrewAI && python test_api_endpoints.py

# Environment setup
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/GopiAI-UI"
```

## Key Configuration

### Environment Variables
The project uses `.env` file for API keys:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` 
- `GOOGLE_API_KEY`
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- Various other API keys for tools (TAVILY, FIRECRAWL, BRAVE, etc.)

### Port Configuration
- CrewAI API Server: Port 5052
- UI Application: Configured via command line args

## Code Structure

### GopiAI-CrewAI
- `crewai_api_server.py`: Main Flask API server
- `crews/`: Agent crew definitions
- `tools/`: CrewAI toolkit and custom tools
- `config/`: Configuration management

### GopiAI-UI  
- `gopiai/ui/main.py`: Main UI entry point
- `gopiai/ui/components/`: UI components
- Uses PySide6 for Qt-based interface

### Testing
- Each component has its own `tests/` directory
- pytest configuration in `GopiAI-Assets/pytest.ini`
- Test markers: `unit`, `slow`, `xfail_known_issue`

## Development Notes

### Dependencies Management
- Main requirements in root `requirements.txt`
- UI-specific requirements in `GopiAI-UI/requirements_ui.txt`  
- CrewAI server requirements in `GopiAI-CrewAI/requirements_server.txt`

### Known Issues
The codebase is actively being refactored. Check `.codex/plan.md` for current refactoring status and known issues.

### Logging
- CrewAI server logs to `$HOME/.gopiai/logs/crewai_api_server_debug.log`
- UI logs to various locations in `logs/` directories
- Debug logs available in `ui_debug.log`