#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

VENV_DIR=".venv"

echo -e "\n=== Запуск GopiAI для Linux ===\n"

# Проверяем наличие виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Ошибка: Виртуальное окружение '$VENV_DIR' не найдено."
    echo "Пожалуйста, сначала выполните setup_linux.sh"
    exit 1
fi

# Убиваем процессы, использующие порт 5051
echo "Останавливаем предыдущий экземпляр сервера CrewAI (если запущен)..."
pkill -f "python3 GopiAI-CrewAI/crewai_api_server.py" || true
echo "Предыдущий экземпляр остановлен (или не был запущен)."

# Активируем виртуальное окружение
echo "Активация окружения: $VENV_DIR"
source "$VENV_DIR/bin/activate"

# Добавляем GopiAI-CrewAI в PYTHONPATH для корректного импорта
export PYTHONPATH="${PYTHONPATH}:$(pwd)/GopiAI-CrewAI"

# Запускаем основной UI приложения
echo "Запуск GopiAI UI..."
python -m gopiai.ui.main 2> ui_errors.log || {
    echo 'Ошибка при запуске UI. Логи сохранены в ui_errors.log'
    cat ui_errors.log
    echo 'Нажмите Enter для выхода...'
    read
}

echo -e "\n=== Приложение GopiAI завершило работу ===\n"