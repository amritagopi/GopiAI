# Решение проблемы циклических импортов

В проекте была критическая ошибка с циклическими импортами между модулями theme_manager.py и theme_utils.py:

1. `app/utils/theme_manager.py` импортировал `get_additional_qss_template` из `app/utils/theme_utils.py`
2. `app/utils/theme_utils.py` импортировал `ThemeManager` из `app/utils/theme_manager.py`

Это создавало циклическую зависимость, из-за которой приложение не могло запуститься.

## Решение

Для решения мы преобразовали глобальные импорты в локальные импорты внутри функций:

1. В файле `app/utils/theme_utils.py`:
   - Удалили импорт `from app.utils.theme_manager import ThemeManager` в начале файла
   - Добавили локальный импорт `from app.utils.theme_manager import ThemeManager` внутри функций `get_additional_qss_template` и `on_theme_changed_event`

2. В файле `app/utils/theme_manager.py`:
   - Удалили импорт `from app.utils.theme_utils import get_additional_qss_template` в начале файла
   - Добавили локальный импорт `from app.utils.theme_utils import get_additional_qss_template` внутри метода `_apply_visual_theme`

Этот подход с локальными импортами - распространенный способ решения циклических зависимостей в Python. Локальные импорты позволяют разорвать круг, так как они выполняются только во время вызова функции, а не при загрузке модуля.

## Важно помнить

При добавлении новой функциональности важно следить за структурой импортов, чтобы не создавать новые циклические зависимости. Если модуль A импортирует модуль B, то модуль B не должен импортировать модуль A (на уровне глобальных импортов).