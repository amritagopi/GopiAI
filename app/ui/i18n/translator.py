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

    def load_translations(self):
        """Загружает все доступные переводы из JSON файлов"""
        self.translations = {}

        # Загружаем английский (базовый)
        en_path = os.path.join(self.translations_dir, "en.json")
        if os.path.exists(en_path):
            with open(en_path, 'r', encoding='utf-8') as f:
                self.translations["en_US"] = json.load(f)

        # Загружаем русский
        ru_path = os.path.join(self.translations_dir, "ru.json")
        if os.path.exists(ru_path):
            with open(ru_path, 'r', encoding='utf-8') as f:
                self.translations["ru_RU"] = json.load(f)

    def get_available_languages(self):
        """Получает список доступных языков"""
        return list(self.translations.keys())

    def get_language_name(self, language_code):
        """Преобразует код языка в читаемое название"""
        language_names = {
            "en_US": "English",
            "ru_RU": "Русский"
        }
        return language_names.get(language_code, language_code)

    def switch_language(self, language_code):
        """Переключает язык приложения"""
        if language_code in self.translations:
            self.current_language = language_code
            self.languageChanged.emit(language_code)
            return True
        return False

    def get_current_language(self):
        """Возвращает текущий язык"""
        return self.current_language

    def get_translation(self, key_path, default=""):
        """Получает перевод по ключу (поддерживает вложенные ключи через точку)"""
        if not key_path:
            return default

        # Получаем текущий словарь переводов
        trans_dict = self.translations.get(self.current_language, {})
        if not trans_dict:
            return default

        # Для вложенных ключей (например, 'menu.file')
        parts = key_path.split('.')
        result = trans_dict

        for part in parts:
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                return default

        if not isinstance(result, str):
            return default

        return result

# Создаем глобальный экземпляр менеджера переводов
translation_manager = JsonTranslationManager()

def tr(key, default=""):
    """Функция для получения перевода по ключу"""
    return translation_manager.get_translation(key, default)
