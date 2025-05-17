# Обновление системы иконок на Lucide

## Основные изменения
1. Установлена библиотека Lucide через npm
2. Создан новый класс `LucideIconManager` в `app/ui/lucide_icon_manager.py`
3. Создан адаптер `IconAdapter` в `app/ui/icon_adapter.py` для обеспечения совместимости
4. Добавлены базовые SVG-иконки в директорию `assets/icons/lucide/`
5. Обновлен `main.py` для использования новой системы иконок

## Удалены старые файлы
- `app/ui/icon_manager.py` - старый менеджер иконок
- `app/icons_rc.py` - ресурсный файл
- Старые SVG-файлы из `assets/icons/`
- Тестовые файлы: `tests/test_icon_manager.py`, `tests/test_themed_icons.py`, `tests/deprecated_test_icon_usage_in_ui.py`

## Обновлены импорты и использование иконок
Все файлы, использующие старый `IconManager` обновлены:
- `browser_agent_dialog.py`
- `coding_agent_dialog.py`
- `dock_title_bar.py`
- `main_window_title_bar.py`
- `settings_widget.py`
- `reasoning_agent_dialog.py`
- `plan_view_widget.py`
- `window_control_widget.py`
- `thought_tree_widget.py`
- `code_editor_widget.py`
- `main_window.py`
- `project_explorer.py`
- `menu_manager.py`

## Обновлена документация
- `docs/design/icon_system.md`
- `docs/design/icon_usage_in_ui.md`

## Инструменты для тестирования
Создан `test_lucide_icons.py` для просмотра и тестирования иконок.

## Преимущества новой системы
- Единый современный стиль иконок с Lucide
- Масштабируемые SVG-иконки без потери качества
- Поддержка тем и изменения цвета иконок
- Более простое добавление новых иконок
- Улучшенная производительность и меньший размер файлов