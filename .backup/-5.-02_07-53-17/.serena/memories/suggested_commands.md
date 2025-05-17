# Suggested Commands

These commands can be used to develop, test, and run the GopiAI application.

## Running the Application
- `python main.py` - Start the main application
- `python run_pocketflow.py` - Run the PocketFlow component
- `python run_mcp.py` - Run the MCP (Modular Coding Platform) component
- `python run_web_interface.py` - Run the web interface
- `python run_fixed_pocketflow.py` - Run the fixed version of PocketFlow

## Development
- `pip install -r requirements.txt` - Install all required dependencies
- `python compile_resources.py` - Compile Qt resources (icons)
- `python download_fonts.py` - Download fonts for the application

## Testing
- `pytest tests/` - Run all tests
- `pytest tests/sandbox/` - Run sandbox tests

## Virtual Environment (Windows)
- `python -m venv venv` - Create a virtual environment
- `venv\Scripts\activate` - Activate the virtual environment
- `deactivate` - Deactivate the virtual environment

## Git Commands
- `git status` - Check the status of the repository
- `git add .` - Add all changes to staging
- `git commit -m "message"` - Commit staged changes
- `git pull` - Pull changes from the remote repository
- `git push` - Push committed changes to the remote repository

## File Management (Windows)
- `dir` - List files in the current directory
- `cd directory_name` - Change to the specified directory
- `cd ..` - Move up one directory
- `mkdir directory_name` - Create a new directory
- `del filename` - Delete a file
- `type filename` - Display file contents (similar to cat on Unix)
- `copy source destination` - Copy files
- `move source destination` - Move files
- `ren oldname newname` - Rename files

## Searching (Windows)
- `findstr /s /i "search_term" *.py` - Search for text in Python files (case-insensitive)
- `dir /s /b *.py` - Find all Python files recursively

## File Operations
- `python -m json.tool filename.json` - Format a JSON file