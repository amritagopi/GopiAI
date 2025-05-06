"""
Browser Access Module для Reasoning Agent

Модуль предоставляет контролируемый доступ к браузеру для ReasoningAgent
с системой разрешений и безопасным выполнением браузерных действий.
"""

import asyncio
import json
from typing import Dict, List, Optional, Union, Tuple, Any, TypeVar

from app.logger import logger
from app.tool.browser_use_tool import BrowserUseTool

Context = TypeVar("Context")


class BrowserAccess:
    """
    Класс для безопасного доступа к браузеру в режиме reasoning.

    Предоставляет:
    1. Проверку безопасности браузерных действий перед выполнением
    2. Логирование всех выполняемых действий
    3. Ограничение опасных операций
    4. Возможность настройки параметров браузера
    """

    # Список потенциально опасных URL паттернов
    UNSAFE_URL_PATTERNS = [
        "file://",  # Локальные файлы
        "chrome://",  # Внутренние страницы Chrome
        "about:",  # Внутренние страницы браузера
        "data:",  # Data URLs (могут содержать JavaScript)
        "javascript:",  # JavaScript URLs
        "view-source:",  # Просмотр исходного кода
        "ftp://",  # FTP протокол (устаревший и потенциально небезопасный)
    ]

    # Список потенциально опасных действий
    UNSAFE_ACTIONS = [
        "execute_script",  # Произвольное выполнение JavaScript
        "raw_input",       # Прямой ввод без фильтрации
        "file_upload"      # Загрузка файлов
    ]

    def __init__(
        self,
        max_tabs: int = 5,
        safe_mode: bool = True,
        headless: bool = False,
        disable_security: bool = False,
    ):
        """
        Инициализирует объект доступа к браузеру.

        Args:
            max_tabs: Максимальное количество открытых вкладок
            safe_mode: Включение проверок безопасности
            headless: Запуск браузера в режиме без интерфейса
            disable_security: Отключение защиты браузера (не рекомендуется)
        """
        self.max_tabs = max_tabs
        self.safe_mode = safe_mode
        self.headless = headless
        self.disable_security = disable_security
        self.action_history: List[Dict[str, Any]] = []

        # Инициализация браузерного инструмента будет происходить при первом вызове
        self.browser_tool: Optional[BrowserUseTool] = None
        self.browser_lock = asyncio.Lock()

        logger.info(f"Browser access initialized with safe_mode: {safe_mode}, headless: {headless}")

    def _is_url_safe(self, url: str) -> Tuple[bool, str]:
        """
        Проверяет безопасность URL для открытия.

        Args:
            url: URL для проверки

        Returns:
            Кортеж (безопасность, причина небезопасности)
        """
        if not self.safe_mode:
            return True, ""

        # Проверяем паттерны небезопасных URL
        for pattern in self.UNSAFE_URL_PATTERNS:
            if url.lower().startswith(pattern):
                return False, f"URL содержит потенциально опасный протокол: {pattern}"

        # Проверяем на дополнительные признаки подозрительных URL
        if "<script>" in url or "alert(" in url:
            return False, "URL содержит потенциально вредоносный JavaScript"

        return True, ""

    def _is_action_safe(
        self, action: str, **params
    ) -> Tuple[bool, str]:
        """
        Проверяет безопасность браузерного действия.

        Args:
            action: Тип действия
            **params: Параметры действия

        Returns:
            Кортеж (безопасность, причина небезопасности)
        """
        if not self.safe_mode:
            return True, ""

        # Проверяем тип действия
        if action in self.UNSAFE_ACTIONS:
            return False, f"Действие '{action}' ограничено из соображений безопасности"

        # Проверяем URL для действий навигации
        if action in ["go_to_url", "open_tab"] and "url" in params:
            url_safe, reason = self._is_url_safe(params["url"])
            if not url_safe:
                return False, reason

        # Проверяем ввод текста на потенциально опасные паттерны
        if action == "input_text" and "text" in params:
            text = params["text"]
            if "<script>" in text or "javascript:" in text:
                return False, "Ввод содержит потенциально опасный JavaScript"

        return True, ""

    async def _ensure_browser_initialized(self) -> BrowserUseTool:
        """
        Инициализирует браузерный инструмент, если он еще не инициализирован.

        Returns:
            Инициализированный инструмент BrowserUseTool
        """
        if self.browser_tool is None:
            self.browser_tool = BrowserUseTool()
            # Дожидаемся инициализации браузера при первом вызове
            await self.browser_tool._ensure_browser_initialized()
            logger.info("Browser tool initialized successfully")
        return self.browser_tool

    async def execute_action(
        self,
        action: str,
        **action_params,
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет действие в браузере.

        Args:
            action: Тип действия (go_to_url, click_element и т.д.)
            **action_params: Параметры действия (url, index, text и т.д.)

        Returns:
            Словарь с результатами выполнения действия
        """
        async with self.browser_lock:
            # Проверяем безопасность действия
            is_safe, reason = self._is_action_safe(action, **action_params)
            if not is_safe:
                logger.warning(f"Unsafe browser action rejected: {action}. Reason: {reason}")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Action rejected due to safety concerns: {reason}",
                    "action": action,
                    "params": action_params,
                }

            # Создаем запись в истории
            action_record = {
                "action": action,
                "params": action_params,
                "timestamp": asyncio.get_event_loop().time()
            }
            self.action_history.append(action_record)

            # Логируем выполнение
            logger.info(f"Executing browser action: {action} with params: {action_params}")

            try:
                # Инициализируем браузерный инструмент
                browser_tool = await self._ensure_browser_initialized()

                # Выполняем действие в браузере
                result = await browser_tool.execute(action=action, **action_params)

                # Обновляем запись в истории
                action_record.update({
                    "success": not result.error,
                    "output": result.output,
                    "error": result.error
                })

                # Формируем результат
                return {
                    "success": not result.error,
                    "output": result.output,
                    "error": result.error,
                    "action": action,
                    "params": action_params
                }

            except Exception as e:
                logger.error(f"Error executing browser action: {str(e)}")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Error executing browser action: {str(e)}",
                    "action": action,
                    "params": action_params
                }

    async def get_current_state(self) -> Dict[str, Any]:
        """
        Получает текущее состояние браузера (URL, содержимое, доступные элементы).

        Returns:
            Словарь с информацией о текущем состоянии браузера
        """
        async with self.browser_lock:
            try:
                browser_tool = await self._ensure_browser_initialized()
                result = await browser_tool.get_current_state()

                return {
                    "success": not result.error,
                    "state": result.output if not result.error else None,
                    "error": result.error
                }
            except Exception as e:
                logger.error(f"Error getting browser state: {str(e)}")
                return {
                    "success": False,
                    "state": None,
                    "error": f"Error getting browser state: {str(e)}"
                }

    def get_action_history(self) -> List[Dict[str, Any]]:
        """
        Возвращает историю выполненных действий.

        Returns:
            Список словарей с информацией о выполненных действиях
        """
        return self.action_history

    async def cleanup(self) -> None:
        """
        Освобождает ресурсы модуля браузерного доступа.
        """
        logger.info("Cleaning up browser access resources")
        # Здесь может быть код для освобождения ресурсов, если они были выделены
        return None
