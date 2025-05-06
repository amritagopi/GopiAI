@echo off
echo Starting GopiAI using Python from virtual environment

:: Check for virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at venv\Scripts\python.exe
    pause
    exit /b 1
)

:: Activate virtual environment and run the application
call venv\Scripts\activate.bat

:: Run the application
python main.py %*

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat
