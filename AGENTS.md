# AGENTS.md

## Environment Setup
Jules, для работы с проектом GopiAI требуется три виртуальных окружения, чтобы избежать конфликтов зависимостей: crewai_env, gopiai_env и txtai_env. Эти окружения создаются и настраиваются на основе скрипта setup_linux.sh. Ты должен воспроизвести этот процесс в своей VM шаг за шагом. Используй Python 3.8+ (доступен в твоей среде). Не объединяй зависимости — оставь их раздельными.

Вот инструкции для автоматизации setup (ты можешь выполнить это как bash-скрипт или последовательно в терминале VM):

1. **Подготовка**:
   - Убедись, что в корне проекта есть необходимые директории: mkdir -p scripts docs config tests/unit tests/integration tests/e2e.
   - Убедись, что есть файлы зависимостей: GopiAI-CrewAI/requirements.txt, GopiAI-UI/requirements.txt и requirements.txt (для dev).

2. **Создание и настройка окружений**:
   - Для каждого окружения: создай venv, активируй, обнови pip, установи зависимости, деактивируй.
   - Команды (выполни последовательно):

     ```
     # Создание crewai_env
     python -m venv crewai_env
     source crewai_env/bin/activate
     pip install --upgrade pip
     pip install -r GopiAI-CrewAI/requirements.txt
     deactivate

     # Создание gopiai_env
     python -m venv gopiai_env
     source gopiai_env/bin/activate
     pip install --upgrade pip
     pip install -r GopiAI-UI/requirements.txt  # Это для UI, но в скрипте оно используется для gopiai_env
     python -m spacy download ru_core_news_sm
     python -m spacy download en_core_web_sm
     pip install -r requirements.txt  # Dev зависимости
     deactivate

     # Создание txtai_env
     python -m venv txtai_env
     source txtai_env/bin/activate
     pip install --upgrade pip
     pip install txtai
     deactivate
     ```

   - После создания: Установи права на скрипты: chmod +x scripts/*.py (если нужно для тестов).

3. **Проверка**: После setup выполни `ls` в корне и убедись, что окружения созданы (директории crewai_env, gopiai_env, txtai_env существуют).

## Dependencies
- Не модифицируй файлы зависимостей: GopiAI-CrewAI/requirements.txt (для CrewAI), GopiAI-UI/requirements.txt (для UI и gopiai), requirements.txt (для dev).
- Для txtai_env: Только txtai, как указано.
- Если конфликты при установке: Запиши ошибки в отчёт и продолжи — мы разберёмся позже.
- Дополнительно: spacy модели (ru_core_news_sm, en_core_web_sm) устанавливаются только в gopiai_env.

## Running Tests
На основе README.md и скриптов, тесты запускаются через scripts/run_tests.py. Сначала настрой окружения (см. выше), затем:

1. **Активация нужного env**: Для большинства тестов используй gopiai_env (оно включает dev зависимости).
   - source gopiai_env/bin/activate

2. **Запуск тестов**:
   - Все тесты: ./scripts/run_tests.py
   - По категории: ./scripts/run_tests.py --category unit (или integration, e2e).
   - Проверь пути: Убедись, что скрипт ищет тесты в tests/unit, tests/integration, tests/e2e. Если сломано после рефакторинга — поправь импорты или пути.

3. **Проверка перед запуском**:
   - Убедись, что нет занятых портов (хотя в VM это редко): Используй lsof -i :порт для проверки (например, 5051, 8000).
   - Если тесты требуют запущенных сервисов: Сначала симулируй запуск (см. ниже), но для базовых тестов это может не нужно.

## Running the Application (for Validation)
Если нужно проверить изменения путём запуска приложения (на основе start_linux.sh):

1. **Подготовка**:
   - Экспорт кодировки: export LANG=en_US.UTF-8; export LC_ALL=en_US.UTF-8
   - Проверка портов: Используй функцию вроде:
     ```
     check_port() {
         if lsof -i ":$1" >/dev/null 2>&1; then
             echo "Порт $1 занят." && exit 1
         fi
     }
     check_port 5051
     check_port 8000
     ```
   - Убедись, что gopiai_env существует.

2. **Запуск сервисов** (симулируй в фоне или последовательно в VM):
   - Активируй gopiai_env: source gopiai_env/bin/activate
   - Запусти TXTAI (в txtai_env): source txtai_env/bin/activate && echo "TXTAI ready" (добавь реальный запуск, если есть команда).
   - Установка UI deps (если не сделано): source gopiai_env/bin/activate && cd GopiAI-UI && pip install -r requirements.txt
   - Запуск UI: source gopiai_env/bin/activate && cd GopiAI-UI && python -m gopiai.ui.main 2> ui_errors.log
   - Для CrewAI: Активируй crewai_env и запусти сервер (предполагаю, что есть команда вроде crewai serve --port 5051; уточни по коду).

   Поскольку VM не имеет GUI, фокусируйся на CLI-тестах и логах. Если UI не запускается — проверь логи и отчётуй.

## Other Instructions
- **Всегда проверяй изменения**: После перемещений/изменений — git diff и проверь импорты/пути.
- **Ошибки**: Если venv не создаётся — проверь права VM (ты имеешь доступ). Если pip fails — попробуй --no-cache-dir.
- **Автоматизация**: Если возможно, создай временный bash-скрипт в VM для полного setup: echo "команды" > temp_setup.sh && bash temp_setup.sh.
- **Финальная проверка**: После setup запусти тесты и подтверди, что ничего не сломано. Коммить только working changes.