import asyncio
import os
import base64
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from app.tool.base import BaseTool, ToolResult
from app.ui.browser_tab_widget import MultiBrowserWidget


class BrowserScreenshotTool(BaseTool):
    """
    Инструмент для создания и сохранения скриншотов веб-страниц.
    Позволяет делать скриншоты текущей страницы и сохранять их на диск.
    """

    name: str = "browser_screenshot"
    description: str = """
    Создает скриншоты текущей веб-страницы в браузере и сохраняет их в указанную директорию.
    Поддерживает полные снимки страницы или выборочные области.
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Директория для сохранения скриншотов (по умолчанию 'screenshots')"
            },
            "filename": {
                "type": "string",
                "description": "Имя файла (по умолчанию 'screenshot_YYYY-MM-DD_HH-MM-SS.png')"
            },
            "full_page": {
                "type": "boolean",
                "description": "Создать полный скриншот страницы (по умолчанию True)"
            },
            "selector": {
                "type": "string",
                "description": "CSS-селектор элемента для создания скриншота"
            }
        }
    }

    # Ссылка на виджет браузера из UI
    browser_widget: Optional[MultiBrowserWidget] = Field(default=None, exclude=True)

    async def execute(self,
                     directory: str = "screenshots",
                     filename: Optional[str] = None,
                     full_page: bool = True,
                     selector: Optional[str] = None,
                     **kwargs) -> ToolResult:
        """
        Делает скриншот веб-страницы.

        Args:
            directory: Директория для сохранения скриншотов
            filename: Имя файла
            full_page: Создать полный скриншот страницы
            selector: CSS-селектор элемента для создания скриншота

        Returns:
            ToolResult с результатом создания скриншота
        """

        if not self.browser_widget:
            return ToolResult(error="Браузер не инициализирован")

        try:
            # Получаем текущую активную вкладку
            current_tab = self._get_current_tab()
            if not current_tab:
                return ToolResult(error="Активная вкладка не найдена")

            if not hasattr(current_tab, "execute_javascript"):
                return ToolResult(error="Браузер не поддерживает выполнение JavaScript")

            # Создаем директорию, если не существует
            os.makedirs(directory, exist_ok=True)

            # Генерируем имя файла, если не указано
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"screenshot_{timestamp}.png"

            # Полный путь к файлу
            full_path = os.path.join(directory, filename)

            # JavaScript для создания скриншота
            js_code = """
            (async function() {
                try {
                    // Функция для преобразования canvas в base64
                    const canvasToBase64 = (canvas) => {
                        return canvas.toDataURL('image/png').split(',')[1];
                    };

                    // Функция для создания скриншота элемента
                    const takeElementScreenshot = async (selector) => {
                        const element = document.querySelector(selector);
                        if (!element) {
                            return { success: false, error: 'Элемент не найден' };
                        }

                        // Получаем размеры и позицию элемента
                        const rect = element.getBoundingClientRect();

                        // Создаем canvas
                        const canvas = document.createElement('canvas');
                        canvas.width = rect.width;
                        canvas.height = rect.height;
                        const ctx = canvas.getContext('2d');

                        // Создаем временное изображение
                        const html2canvas = document.createElement('script');
                        html2canvas.src = 'https://html2canvas.hertzen.com/dist/html2canvas.min.js';
                        document.head.appendChild(html2canvas);

                        // Ждем загрузки скрипта
                        await new Promise(resolve => {
                            html2canvas.onload = resolve;
                        });

                        // Делаем скриншот элемента
                        const canvas = await html2canvas(element);
                        return { success: true, image: canvasToBase64(canvas) };
                    };

                    // Функция для полного скриншота
                    const takeFullPageScreenshot = async () => {
                        // Используем html2canvas для полного скриншота
                        const html2canvas = document.createElement('script');
                        html2canvas.src = 'https://html2canvas.hertzen.com/dist/html2canvas.min.js';
                        document.head.appendChild(html2canvas);

                        // Ждем загрузки скрипта
                        await new Promise(resolve => {
                            html2canvas.onload = resolve;
                        });

                        // Делаем полный скриншот
                        const canvas = await html2canvas(document.documentElement);
                        return { success: true, image: canvasToBase64(canvas) };
                    };

                    // В зависимости от параметров создаем нужный скриншот
                    if ('""" + (selector or "") + """') {
                        return await takeElementScreenshot('""" + (selector or "") + """');
                    } else {
                        return await takeFullPageScreenshot();
                    }
                } catch (error) {
                    return { success: false, error: error.toString() };
                }
            })();
            """

            # Создаем Future для получения результата асинхронно
            loop = asyncio.get_event_loop()
            future = loop.create_future()

            def callback(result):
                loop.call_soon_threadsafe(future.set_result, result)

            # Выполняем JavaScript
            current_tab.execute_javascript(js_code, callback)

            try:
                # Ждем результат с увеличенным таймаутом (10 секунд)
                result = await asyncio.wait_for(future, 10.0)

                if not isinstance(result, dict):
                    return ToolResult(error=f"Неожиданный результат: {result}")

                if not result.get("success", False):
                    return ToolResult(error=f"Ошибка при создании скриншота: {result.get('error', 'неизвестная ошибка')}")

                # Получаем изображение в base64
                image_data = result.get("image")
                if not image_data:
                    return ToolResult(error="Не удалось получить данные изображения")

                # Сохраняем изображение
                with open(full_path, "wb") as f:
                    f.write(base64.b64decode(image_data))

                return ToolResult(output=f"Скриншот сохранен в {full_path}")

            except asyncio.TimeoutError:
                return ToolResult(error="Таймаут при создании скриншота")
            except Exception as e:
                return ToolResult(error=f"Ошибка при обработке скриншота: {str(e)}")

        except Exception as e:
            return ToolResult(error=f"Ошибка при создании скриншота: {str(e)}")

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
