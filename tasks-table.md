# ModelSwitchRefactor
Refactor backend and frontend to support stable provider switching between Gemini and OpenRouter

> ## 📈 Project Summary
> 
> **✅ Done**: 15 | **🔄 In Progress**: 1 | **⬜ Todo**: 5 | **❌ Blocked**: 0
> 
> **Progress**: 71% `██████████████░░░░░░` 15/21 tasks
> 
> **Priorities**: 🚨 **Critical**: 3 | 🔴 **High**: 7 | 🟡 **Medium**: 11 | 🟢 **Low**: 0

## Tasks

| ID | Status | Priority | Title | Description |
|:--:|:------:|:--------:|:------|:------------|
| #1 | ✅ done | 700 | **Project Setup: ModelSwitchRefactor** | Refactor backend and frontend... |
| #2 | 🔄 inprogress | 701 | **Refactor backend llm_rotation_config.py to support OpenRouter and remove duplicates** | Add OpenRouter provider suppo... |
| #3 | ⬜ todo | 699 | **Refactor model_selector_widget.py to single-provider dropdown and remove duplicate signals** | Frontend widget should:
- Pre... |
| #4 | ✅ done | 702 | **Implement provider/model state file synchronization** | Create ~/.gopiai_state.json s... |
| #5 | ✅ done | 698 | **Создание ветки для исправлений** | Создать git ветку fix/llm-pro... |
| #6 | ✅ done | 900 | **Чистка конфигураций - удаление дубликатов** | Удалить .env.override, перене... |
| #7 | ✅ done | 901 | **Выравнивание интерфейса адаптеров LLM** | Ввести абстракцию BaseAdapter... |
| #8 | ✅ done | 899 | **Реализация реинициализации клиента LLM** | Добавить метод swap_provider(... |
| #9 | ✅ done | 703 | **Реализация тайм-аутов и обработка ошибок** | Ввести DEFAULT_TIMEOUT, оберн... |
| #10 | ✅ done | 697 | **Исправление инструментов (filesystem/terminal)** | Перевести callback-менеджер н... |
| #11 | ✅ done | 500 | **Создание тест-матрицы для проверки переключения** | Создать тесты в tests/llm/tes... |
| #12 | ✅ done | 501 | **Обновление документации по переключению LLM** | Обновить 02_DOCUMENTATION/USA... |


### Task #2: Refactor backend llm_rotation_config.py to support OpenRouter and remove duplicates - Subtasks

| ID | Status | Title |
|:--:|:------:|:------|
| #2.1 | ✅ done | Introduce PROVIDERS dict with Gemini and OpenRouter models |
| #2.2 | ⬜ todo | Create UsageTracker class and replace scattered usage dicts |

### Task #3: Refactor model_selector_widget.py to single-provider dropdown and remove duplicate signals - Subtasks

| ID | Status | Title |
|:--:|:------:|:------|
| #3.1 | ⬜ todo | Replace two provider buttons with QComboBox |
| #3.2 | ⬜ todo | Refactor model loading to use get_available_models |
| #3.3 | ⬜ todo | Unify API key handling and save to .env |

### Task #4: Implement provider/model state file synchronization - Subtasks

| ID | Status | Title |
|:--:|:------:|:------|
| #4.1 | ✅ done | Создать модуль управления файлом состояния |
| #4.2 | ✅ done | Интегрировать чтение состояния в backend при запуске |
| #4.3 | ✅ done | Обновить UI виджет для записи в файл состояния |
| #4.4 | ✅ done | Создать тесты для синхронизации состояния |

