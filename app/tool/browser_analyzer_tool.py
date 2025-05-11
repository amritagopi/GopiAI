import asyncio
import json
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.tool.base import BaseTool, ToolResult
from app.ui.browser_tab_widget import MultiBrowserWidget

# Обновляем импорты скриптов из нового пакета browser_scripts
from app.tool.browser_scripts import (
    GET_PAGE_INFO,
    GET_PAGE_TEXT_CONTENT,
    GET_NAVIGATION_MENU,
    GET_TABLE_DATA,
    GET_STRUCTURED_DATA,
    GET_ELEMENTS_BY_SELECTOR,
    CLICK_ELEMENT
)


class BrowserAnalyzerTool(BaseTool):
    """
    Инструмент для анализа содержимого веб-страниц.
    Позволяет получать информацию о странице, извлекать данные и анализировать структуру.
    """

    name: str = "browser_analyzer"
    description: str = """
    Анализирует содержимое веб-страниц: получает структуру, извлекает данные,
    находит навигационные меню, таблицы и другие элементы.
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "get_page_info",
                    "get_page_text",
                    "get_navigation_menu",
                    "get_tables",
                    "get_structured_data",
                    "find_elements",
                    "click_element"
                ],
                "description": "Тип анализа, который необходимо выполнить"
            },
            "selector": {
                "type": "string",
                "description": "CSS-селектор для поиска элементов (для действий find_elements и click_element)"
            },
            "element_index": {
                "type": "integer",
                "description": "Индекс элемента для клика (для действия click_element)"
            }
        },
        "required": ["action"],
        "dependencies": {
            "find_elements": ["selector"],
            "click_element": ["selector"]
        }
    }

    # Ссылка на виджет браузера из UI
    browser_widget: Optional[MultiBrowserWidget] = Field(default=None, exclude=True)

    def notify_ui(self, message: str):
        if self.browser_widget and hasattr(self.browser_widget, 'progress_update'):
            try:
                self.browser_widget.progress_update.emit(message)
            except Exception as e:
                print(f"[GopiAI] Не удалось отправить уведомление в UI: {e}")

    async def execute(self,
                     action: str,
                     selector: Optional[str] = None,
                     element_index: Optional[int] = 0,
                     **kwargs) -> ToolResult:
        """
        Выполняет анализ веб-страницы.

        Args:
            action: Тип анализа для выполнения
            selector: CSS-селектор для поиска элементов
            element_index: Индекс элемента для клика

        Returns:
            ToolResult с результатом анализа
        """

        if not self.browser_widget:
            self.notify_ui("Ошибка: Браузер не инициализирован")
            return ToolResult(error="Браузер не инициализирован")

        try:
            # Получаем текущую активную вкладку
            current_tab = self._get_current_tab()
            if not current_tab:
                self.notify_ui("Ошибка: Активная вкладка не найдена")
                return ToolResult(error="Активная вкладка не найдена")

            if not hasattr(current_tab, "execute_javascript"):
                self.notify_ui("Ошибка: Браузер не поддерживает выполнение JavaScript")
                return ToolResult(error="Браузер не поддерживает выполнение JavaScript")

            # Создаем Future для получения результата асинхронно
            loop = asyncio.get_event_loop()
            future = loop.create_future()

            def callback(result):
                loop.call_soon_threadsafe(future.set_result, result)

            # Получение информации о странице
            if action == "get_page_info":
                current_tab.execute_javascript(GET_PAGE_INFO, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    # Преобразуем в читаемый вид, если результат - объект
                    if isinstance(result, dict):
                        self.notify_ui("Информация о странице получена успешно")
                        return ToolResult(output=json.dumps(result, ensure_ascii=False, indent=2))
                    self.notify_ui("Информация о странице получена, но результат не является объектом")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui("Таймаут при получении информации о странице")
                    return ToolResult(error="Таймаут при получении информации о странице")

            # Получение текстового содержимого страницы
            elif action == "get_page_text":
                current_tab.execute_javascript(GET_PAGE_TEXT_CONTENT, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, dict) and "paragraphs" in result:
                        text_content = "\\n\\n".join(result["paragraphs"])
                        self.notify_ui(f"Текстовое содержимое (слов: {result.get('wordCount', 0)}) получено успешно")
                        return ToolResult(output=f"Текстовое содержимое:\\n{text_content}")
                    self.notify_ui("Текстовое содержимое получено, но результат не содержит 'paragraphs'")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui("Таймаут при получении текстового содержимого")
                    return ToolResult(error="Таймаут при получении текстового содержимого")

            # Получение навигационного меню
            elif action == "get_navigation_menu":
                current_tab.execute_javascript(GET_NAVIGATION_MENU, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, list):
                        if not result:
                            self.notify_ui("На странице не найдено навигационных меню")
                            return ToolResult(output="На странице не найдено навигационных меню")

                        menus_info = []
                        for i, menu in enumerate(result):
                            menu_info = f"Меню #{i+1} ({menu.get('element', 'неизвестный элемент')}):\\n"
                            for item in menu.get('items', []):
                                active_mark = " [АКТИВНО]" if item.get('isActive') else ""
                                menu_info += f"  - {item.get('text', '?')}: {item.get('url', '#')}{active_mark}\\n"
                            menus_info.append(menu_info)

                        self.notify_ui("Навигационное меню получено успешно")
                        return ToolResult(output="\\n".join(menus_info))
                    self.notify_ui("Навигационное меню получено, но результат не является списком")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui("Таймаут при получении навигационного меню")
                    return ToolResult(error="Таймаут при получении навигационного меню")

            # Получение таблиц
            elif action == "get_tables":
                current_tab.execute_javascript(GET_TABLE_DATA, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, list):
                        if not result:
                            self.notify_ui("На странице не найдено таблиц")
                            return ToolResult(output="На странице не найдено таблиц")

                        tables_info = []
                        for table in result:
                            table_info = f"Таблица #{table.get('index', '?')} (строк: {table.get('rowCount', 0)}, колонок: {table.get('columnCount', 0)}):\\n"

                            # Добавляем заголовки
                            headers = table.get('headers', [])
                            if headers:
                                table_info += "  | " + " | ".join(headers) + " |\\n"
                                table_info += "  |" + "-|" * len(headers) + "\\n"

                            # Добавляем данные (ограничиваем количество строк)
                            rows = table.get('rows', [])
                            for i, row in enumerate(rows[:10]):  # Показываем до 10 строк
                                table_info += "  | " + " | ".join(row) + " |\\n"

                            if len(rows) > 10:
                                table_info += f"  ... и еще {len(rows) - 10} строк ...\\n"

                            tables_info.append(table_info)

                        self.notify_ui("Таблицы получены успешно")
                        return ToolResult(output="\\n".join(tables_info))
                    self.notify_ui("Таблицы получены, но результат не является списком")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui("Таймаут при получении таблиц")
                    return ToolResult(error="Таймаут при получении таблиц")

            # Получение структурированных данных
            elif action == "get_structured_data":
                current_tab.execute_javascript(GET_STRUCTURED_DATA, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, list):
                        if not result:
                            self.notify_ui("На странице не найдено структурированных данных")
                            return ToolResult(output="На странице не найдено структурированных данных")

                        self.notify_ui("Структурированные данные получены успешно")
                        return ToolResult(output=json.dumps(result, ensure_ascii=False, indent=2))
                    self.notify_ui("Структурированные данные получены, но результат не является списком")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui("Таймаут при получении структурированных данных")
                    return ToolResult(error="Таймаут при получении структурированных данных")

            # Поиск элементов по селектору
            elif action == "find_elements":
                if not selector:
                    self.notify_ui("CSS-селектор обязателен для действия find_elements")
                    return ToolResult(error="CSS-селектор обязателен для действия find_elements")

                js_code = f"return ({GET_ELEMENTS_BY_SELECTOR})(\"{selector}\")"
                current_tab.execute_javascript(js_code, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, list):
                        if not result:
                            self.notify_ui(f"По селектору '{selector}' элементы не найдены")
                            return ToolResult(output=f"По селектору '{selector}' элементы не найдены")

                        elements_info = []
                        for elem in result:
                            visible_mark = "" if elem.get('isVisible', True) else " [СКРЫТ]"
                            elem_info = f"#{elem.get('index', '?')} <{elem.get('tagName', '?')}{visible_mark}>"
                            if elem.get('id'):
                                elem_info += f" id='{elem.get('id')}'"

                            # Обрезаем текст, если он слишком длинный
                            text = elem.get('textContent', '')
                            if text and len(text) > 50:
                                text = text[:47] + "..."

                            if text:
                                elem_info += f": \"{text}\""

                            elements_info.append(elem_info)

                        self.notify_ui(f"Найдено {len(result)} элементов по селектору '{selector}'")
                        return ToolResult(output=f"Найдено {len(result)} элементов по селектору '{selector}':\\n" + "\\n".join(elements_info))
                    self.notify_ui("Найденные элементы получены, но результат не является списком")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui(f"Таймаут при поиске элементов по селектору '{selector}'")
                    return ToolResult(error=f"Таймаут при поиске элементов по селектору '{selector}'")

            # Клик по элементу
            elif action == "click_element":
                if not selector:
                    self.notify_ui("CSS-селектор обязателен для действия click_element")
                    return ToolResult(error="CSS-селектор обязателен для действия click_element")

                index = element_index if element_index is not None else 0
                js_code = f"return ({CLICK_ELEMENT})(\"{selector}\", {index})"
                current_tab.execute_javascript(js_code, callback)

                try:
                    result = await asyncio.wait_for(future, 5.0)
                    if isinstance(result, dict):
                        if result.get('success'):
                            element_info = result.get('elementInfo', {})
                            self.notify_ui(f"Успешный клик по элементу {element_info.get('tagName', '')} " +
                                          (f"с id='{element_info.get('id')}'" if element_info.get('id') else "") +
                                          (f": \"{element_info.get('text')}\"" if element_info.get('text') else ""))
                            return ToolResult(output=f"Успешный клик по элементу {element_info.get('tagName', '')} " +
                                              (f"с id='{element_info.get('id')}'" if element_info.get('id') else "") +
                                              (f": \"{element_info.get('text')}\"" if element_info.get('text') else ""))
                        else:
                            self.notify_ui(f"Ошибка при клике: {result.get('error', 'неизвестная ошибка')}")
                            return ToolResult(error=f"Ошибка при клике: {result.get('error', 'неизвестная ошибка')}")
                    self.notify_ui("Результат клика получен, но он не является словарем")
                    return ToolResult(output=str(result))
                except asyncio.TimeoutError:
                    self.notify_ui(f"Таймаут при клике по элементу с селектором '{selector}'")
                    return ToolResult(error=f"Таймаут при клике по элементу с селектором '{selector}'")

            else:
                self.notify_ui(f"Неизвестное действие: {action}")
                return ToolResult(error=f"Неизвестное действие: {action}")

        except Exception as e:
            self.notify_ui(f"Ошибка при выполнении действия {action}: {str(e)}")
            return ToolResult(error=f"Ошибка при выполнении действия {action}: {str(e)}")

    def _get_current_tab(self):
        """Получает текущую активную вкладку браузера."""
        if not self.browser_widget:
            return None

        current_index = self.browser_widget.tabs.currentIndex()
        if current_index < 0:
            return None

        return self.browser_widget.tabs.widget(current_index)

    def set_browser_widget(self, browser_widget: MultiBrowserWidget):
        """Устанавливает ссылку на виджет браузера из UI."""
        self.browser_widget = browser_widget
