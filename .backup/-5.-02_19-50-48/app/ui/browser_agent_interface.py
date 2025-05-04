import asyncio
import logging
import json
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
        self._system_prompt = BROWSER_AGENT_SYSTEM_PROMPT
        self._conversation_history = []
        self._model = "claude-3-opus-20240229"  # По умолчанию используем мощную модель
        self._temperature = 0.2  # Низкая температура для более точных ответов
        self._max_tokens = 4000  # Лимит на длину ответа

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

            # Добавляем сообщение пользователя
            await self.agent.add_user_message(query)

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
            self.agent_message.emit("Работа агента остановлена")
            self.agent_thinking.emit(False)
            self.agent_finished.emit()

    async def cleanup(self):
        """
        Очищает ресурсы агента перед закрытием приложения.
        """
        # Останавливаем текущую задачу, если она выполняется
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()

        # Очищаем ресурсы агента, если он был инициализирован
        if self.agent:
            # В будущем здесь можно добавить дополнительную логику очистки
            self.agent = None

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
            # Подготавливаем сообщение с контекстом
            full_message = user_message

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
