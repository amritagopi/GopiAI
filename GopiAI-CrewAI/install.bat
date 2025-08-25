@echo off
REM 🚀 GopiAI-CrewAI Installation Script for Windows
REM Автоматическая установка и настройка интеграции

echo 🎯 === GOPIAI-CREWAI INSTALLATION ===
echo ⏰ Starting installation: %date% %time%

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8+ и попробуйте снова.
    echo 💡 Скачайте с https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Переход в папку проекта
cd /d "%~dp0"
echo 📁 Working directory: %cd%

REM Создание виртуального окружения
echo 🔧 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Активация виртуального окружения
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Обновление pip
echo 📦 Updating pip...
python -m pip install --upgrade pip

REM Установка зависимостей
echo 📦 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Создание необходимых папок
echo 📁 Creating directories...
if not exist "memory" mkdir memory
if not exist "communication" mkdir communication  
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
echo ✅ Directories created

REM Копирование примера .env файла
echo 🔑 Setting up environment file...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ .env file created from example
        echo ⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваши API ключи!
    ) else (
        echo ❌ .env.example not found
    )
) else (
    echo ✅ .env file already exists
)

REM Проверка установки
echo 🧪 Testing installation...
python -c "import sys; import crewai, dotenv, requests; print('✅ Core packages imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Package import failed
    pause
    exit /b 1
)

REM Проверка структуры инструментов
echo 🔧 Checking tools structure...
if exist "gopiai_tools" (
    dir /b gopiai_tools\*.py 2>nul | find /c ".py" >temp_count.txt
    set /p TOOL_COUNT=<temp_count.txt
    del temp_count.txt
    echo ✅ Found %TOOL_COUNT% GopiAI tools
) else (
    echo ❌ GopiAI tools directory not found
    pause
    exit /b 1
)

REM Финальные инструкции
echo.
echo 🎉 === INSTALLATION COMPLETE ===
echo.
echo 📋 Next steps:
echo 1. Edit .env file and add your API keys:
echo    notepad .env
echo.
echo 2. Get free API keys from:
echo    🔸 Groq: https://console.groq.com
echo    🔸 Google Gemini: https://aistudio.google.com
echo    🔸 Cerebras: https://cloud.cerebras.ai
echo.
echo 3. Run the integration:
echo    python main.py
echo.
echo 4. Choose demo mode:
echo    1 - Simple demo (1 agent)
echo    2 - Advanced demo (3 agents)  
echo    3 - Tests only
echo.
echo 📖 Read README.md for detailed documentation
echo.
echo 🚀 Happy coding with GopiAI + CrewAI!
echo.
pause