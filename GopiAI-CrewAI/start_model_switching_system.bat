@echo off
title GopiAI Model Switching System

echo ==================================================
echo GopiAI Model Switching System Startup
echo ==================================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo Starting model switching system...
python start_model_switching_system.py

if %errorlevel% equ 0 (
    echo.
    echo 🎯 System started successfully!
    echo.
    echo Press any key to close this window...
    pause >nul
) else (
    echo.
    echo ❌ Failed to start system
    echo.
    echo Press any key to close this window...
    pause >nul
    exit /b 1
)
