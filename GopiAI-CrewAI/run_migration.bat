@echo off
title GopiAI Model Switching System - Migration

echo ==================================================
echo GopiAI Model Switching System - Migration Guide
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

echo Running migration guide...
python migration_guide.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉 Migration completed successfully!
    echo.
    echo You can now start the model switching system:
    echo   python start_model_switching_system.py
    echo   or
    echo   start_model_switching_system.bat
    echo.
    echo Press any key to close this window...
    pause >nul
) else (
    echo.
    echo ⚠️  Migration requires attention.
    echo Please review the output above and take necessary actions.
    echo.
    echo Press any key to close this window...
    pause >nul
    exit /b 1
)
