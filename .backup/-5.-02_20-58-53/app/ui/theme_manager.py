import os
import json
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtWidgets import QApplication
from app.ui.i18n import JsonTranslationManager

class ThemeManager(QObject):
    """
    Менеджер интегрированных тем.
    Каждая тема содержит как стилевое оформление (QSS), так и языковые данные.

    Структура директорий тем:
    themes/
        DARK-theme.qss
        LIGHT-theme.qss
        compiled/
            dark-theme.qss
            light-theme.qss
        vars/
            dark-colors.qss
            light-colors.qss
        EN-translations.json
        RU-translations.json
        color_system.py
    """

    # Сигнал для оповещения о смене темы
    themeChanged = Signal(str)
    # Сигнал для оповещения о смене только визуальной части темы (без языка)
    visualThemeChanged = Signal(str)
    # Сигнал для оповещения о смене только языка (без визуальной темы)
    languageChanged = Signal(str)

    _instance = None

    @classmethod
    def instance(cls):
        """Возвращает единственный экземпляр класса (singleton)."""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.themes = {}
        self.translations = {}
        self.current_theme = None
        self.settings = QSettings("GopiAI", "UI")

        # Инициализируем флаг доступности системы цветов перед загрузкой тем
        self.has_color_system = False
        self.color_system = None

        # Пытаемся загрузить нашу систему цветов
        try:
            from app.ui.themes.color_system import ColorSystem
            self.color_system = ColorSystem.instance()
            # Подключаем сигнал изменения палитры
            self.color_system.paletteChanged.connect(self._on_color_palette_changed)
            self.has_color_system = True
            print("Система цветов инициализирована успешно")
        except ImportError:
            print("Система цветов недоступна, используем стандартный механизм тем")

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

        # Проверяем наличие файлов QSS и JSON в корне директории themes
        try:
            # Ищем скомпилированные файлы тем в директории compiled/
            compiled_dir = os.path.join(themes_dir, "compiled")
            if os.path.exists(compiled_dir):
                qss_files = [f for f in os.listdir(compiled_dir) if f.endswith('-theme.qss')]
                if qss_files:
                    print("Найдены скомпилированные файлы тем")
                    # Используем скомпилированные файлы
                    for qss_file in qss_files:
                        theme_type = qss_file.split('-')[0].lower()  # dark, light
                        qss_path = os.path.join(compiled_dir, qss_file)

                        # Если существует fixed- версия, используем её
                        fixed_path = os.path.join(compiled_dir, f"fixed-{qss_file}")
                        if os.path.exists(fixed_path):
                            qss_path = fixed_path

                        self.themes[theme_type] = {
                            'qss_path': qss_path,
                            'type': theme_type
                        }
            else:
                # Ищем файлы тем в формате DARK-theme.qss, LIGHT-theme.qss и т.д.
                qss_files = [f for f in os.listdir(themes_dir) if f.endswith('-theme.qss')]

                # Если существуют fixed- версии, используем их
                fixed_qss_files = [f for f in os.listdir(themes_dir) if f.startswith('fixed-') and f.endswith('-theme.qss')]
                if fixed_qss_files:
                    qss_files = fixed_qss_files

                # Добавляем темы
                for qss_file in qss_files:
                    if qss_file.startswith('fixed-'):
                        theme_type = qss_file.split('-')[1].split('-')[0].lower()  # fixed-DARK-theme.qss -> dark
                    else:
                        theme_type = qss_file.split('-')[0].lower()  # DARK -> dark, LIGHT -> light

                    qss_path = os.path.join(themes_dir, qss_file)
                    self.themes[theme_type] = {
                        'qss_path': qss_path,
                        'type': theme_type
                    }

            # Ищем файлы переводов в формате EN-translations.json, RU-translations.json и т.д.
            json_files = [f for f in os.listdir(themes_dir) if f.endswith('-translations.json')]

            # Если нашли файлы переводов, добавляем их
            if json_files:
                for json_file in json_files:
                    lang_code = json_file.split('-')[0].lower()  # EN -> en, RU -> ru
                    translations_path = os.path.join(themes_dir, json_file)

                    # Загружаем переводы
                    try:
                        with open(translations_path, 'r', encoding='utf-8') as f:
                            translations = json.load(f)
                            self.translations[lang_code] = translations
                    except Exception as e:
                        print(f"Ошибка загрузки переводов для языка {lang_code}: {e}")

            # Создаем комбинированные темы (dark_en, light_ru, и т.д.)
            if self.themes and self.translations:
                combined_themes = {}
                for theme_type, theme_data in self.themes.items():
                    for lang_code in self.translations.keys():
                        theme_name = f"{theme_type}_{lang_code}"
                        combined_themes[theme_name] = {
                            'qss_path': theme_data['qss_path'],
                            'type': theme_type,
                            'language': lang_code
                        }

                # Добавляем комбинированные темы к существующим
                self.themes.update(combined_themes)

        except Exception as e:
            print(f"Ошибка при загрузке тем: {e}")

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

        # Синхронизируем цветовую схему, если доступна система цветов
        if self.has_color_system and self.color_system:
            theme_type = self.get_theme_type()
            if theme_type:
                self.color_system.set_theme(theme_type)
                print(f"Установлена цветовая схема: {theme_type}")

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

    def get_theme_type(self, theme_name=None):
        """Возвращает тип темы (dark/light) для указанной или текущей темы."""
        theme = theme_name or self.current_theme
        if theme in self.themes and 'type' in self.themes[theme]:
            return self.themes[theme]['type']

        # Если тип не указан явно, пытаемся определить из имени
        if theme:
            if theme.startswith('dark'):
                return 'dark'
            elif theme.startswith('light'):
                return 'light'

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

            # Синхронизируем цветовую схему, если доступна система цветов
            if self.has_color_system and self.color_system:
                theme_type = self.get_theme_type()
                if theme_type:
                    self.color_system.set_theme(theme_type)
                    print(f"Цветовая схема изменена на: {theme_type}")

            # Применяем тему через QSS
            self.apply_theme()

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
        # Получаем текущий язык
        current_language = self.get_current_language()
        if not current_language:
            print("Не удалось определить текущий язык")
            return False

        # Формируем имя новой темы
        new_theme = f"{theme_type}_{current_language}"

        # Проверяем, доступна ли такая тема
        if new_theme not in self.themes:
            print(f"Тема {new_theme} не найдена")
            return False

        # Переключаем на новую тему
        success = self.switch_theme(new_theme)

        if success:
            # Уведомляем о смене визуальной темы
            self.visualThemeChanged.emit(theme_type)

        return success

    # Для совместимости со старым кодом
    def set_theme(self, theme_name):
        """Синоним для switch_theme (для совместимости)."""
        return self.switch_theme(theme_name)

    def is_dark_theme(self):
        """Определяет, является ли текущая тема темной."""
        theme_type = self.get_theme_type()
        return theme_type == 'dark'

    def get_theme_language(self):
        """Извлекает код языка из имени темы."""
        if not self.current_theme:
            return None

        # Если тема в формате type_lang (например, dark_en)
        if '_' in self.current_theme:
            return self.current_theme.split('_')[1]

        # Если явно указан язык в метаданных темы
        if self.current_theme in self.themes and 'language' in self.themes[self.current_theme]:
            return self.themes[self.current_theme]['language']

        return None

    def get_current_language(self):
        """Возвращает текущий язык интерфейса."""
        return self.get_theme_language()

    def switch_language(self, language_code):
        """
        Переключает только язык, сохраняя текущую визуальную тему.

        Args:
            language_code (str): Код языка ('en', 'ru', и т.д.)

        Returns:
            bool: True, если язык успешно изменен, иначе False
        """
        # Защита от рекурсивных вызовов
        if hasattr(self, '_is_switching_language') and self._is_switching_language:
            print(f"Предотвращен рекурсивный вызов switch_language({language_code})")
            return False

        self._is_switching_language = True

        try:
            # Получаем тип текущей темы
            theme_type = self.get_theme_type()
            if not theme_type:
                print("Не удалось определить тип текущей темы")
                return False

            # Формируем имя новой темы
            new_theme = f"{theme_type}_{language_code}"

            # Проверяем, доступна ли такая тема
            if new_theme not in self.themes:
                print(f"Тема {new_theme} не найдена")
                return False

            # Переключаем на новую тему
            success = self.switch_theme(new_theme)

            # Переключаем язык в менеджере переводов
            JsonTranslationManager.instance().switch_language(language_code)

            # Уведомляем о смене языка
            self.languageChanged.emit(language_code)

            return success

        finally:
            # Снимаем флаг в любом случае
            self._is_switching_language = False

    def _on_color_palette_changed(self, theme_type):
        """Обработчик изменения цветовой палитры."""
        # Применяем обновленную тему
        self.apply_theme()

    def get_translation(self, key, default_text=None):
        """
        Получает перевод для указанного ключа.

        Args:
            key (str): Ключ перевода
            default_text (str, optional): Текст по умолчанию, если перевод не найден

        Returns:
            str: Перевод или текст по умолчанию
        """
        # Перенаправляем в JsonTranslationManager для централизованного управления переводами
        return JsonTranslationManager.instance().get_translation(key, default_text)

    def get_theme_display_name(self, theme_name=None):
        """
        Возвращает отображаемое имя темы.

        Args:
            theme_name (str, optional): Имя темы. Если не указано, используется текущая тема.

        Returns:
            str: Отображаемое имя темы
        """
        theme = theme_name or self.current_theme

        if not theme:
            return "Unknown Theme"

        # Разбираем имя темы
        parts = theme.split('_')

        if len(parts) >= 2:
            theme_type = parts[0]
            language_code = parts[1]

            # Формируем отображаемое имя
            if theme_type == 'dark':
                type_name = "Dark Theme"
                if language_code == 'ru':
                    type_name = "Темная тема"
            elif theme_type == 'light':
                type_name = "Light Theme"
                if language_code == 'ru':
                    type_name = "Светлая тема"
            else:
                type_name = theme_type.capitalize()

            # Добавляем название языка
            if language_code == 'en':
                language_name = "English"
                if theme_type == 'dark':
                    return f"{type_name} ({language_name})"
                return f"{type_name} - {language_name}"
            elif language_code == 'ru':
                language_name = "Русский"
                if theme_type == 'dark':
                    return f"{type_name} ({language_name})"
                return f"{type_name} - {language_name}"
            else:
                return f"{type_name} - {language_code.upper()}"

        # Если не удалось разобрать имя, возвращаем как есть
        return theme.replace('_', ' ').title()

    def apply_theme(self):
        """
        Применяет текущую тему к приложению.
        Загружает QSS стили и применяет их к приложению.
        """
        try:
            # Получаем путь к QSS файлу
            qss_path = self.get_theme_qss_path()
            if not qss_path or not os.path.exists(qss_path):
                print(f"QSS файл не найден: {qss_path}")
                return False

            # Загружаем стиль
            with open(qss_path, 'r', encoding='utf-8') as f:
                qss_content = f.read()

            # Если доступна система цветов, применяем переменные цветов
            if self.has_color_system and self.color_system:
                # Генерируем CSS переменные
                css_vars = self.color_system.generate_css_variables()

                # Добавляем переменные в начало QSS
                qss_content = css_vars + "\n" + qss_content

            # Применяем стиль к приложению
            QApplication.instance().setStyleSheet(qss_content)
            print(f"Применена тема: {self.current_theme} (QSS: {qss_path})")
            return True

        except Exception as e:
            print(f"Ошибка при применении темы: {e}")
            return False

    def get_available_visual_themes(self):
        """
        Возвращает список доступных визуальных тем (без учета языка).

        Returns:
            list: Список уникальных визуальных тем (dark, light, и т.д.)
        """
        visual_themes = set()

        for theme_name in self.themes:
            # Извлекаем тип темы
            if '_' in theme_name:
                theme_type = theme_name.split('_')[0]
                visual_themes.add(theme_type)
            elif 'type' in self.themes[theme_name]:
                theme_type = self.themes[theme_name]['type']
                visual_themes.add(theme_type)

        return list(visual_themes)

    def get_color(self, name, theme_type=None):
        """
        Получает цвет по имени из системы цветов.

        Args:
            name (str): Имя цвета
            theme_type (str, optional): Тип темы. Если не указан, используется текущая тема.

        Returns:
            str: Цвет в формате HEX или None, если система цветов недоступна
        """
        if not self.has_color_system or not self.color_system:
            return None

        if not theme_type:
            theme_type = self.get_theme_type()

        return self.color_system.get_color(name, theme_type)

    def get_qcolor(self, name, theme_type=None):
        """
        Получает цвет в формате QColor из системы цветов.

        Args:
            name (str): Имя цвета
            theme_type (str, optional): Тип темы. Если не указан, используется текущая тема.

        Returns:
            QColor: Цвет в формате QColor или None, если система цветов недоступна
        """
        if not self.has_color_system or not self.color_system:
            return None

        if not theme_type:
            theme_type = self.get_theme_type()

        return self.color_system.get_qcolor(name, theme_type)


# Создаем глобальный экземпляр менеджера тем
theme_manager = ThemeManager()
