# Инструменты для работы с кодовой базой GopiAI

В этой директории находятся инструменты для работы с индексированной кодовой базой проекта.

## Поиск по коду

```bash
python code_search.py . "как работает авторизация"
Анализ зависимостей
bash

Hide
# Поиск файла
python dependency_explorer.py --search "auth"

# Анализ конкретного файла
python dependency_explorer.py --file "src/auth/login.js"
Вопросы о коде
bash

Hide
python code_qa.py . "Как реализована функция входа пользователя?"