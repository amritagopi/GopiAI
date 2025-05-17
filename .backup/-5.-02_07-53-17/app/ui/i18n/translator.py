import os
import json
from PySide6.QtCore import QObject, Signal, QSettings
from app.logger import logger
from PySide6.QtWidgets import QApplication

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
        # Переводы хранятся в директории i18n
        self.translations_dir = os.path.dirname(os.path.abspath(__file__))
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

        # Проверяем наличие файлов переводов в директории i18n
        i18n_dir = self.translations_dir
        logger.info(f"Загрузка переводов из директории: {i18n_dir}")

        en_path = os.path.join(i18n_dir, "en.json")
        ru_path = os.path.join(i18n_dir, "ru.json")

        # Инициализируем словари переводов
        self.translations["en_US"] = {}
        self.translations["ru_RU"] = {}

        # Загружаем английские переводы
        if os.path.exists(en_path):
            try:
                with open(en_path, 'r', encoding='utf-8') as f:
                    en_translations = json.load(f)
                    self.translations["en_US"].update(en_translations)
                    logger.info(f"Загружены английские переводы из {en_path}: {len(en_translations)} записей")
            except Exception as e:
                logger.error(f"Ошибка при загрузке английских переводов из {en_path}: {str(e)}")
        else:
            logger.error(f"Файл английских переводов не найден: {en_path}")

        # Загружаем русские переводы
        if os.path.exists(ru_path):
            try:
                with open(ru_path, 'r', encoding='utf-8') as f:
                    ru_translations = json.load(f)
                    self.translations["ru_RU"].update(ru_translations)
                    logger.info(f"Загружены русские переводы из {ru_path}: {len(ru_translations)} записей")
            except Exception as e:
                logger.error(f"Ошибка при загрузке русских переводов из {ru_path}: {str(e)}")
        else:
            logger.error(f"Файл русских переводов не найден: {ru_path}")

        # Проверка, заполнены ли словари переводов
        if not self.translations["en_US"]:
            logger.warning("Английские переводы не найдены или пусты")
            self.translations["en_US"] = {}

        if not self.translations["ru_RU"]:
            logger.warning("Русские переводы не найдены или пусты")
            self.translations["ru_RU"] = {}

        logger.info(f"Доступные языки после загрузки: {self.get_available_languages()}")
        logger.info(f"Общее количество английских переводов: {len(self.translations['en_US'])}")
        logger.info(f"Общее количество русских переводов: {len(self.translations['ru_RU'])}")

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
        logger.info(f"Попытка переключения языка на {language_code}")
        logger.info(f"Текущий язык перед переключением: {self.current_language}")

        # Проверяем, доступен ли файл перевода для указанного языка
        if language_code in self.translations:
            # Если текущий язык совпадает с запрашиваемым, пропускаем переключение
            if language_code == self.current_language:
                logger.info(f"Язык {language_code} уже установлен, переключение не требуется")
                return

            # Если текущий язык отличается, переключаем
            logger.info(f"Переключение языка с {self.current_language} на {language_code}")

            try:
                # Смена текущего языка
                self.current_language = language_code

                # Сохраняем в настройках пользователя выбранный язык
                self._save_language_settings()

                # Подробное логирование
                logger.debug(f"Настройки обновлены: текущий язык = {language_code}")
                logger.debug(f"Сохраненный язык в настройках = {self.current_language}")

                # Эмиссия сигнала для оповещения подписчиков об изменении языка
                # ВАЖНО: именно после этого должны обновляться все виджеты с переводами
                self.languageChanged.emit(language_code)

                # Дополнительное логирование после эмиссии сигнала
                logger.info(f"Сигнал languageChanged({language_code}) испущен")
                return True
            except Exception as e:
                logger.error(f"Ошибка при переключении языка на {language_code}: {e}")
                return False
        else:
            # Если язык не поддерживается, логируем ошибку
            logger.error(f"Язык {language_code} не найден в доступных переводах: {list(self.translations.keys())}")
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
                # Перевод не найден в текущем языке
                # Пробуем найти в английском словаре (если текущий язык не английский)
                if self.current_language != "en_US" and "en_US" in self.translations:
                    en_result = self.translations["en_US"]
                    found = True
                    for en_part in parts[:i+1]:
                        if isinstance(en_result, dict) and en_part in en_result:
                            en_result = en_result[en_part]
                        else:
                            found = False
                            break

                    if found and isinstance(en_result, str) and "TODO:" not in en_result:
                        logger.debug(f"Используем английский перевод для '{key_path}' вместо отсутствующего в {self.current_language}")
                        return en_result

                # Если перевод не найден нигде или это последняя часть ключа
                if i == len(parts) - 1:
                    logger.debug(f"Отсутствует перевод для ключа '{key_path}' в {self.current_language}")
                    return default
                else:
                    # Если это промежуточная часть ключа, возвращаем default
                    logger.debug(f"Отсутствует часть '{part}' для ключа '{key_path}' в {self.current_language}")
                    return default

        # Проверяем, что результат является строкой
        if isinstance(result, str):
            # Если найден перевод с пометкой TODO, используем default или английский перевод
            if "TODO:" in result:
                logger.debug(f"Найден незавершенный перевод для '{key_path}': {result}")

                # Пытаемся найти перевод на английском
                if self.current_language != "en_US" and "en_US" in self.translations:
                    en_result = self.translations["en_US"]
                    found = True
                    for en_part in parts:
                        if isinstance(en_result, dict) and en_part in en_result:
                            en_result = en_result[en_part]
                        else:
                            found = False
                            break

                    if found and isinstance(en_result, str) and "TODO:" not in en_result:
                        logger.debug(f"Используем английский перевод вместо TODO для '{key_path}'")
                        return en_result

                # Если английского перевода нет или он тоже с TODO, используем default
                return default

            # Возвращаем найденный перевод
            return result

        # Если результат не строка, проверяем специальные случаи
        if result is None:
            logger.debug(f"Результат поиска перевода для '{key_path}' равен None")
            return default

        if isinstance(result, dict):
            logger.warning(f"Перевод для '{key_path}' не является строкой, а словарем")
            # Только для отладки - пытаемся вернуть первый элемент словаря
            for key, value in result.items():
                if isinstance(value, str):
                    logger.debug(f"Возвращаем первый элемент из словаря для '{key_path}': {value}")
                    return value
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

def check_translator():
    """
    Проверяет состояние переводчика и возвращает информацию о нем в виде строки.
    Используется для диагностики UI.
    """
    try:
        translator = JsonTranslationManager.instance()

        # Получаем информацию о текущем языке
        current_lang = translator.get_current_language()

        # Получаем доступные языки
        available_langs = translator.get_available_languages()

        # Проверяем наличие основных файлов переводов
        i18n_dir = os.path.dirname(os.path.abspath(__file__))
        en_path = os.path.join(i18n_dir, "en.json")
        ru_path = os.path.join(i18n_dir, "ru.json")

        files_status = []
        if os.path.exists(en_path):
            files_status.append(f"✓ Английский файл локализации существует: {en_path}")
        else:
            files_status.append(f"⚠️ Английский файл локализации не найден: {en_path}")

        if os.path.exists(ru_path):
            files_status.append(f"✓ Русский файл локализации существует: {ru_path}")
        else:
            files_status.append(f"⚠️ Русский файл локализации не найден: {ru_path}")

        # Проверяем несколько ключей для текущего языка
        test_keys = ["menu.file", "menu.edit", "menu.view", "menu.help"]
        translations_check = []

        for key in test_keys:
            translation = translator.get_translation(key)
            if translation and translation != key:
                translations_check.append(f"✓ Ключ '{key}' имеет перевод: '{translation}'")
            else:
                translations_check.append(f"⚠️ Ключ '{key}' не переведен или отсутствует")

        # Формируем строку с результатами
        result = f"Текущий язык: {current_lang} ({translator.get_language_name(current_lang)})\n"
        result += f"Доступные языки: {', '.join(available_langs)}\n\n"
        result += "Файлы локализации:\n"
        result += "\n".join(files_status) + "\n\n"
        result += "Проверка ключей:\n"
        result += "\n".join(translations_check)

        return result
    except Exception as e:
        return f"Ошибка при проверке переводчика: {str(e)}"

def connect_language_actions(main_window):
    """
    Подключает действия меню для переключения языка.
    Используется при исправлении сигналов в диагностике UI.

    Args:
        main_window: Основное окно приложения

    Returns:
        str: Строка с результатами подключения
    """
    try:
        # Проверяем наличие меню и действий
        if not hasattr(main_window, "menu_manager"):
            return "⚠️ Менеджер меню отсутствует в главном окне"

        menu_manager = main_window.menu_manager
        if not hasattr(menu_manager, "language_menu"):
            return "⚠️ Меню языка отсутствует в менеджере меню"

        # Получаем переводчик
        translator = JsonTranslationManager.instance()

        # Проверяем наличие действий для переключения языка
        language_menu = menu_manager.language_menu
        english_action = None
        russian_action = None

        # Ищем действия по имени
        for action in language_menu.actions():
            if action.text() == tr("language.english", "English"):
                english_action = action
            elif action.text() == tr("language.russian", "Russian"):
                russian_action = action

        if not english_action or not russian_action:
            return "⚠️ Не найдены действия для переключения языка"

        # Отключаем существующие подключения
        try:
            english_action.triggered.disconnect()
            russian_action.triggered.disconnect()
        except:
            pass  # Если нет подключений, просто продолжаем

        # Подключаем сигналы к переводчику
        english_action.triggered.connect(lambda: translator.switch_language("en_US"))
        russian_action.triggered.connect(lambda: translator.switch_language("ru_RU"))

        # Отключаем все существующие подключения сигнала languageChanged
        try:
            # Временно сохраняем количество подключений
            receivers_count = translator.languageChanged.receivers()

            # Отключаем все существующие соединения
            translator.languageChanged.disconnect()
            logger.info(f"Отключены все ({receivers_count}) подключения к сигналу languageChanged")
        except Exception as e:
            logger.debug(f"Нет активных подключений к сигналу languageChanged: {e}")

        # Создаем единственное подключение к методу _on_language_changed_event
        if hasattr(main_window, '_on_language_changed_event'):
            translator.languageChanged.connect(main_window._on_language_changed_event)
            logger.info(f"Создано единственное подключение languageChanged к _on_language_changed_event")
        else:
            logger.error("Метод _on_language_changed_event не найден в главном окне")
            return "⚠️ Метод _on_language_changed_event не найден в главном окне"

        return f"✓ Успешно настроены сигналы для переключения языка.\n" + \
               f"   Текущий язык: {translator.get_current_language()}"
    except Exception as e:
        return f"⚠️ Ошибка при подключении сигналов: {str(e)}"
