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

# Создаем виртуальные окружения
for env_name in "crewai_env" "gopiai_env" "txtai_env"; do
    echo "Создаем виртуальное окружение: $env_name"
    python3 -m venv "$env_name"
    
    # Активируем окружение и обновляем pip
    source "$env_name/bin/activate"
    pip install --upgrade pip
    
    # Устанавливаем зависимости в зависимости от типа окружения
    if [ "$env_name" = "crewai_env" ]; then
        echo "Устанавливаем зависимости для CrewAI..."
        pip install -r "GopiAI-CrewAI/requirements.txt"
    elif [ "$env_name" = "txtai_env" ]; then
        echo "Устанавливаем зависимости для txtai..."
        pip install txtai
    else
        echo "Устанавливаем зависимости для GopiAI-UI..."
        pip install -r "GopiAI-UI/requirements.txt"
    fi
    
    deactivate
done

echo -e "\n=== Настройка завершена успешно! ===\n"
echo "Для запуска приложения выполните команду:"
echo "source start_linux.sh"
