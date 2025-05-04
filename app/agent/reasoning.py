"""
Reasoning Agent для GopiAI

Агент с интегрированными стратегиями мышления Serena и Sequential Thinking.
Выполняет действия по системе "План → Разрешение → Выполнение".
"""

import asyncio
import os
from typing import Any, Dict, List, Optional, Tuple, Set

from pydantic import Field

from app.agent.mcp import MCPAgent
from app.agent.terminal_access import TerminalAccess  # Импортируем класс TerminalAccess
from app.agent.browser_access import BrowserAccess  # Импортируем класс BrowserAccess
from app.agent.file_system_access import FileSystemAccess  # Импортируем класс FileSystemAccess
from app.agent.permission_manager import PermissionManager  # Импортируем новый менеджер разрешений
from app.config import config
from app.config.reasoning_config import ReasoningStrategy
from app.logger import logger
from app.mcp.sequential_thinking import SequentialThinking
from app.mcp.serena_integration import SerenaIntegration  # Импортируем новый класс интеграции с Serena
from app.schema import AgentState, Message
from app.prompt.reasoning import (
    REASONING_SYSTEM_PROMPT,
    PLAN_CREATION_PROMPT,
    APPROVAL_REQUIRED_MESSAGE,
    EXECUTION_BLOCKED_MESSAGE
)


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
    required_tools: List[str] = Field(default_factory=lambda: [
        "mcp_serena_initial_instructions",  # Serena необходим
        "mcp_sequential-thinking_sequentialthinking",  # Sequential Thinking необходим
    ])

    # Состояние для утверждения плана
    current_plan: Optional[str] = None

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

    # Permission Manager
    permission_manager: Optional[PermissionManager] = None

    async def initialize(
        self,
        connection_type: Optional[str] = None,
        server_url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
    ) -> None:
        """
        Инициализирует агента и проверяет наличие необходимых модулей.

        Args:
            connection_type: Тип подключения ("stdio" или "sse")
            server_url: URL MCP сервера (для SSE подключения)
            command: Команда для запуска (для stdio подключения)
            args: Аргументы для команды (для stdio подключения)

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

        # Создаем клиент Sequential Thinking и инициализируем его
        self.sequential_thinking = SequentialThinking(self.mcp_clients)
        sequential_thinking_initialized = await self.sequential_thinking.initialize()
        if not sequential_thinking_initialized:
            error_msg = "Failed to initialize Sequential Thinking module"
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            logger.info("Sequential Thinking integration initialized successfully")

        # Создаем и инициализируем интеграцию с Serena
        self.serena = SerenaIntegration(self.mcp_clients)
        serena_initialized = await self.serena.initialize()
        if not serena_initialized:
            logger.warning("Serena integration initialized with warnings, some features may be limited")
        else:
            logger.info("Serena integration initialized successfully")

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
        headless = browser_config.headless if browser_config else False

        self.browser_access = BrowserAccess(
            safe_mode=safe_mode,
            headless=headless
        )
        logger.info("Browser access module initialized")

        # Инициализируем модуль доступа к файловой системе с учетом настроек
        self.file_system = FileSystemAccess(
            root_dir=os.getcwd(),
            safe_mode=safe_mode,
            max_file_size=15 * 1024 * 1024,  # 15 MB
            chat_paths_enabled=True
        )
        logger.info("File system access module initialized")

        # Добавляем в системное сообщение информацию о режиме reasoning
        self.memory.add_message(
            Message.system_message(
                "You are now in reasoning mode. You must first create a plan, "
                "get approval, and then execute the approved plan."
            )
        )

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

        return missing_tools

    async def process_tool_call(self, name: str, **kwargs) -> Any:
        """
        Обрабатывает вызов инструмента с проверкой разрешений через менеджер разрешений.
        Добавлена интеграция с Serena для обработки Serena-специфичных инструментов.

        Args:
            name: Имя инструмента
            **kwargs: Аргументы для инструмента

        Returns:
            Результат выполнения инструмента

        Raises:
            ValueError: Если использование инструмента запрещено без одобрения плана
        """
        # Используем менеджер разрешений для проверки доступа
        if self.permission_manager:
            # Создаем запрос на разрешение
            explanation = kwargs.get("explanation", "")
            request = self.permission_manager.request_permission(
                tool_name=name,
                args=kwargs,
                reason=explanation
            )

            # Если действие не разрешено
            if not request.approved:
                error_msg = EXECUTION_BLOCKED_MESSAGE.format(tool_name=name)
                logger.warning(error_msg)

                # Добавляем сообщение системы об ошибке
                self.memory.add_message(
                    Message.system_message(error_msg)
                )

                # Возвращаем сообщение об ошибке вместо выполнения инструмента
                return {
                    "status": "error",
                    "message": error_msg
                }

        # Проверяем инструменты Serena
        if name.startswith("mcp_serena_") and self.serena and self.serena.is_available():
            # Логируем запрос к Serena инструменту
            logger.info(f"Processing Serena tool: {name}, args: {kwargs}")

            # Перенаправляем вызов на прямой вызов через SerenaIntegration
            if name == "mcp_serena_read_file":
                return await self.serena.read_file(
                    relative_path=kwargs.get("relative_path", ""),
                    start_line=kwargs.get("start_line", 0),
                    end_line=kwargs.get("end_line", None),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_create_text_file":
                return await self.serena.create_text_file(
                    relative_path=kwargs.get("relative_path", ""),
                    content=kwargs.get("content", "")
                )
            elif name == "mcp_serena_list_dir":
                return await self.serena.list_dir(
                    relative_path=kwargs.get("relative_path", "."),
                    recursive=kwargs.get("recursive", False),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_get_symbols_overview":
                return await self.serena.get_symbols_overview(
                    relative_path=kwargs.get("relative_path", "."),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_find_symbol":
                return await self.serena.find_symbol(
                    name=kwargs.get("name", ""),
                    depth=kwargs.get("depth", 0),
                    include_body=kwargs.get("include_body", False),
                    substring_matching=kwargs.get("substring_matching", False),
                    within_relative_path=kwargs.get("within_relative_path", None),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_find_referencing_symbols":
                return await self.serena.find_referencing_symbols(
                    relative_path=kwargs.get("relative_path", ""),
                    line=kwargs.get("line", 0),
                    column=kwargs.get("column", 0),
                    include_body=kwargs.get("include_body", False),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_read_memory":
                return await self.serena.read_memory(
                    memory_file_name=kwargs.get("memory_file_name", ""),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )
            elif name == "mcp_serena_write_memory":
                return await self.serena.write_memory(
                    memory_file_name=kwargs.get("memory_file_name", ""),
                    content=kwargs.get("content", ""),
                    max_answer_chars=kwargs.get("max_answer_chars", 200000)
                )

        # Проверяем инструменты Sequential Thinking
        if name == "mcp_sequential-thinking_sequentialthinking" and self.sequential_thinking and self.sequential_thinking.is_available():
            # Логируем запрос к Sequential Thinking инструменту
            logger.info(f"Processing Sequential Thinking tool, args: {kwargs}")

            # Прямое использование Sequential Thinking через MCP
            return await self.mcp_clients.call_tool(name, kwargs)

        # Специальные инструменты Sequential Thinking через наш интерфейс
        if self.sequential_thinking and self.sequential_thinking.is_available():
            if name == "analyze_problem":
                return await self.sequential_thinking.analyze_problem(
                    problem_description=kwargs.get("problem_description", ""),
                    depth=kwargs.get("depth", 5)
                )
            elif name == "evaluate_solution":
                return await self.sequential_thinking.evaluate_solution(
                    problem=kwargs.get("problem", ""),
                    solution=kwargs.get("solution", ""),
                    criteria=kwargs.get("criteria", None)
                )
            elif name == "generate_structured_output":
                return await self.sequential_thinking.generate_structured_output(
                    task=kwargs.get("task", ""),
                    output_format=kwargs.get("output_format", {}),
                    depth=kwargs.get("depth", 5)
                )
            elif name == "branching_analysis":
                return await self.sequential_thinking.branching_analysis(
                    question=kwargs.get("question", ""),
                    options=kwargs.get("options", []),
                    depth_per_option=kwargs.get("depth_per_option", 3)
                )

        # Специальная обработка для запуска команд терминала
        if name == "run_terminal_cmd" and self.terminal_access:
            command = kwargs.get("command", "")
            is_background = kwargs.get("is_background", False)
            explanation = kwargs.get("explanation", "")

            # Логируем запрос на выполнение команды
            logger.info(f"Terminal command requested: {command}, bg: {is_background}, reason: {explanation}")

            # Выполняем команду через наш безопасный TerminalAccess
            result = await self.terminal_access.execute_command(
                command=command,
                working_dir=None,  # Используем текущую директорию
                timeout=None if is_background else 30.0,  # Для фоновых задач без таймаута
            )

            # Формируем ответ в формате, ожидаемом от run_terminal_cmd
            return {
                "exit_code": result.get("return_code", 1),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "success": result.get("success", False)
            }

        # Специальная обработка для браузерных инструментов
        if name == "browser_use" and self.browser_access:
            action = kwargs.get("action", "")

            # Удаляем action из kwargs для передачи остальных параметров
            action_params = kwargs.copy()
            if "action" in action_params:
                del action_params["action"]

            # Логируем запрос на выполнение браузерного действия
            logger.info(f"Browser action requested: {action}, params: {action_params}")

            # Выполняем действие через наш безопасный BrowserAccess
            return await self.browser_access.execute_action(action, **action_params)

        # Специальная обработка для файловых операций
        if name == "read_file" and self.file_system:
            target_file = kwargs.get("target_file", "")
            offset = kwargs.get("offset", 0)
            limit = kwargs.get("limit", 0)
            should_read_entire_file = kwargs.get("should_read_entire_file", False)

            # Логируем запрос на чтение файла
            logger.info(f"File read requested: {target_file}, offset={offset}, limit={limit}, entire={should_read_entire_file}")

            # Преобразуем путь при необходимости
            file_path = self.file_system.resolve_path(target_file)

            if should_read_entire_file:
                result = await self.read_file_content(file_path)
                content = result.get("content", "")
                return {
                    "content": content,
                    "status": "success" if content else "error"
                }
            else:
                # Считаем конкретные строки
                result = await self.file_system.read_file_lines(
                    file_path=file_path,
                    start_line=offset,
                    end_line=offset + limit if limit > 0 else None
                )
                return {
                    "content": result.get("content", ""),
                    "status": "success" if result.get("success", False) else "error"
                }

        # Обычные инструменты MCP передаем базовому классу
        return await super().process_tool_call(name, **kwargs)

    async def create_plan(self, task: str) -> str:
        """
        Создает план действий для выполнения задачи.

        Args:
            task: Описание задачи

        Returns:
            Созданный план
        """
        # Используем Sequential Thinking для создания плана
        if not self.sequential_thinking:
            raise ValueError("Sequential Thinking module not initialized")

        logger.info(f"Creating plan for task: {task}")

        # Сбрасываем текущий план и разрешения
        self.current_plan = None
        if self.permission_manager:
            self.permission_manager.reject_plan()

        # Формируем промпт для создания плана
        plan_prompt = PLAN_CREATION_PROMPT.format(task=task)

        # Запускаем цепочку рассуждений для создания плана
        reasonings = await self.sequential_thinking.run_thinking_chain(
            initial_thought=f"Let's create a plan to accomplish the task: {task}",
            max_steps=config.reasoning_config.reasoning_depth
        )

        # Собираем мысли в единый план
        thoughts = []
        for thought_step in reasonings:
            if "thought" in thought_step:
                thoughts.append(thought_step["thought"])

        # Формируем финальный план
        plan_parts = [
            f"# План выполнения задачи\n",
            f"## Задача\n{task}\n",
            "## Шаги выполнения\n",
        ]

        # Добавляем каждую мысль как часть плана
        for i, thought in enumerate(thoughts, 1):
            plan_parts.append(f"### Шаг {i}\n{thought}\n")

        # Добавляем заключение
        plan_parts.append(
            "## Риски и их смягчение\n"
            "- Потенциальные конфликты с существующим кодом - будет произведено тестирование\n"
            "- Потеря данных - резервное копирование перед изменениями\n"
            "- Проблемы с производительностью - профилирование после внедрения\n"
        )

        # Добавляем список нужных инструментов
        tools_needed = [
            "codebase_search",
            "read_file",
            "edit_file",
            "run_terminal_cmd",
        ]
        plan_parts.append("## Необходимые инструменты\n")
        for tool in tools_needed:
            plan_parts.append(f"- {tool}\n")

        # Собираем финальный план
        final_plan = "".join(plan_parts)
        self.current_plan = final_plan

        # Добавляем подсказку о необходимости одобрения
        final_response = final_plan + "\n\n" + APPROVAL_REQUIRED_MESSAGE

        # Добавляем сообщение о плане в историю
        self.memory.add_message(
            Message.system_message(
                "A plan has been created and is waiting for approval."
            )
        )

        return final_response

    def approve_plan(self) -> None:
        """Одобряет текущий план и разрешает выполнение действий"""
        if not self.current_plan:
            logger.warning("No plan to approve")
            return

        # Используем менеджер разрешений для одобрения плана
        if self.permission_manager:
            self.permission_manager.approve_plan()

        # Добавляем сообщение в историю
        self.memory.add_message(
            Message.system_message(
                "Your plan has been approved. You may now proceed with execution."
            )
        )

        logger.info("Plan approved")

    def reject_plan(self) -> None:
        """Отклоняет текущий план"""
        # Используем менеджер разрешений для отклонения плана
        if self.permission_manager:
            self.permission_manager.reject_plan()

        # Сбрасываем текущий план
        self.current_plan = None

        # Добавляем сообщение в историю
        self.memory.add_message(
            Message.system_message(
                "Your plan has been rejected. Please reconsider your approach and create a new plan."
            )
        )

        logger.info("Plan rejected")

    async def get_step_reasoning(self, step_description: str) -> str:
        """
        Получает подробное рассуждение для конкретного шага плана.

        Args:
            step_description: Описание шага

        Returns:
            Подробное рассуждение
        """
        if self.sequential_thinking is None:
            return "Sequential Thinking не инициализирован"

        # Запускаем цепочку рассуждений для шага
        initial_thought = f"Analyzing step: {step_description}"
        thoughts = await self.sequential_thinking.run_thinking_chain(
            initial_thought=initial_thought,
            max_steps=3
        )

        # Формируем рассуждение
        reasoning = "## Анализ шага\n\n"
        for i, thought_record in enumerate(thoughts):
            thought = thought_record.get("thought", "")
            reasoning += f"### Рассуждение {i+1}\n{thought}\n\n"

        return reasoning

    async def execute_terminal_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет команду в терминале через модуль TerminalAccess.

        Args:
            command: Команда для выполнения
            working_dir: Рабочая директория для выполнения команды
            timeout: Таймаут выполнения в секундах

        Returns:
            Словарь с результатами выполнения
        """
        if self.terminal_access is None:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Terminal access module not initialized",
                "command": command
            }

        # Проверяем, одобрен ли план
        if not self.current_plan:
            error_msg = "Cannot execute terminal commands without plan approval."
            logger.warning(error_msg)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_msg,
                "command": command
            }

        # Используем таймаут из конфигурации, если не указан явно
        if timeout is None:
            timeout = config.reasoning_config.operation_timeout

        # Логируем и выполняем команду
        logger.info(f"Executing terminal command: {command}")
        result = await self.terminal_access.execute_command(command, working_dir, timeout)

        # В режиме мониторинга добавляем информацию о выполнении в историю
        if config.reasoning_config.monitoring_enabled:
            monitoring_msg = f"Terminal command executed: {command}\n"
            monitoring_msg += f"Success: {result['success']}\n"
            if result["success"]:
                monitoring_msg += f"Output: {result['stdout'][:200]}...\n"
            else:
                monitoring_msg += f"Error: {result['stderr']}\n"

            self.memory.add_message(
                Message.system_message(monitoring_msg)
            )

        return result

    async def execute_browser_action(
        self,
        action: str,
        **action_params,
    ) -> Dict[str, Any]:
        """
        Безопасно выполняет действие в браузере через модуль BrowserAccess.

        Args:
            action: Тип действия (navigate, click, etc.)
            **action_params: Параметры действия

        Returns:
            Словарь с результатами выполнения
        """
        if self.browser_access is None:
            return {
                "success": False,
                "output": "",
                "error": "Browser access module not initialized",
                "action": action
            }

        # Проверяем, одобрен ли план
        if not self.current_plan:
            error_msg = "Cannot execute browser actions without plan approval."
            logger.warning(error_msg)
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "action": action
            }

        # Логируем и выполняем действие
        logger.info(f"Executing browser action: {action}, params: {action_params}")
        result = await self.browser_access.execute_action(action, **action_params)

        # В режиме мониторинга добавляем информацию о выполнении в историю
        if config.reasoning_config.monitoring_enabled:
            monitoring_msg = f"Browser action executed: {action}\n"
            monitoring_msg += f"Success: {result.get('success', False)}\n"
            if result.get('success', False):
                monitoring_msg += f"Output: {str(result.get('output', ''))[:200]}...\n"
            else:
                monitoring_msg += f"Error: {str(result.get('error', ''))}\n"

            self.memory.add_message(
                Message.system_message(monitoring_msg)
            )

        return result

    async def get_browser_state(self) -> Dict[str, Any]:
        """
        Получает текущее состояние браузера.

        Returns:
            Словарь с информацией о текущем состоянии браузера
        """
        if self.browser_access is None:
            return {
                "success": False,
                "state": None,
                "error": "Browser access module not initialized"
            }

        return await self.browser_access.get_current_state()

    def get_current_terminal_directory(self) -> str:
        """
        Возвращает текущую рабочую директорию терминала.

        Returns:
            Путь к текущей рабочей директории
        """
        if self.terminal_access is None:
            return os.getcwd()
        return self.terminal_access.get_current_directory()

    def set_terminal_directory(self, directory: str) -> bool:
        """
        Устанавливает текущую рабочую директорию терминала.

        Args:
            directory: Новая рабочая директория

        Returns:
            True если директория успешно установлена
        """
        if self.terminal_access is None:
            return False
        return self.terminal_access.set_current_directory(directory)

    async def run(self, request: Optional[str] = None) -> str:
        """
        Запускает агента с проверкой наличия необходимых модулей.

        Args:
            request: Запрос пользователя

        Returns:
            Результат выполнения

        Raises:
            ValueError: Если отсутствуют необходимые модули
        """
        # Обработка специальных команд
        if request and request.lower() == "approve":
            self.approve_plan()
            return "План одобрен. Приступаю к выполнению."

        if request and request.lower() == "reject":
            self.reject_plan()
            return "План отклонен. Пожалуйста, предоставьте новый запрос."

        if request and request.lower().startswith("plan "):
            task = request[5:].strip()
            plan = await self.create_plan(task)
            return f"Предлагаемый план:\n\n{plan}\n\nОтветьте 'approve' для принятия плана или 'reject' для отклонения."

        # Проверяем режим работы
        if not self.current_plan:
            # Если есть план, но он не одобрен, запрашиваем одобрение
            return f"У вас есть неодобренный план. Пожалуйста, ответьте 'approve' для принятия или 'reject' для отклонения."

        # Запускаем базовый метод
        return await super().run(request)

    async def cleanup(self) -> None:
        """Очищает ресурсы агента перед завершением."""
        # Очищаем ресурсы Serena
        if self.serena:
            logger.info("Cleaning up Serena resources")

        # Очищаем ресурсы браузера
        if self.browser_access:
            try:
                await self.browser_access.cleanup()
            except Exception as e:
                logger.error(f"Error during browser cleanup: {str(e)}")

        # Логирование очистки ресурсов файловой системы
        if self.file_system:
            try:
                # Сохраняем историю операций с файлами при необходимости
                history = self.file_system.get_operation_history()
                if history:
                    logger.info(f"File system operations performed: {len(history)}")
            except Exception as e:
                logger.error(f"Error during file system cleanup: {str(e)}")

        # Вызываем базовый метод для стандартной очистки
        await super().cleanup()

    async def read_file_content(
        self,
        file_path: str,
        mode: str = "text",
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Безопасно читает содержимое файла через модуль FileSystemAccess.

        Args:
            file_path: Путь к файлу для чтения
            mode: Режим чтения ("text" или "binary")
            encoding: Кодировка для текстового режима

        Returns:
            Словарь с результатами чтения
        """
        if self.file_system is None:
            return {
                "success": False,
                "content": None,
                "error": "File system access module not initialized",
                "path": file_path
            }

        # Проверяем, одобрен ли план
        if not self.current_plan:
            error_msg = "Cannot read files without plan approval."
            logger.warning(error_msg)
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "path": file_path
            }

        # Логируем и выполняем операцию
        logger.info(f"Reading file: {file_path}")
        result = await self.file_system.read_file(file_path, mode, encoding)

        return result

    async def write_file_content(
        self,
        file_path: str,
        content: str,
        mode: str = "text",
        encoding: str = "utf-8",
        create_dirs: bool = False
    ) -> Dict[str, Any]:
        """
        Безопасно записывает данные в файл через модуль FileSystemAccess.

        Args:
            file_path: Путь к файлу для записи
            content: Содержимое для записи
            mode: Режим записи ("text" или "binary")
            encoding: Кодировка для текстового режима
            create_dirs: Создавать родительские директории, если их нет

        Returns:
            Словарь с результатами записи
        """
        if self.file_system is None:
            return {
                "success": False,
                "error": "File system access module not initialized",
                "path": file_path
            }

        # Проверяем, одобрен ли план
        if not self.current_plan:
            error_msg = "Cannot write files without plan approval."
            logger.warning(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "path": file_path
            }

        # Логируем и выполняем операцию
        logger.info(f"Writing to file: {file_path}")
        result = await self.file_system.write_file(
            file_path, content, mode, encoding, create_dirs
        )

        return result

    async def list_directory_contents(
        self,
        directory: str,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Безопасно перечисляет содержимое директории через модуль FileSystemAccess.

        Args:
            directory: Путь к директории
            pattern: Шаблон для фильтрации файлов
            recursive: Рекурсивный обход директорий

        Returns:
            Словарь с результатами перечисления
        """
        if self.file_system is None:
            return {
                "success": False,
                "error": "File system access module not initialized",
                "path": directory
            }

        # Логируем и выполняем операцию
        logger.info(f"Listing directory: {directory}, pattern: {pattern}, recursive: {recursive}")
        result = await self.file_system.list_directory(directory, pattern, recursive)

        return result

    async def get_file_information(self, file_path: str) -> Dict[str, Any]:
        """
        Получает информацию о файле через модуль FileSystemAccess.

        Args:
            file_path: Путь к файлу

        Returns:
            Словарь с информацией о файле
        """
        if self.file_system is None:
            return {
                "success": False,
                "error": "File system access module not initialized",
                "path": file_path
            }

        # Логируем и выполняем операцию
        logger.info(f"Getting file info: {file_path}")
        result = await self.file_system.get_file_info(file_path)

        return result

    def parse_file_path_from_chat(self, chat_text: str) -> Optional[str]:
        """
        Извлекает и проверяет путь из сообщения в чате через модуль FileSystemAccess.

        Args:
            chat_text: Текст сообщения из чата

        Returns:
            Нормализованный абсолютный путь или None, если путь не найден или небезопасен
        """
        if self.file_system is None:
            return None

        # Логируем и выполняем операцию
        logger.info(f"Parsing path from chat text: {chat_text[:50]}...")
        path = self.file_system.parse_chat_path(chat_text)

        if path:
            logger.info(f"Extracted path from chat: {path}")
        else:
            logger.info("No valid path found in chat text")

        return path

    def get_current_working_directory(self) -> str:
        """
        Возвращает текущую рабочую директорию файловой системы.

        Returns:
            Путь к текущей рабочей директории
        """
        if self.file_system is None:
            return os.getcwd()
        return self.file_system.get_current_directory()

    def set_working_directory(self, directory: str) -> bool:
        """
        Устанавливает текущую рабочую директорию файловой системы.

        Args:
            directory: Новая рабочая директория

        Returns:
            True если директория успешно установлена
        """
        if self.file_system is None:
            return False
        return self.file_system.set_current_directory(directory)
