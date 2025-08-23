#!/bin/bash

# Скрипт для запуска сервера CrewAI после рефакторинга
# Исправляет проблемы с виртуальным окружением и зависимостями

echo "=== Запуск сервера CrewAI ==="

# Переходим в директорию CrewAI
cd "$(dirname "$0")/GopiAI-CrewAI" || exit 1

# Проверяем и создаем виртуальное окружение для Linux
if [ ! -d "crewai_env/bin" ]; then
    echo "Создание виртуального окружения для Linux..."
    rm -rf crewai_env
    python3 -m venv crewai_env
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source crewai_env/bin/activate

# Обновляем pip
echo "Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "Установка зависимостей..."
pip install -r ../requirements.txt
pip install crewai flask

# Проверяем, запущен ли уже сервер
if pgrep -f "crewai_api_server.py" > /dev/null; then
    echo "Сервер CrewAI уже запущен"
    curl -s http://localhost:5051/api/health | python -m json.tool
else
    echo "Запуск сервера CrewAI..."
    nohup python crewai_api_server.py > crewai_server.log 2>&1 &
    
    # Ждем запуска сервера
    echo "Ожидание запуска сервера..."
    for i in {1..30}; do
        if curl -s http://localhost:5051/api/health > /dev/null 2>&1; then
            echo "✅ Сервер CrewAI успешно запущен!"
            curl -s http://localhost:5051/api/health | python -m json.tool
            break
        fi
        sleep 1
        echo -n "."
    done
    
    if ! curl -s http://localhost:5051/api/health > /dev/null 2>&1; then
        echo "❌ Ошибка: сервер не запустился"
        echo "Логи сервера:"
        tail -20 crewai_server.log
        exit 1
    fi
fi

echo "=== Сервер CrewAI готов к работе ==="