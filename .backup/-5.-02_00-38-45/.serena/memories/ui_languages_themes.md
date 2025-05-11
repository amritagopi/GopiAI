# Информация о работе с темами и переводами в GUI

## Переводы (i18n)

Система переводов использует следующие ключевые компоненты:

1. **JsonTranslationManager** в `app/ui/i18n/translator.py`:
   - Singleton для хранения и управления переводами
   - Загружает переводы из JSON файлов в директории `app/ui/i18n/`
   - Отправляет сигнал `languageChanged` при смене языка

2. **Файлы переводов**:
   - `app/ui/i18n/en.json` - английский язык
   - `app/ui/i18n/ru.json` - русский язык

3. **Функция tr()** для получения перевода:
   ```python
   from app.ui.i18n.translator import tr
   label.setText(tr("key.path", "Default text"))
   ```

4. **LanguageSelector** в `app/ui/language_selector.py`:
   - Виджет для переключения языка
   - Интегрируется в меню приложения через диалог

## Темы

Система тем управляется следующими компонентами:

1. **ThemeManager** в `app/utils/theme_manager.py`:
   - Singleton для загрузки и применения тем
   - Хранит цвета и стили, генерирует QSS
   - Отправляет сигнал `visualThemeChanged` при смене темы

2. **Файлы тем**:
   - `app/ui/themes/dark.json` и `app/ui/themes/dark.qss`
   - `app/ui/themes/light.json` и `app/ui/themes/light.qss`

3. **ThemeSettingsDialog** в `app/ui/theme_settings_dialog.py`:
   - Диалог для выбора и настройки тем

## Соединение сигналов

Для корректной работы переводов и тем необходимо правильно соединить сигналы:

1. **Переводы**:
   ```python
   # В MainWindow.__init__
   self.translation_manager = JsonTranslationManager.instance()
   self.translation_manager.languageChanged.connect(self._on_language_changed_event)
   
   # Метод обработки события
   def _on_language_changed_event(self, language_code):
       from app.utils.translation import on_language_changed_event
       on_language_changed_event(self, language_code)
   ```

2. **Темы**:
   ```python
   # В MenuManager в connect_signals
   from ..utils.theme_utils import on_theme_changed_event
   self.theme_changed.connect(lambda theme: on_theme_changed_event(self.main_window, theme))
   ```

## Исправления, внесенные в код

1. Исправлен путь к директории переводов в `translator.py` для правильной загрузки JSON файлов
2. Упрощен метод `load_translations` для прямой загрузки из i18n директории
3. Удалены отладочные print из `theme_utils.py`
4. Улучшена обработка отсутствующих иконок в `theme_utils.py`
5. Усовершенствован `LanguageSelector` для лучшей интеграции с UI:
   - Подключение к сигналу `languageChanged`
   - Добавление логирования
   - Использование функции `tr()`
6. Добавлен диалог выбора языка в меню приложения
7. Добавлен обработчик события изменения языка в `MainWindow`

## Дальнейшие улучшения

1. Проверить правильность подключения сигналов между компонентами
2. Оптимизировать загрузку файлов переводов и тем
3. Добавить возможность создания пользовательских тем
4. Улучшить UX переключения языка и тем