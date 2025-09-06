#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Менеджер тем для GopiaI UI
Обеспечивает интерфейс для работы с темами приложения.
Предоставляет методы для применения выбранной темы, получения текущей темы
и получения списка доступных тем.
Интегрируется с simple_theme_manager.py для работы с предопределенными темами.
"""

import os
import json
import logging
from typing import Dict, Optional, Union

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QCoreApplication, QTimer

# Импорт из простого менеджера тем - используем абсолютный импорт
import gopiai.ui.utils.simple_theme_manager as stm

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к файлу настроек
SETTINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "settings")
THEME_FILE = os.path.join(SETTINGS_DIR, "simple_theme.json")


class ThemeManager(QObject):
    """
    Класс для управления темами пользовательского интерфейса GopiaI.
    Предоставляет методы для применения тем, получения текущей темы и списка доступных тем.
    Интегрируется с simple_theme_manager.py.
    """

    themeChanged = Signal(str)  # Сигнал об изменении темы

    def __init__(self):
        """Инициализация менеджера тем"""
        super().__init__()
        self._current_theme = None
        self._current_variant = "light"
        self._theme_applied = False  # Флаг успешного применения темы

        # Инициализация текущей темы из файла настроек
        self._init_theme()

    def _init_theme(self):
        """Инициализация темы из файла настроек"""
        try:
            theme_data = stm.load_theme()
            if theme_data:
                if "name" in theme_data:
                    self._current_theme = theme_data["name"]
                if "variant" in theme_data:
                    self._current_variant = theme_data["variant"]

            # Применяем загруженную тему к приложению
            app = QApplication.instance()
            if app:
                # Используем QTimer для отложенного применения темы
                # чтобы убедиться, что все виджеты инициализированы
                QTimer.singleShot(100, lambda: self._apply_loaded_theme(app))

            logger.info(f"Загружена тема: {self._current_theme} ({self._current_variant})")
        except Exception as e:
            logger.error(f"Ошибка при инициализации темы: {e}", exc_info=True)

    def _apply_loaded_theme(self, app):
        """Применяет загруженную тему с проверками"""
        try:
            result = stm.apply_theme(app)
            if result:
                self._theme_applied = True
                logger.info("Тема успешно применена при инициализации")
            else:
                logger.warning("Тема загружена, но не применена полностью - возможно отображение fallback темы")
                self._theme_applied = False
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e: # Добавлены более специфичные исключения
            logger.error(f"Ошибка при применении загруженной темы: {e}", exc_info=True)
            self._theme_applied = False

    def apply_theme(self, theme_input: Union[str, QCoreApplication]) -> bool:
        """
        Применяет выбранную тему.

        Args:
            theme_input: Может быть строкой с именем темы или экземпляром QApplication/QCoreApplication

        Returns:
            bool: True, если тема успешно применена, иначе False
        """
        try:
            # Проверяем состояние приложения
            app = QApplication.instance()
            if not app:
                logger.error("QApplication не инициализировано")
                return False

            # Если передано имя темы в виде строки
            if isinstance(theme_input, str):
                theme_name = theme_input
                logger.info(f"Запрос на применение темы: {theme_name}")

                # Обработка специального случая "simple" - используем диалог выбора темы
                if theme_name.lower() == "simple":
                    return self._handle_simple_theme_selection(app)

                # Поиск темы в коллекции
                return self._apply_theme_by_name(theme_name, app)

            # Если передан экземпляр QApplication/QCoreApplication
            elif isinstance(theme_input, QCoreApplication):
                logger.info("Применение темы к QApplication/QCoreApplication")
                result = stm.apply_theme(theme_input)
                if result:
                    self._theme_applied = True
                    return result
            else:
                logger.error(f"Неподдерживаемый тип параметра: {type(theme_input)}")
                return False
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e: # Добавлены более специфичные исключения
            logger.error(f"Ошибка при применении темы: {e}", exc_info=True)
            return False

        return False

    def _handle_simple_theme_selection(self, app) -> bool:
        """Обрабатывает выбор темы через диалог"""
        try:
            theme_data = stm.choose_theme_dialog(app)
            if theme_data:
                self._current_theme = theme_data.get("name")
                self._current_variant = theme_data.get("variant", "light")

                # Сохраняем выбранную тему
                if self._save_theme_data(theme_data):
                    # Применяем тему
                    result = stm.apply_theme(app)
                    if result:
                        self._theme_applied = True
                        self.themeChanged.emit(self._current_theme)
                        return True
                    else:
                        logger.error("Не удалось применить выбранную тему")
                        self._theme_applied = False
                        return False
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора темы: {e}", exc_info=True)

        return False

    def _apply_theme_by_name(self, theme_name: str, app) -> bool:
        """Применяет тему по имени"""
        found = False
        for theme in stm.THEME_COLLECTION:
            if theme["name"].lower() == theme_name.lower():
                variant = self._current_variant  # Сохраняем текущий вариант (light/dark)
                if variant in theme:
                    theme_data = theme[variant].copy()
                    theme_data["name"] = theme["name"]
                    theme_data["variant"] = variant

                    # Сохраняем тему
                    if self._save_theme_data(theme_data):
                        # Обновляем текущую тему
                        self._current_theme = theme["name"]

                        # Применяем тему к приложению
                        result = stm.apply_theme(app)
                        if result:
                            self._theme_applied = True
                            self.themeChanged.emit(self._current_theme)
                            return True
                        else:
                            logger.error("Не удалось применить тему полностью")
                            self._theme_applied = False
                            return False
                    else:
                        logger.error("Не удалось сохранить данные темы")
                        return False
                else:
                    logger.warning(f"Вариант {variant} не найден для темы {theme_name}")
                    found = True
                    break

        if not found:
            logger.warning(f"Тема не найдена: {theme_name}")

        return False

    def _save_theme_data(self, theme_data: dict) -> bool:
        """Сохраняет данные темы в файл"""
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении темы: {e}", exc_info=True)

        return False

    def get_current_theme(self) -> Optional[str]:
        """
        Возвращает имя текущей темы.

        Returns:
            Optional[str]: Имя текущей темы или None, если тема не установлена
        """
        return self._current_theme

    def get_theme_display_names(self) -> Dict[str, str]:
        """
        Возвращает словарь с именами тем для отображения в интерфейсе.

        Returns:
            Dict[str, str]: Словарь вида {ключ_темы: отображаемое_имя}
        """
        theme_names = {}
        for theme in stm.THEME_COLLECTION:
            # Используем имя темы и как ключ, и как отображаемое имя
            theme_names[theme["name"]] = theme["name"]

        return theme_names

    def get_current_theme_data(self) -> Optional[dict]:
        """
        Возвращает данные текущей темы.

        Returns:
            Optional[dict]: Словарь с данными текущей темы или None, если тема не загружена
        """
        try:
            # Загружаем данные текущей темы из файла настроек
            theme_data = stm.load_theme()

            # Если данные загружены успешно, возвращаем их
            if theme_data:
                return theme_data

            # Если текущая тема установлена, но данные не загружены,
            # пытаемся найти тему в коллекции
            if self._current_theme:
                variant = self._current_variant or "light"
                for theme in stm.THEME_COLLECTION:
                    if theme["name"] == self._current_theme and variant in theme:
                        theme_data = theme[variant].copy()
                        theme_data["name"] = theme["name"]
                        theme_data["variant"] = variant
                        return theme_data
        except Exception as e:
            logger.error(f"Ошибка при получении данных текущей темы: {e}", exc_info=True)

        return None

    def show_theme_dialog(self) -> bool:
        """
        Показывает диалог выбора темы.

        Returns:
            bool: True, если тема была выбрана и применена, иначе False
        """
        try:
            app = QApplication.instance()
            if app:
                theme_data = stm.choose_theme_dialog(app)
                if theme_data:
                    self._current_theme = theme_data.get("name")
                    self._current_variant = theme_data.get("variant", "light")

                    # Сохраняем и применяем тему
                    if self._save_theme_data(theme_data):
                        result = stm.apply_theme(app)
                        if result:
                            self._theme_applied = True
                            self.themeChanged.emit(self._current_theme)
                            return True
                        else:
                            logger.error("Не удалось применить выбранную тему")
                            self._theme_applied = False
        except Exception as e:
            logger.error(f"Ошибка при показе диалога выбора темы: {e}", exc_info=True)

        return False

    def reapply_current_theme(self) -> bool:
        """
        Переприменяет текущую тему.

        Returns:
            bool: True, если тема успешно переприменена, иначе False
        """
        if self._current_theme:
            logger.info(f"Переприменение текущей темы: {self._current_theme}")
            return self.apply_theme(self._current_theme)
        else:
            logger.warning("Нет текущей темы для переприменения")

        return False

    def is_theme_applied(self) -> bool:
        """
        Проверяет, была ли тема успешно применена.

        Returns:
            bool: True, если тема применена успешно
        """
        return self._theme_applied

    def reset_theme(self) -> bool:
        """
        Сбрасывает тему к состоянию по умолчанию.

        Returns:
            bool: True, если сброс выполнен успешно
        """
        try:
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                # Очищаем стили
                app.setStyleSheet("")

                # Сбрасываем внутреннее состояние
                self._current_theme = None
                self._current_variant = "light"
                self._theme_applied = False

                # Удаляем файл настроек темы
                if os.path.exists(THEME_FILE):
                    os.remove(THEME_FILE)

                logger.info("Тема сброшена к состоянию по умолчанию")
                self.themeChanged.emit("")

                return True
            else:
                logger.warning("QApplication не инициализирован или неверного типа")
        except Exception as e:
            logger.error(f"Ошибка при сбросе темы: {e}", exc_info=True)

        return False