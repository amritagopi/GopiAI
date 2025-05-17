import asyncio
import logging
import json
import datetime
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtCore import QObject, Signal, Slot

from app.agent.browser_agent import EnhancedBrowserAgent
from app.ui.browser_tab_widget import MultiBrowserWidget
from app.tool.browser_tools_integration import initialize_browser_tools
from app.agent.llm_interaction import llm_agentic_action
from app.prompt.browser_agent import BROWSER_AGENT_SYSTEM_PROMPT
from app.ui.i18n.translator import tr

logger = logging.getLogger(__name__)

class BrowserAgentInterface(QObject):
    """
    Интерфейс для связи между UI браузера и браузерным агентом.
    Управляет запуском агента и передачей сообщений между UI и агентом.
    """

    # Сигналы для взаимодействия с UI
    agent_message = Signal(str)  # Сообщение от агента
    agent_error = Signal(str)  # Сообщение об ошибке
    agent_thinking = Signal(bool)  # Сигнал о том, что агент обрабатывает запрос
    agent_finished = Signal()  # Сигнал о завершении работы агента

    def __init__(self, parent=None):
        super(BrowserAgentInterface, self).__init__(parent)
        self.browser_widget: Optional[MultiBrowserWidget] = None
        self.agent: Optional[EnhancedBrowserAgent] = None
        self._running_task = None

        # Обновляем системный промпт с информацией о доступе к времени
        self._system_prompt = BROWSER_AGENT_SYSTEM_PROMPT + """
Additionally, you now have access to the current date and time information.
You are able to use this information to provide time-contextualized responses,
assist with scheduling, and perform time-based calculations when needed.
When referencing the current time in your responses, use the time data provided to you.
"""

        self._conversation_history = []
        self._model = "claude-3-opus-20240229"  # По умолчанию используем мощную модель
        self._temperature = 0.2  # Низкая температура для более точных ответов
        self._max_tokens = 4000  # Лимит на длину ответа
        self._cleanup_timeout = 3  # Таймаут для очистки в секундах

    def set_browser_widget(self, browser_widget: MultiBrowserWidget):
        """
        Устанавливает виджет браузера и инициализирует инструменты для агента.

        Args:
            browser_widget: Виджет браузера из UI
        """
        self.browser_widget = browser_widget

        # Инициализируем инструменты
        initialize_browser_tools(browser_widget)

    def initialize_agent(self):
        """
        Инициализирует агента браузера.
        Вызывается после установки виджета браузера.
        """
        if not self.browser_widget:
            self.agent_error.emit("Ошибка: виджет браузера не установлен")
            return False

        try:
            self.agent = EnhancedBrowserAgent()
            return True
        except Exception as e:
            self.agent_error.emit(f"Ошибка инициализации агента: {str(e)}")
            return False

    @Slot(str)
    def process_user_query(self, query: str):
        """
        Обрабатывает запрос пользователя и запускает агента.

        Args:
            query: Запрос пользователя
        """
        if not self.agent:
            if not self.initialize_agent():
                return

        self.agent_thinking.emit(True)

        # Создаем и запускаем задачу
        self._running_task = asyncio.create_task(self._run_agent(query))

    async def _run_agent(self, query: str):
        """
        Запускает агента для обработки запроса пользователя.

        Args:
            query: Запрос пользователя
        """
        try:
            # Обновляем сообщения в агенте
            self.agent.messages = []

            # Получаем информацию о текущем времени
            datetime_info = self.agent.get_datetime_info()

            # Добавляем информацию о времени к запросу пользователя
            time_context = f"Current time: {datetime_info['current_time']}, Date: {datetime_info['current_date']}, Day: {datetime_info['day_of_week']}"

            # Добавляем сообщение пользователя с контекстом времени
            await self.agent.add_user_message(f"{time_context}\n\nUser query: {query}")

            # Запускаем агента
            result = await self.agent.run()

            # Отправляем результат в UI
            if result:
                self.agent_message.emit(result)
            else:
                self.agent_message.emit("Агент завершил работу без результата")

        except Exception as e:
            self.agent_error.emit(f"Ошибка при выполнении запроса: {str(e)}")
        finally:
            self.agent_thinking.emit(False)
            self.agent_finished.emit()

    @Slot()
    def stop_agent(self):
        """
        Останавливает работающего агента.
        """
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()

            # Добавляем сообщение о принудительной остановке в историю
            time_info = self.agent.get_datetime_info() if self.agent else {"current_time": datetime.datetime.now().strftime("%H:%M:%S")}
            system_message = {
                "role": "system",
                "content": f"[{time_info['current_time']}] Agent execution was stopped by user."
            }
            self._conversation_history.append(system_message)

            # Эмитируем сигналы для UI
            self.agent_message.emit("Operation stopped by user")
            self.agent_thinking.emit(False)
            self.agent_finished.emit()

            logger.info("Browser agent was stopped by user")
        else:
            logger.info("No running browser agent task to stop")

    async def cleanup(self):
        """
        Очищает ресурсы агента перед закрытием приложения.
        Ожидает заданный таймаут для завершения асинхронных операций.
        """
        # Останавливаем текущую задачу, если она выполняется
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()

        # Ожидаем таймаут для корректного завершения
        await asyncio.sleep(self._cleanup_timeout)

        # Очищаем ресурсы агента, если он был инициализирован
        if self.agent:
            # В будущем здесь можно добавить дополнительную логику очистки
            self.agent = None

        logger.info("Browser agent resources cleaned up successfully")

    async def cleanup_tab(self, tab_index, tab_widget):
        """
        Очищает ресурсы, связанные с конкретной вкладкой браузера.

        Args:
            tab_index: Индекс закрываемой вкладки
            tab_widget: Виджет закрываемой вкладки
        """
        try:
            # Логируем информацию о закрытии вкладки
            tab_url = ""
            if hasattr(tab_widget, "get_current_url"):
                tab_url = tab_widget.get_current_url()
            elif hasattr(tab_widget, "browser") and hasattr(tab_widget.browser, "get_current_url"):
                tab_url = tab_widget.browser.get_current_url()

            logger.info(f"Очистка ресурсов вкладки {tab_index} с URL: {tab_url}")

            # Если агент в данный момент работает с этой вкладкой, останавливаем его
            if self._running_task and not self._running_task.done():
                current_url = ""
                if self.browser_widget:
                    current_url = self.browser_widget.get_current_url()

                # Если агент работает с текущей вкладкой, останавливаем его
                if tab_url and tab_url == current_url:
                    logger.info(f"Останавливаем агента, работающего с вкладкой {tab_index}")
                    self._running_task.cancel()

            # Очищаем историю разговора, связанную с этой вкладкой
            # Так как мы не храним отдельную историю для каждой вкладки,
            # просто добавляем системное сообщение, что вкладка была закрыта
            if tab_url:
                time_info = self.agent.get_datetime_info() if self.agent else {"current_time": datetime.datetime.now().strftime("%H:%M:%S")}
                system_message = {
                    "role": "system",
                    "content": f"[{time_info['current_time']}] Вкладка с URL {tab_url} была закрыта пользователем."
                }
                self._conversation_history.append(system_message)

            # Ждем небольшую паузу для завершения асинхронных операций
            await asyncio.sleep(0.1)

            logger.info(f"Ресурсы вкладки {tab_index} успешно очищены")
            return True

        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов вкладки {tab_index}: {str(e)}")
            return False

    async def process_request(self,
                           user_message: str,
                           browser_content: Optional[str] = None,
                           url: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None) -> str:
        """
        Обрабатывает запрос пользователя и возвращает ответ от ИИ.

        Аргументы:
            user_message: Сообщение пользователя
            browser_content: Текстовое содержимое текущей страницы браузера
            url: URL текущей страницы
            context: Дополнительный контекст для запроса

        Возвращает:
            Ответ от ИИ
        """
        try:
            # Получаем текущее время и дату
            current_datetime = datetime.datetime.now()
            time_info = {
                "current_datetime": current_datetime.isoformat(),
                "current_date": current_datetime.strftime("%Y-%m-%d"),
                "current_time": current_datetime.strftime("%H:%M:%S"),
                "day_of_week": current_datetime.strftime("%A")
            }

            # Подготавливаем сообщение с контекстом
            full_message = user_message

            # Добавляем информацию о времени
            time_context = f"Current time information: {json.dumps(time_info)}"
            full_message = f"{time_context}\n\n{full_message}"

            # Добавляем информацию о странице, если она есть
            if url:
                full_message = f"Current URL: {url}\n\n{full_message}"

            if browser_content:
                # Ограничиваем размер контента, чтобы не превышать лимиты токенов
                browser_content_truncated = browser_content[:50000]
                context_message = f"Here is the content of the current page (it may be truncated):\n\n{browser_content_truncated}"

                # Добавляем это сообщение в историю разговора отдельно
                self._conversation_history.append({"role": "user", "content": context_message})

            # Добавляем сообщение пользователя в историю
            self._conversation_history.append({"role": "user", "content": full_message})

            # Формируем запрос к ИИ
            response = await llm_agentic_action(
                model=self._model,
                system_prompt=self._system_prompt,
                conversation_history=self._conversation_history,
                temperature=self._temperature,
                max_tokens=self._max_tokens
            )

            # Добавляем ответ в историю разговора
            self._conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            logger.error(f"Error processing browser agent request: {e}")
            error_message = tr("dialogs.browser_agent_error",
                               "Error processing your request. Please try again or rephrase your question. Error: {error}")
            return error_message.format(error=str(e))

    async def analyze_webpage(self, url: str, content: str) -> str:
        """
        Анализирует веб-страницу и возвращает результат анализа.

        Аргументы:
            url: URL страницы
            content: Содержимое страницы

        Возвращает:
            Результат анализа от ИИ
        """
        try:
            message = f"Please analyze this webpage at {url}. Provide a summary of what this page is about, its main topics or sections, and any key information."
            return await self.process_request(message, content, url)
        except Exception as e:
            logger.error(f"Error analyzing webpage: {e}")
            return tr("dialogs.analyze_error", "Error analyzing webpage: {error}").format(error=str(e))

    async def search_in_content(self, query: str, content: str, url: str) -> str:
        """
        Ищет информацию в содержимом страницы.

        Аргументы:
            query: Поисковый запрос
            content: Содержимое страницы
            url: URL страницы

        Возвращает:
            Результаты поиска от ИИ
        """
        try:
            message = f"Find information about '{query}' in the content of this page. If found, provide the relevant information and where it appears on the page."
            return await self.process_request(message, content, url)
        except Exception as e:
            logger.error(f"Error searching in content: {e}")
            return tr("dialogs.search_error", "Error searching in content: {error}").format(error=str(e))

    async def suggest_next_actions(self, url: str, content: str, goal: str) -> List[Dict[str, Any]]:
        """
        Предлагает следующие действия для достижения цели пользователя.

        Аргументы:
            url: URL текущей страницы
            content: Содержимое страницы
            goal: Цель пользователя

        Возвращает:
            Список возможных действий в формате JSON
        """
        try:
            message = f"Based on my goal: '{goal}', suggest the next actions I should take on this webpage or where I should navigate next. Return the response as a JSON list of actions with 'description' and 'reason' for each action."

            response = await self.process_request(message, content, url)

            # Пытаемся извлечь JSON из ответа
            try:
                # Ищем JSON в ответе (может быть обернут в текст или код)
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    actions = json.loads(json_str)
                    return actions
                else:
                    # Если JSON не найден, структурируем ответ вручную
                    lines = response.splitlines()
                    actions = []

                    current_action = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('- ') or line.startswith('* '):
                            if current_action:
                                actions.append(current_action)
                            current_action = {"description": line[2:], "reason": ""}
                        elif current_action and line:
                            current_action["reason"] += line + " "

                    if current_action:
                        actions.append(current_action)

                    return actions
            except json.JSONDecodeError:
                # Если не удалось извлечь JSON, возвращаем ответ как одно действие
                return [{"description": "Review AI's response", "reason": response}]

        except Exception as e:
            logger.error(f"Error suggesting next actions: {e}")
            return [{"description": "Error", "reason": str(e)}]

    def clear_conversation(self):
        """Очищает историю разговора."""
        self._conversation_history = []

    def set_model(self, model_name: str):
        """Устанавливает модель для использования."""
        self._model = model_name

    def set_temperature(self, temperature: float):
        """Устанавливает температуру для генерации ответов."""
        self._temperature = max(0.0, min(1.0, temperature))  # Ограничиваем в диапазоне от 0 до 1
