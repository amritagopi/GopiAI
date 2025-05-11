"""
Reasoning Agent для GopiAI

Агент с интегрированными стратегиями мышления Serena и Sequential Thinking.
Выполняет действия по системе "План → Разрешение → Выполнение".
"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Set, Callable, Awaitable
from datetime import datetime

from pydantic import Field

from app.agent.mcp import MCPAgent
from app.agent.terminal_access import TerminalAccess  # Импортируем класс TerminalAccess
from app.agent.browser_access import BrowserAccess  # Импортируем класс BrowserAccess
from app.agent.file_system_access import FileSystemAccess  # Импортируем класс FileSystemAccess
from app.agent.text_editor_access import TextEditorAccess  # Импортируем класс TextEditorAccess
from app.agent.permission_manager import PermissionManager  # Импортируем новый менеджер разрешений
from app.agent.planning_strategy import get_planning_strategy, PlanningStrategy, TaskComplexity  # Импортируем стратегии планирования и TaskComplexity
from app.agent.thought_tree import ThoughtTree  # Импортируем дерево мыслей
# Добавляем импорты для стратегий исследования
from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationSource, InformationItem, InformationCollection
)
from app.agent.web_exploration_strategy import WebExplorationStrategy
from app.agent.file_exploration_strategy import FileExplorationStrategy
from app.agent.error_manager import ErrorManager  # Импортируем менеджер ошибок
from app.agent.error_analysis_system import ErrorSource, ErrorSeverity  # Импортируем типы ошибок
from app.agent.personalization_manager import PersonalizationManager, InteractionType, ContentDomain, UserProfile  # Добавляем импорт PersonalizationManager
from app.agent.experience_manager import ExperienceArchive  # Добавляем импорт ExperienceArchive
from app.agent.experience_adapter import ExperienceAdapter  # Добавляем импорт ExperienceAdapter
from app.config import config
from app.config.reasoning_config import ReasoningStrategy
from app.logger import logger
from app.mcp.sequential_thinking import SequentialThinking
from app.mcp.serena_integration import SerenaIntegration  # Импортируем новый класс интеграции с Serena
from app.schema import AgentState, Message
from app.prompt.reasoning import (
    REASONING_SYSTEM_PROMPT
)
from app.agent.metacognitive_analyzer import MetacognitiveAnalyzer  # Импортируем новый метакогнитивный анализатор
from app.agent.resource_manager import ResourceManager, Task, ResourceRequirement, TaskPriority, ResourceType
from app.agent.performance_monitor import PerformanceMonitor, MetricType, AlertLevel


class ReasoningAgent(MCPAgent):
    """
    Reasoning Agent интегрирует MCP Serena и Sequential Thinking
    для логического рассуждения и решения сложных задач.

    Агент работает в три этапа:
    1. Формирование плана действий и рассуждений
    2. Получение одобрения от пользователя
    3. Выполнение одобренных действий
    """

    name: str = "reasoning_agent"
    description: str = "A reasoning agent with Serena and Sequential Thinking capabilities"

    # Переопределяем системный промпт
    system_prompt: str = REASONING_SYSTEM_PROMPT

    # Модули, которые должны быть активны
    required_tools = [
        "mcp_serena_initial_instructions",  # Serena необходим
        "mcp_sequential-thinking_sequentialthinking",  # Sequential Thinking необходим
    ]

    # Состояние для утверждения плана
    current_plan: Optional[str] = None
    current_plan_data: Optional[Dict[str, Any]] = None

    # Sequential Thinking клиент
    sequential_thinking: Optional[SequentialThinking] = None

    # Serena интеграция
    serena: Optional[SerenaIntegration] = None

    # Terminal Access клиент
    terminal_access: Optional[TerminalAccess] = None

    # Browser Access клиент
    browser_access: Optional[BrowserAccess] = None

    # File System Access клиент
    file_system: Optional[FileSystemAccess] = None

    # Text Editor Access клиент
    text_editor: Optional[TextEditorAccess] = None

    # Permission Manager
    permission_manager: Optional[PermissionManager] = None

    # Стратегия планирования
    planning_strategy: Optional[PlanningStrategy] = None

    # Дерево мыслей
    thought_tree: Optional[ThoughtTree] = None

    # Метакогнитивный анализатор
    metacognitive_analyzer: Optional[MetacognitiveAnalyzer] = None

    # Менеджер ошибок для анализа и категоризации
    error_manager: Optional[ErrorManager] = None

    # Менеджер персонализации
    personalization_manager: Optional[PersonalizationManager] = None

    # Менеджер опыта для импорта/экспорта
    experience_archive: Optional[ExperienceArchive] = None

    # Адаптер опыта для адаптации к предыдущему опыту
    experience_adapter: Optional[ExperienceAdapter] = None

    # Стратегии исследования
    web_exploration: Optional[WebExplorationStrategy] = None
    file_exploration: Optional[FileExplorationStrategy] = None
    exploration_strategies: Dict[str, ExplorationStrategy] = {}

    # Менеджер ресурсов для приоритизации задач
    resource_manager: Optional[ResourceManager] = None

    async def initialize(
        self,
        connection_type: Optional[str] = None,
        server_url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        skip_serena_check: bool = False,
    ) -> None:
        """
        Инициализирует агента и проверяет наличие необходимых модулей.

        Args:
            connection_type: Тип подключения ("stdio" или "sse")
            server_url: URL MCP сервера (для SSE подключения)
            command: Команда для запуска (для stdio подключения)
            args: Аргументы для команды (для stdio подключения)
            skip_serena_check: Пропускает проверку модуля Serena (для тестирования)

        Raises:
            ValueError: Если отсутствуют необходимые модули Serena или Sequential Thinking
        """
        # Инициализируем базовый агент
        await super().initialize(connection_type, server_url, command, args)

        # Проверяем наличие необходимых инструментов
        missing_tools = self._check_required_tools()
        if missing_tools:
            missing_names = ', '.join(missing_tools)
            error_msg = f"Missing required reasoning tools: {missing_names}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("All required reasoning tools are available")

        # Сначала пробуем инициализировать Sequential Thinking, так как он обязателен
        try:
            # Создаем клиент Sequential Thinking и инициализируем его
            self.sequential_thinking = SequentialThinking(self.mcp_clients)
            sequential_thinking_initialized = await self.sequential_thinking.initialize()
            if not sequential_thinking_initialized:
                error_msg = "Failed to initialize Sequential Thinking module"
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                logger.info("Sequential Thinking integration initialized successfully")
        except Exception as e:
            error_msg = f"Fatal error initializing Sequential Thinking: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Затем пробуем инициализировать Serena
        if not skip_serena_check:
            try:
                # Создаем и инициализируем интеграцию с Serena
                self.serena = SerenaIntegration(self.mcp_clients)
                serena_initialized = await self.serena.initialize()
                if not serena_initialized:
                    error_msg = "Failed to initialize Serena module"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                else:
                    logger.info("Serena integration initialized successfully")
            except Exception as e:
                error_msg = f"Fatal error initializing Serena: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            logger.info("Skipping Serena check as requested")

        # Получаем настройки из конфигурации
        reasoning_config = config.reasoning_config
        safe_mode = reasoning_config.safe_mode
        operation_timeout = reasoning_config.operation_timeout

        # Логируем информацию о настройках
        logger.info(f"Initializing reasoning agent with settings: depth={reasoning_config.reasoning_depth}, "
                   f"strategy={reasoning_config.reasoning_strategy.value}, "
                   f"detailed_logging={reasoning_config.detailed_logging}, "
                   f"monitoring={reasoning_config.monitoring_enabled}, "
                   f"interactive={reasoning_config.interactive_mode}, "
                   f"safe_mode={safe_mode}, timeout={operation_timeout}")

        # Инициализируем менеджер разрешений
        self.permission_manager = PermissionManager(safe_mode=safe_mode)
        logger.info("Permission manager initialized")

        # Инициализируем модуль доступа к терминалу с учетом настроек
        self.terminal_access = TerminalAccess(
            root_dir=os.getcwd(),
            safe_mode=safe_mode,
            timeout=operation_timeout
        )
        logger.info("Terminal access module initialized")

        # Инициализируем модуль доступа к браузеру с учетом настроек
        browser_config = config.browser_config

        # Инициализируем модуль доступа к файловой системе с учетом настроек
        self.file_system = FileSystemAccess(
            root_dir=os.getcwd(),
            safe_mode=safe_mode,
            default_timeout=operation_timeout
        )
        logger.info("File system access module initialized")

        # Инициализируем модуль доступа к текстовому редактору с учетом настроек
        self.text_editor = TextEditorAccess(
            root_dir=os.getcwd(),
            safe_mode=safe_mode
        )
        logger.info("Text editor access module initialized")

        # Инициализируем менеджер ошибок
        self.error_manager = ErrorManager()
        logger.info("Error manager initialized")

        # Инициализируем стратегии исследования
        self._initialize_exploration_strategies()

        # Инициализируем менеджер персонализации
        self.personalization_manager = PersonalizationManager()
        logger.info("Personalization manager initialized")

        # Инициализируем архив опыта
        self.experience_archive = ExperienceArchive(
            personalization_manager=self.personalization_manager,
            error_manager=self.error_manager
        )
        logger.info("Experience archive initialized")

        # Инициализируем адаптер опыта
        self.experience_adapter = ExperienceAdapter(
            personalization_manager=self.personalization_manager,
            error_manager=self.error_manager,
            experience_archive=self.experience_archive,
            metacognitive_analyzer=self.metacognitive_analyzer
        )
        logger.info("Experience adapter initialized")

        # Создаем/загружаем профиль пользователя для текущей сессии
        self._initialize_user_profile()

        # Инициализируем стратегию планирования
        try:
            self.planning_strategy = get_planning_strategy(
                strategy_type=reasoning_config.reasoning_strategy,
                max_depth=reasoning_config.reasoning_depth
            )
            logger.info(f"Planning strategy initialized with type {reasoning_config.reasoning_strategy.value}")
        except Exception as e:
            error_msg = f"Error initializing planning strategy: {str(e)}"
            logger.error(error_msg)
            self._log_error(error_msg, ErrorSource.PLANNING, ErrorSeverity.HIGH)
            # Используем базовую стратегию в случае ошибки
            self.planning_strategy = get_planning_strategy(
                strategy_type=ReasoningStrategy.BASIC,
                max_depth=3
            )

        # Инициализируем дерево мыслей
        self.thought_tree = ThoughtTree()
        logger.info("Thought tree initialized")

        # Инициализируем метакогнитивный анализатор
        self.metacognitive_analyzer = MetacognitiveAnalyzer()
        logger.info("Metacognitive analyzer initialized")

        # Инициализируем менеджер ресурсов
        self.resource_manager = ResourceManager()
        logger.info("ReasoningAgent: менеджер ресурсов инициализирован")

        # Настраиваем ресурсы
        self.resource_manager.configure_resource(ResourceType.CPU, 0.8)
        self.resource_manager.configure_resource(ResourceType.MEMORY, 0.6)
        self.resource_manager.configure_resource(ResourceType.API_CALL, 0.5)
        self.resource_manager.configure_resource(ResourceType.LLM_CALL, 0.7)

        # Устанавливаем максимальное количество одновременных задач
        max_concurrent = self.config.get("max_concurrent_tasks", 5)
        self.resource_manager.set_max_concurrent_tasks(max_concurrent)

        # Включаем мониторинг производительности
        if reasoning_config.monitoring_enabled:
            self.resource_manager.enable_performance_monitoring(
                collection_interval=reasoning_config.monitoring_interval
            )
            # Запускаем мониторинг асинхронно
            await self.resource_manager.start_performance_monitoring()
            logger.info("ReasoningAgent: запущен мониторинг производительности")

        logger.info("Reasoning agent initialization completed successfully")

    def _initialize_user_profile(self) -> None:
        """
        Инициализирует профиль пользователя для текущей сессии.
        Если профиль не существует, создает новый.
        """
        if not self.personalization_manager:
            logger.warning("Personalization manager not initialized, skipping profile initialization")
            return

        try:
            # Используем фиксированный user_id для текущей реализации
            # В будущих версиях можно добавить механизм аутентификации
            user_id = "default_user"

            # Пытаемся загрузить существующий профиль
            profile = self.personalization_manager.load_profile(user_id)

            # Если профиля нет, создаем новый
            if not profile:
                logger.info(f"Creating new user profile for {user_id}")
                profile = self.personalization_manager.create_profile(user_id)
            else:
                # Устанавливаем загруженный профиль как активный
                self.personalization_manager.set_active_profile(user_id)
                logger.info(f"Loaded existing profile for {user_id}")

            # Сохраняем профиль для обеспечения целостности данных
            self.personalization_manager.save_profile(user_id)

        except Exception as e:
            logger.error(f"Error initializing user profile: {str(e)}")
            # Продолжаем работу даже при ошибке инициализации профиля
            # для обеспечения базовой функциональности

    def _initialize_exploration_strategies(self) -> None:
        """
        Инициализирует стратегии исследования для сбора информации.
        """
        # Стратегия для исследования веб-ресурсов
        if self.browser_access:
            self.web_exploration = WebExplorationStrategy(
                browser_access=self.browser_access,
                file_system=self.file_system,
                text_editor=self.text_editor,
                thought_tree=self.thought_tree
            )
            self.exploration_strategies["web"] = self.web_exploration
            logger.info("Web exploration strategy initialized")

        # Стратегия для исследования файловой системы
        if self.file_system:
            self.file_exploration = FileExplorationStrategy(
                file_system=self.file_system,
                text_editor=self.text_editor,
                thought_tree=self.thought_tree
            )
            self.exploration_strategies["file"] = self.file_exploration
            logger.info("File exploration strategy initialized")

    async def explore_web(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Исследует веб-ресурсы по запросу.

        Args:
            query: Запрос для поиска
            **kwargs: Дополнительные параметры для стратегии

        Returns:
            Результаты исследования
        """
        if not self.web_exploration:
            return {
                "success": False,
                "error": "Web exploration strategy not initialized",
                "query": query
            }

        try:
            # Проверяем разрешение
            if self.permission_manager:
                request = self.permission_manager.request_permission(
                    tool_name="web_exploration",
                    args={"query": query, **kwargs},
                    reason=f"Web exploration for query: {query}"
                )

                if not request.approved:
                    return {
                        "success": False,
                        "error": "Permission denied for web exploration",
                        "query": query
                    }

            # Выполняем исследование
            collection = await self.web_exploration.explore(query, **kwargs)

            # Обрабатываем результаты
            results = await self.web_exploration.process_results(collection)

            return {
                "success": True,
                "collection": collection,
                "results": results,
                "items_count": len(collection.items),
                "query": query
            }

        except Exception as e:
            logger.error(f"Error during web exploration: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def explore_files(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Исследует файловую систему по запросу.

        Args:
            query: Запрос для поиска
            **kwargs: Дополнительные параметры для стратегии

        Returns:
            Результаты исследования
        """
        if not self.file_exploration:
            return {
                "success": False,
                "error": "File exploration strategy not initialized",
                "query": query
            }

        try:
            # Проверяем разрешение
            if self.permission_manager:
                request = self.permission_manager.request_permission(
                    tool_name="file_exploration",
                    args={"query": query, **kwargs},
                    reason=f"File exploration for query: {query}"
                )

                if not request.approved:
                    return {
                        "success": False,
                        "error": "Permission denied for file exploration",
                        "query": query
                    }

            # Выполняем исследование
            collection = await self.file_exploration.explore(query, **kwargs)

            # Обрабатываем результаты
            results = await self.file_exploration.process_results(collection)

            return {
                "success": True,
                "collection": collection,
                "results": results,
                "items_count": len(collection.items),
                "query": query
            }

        except Exception as e:
            logger.error(f"Error during file exploration: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def get_combined_exploration(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Выполняет комбинированное исследование из нескольких источников.

        Args:
            query: Запрос для поиска
            **kwargs: Дополнительные параметры для стратегий

        Returns:
            Комбинированные результаты исследования
        """
        strategies = kwargs.get("strategies", ["file", "web"])
        combined_collection = InformationCollection(name=f"combined_exploration_{int(time.time())}")
        results = {
            "success": True,
            "query": query,
            "strategies_executed": [],
            "items_collected": 0,
            "results_by_strategy": {}
        }

        # Выполняем каждую стратегию
        for strategy_name in strategies:
            if strategy_name not in self.exploration_strategies:
                logger.warning(f"Strategy {strategy_name} not available")
                continue

            strategy = self.exploration_strategies[strategy_name]

            try:
                # Проверяем разрешение
                if self.permission_manager:
                    request = self.permission_manager.request_permission(
                        tool_name=f"{strategy_name}_exploration",
                        args={"query": query},
                        reason=f"{strategy_name.capitalize()} exploration for query: {query}"
                    )

                    if not request.approved:
                        results["results_by_strategy"][strategy_name] = {
                            "success": False,
                            "error": f"Permission denied for {strategy_name} exploration"
                        }
                        continue

                # Выполняем исследование
                collection = await strategy.explore(query, **kwargs)

                # Обрабатываем результаты
                strategy_results = await strategy.process_results(collection)

                # Добавляем в комбинированную коллекцию
                for item_id, item in collection.items.items():
                    combined_collection.add_item(item)

                # Записываем результаты стратегии
                results["strategies_executed"].append(strategy_name)
                results["results_by_strategy"][strategy_name] = {
                    "success": True,
                    "items_count": len(collection.items),
                    "results": strategy_results
                }

            except Exception as e:
                logger.error(f"Error during {strategy_name} exploration: {str(e)}")
                results["results_by_strategy"][strategy_name] = {
                    "success": False,
                    "error": str(e)
                }

        # Обновляем общую статистику
        results["items_collected"] = len(combined_collection.items)
        results["collection"] = combined_collection

        return results

    def _check_required_tools(self) -> List[str]:
        """
        Проверяет наличие всех необходимых инструментов.

        Returns:
            Список отсутствующих инструментов
        """
        available_tools = set(self.mcp_clients.tool_map.keys())
        missing_tools = []

        for tool_name in self.required_tools:
            if tool_name not in available_tools:
                missing_tools.append(tool_name)

        # Дополнительно проверяем наличие сервисов Serena и Sequential Thinking
        if not [tool for tool in available_tools if tool.startswith("mcp_serena_")]:
            missing_tools.append("Serena services")

        if not [tool for tool in available_tools if tool.startswith("mcp_sequential-thinking_")]:
            missing_tools.append("Sequential Thinking services")

        return missing_tools

    async def process_tool_call(self, name: str, **kwargs) -> Any:
        """
        Обрабатывает вызов инструмента.

        Args:
            name: Имя инструмента
            **kwargs: Аргументы инструмента

        Returns:
            Результат выполнения инструмента
        """
        try:
            result = await super().process_tool_call(name, **kwargs)
            return result
        except Exception as e:
            # Логируем ошибку в системе анализа ошибок
            error_id = self._log_error(
                message=str(e),
                source=ErrorSource.TOOL_CALL,
                severity=ErrorSeverity.MEDIUM,
                context={"tool_name": name, "tool_args": kwargs}
            )

            # Возвращаем сообщение об ошибке с идентификатором
            error_message = f"Error executing tool '{name}': {str(e)} [Error ID: {error_id}]"
            logger.error(error_message)

            return {"error": error_message}

    async def execute_with_priority(
        self,
        name: str,
        callback: Callable[..., Awaitable[Any]],
        priority: TaskPriority = TaskPriority.MEDIUM,
        resources: Optional[List[ResourceRequirement]] = None,
        can_be_paused: bool = False,
        progress_callback: Optional[Callable[[float, Any], None]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Выполняет функцию с указанным приоритетом через менеджер ресурсов.

        Args:
            name: Имя операции
            callback: Асинхронная функция для выполнения
            priority: Приоритет операции
            resources: Требования к ресурсам
            can_be_paused: Может ли операция быть приостановлена
            progress_callback: Функция обратного вызова для обновления прогресса
            timeout: Таймаут выполнения в секундах
            **kwargs: Дополнительные аргументы для callback

        Returns:
            Словарь с информацией о созданной задаче
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            task_id = await self.resource_manager.run_long_operation(
                name=name,
                callback=callback,
                priority=priority,
                resources=resources,
                can_be_paused=can_be_paused,
                progress_callback=progress_callback,
                timeout=timeout,
                **kwargs
            )

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Операция '{name}' запущена с приоритетом {priority.name}"
            }
        except Exception as e:
            logger.error(f"Ошибка при выполнении операции {name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Не удалось запустить операцию '{name}'"
            }

    async def get_task_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает информацию о статусе задачи или всех активных задач.

        Args:
            task_id: Идентификатор задачи или None для получения всех активных задач

        Returns:
            Словарь с информацией о задаче или задачах
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            if task_id:
                # Получаем информацию о конкретной задаче
                task_info = self.resource_manager.get_task_with_intermediate_results(task_id)
                if task_info is None:
                    return {"success": False, "error": f"Задача с ID {task_id} не найдена"}

                # Получаем дополнительно дерево подзадач, если это родительская задача
                if task_info.get("subtasks"):
                    task_tree = self.resource_manager.get_task_tree(task_id)
                    task_info["task_tree"] = task_tree

                return {"success": True, "task": task_info}
            else:
                # Получаем информацию обо всех активных задачах
                active_tasks = self.resource_manager.get_active_tasks_with_progress()
                queue = self.resource_manager.get_task_queue_info()
                history = self.resource_manager.get_task_history_info(limit=10)
                system_status = self.resource_manager.get_system_status()

                return {
                    "success": True,
                    "active_tasks": active_tasks,
                    "queue": queue,
                    "history": history,
                    "system_status": system_status
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статуса задач: {str(e)}")
            return {"success": False, "error": str(e)}

    async def cancel_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """
        Отменяет выполнение задачи по ID.

        Args:
            task_id: Идентификатор задачи

        Returns:
            Словарь с результатом операции
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            result = await self.resource_manager.cancel_task(task_id)
            if result:
                return {
                    "success": True,
                    "message": f"Задача с ID {task_id} успешно отменена"
                }
            else:
                return {
                    "success": False,
                    "error": f"Задача с ID {task_id} не найдена или не может быть отменена"
                }
        except Exception as e:
            logger.error(f"Ошибка при отмене задачи {task_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def pause_resume_task(self, task_id: str, pause: bool = True) -> Dict[str, Any]:
        """
        Приостанавливает или возобновляет выполнение задачи.

        Args:
            task_id: Идентификатор задачи
            pause: True для приостановки, False для возобновления

        Returns:
            Словарь с результатом операции
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            if pause:
                result = await self.resource_manager.pause_task(task_id)
                action = "приостановлена"
            else:
                result = await self.resource_manager.resume_task(task_id)
                action = "возобновлена"

            if result:
                return {
                    "success": True,
                    "message": f"Задача с ID {task_id} успешно {action}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Задача с ID {task_id} не найдена или не может быть {action}"
                }
        except Exception as e:
            logger.error(f"Ошибка при изменении статуса задачи {task_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_resource_usage(self) -> Dict[str, Any]:
        """
        Получает информацию об использовании ресурсов.

        Returns:
            Словарь с информацией об использовании ресурсов
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            resources = self.resource_manager.get_resource_usage_info()
            system_status = self.resource_manager.get_system_status()

            # Получаем также данные мониторинга производительности, если доступны
            performance_data = {}
            if hasattr(self.resource_manager, 'performance_monitor') and self.resource_manager.performance_monitor:
                performance_data = self.resource_manager.get_performance_metrics()

            return {
                "success": True,
                "resources": resources,
                "system_status": system_status,
                "performance_metrics": performance_data
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации об использовании ресурсов: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_performance_metrics(self, timespan_seconds: int = 300) -> Dict[str, Any]:
        """
        Получает метрики производительности за указанный период.

        Args:
            timespan_seconds: Период в секундах

        Returns:
            Словарь с метриками производительности
        """
        if self.resource_manager is None or not hasattr(self.resource_manager, 'performance_monitor') or not self.resource_manager.performance_monitor:
            return {"success": False, "error": "Мониторинг производительности не активен"}

        try:
            performance_data = self.resource_manager.get_performance_metrics()

            # Получаем рекомендации по оптимизации
            if hasattr(self.resource_manager.performance_monitor, 'get_optimization_recommendations'):
                recommendations = self.resource_manager.performance_monitor.get_optimization_recommendations()
                performance_data["optimization_recommendations"] = recommendations

            # Получаем последние оповещения
            if hasattr(self.resource_manager.performance_monitor, 'get_recent_alerts'):
                alerts = self.resource_manager.performance_monitor.get_recent_alerts(10)
                performance_data["recent_alerts"] = [
                    {
                        "level": alert.level.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat(),
                        "metric_type": alert.metric_type.value
                    }
                    for alert in alerts
                ]

            return {
                "success": True,
                "performance_data": performance_data,
                "timespan_seconds": timespan_seconds
            }
        except Exception as e:
            logger.error(f"Ошибка при получении метрик производительности: {str(e)}")
            return {"success": False, "error": str(e)}

    async def apply_performance_optimization(self, optimization_id: str) -> Dict[str, Any]:
        """
        Применяет рекомендацию по оптимизации производительности.

        Args:
            optimization_id: Идентификатор оптимизации

        Returns:
            Словарь с результатом применения оптимизации
        """
        if self.resource_manager is None or not hasattr(self.resource_manager, 'apply_performance_optimization'):
            return {"success": False, "error": "Функция оптимизации производительности недоступна"}

        try:
            result = self.resource_manager.apply_performance_optimization(optimization_id)

            # Если применение успешно, записываем в профиль пользователя
            if result.get("success", False) and self.personalization_manager:
                self.personalization_manager.record_interaction(
                    InteractionType.SYSTEM_CONFIG,
                    f"Применена оптимизация производительности: {optimization_id}",
                    {
                        "optimization_id": optimization_id,
                        "details": result.get("message", ""),
                        "old_value": result.get("old_value"),
                        "new_value": result.get("new_value")
                    }
                )

            return result
        except Exception as e:
            logger.error(f"Ошибка при применении оптимизации: {str(e)}")
            return {"success": False, "error": str(e)}

    async def export_performance_data(self, filepath: str, timespan_seconds: int = 3600) -> Dict[str, Any]:
        """
        Экспортирует данные о производительности в JSON-файл.

        Args:
            filepath: Путь к файлу для сохранения
            timespan_seconds: Период в секундах

        Returns:
            Словарь с результатом экспорта
        """
        if self.resource_manager is None or not hasattr(self.resource_manager, 'export_performance_data'):
            return {"success": False, "error": "Функция экспорта данных о производительности недоступна"}

        try:
            result = self.resource_manager.export_performance_data(filepath, timespan_seconds)
            return result
        except Exception as e:
            logger.error(f"Ошибка при экспорте данных о производительности: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_resource_usage_report(self) -> Dict[str, Any]:
        """
        Формирует отчет об использовании ресурсов с рекомендациями по оптимизации.

        Returns:
            Словарь с отчетом об использовании ресурсов
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            # Получаем базовую информацию о ресурсах
            resource_info = self.resource_manager.get_resource_usage_info()
            system_status = self.resource_manager.get_system_status()

            # Получаем метрики производительности, если доступны
            performance_data = {}
            has_performance_data = False

            if hasattr(self.resource_manager, 'performance_monitor') and self.resource_manager.performance_monitor:
                performance_data = self.resource_manager.get_performance_metrics()
                has_performance_data = True

            # Формируем рекомендации
            recommendations = []

            # Проверяем загрузку ресурсов
            for resource_type, info in resource_info.items():
                utilization = info.get("allocated", 0) / info.get("capacity", 1) if info.get("capacity", 0) > 0 else 0

                if utilization > 0.9:
                    recommendations.append({
                        "type": "resource_warning",
                        "resource": resource_type,
                        "message": f"Высокая загрузка ресурса {resource_type} ({utilization:.1%})",
                        "priority": "high"
                    })
                elif utilization < 0.1 and info.get("capacity", 0) > 0.5:
                    recommendations.append({
                        "type": "resource_info",
                        "resource": resource_type,
                        "message": f"Низкая загрузка ресурса {resource_type} ({utilization:.1%}). Возможно, емкость может быть уменьшена.",
                        "priority": "low"
                    })

            # Проверяем баланс очереди задач
            queue_length = system_status.get("queue_length", 0)
            active_tasks = system_status.get("active_tasks", 0)
            max_concurrent = system_status.get("max_concurrent_tasks", 5)

            if queue_length > max_concurrent * 2 and active_tasks >= max_concurrent:
                recommendations.append({
                    "type": "queue_warning",
                    "message": f"Большая очередь задач ({queue_length}) при максимальном количестве одновременных задач {max_concurrent}",
                    "priority": "medium",
                    "suggested_action": "increase_concurrent_tasks"
                })

            # Добавляем рекомендации из монитора производительности
            if has_performance_data and performance_data.get("optimization_recommendations"):
                for rec in performance_data.get("optimization_recommendations", []):
                    recommendations.append(rec)

            # Формируем итоговый отчет
            report = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "resources": resource_info,
                "system_status": system_status,
                "has_performance_data": has_performance_data,
                "recommendations": recommendations,
                "summary": {
                    "total_resources": len(resource_info),
                    "active_tasks": active_tasks,
                    "queued_tasks": queue_length,
                    "recommendation_count": len(recommendations)
                }
            }

            if has_performance_data:
                report["performance_data"] = performance_data

            return report
        except Exception as e:
            logger.error(f"Ошибка при формировании отчета об использовании ресурсов: {str(e)}")
            return {"success": False, "error": str(e)}

    async def create_task_group(self, name: str, tasks: List[Dict[str, Any]], priority: TaskPriority = TaskPriority.MEDIUM) -> Dict[str, Any]:
        """
        Создает группу связанных задач с общим родителем.

        Args:
            name: Имя группы задач
            tasks: Список словарей с параметрами задач
            priority: Приоритет родительской задачи

        Returns:
            Словарь с результатом операции
        """
        if self.resource_manager is None:
            return {"success": False, "error": "Менеджер ресурсов не инициализирован"}

        try:
            # Создаем пустую родительскую задачу как контейнер
            async def parent_task_handler():
                # Задача-контейнер просто ждет завершения всех подзадач
                return {"completed": True}

            # Создаем родительскую задачу
            parent_task = Task(
                task_id=f"group_{int(time.time())}_{name.replace(' ', '_')}",
                name=f"Группа задач: {name}",
                priority=priority,
                resources=[],  # Родительская задача не требует ресурсов
                callback=parent_task_handler,
                can_be_paused=False
            )

            parent_id = await self.resource_manager.add_task(parent_task)
            logger.info(f"Создана группа задач '{name}' с ID {parent_id}")

            # Создаем подзадачи
            subtask_ids = []
            for task_info in tasks:
                try:
                    subtask = Task(
                        task_id=f"subtask_{int(time.time())}_{task_info.get('name', 'task').replace(' ', '_')}",
                        name=task_info.get("name", "Подзадача"),
                        priority=task_info.get("priority", TaskPriority.MEDIUM),
                        resources=task_info.get("resources", []),
                        callback=task_info["callback"],
                        args=task_info.get("args", ()),
                        kwargs=task_info.get("kwargs", {}),
                        timeout=task_info.get("timeout"),
                        can_be_paused=task_info.get("can_be_paused", False),
                        progress_callback=task_info.get("progress_callback")
                    )

                    subtask_id = await self.resource_manager.create_subtask(parent_id, subtask)
                    subtask_ids.append(subtask_id)
                except Exception as e:
                    logger.error(f"Ошибка при создании подзадачи: {str(e)}")

            return {
                "success": True,
                "group_id": parent_id,
                "subtask_ids": subtask_ids,
                "message": f"Создана группа задач '{name}' с {len(subtask_ids)} подзадачами"
            }
        except Exception as e:
            logger.error(f"Ошибка при создании группы задач: {str(e)}")
            return {"success": False, "error": str(e)}

    async def create_plan(self, task_description: str) -> Dict[str, Any]:
        """
        Создает план выполнения задачи с учетом предыдущего опыта.

        Args:
            task_description: Описание задачи

        Returns:
            План выполнения задачи
        """
        # Используем адаптацию предыдущего опыта, если доступна
        planning_params = {}
        if self.experience_adapter:
            try:
                adapted_params = await self.experience_adapter.adapt_planning_parameters(task_description)
                planning_params = adapted_params
                logger.info(f"Параметры планирования адаптированы для задачи: {task_description[:50]}...")
            except Exception as e:
                logger.error(f"Ошибка при адаптации параметров планирования: {str(e)}")

        # Список ресурсов для планирования
        resources = [
            ResourceRequirement(ResourceType.CPU, amount=0.3, min_amount=0.1),
            ResourceRequirement(ResourceType.MEMORY, amount=0.3, min_amount=0.1),
            ResourceRequirement(ResourceType.LLM_CALL, amount=0.5, min_amount=0.3)
        ]

        # Выполняем планирование с приоритетом
        try:
            # Определяем функцию, которая будет выполнена с приоритетом
            async def _planning_task():
                # Здесь логика планирования
                # Вызываем self.planning_strategy.create_plan, если он инициализирован
                # или используем базовый подход к планированию
                if self.planning_strategy:
                    plan = await self.planning_strategy.create_plan(task_description, params=planning_params)
                    return plan
                else:
                    # Базовый план, если стратегия планирования недоступна
                    return {
                        "task": task_description,
                        "steps": ["Шаг 1: Анализ задачи", "Шаг 2: Разработка решения", "Шаг 3: Реализация"],
                        "approach": "structured",
                        "estimated_time": "10 минут",
                        "success_metrics": ["Корректность результата", "Эффективность"],
                        "adapted_parameters": planning_params
                    }

            # Выполняем с приоритетом
            result = await self.execute_with_priority(
                _planning_task,
                TaskPriority.HIGH,  # Планирование имеет высокий приоритет
                resources,
                f"Планирование: {task_description[:30]}..."
            )

            # Записываем успешное планирование в персонализацию, если она доступна
            if self.personalization_manager:
                self.personalization_manager.record_interaction(
                    InteractionType.PLANNING,
                    task_description,
                    {
                        "success": True,
                        "approach": result.get("approach", ""),
                        "steps_count": len(result.get("steps", [])),
                        "adapted": planning_params != {}
                    }
                )

            return result
        except Exception as e:
            logger.error(f"Ошибка при создании плана: {str(e)}")
            # Записываем неудачное планирование, если персонализация доступна
            if self.personalization_manager:
                self.personalization_manager.record_interaction(
                    InteractionType.PLANNING,
                    task_description,
                    {
                        "success": False,
                        "error": str(e)
                    }
                )

            # Возвращаем базовый план в случае ошибки
            return {
                "task": task_description,
                "steps": ["Анализ", "Реализация", "Проверка"],
                "error": str(e)
            }

    async def get_personalized_parameters(self) -> Dict[str, Any]:
        """
        Получает персонализированные параметры для адаптации поведения агента.

        Returns:
            Словарь с персонализированными параметрами
        """
        if not self.personalization_manager:
            return {
                "personalized": False,
                "verbosity": 0.5,
                "code_comments": 0.5,
                "risk_tolerance": 0.3
            }

        try:
            return self.personalization_manager.get_personalized_parameters()
        except Exception as e:
            logger.error(f"Error getting personalized parameters: {str(e)}")
            return {
                "personalized": False,
                "verbosity": 0.5,
                "code_comments": 0.5,
                "risk_tolerance": 0.3
            }

    async def export_user_experience(self, output_path: str) -> Dict[str, Any]:
        """
        Экспортирует накопленный пользовательский опыт в файл.

        Args:
            output_path: Путь для сохранения файла

        Returns:
            Словарь с результатом операции
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            # Получаем активный профиль
            profile = self.personalization_manager.get_active_profile()
            if not profile:
                return {
                    "success": False,
                    "error": "No active user profile"
                }

            # Экспортируем профиль
            success = self.personalization_manager.export_profile(profile.user_id, output_path)

            if success:
                return {
                    "success": True,
                    "message": f"User experience exported to {output_path}",
                    "path": output_path,
                    "user_id": profile.user_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to export user experience to {output_path}"
                }
        except Exception as e:
            error_msg = f"Error exporting user experience: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def import_user_experience(self, input_path: str) -> Dict[str, Any]:
        """
        Импортирует пользовательский опыт из файла.

        Args:
            input_path: Путь к файлу опыта

        Returns:
            Словарь с результатом операции
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            # Импортируем профиль
            user_id = self.personalization_manager.import_profile(input_path)

            if user_id:
                # Устанавливаем импортированный профиль как активный
                self.personalization_manager.set_active_profile(user_id)

                return {
                    "success": True,
                    "message": f"User experience imported from {input_path}",
                    "path": input_path,
                    "user_id": user_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to import user experience from {input_path}"
                }
        except Exception as e:
            error_msg = f"Error importing user experience: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def merge_user_experiences(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Объединяет два пользовательских профиля опыта.

        Args:
            source_id: Идентификатор профиля-источника
            target_id: Идентификатор целевого профиля

        Returns:
            Словарь с результатом операции
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            # Проверяем наличие профилей
            source_profile = self.personalization_manager.get_profile(source_id)
            if not source_profile:
                # Пытаемся загрузить профиль, если он не загружен
                source_profile = self.personalization_manager.load_profile(source_id)
                if not source_profile:
                    return {
                        "success": False,
                        "error": f"Source profile {source_id} not found"
                    }

            target_profile = self.personalization_manager.get_profile(target_id)
            if not target_profile:
                # Пытаемся загрузить профиль, если он не загружен
                target_profile = self.personalization_manager.load_profile(target_id)
                if not target_profile:
                    return {
                        "success": False,
                        "error": f"Target profile {target_id} not found"
                    }

            # Объединяем профили
            success = self.personalization_manager.merge_profiles(source_id, target_id)

            if success:
                # Сохраняем результат объединения
                self.personalization_manager.save_profile(target_id)

                return {
                    "success": True,
                    "message": f"User experiences merged from {source_id} to {target_id}",
                    "source_id": source_id,
                    "target_id": target_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to merge user experiences"
                }
        except Exception as e:
            error_msg = f"Error merging user experiences: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def get_user_preferences(self) -> Dict[str, Any]:
        """
        Получает текущие предпочтения пользователя.

        Returns:
            Словарь с предпочтениями пользователя
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            profile = self.personalization_manager.get_active_profile()
            if not profile:
                return {
                    "success": False,
                    "error": "No active user profile"
                }

            preferences = {}
            for pref_id, preference in profile.preferences.items():
                preferences[pref_id] = {
                    "name": preference.name,
                    "value": preference.value,
                    "confidence": preference.confidence,
                    "last_updated": preference.last_updated.isoformat()
                }

            return {
                "success": True,
                "preferences": preferences,
                "user_id": profile.user_id
            }
        except Exception as e:
            error_msg = f"Error getting user preferences: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def update_user_preference(
        self,
        preference_id: str,
        value: float,
        explicit: bool = True
    ) -> Dict[str, Any]:
        """
        Обновляет предпочтение пользователя.

        Args:
            preference_id: Идентификатор предпочтения
            value: Новое значение (от 0.0 до 1.0)
            explicit: Флаг явного обновления (пользователем)

        Returns:
            Словарь с результатом операции
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            profile = self.personalization_manager.get_active_profile()
            if not profile:
                return {
                    "success": False,
                    "error": "No active user profile"
                }

            # Проверяем наличие предпочтения
            if preference_id not in profile.preferences:
                return {
                    "success": False,
                    "error": f"Preference {preference_id} not found"
                }

            # Определяем уверенность в зависимости от источника
            confidence = 0.9 if explicit else 0.5

            # Обновляем предпочтение
            preference = profile.preferences[preference_id]
            profile.set_preference(preference_id, preference.name, value, confidence)

            # Записываем обновление в историю взаимодействий
            if explicit:
                self.personalization_manager.record_interaction(
                    InteractionType.FEEDBACK,
                    f"Обновление предпочтения {preference.name}",
                    {
                        "feedback_type": preference_id,
                        "value": value,
                        "previous_value": preference.value
                    }
                )

            # Сохраняем обновленный профиль
            self.personalization_manager.save_profile()

            return {
                "success": True,
                "message": f"Preference {preference_id} updated",
                "preference_id": preference_id,
                "new_value": value,
                "previous_value": preference.value
            }
        except Exception as e:
            error_msg = f"Error updating user preference: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def list_available_user_profiles(self) -> Dict[str, Any]:
        """
        Получает список доступных профилей пользователей.

        Returns:
            Словарь со списком профилей
        """
        if not self.personalization_manager:
            return {
                "success": False,
                "error": "Personalization manager not initialized"
            }

        try:
            profiles = self.personalization_manager.list_profiles()
            return {
                "success": True,
                "profiles": profiles,
                "active_profile_id": self.personalization_manager.active_profile_id
            }
        except Exception as e:
            error_msg = f"Error listing user profiles: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def export_all_experience(self,
                                   archive_name: str,
                                   include_errors: bool = True) -> Dict[str, Any]:
        """
        Экспортирует весь накопленный опыт в архив.

        Args:
            archive_name: Имя архива
            include_errors: Включать ли данные об ошибках

        Returns:
            Словарь с результатами операции
        """
        if not self.experience_archive:
            return {
                "success": False,
                "error": "Архив опыта не инициализирован"
            }

        try:
            # Сначала сохраняем текущий активный профиль
            if self.personalization_manager and self.personalization_manager.active_profile_id:
                self.personalization_manager.save_profile()

            # Создаем архив со всеми профилями
            result = self.experience_archive.create_archive(
                archive_name=archive_name,
                profiles_to_include=None,  # все профили
                include_errors=include_errors,
                include_metadata=True
            )

            return result

        except Exception as e:
            error_msg = f"Ошибка экспорта опыта: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def import_all_experience(self,
                                   archive_path: str,
                                   merge_with_existing: bool = True) -> Dict[str, Any]:
        """
        Импортирует весь накопленный опыт из архива.

        Args:
            archive_path: Путь к архиву
            merge_with_existing: Объединять с существующими данными

        Returns:
            Словарь с результатами операции
        """
        if not self.experience_archive:
            return {
                "success": False,
                "error": "Архив опыта не инициализирован"
            }

        try:
            # Импортируем архив
            result = self.experience_archive.import_archive(
                archive_path=archive_path,
                import_profiles=True,
                import_errors=True,
                merge_existing=merge_with_existing
            )

            # Если импорт успешен и есть активный профиль, сохраняем его
            if result["success"] and self.personalization_manager and self.personalization_manager.active_profile_id:
                self.personalization_manager.save_profile()

            return result

        except Exception as e:
            error_msg = f"Ошибка импорта опыта: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def get_experience_archives_list(self) -> Dict[str, Any]:
        """
        Получает список доступных архивов опыта.

        Returns:
            Словарь со списком архивов
        """
        if not self.experience_archive:
            return {
                "success": False,
                "error": "Архив опыта не инициализирован",
                "archives": []
            }

        try:
            archives = self.experience_archive.list_archives()

            return {
                "success": True,
                "archives": archives,
                "count": len(archives)
            }

        except Exception as e:
            error_msg = f"Ошибка получения списка архивов: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "archives": []
            }

    async def get_experience_statistics(self, archive_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает статистику опыта из архива или текущего состояния.

        Args:
            archive_path: Путь к архиву (None для текущего состояния)

        Returns:
            Словарь со статистикой
        """
        if not self.experience_archive:
            return {
                "success": False,
                "error": "Архив опыта не инициализирован"
            }

        try:
            if archive_path:
                # Получаем статистику из архива
                statistics = self.experience_archive.extract_aggregate_statistics(archive_path)

                return {
                    "success": True,
                    "statistics": statistics,
                    "source": "archive",
                    "archive_path": archive_path
                }
            else:
                # Получаем статистику текущего состояния

                # Создаем временный архив
                import tempfile
                import os

                temp_dir = tempfile.mkdtemp()
                temp_archive_path = os.path.join(temp_dir, "temp_archive.zip")

                # Сохраняем текущий активный профиль
                if self.personalization_manager and self.personalization_manager.active_profile_id:
                    self.personalization_manager.save_profile()

                # Создаем временный архив
                create_result = self.experience_archive.create_archive(
                    archive_name="temp",
                    profiles_to_include=None,
                    include_errors=True,
                    include_metadata=True
                )

                if not create_result["success"]:
                    return {
                        "success": False,
                        "error": f"Ошибка создания временного архива: {create_result.get('error', 'Неизвестная ошибка')}",
                    }

                # Получаем статистику из временного архива
                statistics = self.experience_archive.extract_aggregate_statistics(create_result["archive_path"])

                # Удаляем временный архив
                os.remove(create_result["archive_path"])

                return {
                    "success": True,
                    "statistics": statistics,
                    "source": "current"
                }

        except Exception as e:
            error_msg = f"Ошибка получения статистики опыта: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def get_error_prevention_for_task(self, task: str, approach: str) -> Dict[str, Any]:
        """
        Получает рекомендации по предотвращению ошибок для задачи.

        Args:
            task: Текущая задача
            approach: Выбранный подход

        Returns:
            Словарь с рекомендациями
        """
        if not self.experience_adapter:
            return {
                "success": False,
                "error": "Experience adapter not initialized",
                "tips": []
            }

        try:
            tips = await self.experience_adapter.get_error_prevention_tips(task, approach)

            return {
                "success": True,
                "tips": tips,
                "count": len(tips)
            }
        except Exception as e:
            logger.error(f"Error getting error prevention tips: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tips": []
            }

    async def get_experience_based_suggestions(self, task: str) -> Dict[str, Any]:
        """
        Получает предложения на основе предыдущего опыта для задачи.

        Args:
            task: Текущая задача

        Returns:
            Словарь с предложениями
        """
        if not self.experience_adapter:
            return {
                "success": False,
                "error": "Experience adapter not initialized",
                "suggestions": []
            }

        try:
            suggestions = await self.experience_adapter.analyze_current_task(task)

            result = {
                "success": True,
                "suggestions": [],
                "count": len(suggestions)
            }

            for suggestion in suggestions:
                result["suggestions"].append({
                    "type": suggestion.suggestion_type,
                    "suggestion": suggestion.suggestion,
                    "confidence": suggestion.confidence,
                    "reasoning": suggestion.reasoning,
                    "source": suggestion.source
                })

            return result
        except Exception as e:
            logger.error(f"Error getting experience-based suggestions: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": []
            }

    async def improve_solution(self, task: str, initial_solution: str) -> Dict[str, Any]:
        """
        Улучшает решение задачи на основе предыдущего опыта.

        Args:
            task: Текущая задача
            initial_solution: Начальное решение

        Returns:
            Словарь с улучшенным решением
        """
        if not self.experience_adapter:
            return {
                "success": False,
                "error": "Experience adapter not initialized",
                "improved_solution": initial_solution,
                "has_improvement": False
            }

        try:
            result = await self.experience_adapter.get_improved_solution(task, initial_solution)

            if not result:
                return {
                    "success": True,
                    "improved_solution": initial_solution,
                    "has_improvement": False,
                    "message": "Невозможно улучшить текущее решение на основе предыдущего опыта"
                }

            return {
                "success": True,
                **result
            }
        except Exception as e:
            logger.error(f"Error improving solution: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "improved_solution": initial_solution,
                "has_improvement": False
            }
