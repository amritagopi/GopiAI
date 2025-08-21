#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo -e "\n=== Настройка окружения GopiAI для Linux ===\n"

# Проверяем наличие python3 и venv
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен. Пожалуйста, установите Python 3.8 или выше."
    exit 1
fi

# Создаем необходимые директории
echo "Создаем необходимые директории..."
mkdir -p scripts docs config tests/unit tests/integration tests/e2e

# Создаем единое виртуальное окружение
VENV_NAME=".venv"
echo "Создаем виртуальное окружение: $VENV_NAME"
python3 -m venv "$VENV_NAME"

# Активируем окружение и обновляем pip
source "$VENV_NAME/bin/activate"
echo "Обновляем pip..."
pip install --upgrade pip

# Устанавливаем все зависимости из корневого requirements.txt
echo "Устанавливаем зависимости из requirements.txt..."
pip install -r "requirements.txt"

# Устанавливаем права на выполнение скриптов
echo "Устанавливаем права на выполнение скриптов..."
chmod +x scripts/*.py

deactivate

echo -e "\n=== Настройка завершена успешно! ===\n"
echo "Для активации окружения выполните команду:"
echo "source $VENV_NAME/bin/activate"
echo "Для запуска приложения выполните команду:"
echo "source start_linux.sh"
