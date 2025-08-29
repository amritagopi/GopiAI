# План рефакторинга инструментов GopiAI

## Цель
Очистить директорию tools/, оставив только нативные инструменты CrewAI из crewai_toolkit/tools/, удалив все кастомные инструменты для упрощения архитектуры и предотвращения конфликтов.

## Текущая структура
### Инструменты для удаления (кастомные):
- `tools/code_interpreter_tool.py`
- `tools/command_executor.py`
- `tools/graceful_shutdown.py`
- `tools/simple_code_executor.py`
- `tools/simple_filesystem_tool.py`
- `tools/tools_config.py`
- `tools/unrestricted_code_executor.py`
- `tools/unrestricted_filesystem_tool.py`
- `tools/unrestricted_tools_manager.py`
- `tools/gopiai_integration/` (вся директория с ~30 файлами)

### Инструменты для сохранения (нативные CrewAI):
- `tools/crewai_toolkit/tools/` со всеми поддиректориями (~40 нативных инструментов)

## Зависимости и импорты
Найдено 24 импорта из `tools.gopiai_integration` в следующих файлах:
- `GopiAI-CrewAI/demo_dynamic_instructions.py`
- `GopiAI-CrewAI/test_github_tool.py`
- `GopiAI-CrewAI/tests/e2e/test_terminal_tool.py`
- `GopiAI-CrewAI/tests/test_command_processor_strict_json.py`
- `GopiAI-CrewAI/main.py`
- `GopiAI-CrewAI/crewai_api_server.py`
- `GopiAI-CrewAI/tools/gopiai_integration/system_prompts.py`
- `GopiAI-CrewAI/tools/gopiai_integration/crewai_tools_integration.py`
- `GopiAI-CrewAI/tools/gopiai_integration/smart_delegator.py`
- `tests/memory/test_memory_system.py`
- `GopiAI-UI/gopiai/ui/components/openrouter_model_widget.py`

## Риски
1. **Высокий риск поломки**: Удаление gopiai_integration/ затронет критические компоненты (SmartDelegator, ToolDispatcher)
2. **Конфликты с tool_dispatcher**: Предыдущий контекст показывает проблемы с конфликтами между кастомными и нативными инструментами
3. **Потеря функциональности**: Некоторые кастомные инструменты могут быть необходимы для работы системы
4. **Тестирование**: После изменений потребуется полное тестирование всех функций

## План действий
### Этап 1: Анализ и резервное копирование
1. Создать резервную копию всей директории tools/
2. Проанализировать каждый файл в gopiai_integration/ на предмет критической функциональности
3. Определить, какие компоненты можно заменить нативными CrewAI инструментами

### Этап 2: Подготовка нативных инструментов
1. Изучить структуру crewai_toolkit/tools/
2. Определить соответствия между кастомными и нативными инструментами
3. Обновить tools/__init__.py для импорта только нативных инструментов

### Этап 3: Обновление импортов
1. Обновить все файлы, импортирующие из gopiai_integration/
2. Заменить кастомные инструменты на соответствующие нативные
3. Обновить конфигурационные файлы

### Этап 4: Удаление кастомных инструментов
1. Удалить все кастомные файлы из tools/
2. Очистить tools/__init__.py
3. Удалить gopiai_integration/ целиком

### Этап 5: Тестирование
1. Проверить запуск сервера
2. Протестировать основные функции
3. Проверить логи на отсутствие ошибок
4. Выполнить интеграционное тестирование

## Критические компоненты для сохранения
- SmartDelegator (используется в crewai_api_server.py)
- ToolDispatcher (центральный диспетчер инструментов)
- Настройки моделей и конфигурация

## Альтернативный подход
Вместо полной замены, рассмотреть постепенную миграцию:
1. Сначала заменить только дублирующиеся инструменты
2. Постепенно мигрировать функциональность
3. Сохранить gopiai_integration/ как отдельный модуль для обратной совместимости