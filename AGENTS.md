AGENTS.md
Overview
Jules, этот файл содержит инструкции для настройки окружений, установки зависимостей, запуска тестов и валидации приложения GopiAI в твоей изолированной VM. Проект требует три окружения (crewai_env, gopiai_env, txtai_env), чтобы избежать конфликтов зависимостей. Из-за ограничений sandbox на команду python -m venv, используй встроенный механизм изоляции зависимостей с pip --user. Следуй шагам ниже последовательно.
Environment Setup
Из-за блокировки python -m venv в run_in_bash_session, устанавливай зависимости в изолированные пользовательские контексты. Используй Python 3.8+ (доступен в твоей VM). Не объединяй файлы зависимостей — они должны оставаться раздельными.

Подготовка:

Создай необходимые директории: mkdir -p scripts docs config tests/unit tests/integration tests/e2e.
Убедись, что файлы зависимостей существуют:
GopiAI-CrewAI/requirements.txt (для CrewAI).
GopiAI-UI/requirements.txt (для UI и gopiai_env).
requirements.txt (для dev-зависимостей).


Установи права на скрипты: chmod +x scripts/*.py.


Установка зависимостей:

Для crewai_env:pip install --user -r GopiAI-CrewAI/requirements.txt


Для gopiai_env:pip install --user -r GopiAI-UI/requirements.txt
pip install --user -r requirements.txt
python -m spacy download ru_core_news_sm
python -m spacy download en_core_web_sm


Для txtai_env:pip install --user txtai


Используй флаг --user для установки в изолированный контекст.
Если возникают ошибки (например, конфликты зависимостей), добавь флаг --no-cache-dir и запиши ошибки в отчёт.
Проверь установленные пакеты: pip list --user.


Проверка:

Убедись, что зависимости установлены для каждого окружения (проверь pip list --user).
Подтверди наличие директорий и файлов: ls scripts docs config tests.



Running Tests
Для запуска тестов используй контекст gopiai_env (зависимости из GopiAI-UI/requirements.txt и requirements.txt). Тесты запускаются через scripts/run_tests.py.

Подготовка:

Убедись, что pytest установлен: pip install --user pytest.
Проверь порты (5051 для CrewAI API, 8000 для UI): check_port() {
    if lsof -i ":$1" >/dev/null 2>&1; then
        echo "Порт $1 занят." && exit 1
    fi
}
check_port 5051
check_port 8000




Запуск тестов:

Все тесты: ./scripts/run_tests.py
По категориям: ./scripts/run_tests.py --category unit (или integration, e2e).
Проверь пути в тестах (tests/unit, tests/integration, tests/e2e). Если импорты или пути сломаны после рефакторинга, исправь их и запиши изменения в отчёт.


Обработка ошибок:

Если тесты не запускаются, проверь логи и укажи ошибки (например, stderr от pytest).
Сохраняй логи в файл (например, pytest tests/ > test_output.log 2>&1).



Running the Application (for Validation)
Для проверки изменений запусти приложение в CLI-режиме (без GUI, так как VM не поддерживает графический интерфейс). Следуй этим шагам:

Подготовка:

Экспорт кодировки: export LANG=en_US.UTF-8; export LC_ALL=en_US.UTF-8.
Убедись, что зависимости для gopiai_env установлены (см. Environment Setup).


Запуск сервисов:

TXTAI (txtai_env контекст):pip install --user txtai
echo "TXTAI service is ready"

(Если есть конкретная команда для запуска txtai, уточни её в коде и добавь.)
UI (gopiai_env контекст):pip install --user -r GopiAI-UI/requirements.txt
cd GopiAI-UI
python -m gopiai.ui.main 2> ui_errors.log


CrewAI API (crewai_env контекст):pip install --user -r GopiAI-CrewAI/requirements.txt
cd GopiAI-CrewAI
# Уточни команду запуска CrewAI API, например: crewai serve --port 5051


Если запуск UI или CrewAI не требуется для тестов, пропусти этот шаг и фокусируйся на тестах.


Логирование:

Сохраняй ошибки в ui_errors.log или аналогичный файл.
Если сервис не запускается, включи логи в отчёт.



Alternative Environment Setup (Docker)
Если pip --user не работает из-за ограничений sandbox, используй Docker. В репозитории есть три Dockerfile для каждого окружения. Построй и используй их:

Создание образов:

Для crewai_env: docker build -f Dockerfile.crewai -t crewai_env .
Для gopiai_env: docker build -f Dockerfile.gopiai -t gopiai_env .
Для txtai_env: docker build -f Dockerfile.txtai -t txtai_env .


Запуск тестов:

docker run --rm gopiai_env ./scripts/run_tests.py
Для конкретных тестов: docker run --rm gopiai_env ./scripts/run_tests.py --category unit


Запуск приложения:

UI: docker run --rm gopiai_env bash -c "cd GopiAI-UI && python -m gopiai.ui.main 2> ui_errors.log"



Other Instructions

Проверка изменений: Перед коммитом проверяй изменения: git diff. Убедись, что пути и импорты в тестах/скриптах валидны после рефакторинга.
Ошибки: Если pip или тесты не работают, попробуй pip install --no-cache-dir --user. Включи полные логи (stdout/stderr) в отчёт.
Автоматизация: Если хочешь, создай временный скрипт в VM:echo "pip install --user -r GopiAI-CrewAI/requirements.txt" > temp_setup.sh
bash temp_setup.sh


Финальная проверка: После настройки и запуска тестов подтверди, что ничего не сломано. Коммить только рабочие изменения.
Запрет на внешние сервисы: Не используй PythonAnywhere или другие облачные платформы — всё должно работать в твоей VM.
