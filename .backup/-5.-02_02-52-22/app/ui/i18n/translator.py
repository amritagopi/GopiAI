import os
import json
from PySide6.QtCore import QObject, Signal

class JsonTranslationManager(QObject):
    # Сигнал для оповещения о смене языка
    languageChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_language = "en_US"
        self.translations_dir = os.path.dirname(os.path.abspath(__file__))
        self.translations = {}
        self.load_translations()

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за загрузку файлов переводов и подготовку их к использованию
    # Изменение логики может привести к поломке UI и нарушению работы локализации
    # Особенно важна кодировка файлов и обработка отсутствующих переводов
    # Тесно связан с методами switch_language и get_translation
    ############################################################################
    def load_translations(self):
        """Загружает все доступные переводы из JSON файлов"""
        self.translations = {}

        # Загружаем английский (базовый)
        en_path = os.path.join(self.translations_dir, "en.json")
        if os.path.exists(en_path):
            with open(en_path, 'r', encoding='utf-8') as f:
                self.translations["en_US"] = json.load(f)
                print(f"Loaded English translations: {len(self.translations['en_US'])} entries")
        else:
            print(f"Warning: English translation file not found at {en_path}")

        # Загружаем русский
        ru_path = os.path.join(self.translations_dir, "ru.json")
        if os.path.exists(ru_path):
            with open(ru_path, 'r', encoding='utf-8') as f:
                self.translations["ru_RU"] = json.load(f)
                print(f"Loaded Russian translations: {len(self.translations['ru_RU'])} entries")
        else:
            print(f"Warning: Russian translation file not found at {ru_path}")

        print(f"Available languages after loading: {self.get_available_languages()}")

    def get_available_languages(self):
        """Получает список доступных языков"""
        languages = list(self.translations.keys())
        return languages

    def get_language_name(self, language_code):
        """Преобразует код языка в читаемое название"""
        language_names = {
            "en_US": "English",
            "ru_RU": "Русский"
        }
        return language_names.get(language_code, language_code)

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за переключение языка и оповещение всех подписчиков
    # Изменение логики может привести к рассинхронизации UI и локализации
    # Сигнал languageChanged критичен для обновления всех виджетов
    # Тесно связан с ThemeManager.switch_language в theme_manager.py
    ############################################################################
    def switch_language(self, language_code):
        """Переключает язык приложения"""
        print(f"Attempting to switch language to: {language_code}")

        if language_code in self.translations:
            self.current_language = language_code
            self.languageChanged.emit(language_code)
            print(f"Successfully switched to {language_code}")
            return True
        else:
            print(f"Failed to switch language: {language_code} not in available translations")
            return False

    def get_current_language(self):
        """Возвращает текущий язык"""
        return self.current_language

    ############################################################################
    # !!! КРИТИЧЕСКИ ВАЖНО !!! НЕ ИЗМЕНЯТЬ ЭТОТ МЕТОД БЕЗ КРАЙНЕЙ НЕОБХОДИМОСТИ!
    # Метод отвечает за получение переводов по ключу с учетом иерархии
    # Изменение логики может привести к отсутствию переводов в интерфейсе
    # Обработка вложенных ключей и значений по умолчанию критически важна
    # Используется всеми компонентами UI для локализации
    ############################################################################
    def get_translation(self, key_path, default=""):
        """Получает перевод по ключу (поддерживает вложенные ключи через точку)"""
        if not key_path:
            return default

        # Получаем текущий словарь переводов
        trans_dict = self.translations.get(self.current_language, {})
        if not trans_dict:
            print(f"Warning: No translations available for {self.current_language}")
            return default

        # Для вложенных ключей (например, 'menu.file')
        parts = key_path.split('.')
        result = trans_dict

        for i, part in enumerate(parts):
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                # Отладка отсутствующих ключей - убираем детальный вывод
                if self.current_language != "en_US":  # Не выводим для английского (базового) языка
                    print(f"Missing translation for key '{key_path}' in {self.current_language}")
                return default

        if not isinstance(result, str):
            print(f"Warning: Translation for '{key_path}' is not a string: {result}")
            return default

        return result

# Создаем глобальный экземпляр менеджера переводов
translation_manager = JsonTranslationManager()

def tr(key, default=""):
    """Функция для получения перевода по ключу"""
    return translation_manager.get_translation(key, default)
