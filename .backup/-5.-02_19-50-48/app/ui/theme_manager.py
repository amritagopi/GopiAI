import os
import json
from PySide6.QtCore import QObject, Signal, QSettings
from app.ui.i18n import JsonTranslationManager

class ThemeManager(QObject):
    """
    Менеджер интегрированных тем.
    Каждая тема содержит как стилевое оформление (QSS), так и языковые данные.

    Структура директорий тем:
    themes/
        dark_ru/
            theme.qss
            theme.jpeg (опционально)
            translations.json
        dark_en/
            theme.qss
            theme.jpeg (опционально)
            translations.json
        light_ru/
            theme.qss
            theme.jpeg (опционально)
            translations.json
        light_en/
            theme.qss
            theme.jpeg (опционально)
            translations.json
    """

    # Сигнал для оповещения о смене темы
    themeChanged = Signal(str)
    # Сигнал для оповещения о смене только визуальной части темы (без языка)
    visualThemeChanged = Signal(str)
    # Сигнал для оповещения о смене только языка (без визуальной темы)
    languageChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.themes = {}
        self.translations = {}
        self.current_theme = None
        self.settings = QSettings("GopiAI", "UI")

        # Загружаем все доступные темы
        self._load_themes()

        # Устанавливаем тему по умолчанию или из настроек
        self._set_initial_theme()

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за загрузку тем из файловой системы и их подготовку к использованию
    # Изменение логики может привести к поломке UI и нарушению работы приложения
    # Ошибки здесь приведут к неправильному отображению интерфейса и текстов
    # Тесно связан с методами switch_theme и _set_initial_theme
    ############################################################################
    def _load_themes(self):
        """Загружает все доступные темы из директории тем."""
        themes_dir = os.path.join(os.path.dirname(__file__), "themes")

        # Проверяем все поддиректории
        for theme_dir in os.listdir(themes_dir):
            theme_path = os.path.join(themes_dir, theme_dir)

            # Пропускаем, если это не директория
            if not os.path.isdir(theme_path):
                continue

            # Проверяем наличие необходимых файлов
            qss_path = os.path.join(theme_path, "theme.qss")
            translations_path = os.path.join(theme_path, "translations.json")

            if not os.path.exists(qss_path) or not os.path.exists(translations_path):
                print(f"Пропускаем неполную тему: {theme_dir}")
                continue

            # Загружаем переводы
            try:
                with open(translations_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations[theme_dir] = translations
            except Exception as e:
                print(f"Ошибка загрузки переводов для темы {theme_dir}: {e}")
                continue

            # Добавляем тему в список доступных
            self.themes[theme_dir] = {
                'qss_path': qss_path,
                'translations_path': translations_path,
                'image_path': os.path.join(theme_path, "theme.jpeg") if os.path.exists(os.path.join(theme_path, "theme.jpeg")) else None
            }

        print(f"Загружено тем: {len(self.themes)}")

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за выбор начальной темы и синхронизацию с языком
    # Изменение логики может привести к поломке UI и нарушению работы приложения
    # Особенно важно для правильного запуска с сохраненными настройками
    # Тесно связан с методами _load_themes и get_theme_language
    ############################################################################
    def _set_initial_theme(self):
        """Устанавливает начальную тему из настроек или тему по умолчанию."""
        # Восстанавливаем из настроек или используем тему по умолчанию
        saved_theme = self.settings.value("theme", None)

        if saved_theme and saved_theme in self.themes:
            self.current_theme = saved_theme
        else:
            # По умолчанию используем dark_en или первую доступную тему
            if "dark_en" in self.themes:
                self.current_theme = "dark_en"
            elif len(self.themes) > 0:
                self.current_theme = list(self.themes.keys())[0]

        print(f"Установлена начальная тема: {self.current_theme}")

        # Синхронизируем язык при инициализации
        language_code = self.get_theme_language()
        if language_code:
            JsonTranslationManager.instance().switch_language(language_code)
            print(f"Установлен начальный язык: {language_code}")

    def get_available_themes(self):
        """Возвращает список доступных тем."""
        return list(self.themes.keys())

    def get_current_theme(self):
        """Возвращает текущую тему."""
        return self.current_theme

    def get_theme_qss_path(self, theme_name=None):
        """Возвращает путь к файлу QSS для указанной или текущей темы."""
        theme = theme_name or self.current_theme
        if theme in self.themes:
            return self.themes[theme]['qss_path']
        return None

    def get_theme_image_path(self, theme_name=None):
        """Возвращает путь к изображению темы для указанной или текущей темы."""
        theme = theme_name or self.current_theme
        if theme in self.themes and 'image_path' in self.themes[theme]:
            return self.themes[theme]['image_path']
        return None

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за переключение темы и синхронизацию языка интерфейса
    # Изменение логики может привести к поломке UI и нарушению работы приложения
    # Особенно важно правильное управление сигналами и предотвращение рекурсии
    # Тесно связан с методами get_theme_language и switch_language
    ############################################################################
    def switch_theme(self, theme_name):
        """Переключает на указанную тему."""
        # Защита от рекурсивных вызовов
        if hasattr(self, '_is_switching_theme') and self._is_switching_theme:
            print(f"Предотвращен рекурсивный вызов switch_theme({theme_name})")
            return False

        self._is_switching_theme = True

        try:
            if theme_name not in self.themes:
                print(f"Тема {theme_name} не найдена")
                return False

            if theme_name == self.current_theme:
                print(f"Тема {theme_name} уже активна")
                return True

            self.current_theme = theme_name

            # Сохраняем выбор в настройках
            self.settings.setValue("theme", theme_name)
            self.settings.sync()

            # Синхронизируем язык интерфейса с языком темы
            language_code = self.get_theme_language()
            if language_code:
                JsonTranslationManager.instance().switch_language(language_code)
                print(f"Язык изменен на: {language_code}")

            # Уведомляем об изменении темы
            self.themeChanged.emit(theme_name)

            print(f"Тема изменена на: {theme_name}")
            return True

        finally:
            # Снимаем флаг в любом случае
            self._is_switching_theme = False

    # Новый метод для переключения только визуальной темы без изменения языка
    def switch_visual_theme(self, theme_type):
        """
        Переключает только визуальную часть темы (светлая/темная), сохраняя текущий язык.

        Args:
            theme_type (str): Тип темы ('dark' или 'light')

        Returns:
            bool: True, если тема успешно изменена, иначе False
        """
        # Защита от рекурсивных вызовов
        if hasattr(self, '_is_switching_visual_theme') and self._is_switching_visual_theme:
            print(f"Предотвращен рекурсивный вызов switch_visual_theme({theme_type})")
            return False

        self._is_switching_visual_theme = True

        try:
            if theme_type not in ['dark', 'light']:
                print(f"Тип темы {theme_type} не поддерживается")
                return False

            # Получаем текущий язык
            current_lang = 'en'
            if self.current_theme and '_' in self.current_theme:
                current_lang = self.current_theme.split('_')[1]

            # Формируем новое имя темы
            new_theme = f"{theme_type}_{current_lang}"

            if new_theme not in self.themes:
                print(f"Тема {new_theme} не найдена")
                return False

            if new_theme == self.current_theme:
                print(f"Тема {new_theme} уже активна")
                return True

            # Обновляем текущую тему
            self.current_theme = new_theme

            # Сохраняем выбор в настройках
            self.settings.setValue("theme", new_theme)
            self.settings.setValue("visual_theme", theme_type)
            self.settings.sync()

            # Уведомляем об изменении только визуальной части темы
            self.visualThemeChanged.emit(new_theme)

            print(f"Визуальная тема изменена на: {new_theme}")
            return True

        finally:
            # Снимаем флаг в любом случае
            self._is_switching_visual_theme = False

    # Алиас для обратной совместимости
    def set_theme(self, theme_name):
        """Алиас для метода switch_theme для обратной совместимости."""
        return self.switch_theme(theme_name)

    def is_dark_theme(self):
        """Определяет, является ли текущая тема темной."""
        return self.current_theme and 'dark' in self.current_theme

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за определение языка на основе текущей темы
    # Изменение логики может привести к поломке UI и нарушению работы приложения
    # Используется для синхронизации темы и языка в интерфейсе
    # Тесно связан с методами switch_theme и switch_language
    ############################################################################
    def get_theme_language(self):
        """Возвращает язык текущей темы (ru_RU или en_US)."""
        if self.current_theme:
            if '_ru' in self.current_theme:
                return 'ru_RU'
            elif '_en' in self.current_theme:
                return 'en_US'
        # По умолчанию английский
        return 'en_US'

    def get_current_language(self):
        """Возвращает текущий язык приложения."""
        return self.get_theme_language()

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за переключение языка интерфейса через смену темы
    # Изменение логики может привести к поломке UI и рассинхронизации языка/темы
    # Изменение префиксов или логики может сломать весь процесс локализации
    # Тесно связан с методами switch_theme и get_theme_language
    ############################################################################
    def switch_language(self, language_code):
        """Переключает язык интерфейса.

        Args:
            language_code (str): Код языка ('ru_RU' или 'en_US')

        Returns:
            bool: True, если язык успешно изменен, иначе False
        """
        # Проверяем поддерживаемые языки
        if language_code not in ['ru_RU', 'en_US']:
            print(f"Язык {language_code} не поддерживается")
            return False

        # Находим тему, соответствующую выбранному языку
        theme_prefix = 'dark' if self.is_dark_theme() else 'light'
        lang_suffix = 'ru' if language_code == 'ru_RU' else 'en'
        new_theme = f"{theme_prefix}_{lang_suffix}"

        # Проверяем, существует ли такая тема
        if new_theme not in self.themes:
            print(f"Тема {new_theme} для языка {language_code} не найдена")
            return False

        # Новая реализация с отдельным сигналом
        if new_theme == self.current_theme:
            print(f"Тема {new_theme} уже активна")
            return True

        # Обновляем текущую тему
        old_theme = self.current_theme
        self.current_theme = new_theme

        # Сохраняем выбор в настройках
        self.settings.setValue("theme", new_theme)
        self.settings.setValue("language", lang_suffix)
        self.settings.sync()

        # Синхронизируем язык интерфейса
        if hasattr(JsonTranslationManager.instance(), 'switch_language'):
            JsonTranslationManager.instance().switch_language(language_code)
            print(f"Язык изменен на: {language_code}")

        # Уведомляем об изменении только языка
        self.languageChanged.emit(new_theme)

        print(f"Язык изменен на: {language_code} (тема: {new_theme})")
        return True

    def get_translation(self, key, default_text=None):
        """Получает перевод для текущей темы или использует менеджер переводов."""
        if self.current_theme and self.current_theme in self.translations:
            parts = key.split('.')
            cur = self.translations[self.current_theme]

            for part in parts:
                if part in cur:
                    cur = cur[part]
                else:
                    return default_text or key

            if isinstance(cur, str):
                return cur

        # Если не нашли в переводах темы, используем общий менеджер переводов
        if hasattr(JsonTranslationManager.instance(), 'get_translation'):
            return JsonTranslationManager.instance().get_translation(key, default_text or key)

        return default_text or key

    def get_theme_display_name(self, theme_name=None):
        """Возвращает отображаемое имя темы для указанной или текущей темы."""
        theme = theme_name or self.current_theme
        if not theme:
            return "Unknown Theme"

        # Разбиваем имя темы на части (например, "dark_en" -> "dark", "en")
        parts = theme.split('_')
        if len(parts) >= 2:
            theme_type = parts[0]
            lang_code = parts[1]

            # Словарь отображаемых имен
            display_names = {
                'dark_en': "Dark Theme (English)",
                'dark_ru': "Тёмная тема (Русский)",
                'light_en': "Light Theme (English)",
                'light_ru': "Светлая тема (Русский)",
            }

            if theme in display_names:
                return display_names[theme]

            # Создаем имя на основе составляющих
            lang_names = {'en': "English", 'ru': "Русский"}
            theme_types = {'dark': "Dark Theme", 'light': "Light Theme"}

            lang_name = lang_names.get(lang_code, lang_code)
            theme_type_name = theme_types.get(theme_type, theme_type.capitalize())

            return f"{theme_type_name} ({lang_name})"

        return theme.capitalize()


# Создаем глобальный экземпляр менеджера тем
theme_manager = ThemeManager()
