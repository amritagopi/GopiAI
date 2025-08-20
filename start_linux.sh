#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Функция для проверки доступности порта
check_port() {
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i ":$1" >/dev/null 2>&1; then
            echo "Порт $1 уже занят. Освободите порт и попробуйте снова."
            exit 1
        fi
    fi
}

# Проверяем порты
check_port 5051  # Порт для CrewAI API
check_port 8000  # Порт для GopiAI-UI

# Проверяем наличие виртуального окружения
if [ ! -d "gopiai_env" ]; then
    echo "Ошибка: Виртуальное окружение не найдено. Сначала выполните setup_linux.sh"
    exit 1
fi

# Активируем виртуальное окружение
source gopiai_env/bin/activate

echo "Ожидаем запуск CrewAI сервера..."
sleep 5

run_in_terminal "TXTAI Service" "
    echo 'Активация окружения TXTAI...'
    source $TXTAI_ENV/bin/activate
    echo 'TXTAI service is ready'
    sleep infinity
"

# Устанавливаем зависимости для UI перед запуском
run_in_terminal "Установка зависимостей UI" "
    echo 'Активация окружения UI...'
    source $UI_ENV/bin/activate
    cd GopiAI-UI
    echo 'Установка зависимостей из requirements.txt...'
    pip install -r requirements.txt
    echo 'Зависимости установлены!'
    echo 'Нажмите Enter для продолжения...'
    read
"

# Даем время на установку зависимостей
echo "Ожидаем завершение установки зависимостей..."
sleep 5

# Запускаем UI
run_in_terminal "GopiAI UI" "
    echo 'Активация окружения UI...'
    source $UI_ENV/bin/activate
    cd GopiAI-UI
    echo 'Текущий путь: ' && pwd
    echo 'Python путь: ' && which python
    echo 'Запуск GopiAI UI...'
    python -m gopiai.ui.main 2> ui_errors.log || {
        echo 'Ошибка при запуске UI. Логи сохранены в ui_errors.log'
        cat ui_errors.log
        echo 'Нажмите Enter для выхода...'
        read
    }
"

echo -e "\n=== Все сервисы запускаются... ===\n"
echo "CrewAI API будет доступен по адресу: http://localhost:5051"
echo "GopiAI-UI запускается в отдельном окне терминала"
