#!/bin/bash
# 🚀 GopiAI-CrewAI Installation Script
# Автоматическая установка и настройка интеграции

echo "🎯 === GOPIAI-CREWAI INSTALLATION ==="
echo "⏰ Starting installation: $(date)"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Проверка минимальной версии Python
if python3 -c 'import sys; exit(1) if sys.version_info < (3, 8) else exit(0)'; then
    echo "✅ Python version $PYTHON_VERSION is compatible."
else
    echo "❌ Требуется Python 3.8+. Текущая версия: $PYTHON_VERSION"
    exit 1
fi

# Переход в папку проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Создание виртуального окружения
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Активация виртуального окружения
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Обновление pip
echo "📦 Updating pip..."
pip install --upgrade pip

# Установка зависимостей
echo "📦 Installing dependencies..."
if [ -f "requirements_server.txt" ]; then
    pip install -r requirements_server.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements_server.txt not found"
    exit 1
fi

# Создание необходимых папок
echo "📁 Creating directories..."
mkdir -p memory
mkdir -p communication
mkdir -p cache
mkdir -p logs
echo "✅ Directories created"

# Копирование примера .env файла
echo "🔑 Setting up environment file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from example"
        echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваши API ключи!"
    else
        echo "❌ .env.example not found"
    fi
else
    echo "✅ .env file already exists"
fi

# Проверка установки
echo "🧪 Testing installation..."
python3 -c "
import sys
try:
    import crewai
    import dotenv
    import requests
    print('✅ Core packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Проверка структуры инструментов
echo "🔧 Checking tools structure..."
if [ -d "tools/gopiai_integration" ]; then
    TOOL_COUNT=$(find tools/gopiai_integration -name "*.py" | wc -l)
    echo "✅ Found $TOOL_COUNT GopiAI tools"
else
    echo "❌ GopiAI tools directory not found"
    exit 1
fi

# Финальные инструкции
echo ""
echo "🎉 === INSTALLATION COMPLETE ==="
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Get free API keys from:"
echo "   🔸 Groq: https://console.groq.com"
echo "   🔸 Google Gemini: https://aistudio.google.com"
echo "   🔸 Cerebras: https://cloud.cerebras.ai"
echo ""
echo "3. Run the integration:"
echo "   python3 main.py"
echo ""
echo "4. Choose demo mode:"
echo "   1 - Simple demo (1 agent)"
echo "   2 - Advanced demo (3 agents)"
echo "   3 - Tests only"
echo ""
echo "📖 Read README.md for detailed documentation"
echo ""
echo "🚀 Happy coding with GopiAI + CrewAI!"