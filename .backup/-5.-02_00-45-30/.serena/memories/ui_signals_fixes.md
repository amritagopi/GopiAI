# Исправления в системе сигналов UI

## Проблемы, которые были исправлены

1. **Непрямая обработка событий смены языка**:
   - Раньше: Действия меню -> MenuManager.language_changed -> MainWindow -> translation.on_language_changed_event
   - Теперь: Действия меню -> JsonTranslationManager.switch_language -> JsonTranslationManager.languageChanged -> MainWindow._on_language_changed_event -> translation.on_language_changed_event

2. **Непрямая обработка событий смены темы**:
   - Раньше: Действия меню -> MenuManager.theme_changed -> MainWindow -> theme_utils.on_theme_changed_event
   - Теперь: Действия меню -> ThemeManager.switch_visual_theme -> ThemeManager.visualThemeChanged -> theme_utils.on_theme_changed_event

3. **Отсутствующие соединения сигналов**:
   - Добавлено подключение сигнала language_changed от LanguageSelector к MainWindow._on_language_changed_event в методе _show_language_selector
   - Добавлено прямое подключение ThemeManager.visualThemeChanged к обработчику в MainWindow

## Внесенные изменения

1. В **menu_manager.py**:
   - Метод `update_language_menu` теперь напрямую вызывает `JsonTranslationManager.switch_language` вместо эмиссии сигнала
   - Метод `update_themes_menu` теперь напрямую вызывает `ThemeManager.switch_visual_theme` вместо эмиссии сигнала

2. В **main_window.py**:
   - Добавлено подключение сигнала `language_changed` от LanguageSelector к `_on_language_changed_event` в методе `_show_language_selector`
   - Добавлено подключение сигнала `visualThemeChanged` от ThemeManager к `on_theme_changed_event` в методе `__init__`
   - Удалены подключения к сигналам MenuManager в методе `_connect_global_ui_signals`, так как они больше не нужны

## Преимущества нового подхода

1. **Единый поток событий**: Все события теперь проходят через одни и те же обработчики, что предотвращает дублирование и рассинхронизацию
2. **Централизованное управление**: Менеджеры (JsonTranslationManager и ThemeManager) полностью контролируют изменения языка и темы
3. **Устранение дублирующихся сигналов**: Нет риска двойной обработки одного и того же события
4. **Более понятная архитектура**: Четко определены источники событий и их обработчики