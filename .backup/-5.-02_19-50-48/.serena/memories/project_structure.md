# Project Structure

The GopiAI project has the following structure:

## Main Directories
- `app/`: Contains the main application code
  - `agent/`: Agent implementations (Manus, ReactAgent, PlanningAgent, etc.)
  - `flow/`: Flow management and visualization
  - `marketing/`: Marketing-related functionality
  - `mcp/`: Modular Coding Platform integration
  - `pocketflow/`: PocketFlow framework implementation
  - `prompt/`: Prompt templates and management
  - `sandbox/`: Sandbox environment
  - `tool/`: Tool implementations for agents
  - `ui/`: User interface components
    - `i18n/`: Internationalization
    - `themes/`: UI themes (light/dark)

- `assets/`: Application assets
  - `fonts/`: UI fonts (Inter, etc.)
  - `icons/`: SVG icons for the UI

- `config/`: Configuration files

- `docs/`: Documentation
  - `design/`: Design documents

- `examples/`: Example code and use cases
  - `benchmarks/`: Benchmark examples
  - `pocketflow_marketing/`: PocketFlow marketing examples
  - `use_case/`: Use case examples

- `GopiAI_Flow/`: Flow framework components
  - `cookbook/`: Recipe examples
  - `docs/`: Flow framework documentation
  - `pocketflow/`: PocketFlow core code
  - `pocketflow_framework/`: Framework implementation
  - `tests/`: Framework tests

- `tests/`: Application tests

## Key Files
- `main.py`: Application entry point
- `requirements.txt`: Package dependencies
- `setup.py`: Package setup configuration
- `run_pocketflow.py`: Script to run PocketFlow
- `run_mcp.py`: Script to run MCP
- `run_web_interface.py`: Script to run the web interface

## UI Components
The UI is built with PySide6 (Qt for Python) and includes:
- `main_window.py`: The main application window
- `chat_widget.py`: Chat interface widget
- `code_editor.py`: Code editing widget
- `terminal_widget.py`: Terminal emulation widget
- `flow_visualizer.py`: Flow visualization component
- `emoji_dialog.py`: Dialog for emoji selection
- `icon_manager.py`: Manager for application icons

## Agent System
The agent system is based on:
- `app/agent/manus.py`: Base agent implementation
- `app/agent/react.py`: Reactive agent implementation
- `app/agent/planning.py`: Planning agent implementation
- `app/agent/base.py`: Base agent abstract class
- `app/agent/toolcall.py`: Tool calling functionality

## Internationalization
The app supports multiple languages through:
- `app/ui/i18n/translator.py`: Translation management
- `app/ui/i18n/en.json`: English translations
- `app/ui/i18n/ru.json`: Russian translations