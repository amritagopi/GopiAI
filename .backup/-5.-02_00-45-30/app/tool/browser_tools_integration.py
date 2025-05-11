from typing import Optional

from app.ui.browser_tab_widget import MultiBrowserWidget
from app.tool.browser_control_tool import BrowserControlTool
from app.tool.browser_analyzer_tool import BrowserAnalyzerTool
from app.tool.browser_screenshot_tool import BrowserScreenshotTool


class BrowserToolsManager:
    """
    Менеджер инструментов браузера.
    Создает и настраивает инструменты для взаимодействия с браузером.
    """

    def __init__(self):
        self.browser_widget: Optional[MultiBrowserWidget] = None
        self.browser_control_tool: Optional[BrowserControlTool] = None
        self.browser_analyzer_tool: Optional[BrowserAnalyzerTool] = None
        self.browser_screenshot_tool: Optional[BrowserScreenshotTool] = None

    def set_browser_widget(self, browser_widget: MultiBrowserWidget):
        """
        Устанавливает ссылку на виджет браузера и инициализирует инструменты.

        Args:
            browser_widget: Виджет браузера из UI
        """
        self.browser_widget = browser_widget

        # Инициализируем инструменты, если они не были созданы
        if not self.browser_control_tool:
            self.browser_control_tool = BrowserControlTool()

        if not self.browser_analyzer_tool:
            self.browser_analyzer_tool = BrowserAnalyzerTool()

        if not self.browser_screenshot_tool:
            self.browser_screenshot_tool = BrowserScreenshotTool()

        # Устанавливаем ссылку на виджет браузера в инструменты
        self.browser_control_tool.set_browser_widget(browser_widget)
        self.browser_analyzer_tool.set_browser_widget(browser_widget)
        self.browser_screenshot_tool.set_browser_widget(browser_widget)

    def get_tools(self):
        """
        Возвращает список всех инструментов для браузера.

        Returns:
            Список инструментов для работы с браузером
        """
        tools = []

        if self.browser_control_tool:
            tools.append(self.browser_control_tool)

        if self.browser_analyzer_tool:
            tools.append(self.browser_analyzer_tool)

        if self.browser_screenshot_tool:
            tools.append(self.browser_screenshot_tool)

        return tools


# Глобальный экземпляр менеджера инструментов браузера
browser_tools_manager = BrowserToolsManager()


def initialize_browser_tools(browser_widget: MultiBrowserWidget):
    """
    Инициализирует инструменты браузера и связывает их с виджетом браузера.

    Args:
        browser_widget: Виджет браузера из UI
    """
    browser_tools_manager.set_browser_widget(browser_widget)
    return browser_tools_manager.get_tools()


def get_browser_tools():
    """
    Возвращает список инструментов браузера.

    Returns:
        Список инструментов для работы с браузером
    """
    return browser_tools_manager.get_tools()
