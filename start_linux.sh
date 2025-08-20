#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Пути к виртуальным окружениям
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREWAI_ENV="$BASE_DIR/crewai_env"
UI_ENV="$BASE_DIR/gopiai_env"
TXTAI_ENV="$BASE_DIR/txtai_env"

# Функция для запуска сервиса в новом терминале
start_service() {
    local name=$1
    local env_path=$2
    local command=$3
    
    echo "Запуск $name..."
    gnome-terminal --tab --title="$name" -- bash -c "
        cd '$BASE_DIR' && \
        source '$env_path/bin/activate' && \
        echo '=== $name ===' && \
        echo 'Окружение: $env_path' && \
        echo 'Директория: ' && pwd && \
        echo 'Команда: $command' && \
        echo '========================' && \
        $command
    "
}

# Создаем необходимые директории
echo "Создаем необходимые директории..."
mkdir -p "$BASE_DIR/GopiAI-CrewAI/memory/vectors"
touch "$BASE_DIR/GopiAI-CrewAI/memory/chats.json"

# Функция для запуска в новом терминале
run_in_terminal() {
    local title="$1"
    local cmd="$2"
    gnome-terminal --title="$title" -- bash -c "$cmd; exec bash"
}

# Запускаем сервисы в отдельных терминалах
run_in_terminal "CrewAI API Server" "
    echo 'Активация окружения CrewAI...'
    source $CREWAI_ENV/bin/activate
    cd GopiAI-CrewAI
    echo 'Запуск CrewAI API Server...'
    python crewai_api_server.py --port 5051 --debug
"

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
