import asyncio
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.tool.base import BaseTool, ToolResult
from app.ui.browser_tab_widget import MultiBrowserWidget


class BrowserControlTool(BaseTool):
    """
    Инструмент для управления браузером внутри приложения.
    Позволяет агенту управлять браузером, выполнять JavaScript, получать содержимое страницы и делать скриншоты.
    """

    name: str = "browser_control"
    description: str = """
    Управляет браузером внутри приложения: навигация, управление вкладками,
    выполнение JavaScript и другие операции.
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "navigate",
                    "go_back",
                    "go_forward",
                    "reload",
                    "stop",
                    "get_current_url",
                    "execute_javascript",
                    "add_new_tab",
                    "close_tab",
                    "switch_to_tab",
                    "get_tabs_info",
                    "get_page_source"
                ],
                "description": "Действие, которое необходимо выполнить"
            },
            "url": {
                "type": "string",
                "description": "URL для навигации или создания новой вкладки"
            },
            "tab_index": {
                "type": "integer",
                "description": "Индекс вкладки для действий с вкладками"
            },
            "javascript_code": {
                "type": "string",
                "description": "JavaScript код для выполнения"
            }
        },
        "required": ["action"],
        "dependencies": {
            "navigate": ["url"],
            "add_new_tab": ["url"],
            "switch_to_tab": ["tab_index"],
            "execute_javascript": ["javascript_code"]
        }
    }

    # Ссылка на виджет браузера из UI
    browser_widget: Optional[MultiBrowserWidget] = Field(default=None, exclude=True)

    async def execute(self,
                     action: str,
                     url: Optional[str] = None,
                     tab_index: Optional[int] = None,
                     javascript_code: Optional[str] = None,
                     **kwargs) -> ToolResult:
        """
        Выполняет действие с браузером.

        Args:
            action: Действие для выполнения
            url: URL для навигации или создания новой вкладки
            tab_index: Индекс вкладки для действий с вкладками
            javascript_code: JavaScript код для выполнения

        Returns:
            ToolResult с результатом выполнения действия
        """

        def notify_ui(message: str):
            if self.browser_widget and hasattr(self.browser_widget, 'progress_update'):
                try:
                    self.browser_widget.progress_update.emit(message)
                except Exception as e:
                    print(f"[GopiAI] Не удалось отправить уведомление в UI: {e}")

        if not self.browser_widget:
            notify_ui("Ошибка: Браузер не инициализирован")
            return ToolResult(error="Браузер не инициализирован")

        try:
            # Действия управления браузером
            if action == "navigate":
                if not url:
                    notify_ui("Ошибка: URL обязателен для перехода")
                    return ToolResult(error="URL обязателен для действия navigate")

                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                current_tab.navigate(url)
                notify_ui(f"Переход на {url}")
                return ToolResult(output=f"Переход на {url}")

            elif action == "go_back":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                if hasattr(current_tab, "go_back"):
                    current_tab.go_back()
                    notify_ui("Переход назад")
                    return ToolResult(output="Переход назад")
                notify_ui("Действие go_back не поддерживается текущим браузером")
                return ToolResult(error="Действие go_back не поддерживается текущим браузером")

            elif action == "go_forward":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                if hasattr(current_tab, "go_forward"):
                    current_tab.go_forward()
                    notify_ui("Переход вперед")
                    return ToolResult(output="Переход вперед")
                notify_ui("Действие go_forward не поддерживается текущим браузером")
                return ToolResult(error="Действие go_forward не поддерживается текущим браузером")

            elif action == "reload":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                if hasattr(current_tab, "reload"):
                    current_tab.reload()
                    notify_ui("Перезагрузка страницы")
                    return ToolResult(output="Перезагрузка страницы")
                notify_ui("Действие reload не поддерживается текущим браузером")
                return ToolResult(error="Действие reload не поддерживается текущим браузером")

            elif action == "stop":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                if hasattr(current_tab, "stop"):
                    current_tab.stop()
                    notify_ui("Загрузка остановлена")
                    return ToolResult(output="Загрузка остановлена")
                notify_ui("Действие stop не поддерживается текущим браузером")
                return ToolResult(error="Действие stop не поддерживается текущим браузером")

            elif action == "get_current_url":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                if hasattr(current_tab, "get_current_url"):
                    url = current_tab.get_current_url()
                    notify_ui(f"Текущий URL: {url}")
                    return ToolResult(output=url)
                notify_ui("Не удалось получить текущий URL")
                return ToolResult(error="Не удалось получить текущий URL")

            elif action == "execute_javascript":
                if not javascript_code:
                    notify_ui("Ошибка: JavaScript код обязателен для действия execute_javascript")
                    return ToolResult(error="JavaScript код обязателен для действия execute_javascript")

                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                # Создаем Future для получения результата асинхронно
                loop = asyncio.get_event_loop()
                future = loop.create_future()

                def callback(result):
                    loop.call_soon_threadsafe(future.set_result, result)

                # Выполняем JavaScript
                if hasattr(current_tab, "execute_javascript"):
                    current_tab.execute_javascript(javascript_code, callback)

                    try:
                        result = await asyncio.wait_for(future, 5.0)
                        notify_ui(f"Результат выполнения JavaScript: {result}")
                        return ToolResult(output=str(result))
                    except asyncio.TimeoutError:
                        notify_ui("Таймаут при выполнении JavaScript")
                        return ToolResult(error="Таймаут при выполнении JavaScript")

                notify_ui("Действие execute_javascript не поддерживается текущим браузером")
                return ToolResult(error="Действие execute_javascript не поддерживается текущим браузером")

            # Действия управления вкладками
            elif action == "add_new_tab":
                if not url:
                    notify_ui("Ошибка: URL обязателен для действия add_new_tab")
                    return ToolResult(error="URL обязателен для действия add_new_tab")

                new_index = self.browser_widget.add_new_tab(url)
                notify_ui(f"Создана новая вкладка с URL {url}")
                return ToolResult(output=f"Создана новая вкладка с URL {url}")

            elif action == "close_tab":
                current_index = self.browser_widget.tabs.currentIndex()
                if tab_index is not None:
                    # Закрываем указанную вкладку
                    if tab_index < 0 or tab_index >= self.browser_widget.tabs.count():
                        notify_ui(f"Ошибка: Индекс вкладки {tab_index} вне допустимого диапазона")
                        return ToolResult(error=f"Индекс вкладки {tab_index} вне допустимого диапазона")

                    self.browser_widget.close_tab(tab_index)
                    notify_ui(f"Закрыта вкладка с индексом {tab_index}")
                    return ToolResult(output=f"Закрыта вкладка с индексом {tab_index}")
                else:
                    # Закрываем текущую вкладку
                    self.browser_widget.close_tab(current_index)
                    notify_ui("Закрыта текущая вкладка")
                    return ToolResult(output="Закрыта текущая вкладка")

            elif action == "switch_to_tab":
                if tab_index is None:
                    notify_ui("Ошибка: Индекс вкладки обязателен для действия switch_to_tab")
                    return ToolResult(error="Индекс вкладки обязателен для действия switch_to_tab")

                tab_count = self.browser_widget.tabs.count()
                if tab_index < 0 or tab_index >= tab_count:
                    notify_ui(f"Ошибка: Индекс вкладки {tab_index} вне допустимого диапазона (0-{tab_count-1})")
                    return ToolResult(error=f"Индекс вкладки {tab_index} вне допустимого диапазона (0-{tab_count-1})")

                self.browser_widget.tabs.setCurrentIndex(tab_index)
                notify_ui(f"Переключение на вкладку с индексом {tab_index}")
                return ToolResult(output=f"Переключение на вкладку с индексом {tab_index}")

            elif action == "get_tabs_info":
                tabs_info = []

                for i in range(self.browser_widget.tabs.count()):
                    tab = self.browser_widget.tabs.widget(i)
                    tab_title = self.browser_widget.tabs.tabText(i)

                    if hasattr(tab, "get_current_url"):
                        tab_url = tab.get_current_url()
                    else:
                        tab_url = "Не удалось получить URL"

                    tabs_info.append({
                        "index": i,
                        "title": tab_title,
                        "url": tab_url,
                        "is_current": i == self.browser_widget.tabs.currentIndex()
                    })

                if not tabs_info:
                    notify_ui("Нет открытых вкладок")
                    return ToolResult(output="Нет открытых вкладок")

                # Форматируем информацию в читаемом виде
                result = "Открытые вкладки:\n"
                for tab in tabs_info:
                    current_mark = " [ТЕКУЩАЯ]" if tab["is_current"] else ""
                    result += f"{tab['index']}: {tab['title']} - {tab['url']}{current_mark}\n"

                notify_ui(result)
                return ToolResult(output=result)

            elif action == "get_page_source":
                current_tab = self._get_current_tab()
                if not current_tab:
                    notify_ui("Ошибка: Активная вкладка не найдена")
                    return ToolResult(error="Активная вкладка не найдена")

                # Выполняем JavaScript для получения HTML страницы
                loop = asyncio.get_event_loop()
                future = loop.create_future()

                def callback(result):
                    loop.call_soon_threadsafe(future.set_result, result)

                if hasattr(current_tab, "execute_javascript"):
                    current_tab.execute_javascript("document.documentElement.outerHTML", callback)

                    try:
                        result = await asyncio.wait_for(future, 5.0)
                        notify_ui(f"HTML страницы:\n{result}")
                        return ToolResult(output=f"HTML страницы:\n{result}")
                    except asyncio.TimeoutError:
                        notify_ui("Таймаут при получении HTML страницы")
                        return ToolResult(error="Таймаут при получении HTML страницы")

                notify_ui("Не удалось получить HTML страницы")
                return ToolResult(error="Не удалось получить HTML страницы")

            else:
                notify_ui(f"Неизвестное действие: {action}")
                return ToolResult(error=f"Неизвестное действие: {action}")

        except Exception as e:
            notify_ui(f"Ошибка при выполнении действия {action}: {str(e)}")
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
