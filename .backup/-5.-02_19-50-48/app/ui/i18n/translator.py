import os
import json
from PySide6.QtCore import QObject, Signal, QSettings
from app.logger import logger

# Константа для имени приложения
APP_NAME = "GopiAI"

class JsonTranslationManager(QObject):
    # Сигнал для оповещения о смене языка
    languageChanged = Signal(str)

    _instance = None

    @classmethod
    def instance(cls):
        """Получение единственного экземпляра менеджера переводов (паттерн Singleton)."""
        if cls._instance is None:
            cls._instance = JsonTranslationManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.current_language = "en_US"
        # Переводы хранятся в директории themes
        self.translations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "themes")
        self.translations = {}

        # Загружаем настройки языка
        self._load_language_settings()

        # Загружаем все доступные переводы
        self.load_translations()

    def _load_language_settings(self):
        """Загружает настройки языка из QSettings."""
        settings = QSettings(APP_NAME, "UI")
        saved_language = settings.value("language", "en_US")
        if saved_language in ["en_US", "ru_RU"]:
            self.current_language = saved_language
            logger.info(f"Загружены настройки языка: {self.current_language}")
        else:
            logger.warning(f"Неизвестный язык: {saved_language}, используем язык по умолчанию: en_US")

    def _save_language_settings(self):
        """Сохраняет настройки языка в QSettings."""
        settings = QSettings(APP_NAME, "UI")
        settings.setValue("language", self.current_language)
        settings.sync()
        logger.info(f"Сохранены настройки языка: {self.current_language}")

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

        # Сначала проверим наличие новых файлов переводов в директории i18n
        i18n_dir = os.path.dirname(os.path.abspath(__file__))
        en_path_i18n = os.path.join(i18n_dir, "en.json")
        ru_path_i18n = os.path.join(i18n_dir, "ru.json")

        # Затем проверим наличие основных файлов в директории themes
        en_path_themes = os.path.join(self.translations_dir, "EN-translations.json")
        ru_path_themes = os.path.join(self.translations_dir, "RU-translations.json")

        # Загружаем английский (базовый)
        if os.path.exists(en_path_themes):
            try:
                with open(en_path_themes, 'r', encoding='utf-8') as f:
                    self.translations["en_US"] = json.load(f)
                    logger.info(f"Загружены английские переводы (themes): {len(self.translations['en_US'])} записей")
            except Exception as e:
                logger.error(f"Ошибка при загрузке английских переводов (themes): {str(e)}")
                if os.path.exists(en_path_i18n):
                    self._load_fallback_translations("en_US", en_path_i18n)
        elif os.path.exists(en_path_i18n):
            self._load_fallback_translations("en_US", en_path_i18n)
        else:
            logger.warning(f"Файлы английских переводов не найдены")
            # Создаем пустой словарь переводов, если файл не найден
            self.translations["en_US"] = {}

        # Загружаем русский
        if os.path.exists(ru_path_themes):
            try:
                with open(ru_path_themes, 'r', encoding='utf-8') as f:
                    self.translations["ru_RU"] = json.load(f)
                    logger.info(f"Загружены русские переводы (themes): {len(self.translations['ru_RU'])} записей")
            except Exception as e:
                logger.error(f"Ошибка при загрузке русских переводов (themes): {str(e)}")
                if os.path.exists(ru_path_i18n):
                    self._load_fallback_translations("ru_RU", ru_path_i18n)
        elif os.path.exists(ru_path_i18n):
            self._load_fallback_translations("ru_RU", ru_path_i18n)
        else:
            logger.warning(f"Файлы русских переводов не найдены")
            # Создаем пустой словарь переводов, если файл не найден
            self.translations["ru_RU"] = {}

        logger.info(f"Доступные языки после загрузки: {self.get_available_languages()}")

    def _load_fallback_translations(self, language_code, file_path):
        """Загружает переводы из указанного файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations[language_code] = json.load(f)
                logger.info(f"Загружены переводы из файла ({language_code}): {file_path}, "
                            f"{len(self.translations[language_code])} записей")
        except Exception as e:
            logger.error(f"Ошибка при загрузке переводов из файла ({language_code}): {str(e)}")
            # Создаем пустой словарь переводов, если не удалось загрузить
            self.translations[language_code] = {}

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
    ############################################################################
    def switch_language(self, language_code):
        """Переключает язык приложения"""
        logger.info(f"Попытка переключения языка на: {language_code}")

        if language_code in self.translations:
            if language_code == self.current_language:
                logger.info(f"Язык {language_code} уже установлен")
                return True

            self.current_language = language_code
            # Сохраняем выбранный язык
            self._save_language_settings()
            # Уведомляем подписчиков об изменении языка
            self.languageChanged.emit(language_code)
            logger.info(f"Успешно переключено на {language_code}")
            return True
        else:
            logger.error(f"Не удалось переключить язык: {language_code} отсутствует в доступных переводах")
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
            logger.warning(f"Нет доступных переводов для {self.current_language}")
            return default

        # Для вложенных ключей (например, 'menu.file')
        parts = key_path.split('.')
        result = trans_dict

        for i, part in enumerate(parts):
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                # Если перевод не найден в текущем языке, пробуем найти в английском
                if self.current_language != "en_US" and "en_US" in self.translations:
                    en_result = self.translations["en_US"]
                    found = True
                    for en_part in parts[:i+1]:
                        if isinstance(en_result, dict) and en_part in en_result:
                            en_result = en_result[en_part]
                        else:
                            found = False
                            break

                    if found and isinstance(en_result, str):
                        return en_result

                # Отладка отсутствующих ключей
                if self.current_language != "en_US":
                    logger.debug(f"Отсутствует перевод для ключа '{key_path}' в {self.current_language}")
                return default

        # Проверяем, что результат является строкой
        if isinstance(result, str):
            return result

        # Если результат не строка, возвращаем дефолтное значение или преобразуем к строке
        if isinstance(result, dict):
            logger.warning(f"Перевод для '{key_path}' не является строкой, а словарем")
            # Пытаемся вернуть первый элемент словаря, если это строка
            for key, value in result.items():
                if isinstance(value, str):
                    return value
            return default

        if result is None:
            return default

        # Преобразуем числа и булевы значения к строке
        if isinstance(result, (int, float, bool)):
            return str(result)

        logger.warning(f"Перевод для '{key_path}' не является строкой: {result}")
        return default

# Используем паттерн Singleton для получения экземпляра менеджера переводов
# Важно: Не создавать другие экземпляры, всегда использовать JsonTranslationManager.instance()

def tr(key, default=""):
    """Функция для получения перевода по ключу"""
    return JsonTranslationManager.instance().get_translation(key, default)
