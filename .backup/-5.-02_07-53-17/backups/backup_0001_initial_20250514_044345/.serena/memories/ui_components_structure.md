# Структура UI-компонентов GopiAI

## Основные UI-файлы
- `app/ui/main_window.py` - главное окно приложения
- `app/ui/central_widget.py` - центральный виджет
- `app/ui/docks.py` - создание докируемых панелей
- `app/ui/menus.py` - настройка меню приложения
- `app/ui/toolbars.py` - настройка панелей инструментов
- `app/ui/icon_manager.py` - управление иконками
- `app/ui/theme_settings_dialog.py` - диалог настройки тем
- `app/ui/browser_tab_widget.py` - вкладки браузера
- `app/ui/reasoning_agent_dialog.py` - диалог агента рассуждений
- `app/ui/agent_ui_integration.py` - интеграция агентов с UI

## Утилиты для UI
- `app/utils/theme_manager.py` - менеджер тем
- `app/utils/theme_utils.py` - утилиты для работы с темами
- `app/utils/ui_utils.py` - общие утилиты для UI

## Система тем
- Настраивается через ThemeManager (Singleton)
- Темы хранятся в JSON-файлах в `app/ui/themes/`
- Стили применяются через QSS (Qt Style Sheets)
- Поддерживаются светлая и тёмная темы, с возможностью добавления кастомных

## Локализация
- Управляется JsonTranslationManager (Singleton)
- Переводы хранятся в JSON-файлах в `app/ui/i18n/`
- Доступны английский и русский языки
- Используется функция tr() для получения переводов

## Интеграция с агентами
- Связь UI и агентов через сигналы
- Компоненты для взаимодействия с агентами:
  - reasoning_agent_dialog.py
  - coding_agent_dialog.py
  - browser_agent_dialog.py
  - agent_ui_integration.py

## Система иконок
- IconManager управляет всеми иконками
- Поддерживаются различные форматы (SVG, PNG)
- Иконки могут адаптироваться под текущую тему
- Функция get_icon() для унифицированного доступа к иконкам