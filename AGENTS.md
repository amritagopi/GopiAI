AGENTS.md
Overview
Jules, из-за проблем с disk space в твоей VM, не устанавливай ничего локально. Вместо этого перенеси проект в Coiled (облачная платформа Python), используя предоставленный API-токен. Твоя задача: залогиниться в Coiled, клонировать репозиторий, настроить три виртуальных окружения (crewai_env, gopiai_env, txtai_env) по аналогии с setup_linux.sh, и выполнить рефакторинг проекта, будь предельно внимателен и осторожен (тесты или ручную валидацию). Следуй шагам последовательно, отчитывайся о каждом шаге с логами (df -h, stdout/stderr).
Step 1: Read Coiled Documentation

Ознакомься с документацией Coiled: https://docs.coiled.io/en/latest/
Ключевые разделы: "Getting Started", "Environments", "Python Packages". Это нужно для понимания coiled login и управления окружениями.
Подтверди: echo "Read Coiled docs at https://docs.coiled.io/en/latest/" > coiled_read.log

Step 2: Login to Coiled

Установи Coiled CLI (минимально, только для login, не жди disk errors):pip install --user --no-cache-dir coiled


Залогинись с токеном:coiled login --token 2744f6a48bcb4c2db97dcbb8ecc0f648-4be3a948bd7a97bc1685b9deb02dd6ea79ad089b


Проверь логин: coiled whoami > coiled_login.log
Если ошибка (например, disk space), отчётуй: echo "Coiled login failed" && cat coiled_login.log

Step 3: Clone Repository in Coiled

Создай новую Coiled среду (compute environment):coiled create environment --name gopiai-project --python 3.8


Клонируй репо в Coiled:coiled run --environment gopiai-project -- git clone https://github.com/amritagopi/GopiAI /app


Перейди в директорию: coiled run --environment gopiai-project -- bash -c "cd /app && pwd > clone_log.txt"
Проверь: coiled run --environment gopiai-project -- bash -c "ls -l /app > repo_files.txt"
Отчётуй: Сохрани clone_log.txt, repo_files.txt.

Step 4: Setup Environments in Coiled

Настрой три виртуальных окружения (crewai_env, gopiai_env, txtai_env) по аналогии с setup_linux.sh. Выполняй команды в Coiled:coiled run --environment gopiai-project -- bash -c "cd /app && mkdir -p scripts docs config tests/unit tests/integration tests/e2e"


Для каждого окружения:
crewai_env:coiled run --environment gopiai-project -- bash -c "cd /app && python3 -m venv crewai_env && source crewai_env/bin/activate && pip install --upgrade pip && pip install -r GopiAI-CrewAI/requirements.txt && deactivate"


gopiai_env:coiled run --environment gopiai-project -- bash -c "cd /app && python3 -m venv gopiai_env && source gopiai_env/bin/activate && pip install --upgrade pip && pip install -r GopiAI-UI/requirements.txt && pip install -r requirements.txt && python -m spacy download ru_core_news_sm && python -m spacy download en_core_web_sm && deactivate"


txtai_env:coiled run --environment gopiai-project -- bash -c "cd /app && python3 -m venv txtai_env && source txtai_env/bin/activate && pip install --upgrade pip && pip install txtai && deactivate"




Установи права: coiled run --environment gopiai-project -- bash -c "cd /app && chmod +x scripts/*.py"
Проверь диск: coiled run --environment gopiai-project -- bash -c "df -h > disk_usage.txt"
Если ошибка (например, pip fails), добавь --no-cache-dir и сохрани логи: pip ... 2> pip_error.log

Step 5: Run Tests

Используй gopiai_env для тестов (оно включает dev deps):coiled run --environment gopiai-project -- bash -c "cd /app && source gopiai_env/bin/activate && ./scripts/run_tests.py --category unit > test_log.txt 2>&1"


Если disk error или тесты не нужны, пропусти и перейди к ручной проверке:coiled run --environment gopiai-project -- bash -c "cd /app && git diff > diff.txt && ls -l tests/ > test_files.txt"



Step 6: Validate Application (Optional)

Если тесты не нужны, симулируй запуск (по start_linux.sh, без UI, так как Coiled — CLI-only):
TXTAI: coiled run --environment gopiai-project -- bash -c "cd /app && source txtai_env/bin/activate && echo 'TXTAI ready' > txtai_log.txt"
UI (dry-run): coiled run --environment gopiai-project -- bash -c "cd /app && source gopiai_env/bin/activate && cd GopiAI-UI && python -m gopiai.ui.main --dry-run 2> ui_errors.log"
CrewAI (если есть команда): уточни запуск сервера (например, crewai serve --port 5051) и выполни в crewai_env.


Сохрани логи: txtai_log.txt, ui_errors.log.

Other Instructions

Логирование: Сохраняй все логи (coiled_login.log, clone_log.txt, repo_files.txt, disk_usage.txt, pip_error.log, test_log.txt, diff.txt, test_files.txt, ui_errors.log) и включай в отчёт.
Ошибки: Если disk space error в Coiled, выполни coiled run --environment gopiai-project -- bash -c "pip cache purge && rm -rf ~/.cache/pip && df -h > disk_error.txt".
Проверка: Перед коммитом: coiled run --environment gopiai-project -- bash -c "cd /app && git diff > final_diff.txt".
Запрет: Не устанавливай ничего в своей VM — только Coiled.
Отчёт: После каждого шага пиши: успех/ошибка, приложи логи, укажи свободное место (df -h).
