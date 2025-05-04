"""
Permission Manager для Reasoning Agent

Модуль управления разрешениями для Reasoning Agent, обеспечивающий безопасность
выполнения действий с контролем доступа к различным инструментам.
"""

from typing import Any, Dict, List, Optional, Set
from enum import Enum
import time
from dataclasses import dataclass

from app.logger import logger


class PermissionLevel(str, Enum):
    """Уровни разрешений для действий агента"""
    LOW = "low"          # Безопасные действия, не требующие подтверждения
    MEDIUM = "medium"    # Действия с умеренным риском, требующие подтверждения плана
    HIGH = "high"        # Потенциально опасные действия, требующие явного подтверждения
    ADMIN = "admin"      # Действия администратора, требующие специального разрешения


@dataclass
class PermissionRequest:
    """Запрос на выполнение действия с определенным уровнем разрешения"""
    action: str                    # Название действия
    tool_name: str                 # Имя инструмента
    args: Dict[str, Any]           # Аргументы действия
    level: PermissionLevel         # Требуемый уровень разрешения
    timestamp: float = 0.0         # Время запроса
    approved: bool = False         # Статус одобрения
    approval_timestamp: float = 0.0  # Время одобрения
    reason: Optional[str] = None   # Причина запроса/отказа


class PermissionManager:
    """
    Менеджер разрешений для Reasoning Agent.

    Отвечает за контроль доступа к инструментам, проверку разрешений
    и учет одобренных/отклоненных действий.
    """

    def __init__(self, safe_mode: bool = True):
        """
        Инициализирует менеджер разрешений.

        Args:
            safe_mode: Включение проверок безопасности
        """
        self.safe_mode = safe_mode
        self.plan_approved = False

        # История запросов на разрешения
        self.permission_history: List[PermissionRequest] = []

        # Инструменты по уровням разрешений
        self.tool_permission_levels: Dict[str, PermissionLevel] = {
            # Инструменты LOW уровня (безопасные, доступны всегда)
            "codebase_search": PermissionLevel.LOW,
            "grep_search": PermissionLevel.LOW,
            "file_search": PermissionLevel.LOW,
            "list_dir": PermissionLevel.LOW,
            "mcp_serena_list_dir": PermissionLevel.LOW,
            "mcp_serena_get_symbols_overview": PermissionLevel.LOW,
            "mcp_serena_find_symbol": PermissionLevel.LOW,
            "mcp_serena_read_file": PermissionLevel.LOW,
            "mcp_serena_search_for_pattern": PermissionLevel.LOW,
            "read_file": PermissionLevel.LOW,
            "web_search": PermissionLevel.LOW,

            # Инструменты MEDIUM уровня (требуют одобрения плана)
            "run_terminal_cmd": PermissionLevel.MEDIUM,
            "edit_file": PermissionLevel.MEDIUM,
            "mcp_serena_edit_file": PermissionLevel.MEDIUM,
            "mcp_serena_create_text_file": PermissionLevel.MEDIUM,
            "mcp_serena_replace_lines": PermissionLevel.MEDIUM,
            "mcp_serena_insert_at_line": PermissionLevel.MEDIUM,
            "mcp_serena_replace_symbol_body": PermissionLevel.MEDIUM,
            "mcp_serena_insert_after_symbol": PermissionLevel.MEDIUM,
            "mcp_serena_insert_before_symbol": PermissionLevel.MEDIUM,
            "mcp_serena_execute_shell_command": PermissionLevel.MEDIUM,
            "browser_use": PermissionLevel.MEDIUM,

            # Инструменты HIGH уровня (повышенный риск)
            "delete_file": PermissionLevel.HIGH,
            "mcp_serena_delete_file": PermissionLevel.HIGH,
            "mcp_serena_delete_lines": PermissionLevel.HIGH,
        }

        # Инструменты не требующие проверки разрешений
        self.exempt_tools: Set[str] = {
            "mcp_sequential-thinking_sequentialthinking",
            "mcp_serena_initial_instructions",
            "mcp_serena_check_onboarding_performed",
            "mcp_serena_onboarding",
            "mcp_serena_write_memory",
            "mcp_serena_read_memory",
            "mcp_serena_list_memories",
            "mcp_serena_think_about_collected_information",
            "mcp_serena_think_about_task_adherence",
            "mcp_serena_think_about_whether_you_are_done",
            "mcp_serena_summarize_changes",
        }

        logger.info(f"Permission manager initialized with safe_mode={safe_mode}")

    def approve_plan(self) -> None:
        """Одобряет план и разрешает действия среднего уровня"""
        self.plan_approved = True
        logger.info("Plan approved, enabled medium-level tools")

    def reject_plan(self) -> None:
        """Отклоняет план и запрещает действия среднего уровня"""
        self.plan_approved = False
        logger.info("Plan rejected, disabled medium-level tools")

    def get_tool_permission_level(self, tool_name: str) -> PermissionLevel:
        """
        Возвращает уровень разрешения для инструмента.

        Args:
            tool_name: Имя инструмента

        Returns:
            Уровень разрешения
        """
        # Инструменты в exempt_tools всегда имеют LOW уровень
        if tool_name in self.exempt_tools:
            return PermissionLevel.LOW

        # Возвращаем уровень для известного инструмента или MEDIUM по умолчанию
        return self.tool_permission_levels.get(tool_name, PermissionLevel.MEDIUM)

    def is_action_allowed(
        self,
        tool_name: str,
        args: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Проверяет, разрешено ли действие с текущими настройками.

        Args:
            tool_name: Имя инструмента
            args: Аргументы инструмента

        Returns:
            True если действие разрешено
        """
        if not self.safe_mode:
            return True

        # Exempt инструменты всегда разрешены
        if tool_name in self.exempt_tools:
            return True

        # Получаем уровень разрешения для инструмента
        level = self.get_tool_permission_level(tool_name)

        # Проверяем разрешение в зависимости от уровня
        if level == PermissionLevel.LOW:
            return True
        elif level == PermissionLevel.MEDIUM:
            return self.plan_approved
        elif level == PermissionLevel.HIGH:
            # HIGH требует не только одобрения плана, но и особой проверки
            return self.plan_approved and self._check_high_risk_action(tool_name, args)
        elif level == PermissionLevel.ADMIN:
            return False  # ADMIN всегда требует явного разрешения

        return False

    def _check_high_risk_action(
        self,
        tool_name: str,
        args: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Дополнительная проверка для действий высокого риска.

        Args:
            tool_name: Имя инструмента
            args: Аргументы инструмента

        Returns:
            True если действие разрешено
        """
        args = args or {}

        # Дополнительные проверки для удаления файлов
        if tool_name in ["delete_file", "mcp_serena_delete_file"]:
            target_file = args.get("target_file", "")

            # Запрещаем удаление системных файлов
            if any(path in target_file for path in [
                "requirements.txt", "setup.py", "main.py", "run_mcp.py"
            ]):
                logger.warning(f"Attempted to delete critical file: {target_file}")
                return False

        return True  # По умолчанию разрешаем

    def request_permission(
        self,
        tool_name: str,
        args: Dict[str, Any],
        reason: Optional[str] = None
    ) -> PermissionRequest:
        """
        Регистрирует запрос на выполнение действия.

        Args:
            tool_name: Имя инструмента
            args: Аргументы инструмента
            reason: Причина запроса

        Returns:
            Объект запроса с информацией о разрешении
        """
        level = self.get_tool_permission_level(tool_name)
        allowed = self.is_action_allowed(tool_name, args)

        # Создаем запрос
        request = PermissionRequest(
            action=f"Use tool {tool_name}",
            tool_name=tool_name,
            args=args,
            level=level,
            timestamp=time.time(),
            approved=allowed,
            reason=reason
        )

        # Если разрешено, устанавливаем время одобрения
        if allowed:
            request.approval_timestamp = time.time()

        # Сохраняем в историю
        self.permission_history.append(request)

        # Логируем решение
        if allowed:
            logger.info(f"Permission granted for {tool_name}")
        else:
            logger.warning(f"Permission denied for {tool_name}: plan not approved or high risk action")

        return request

    def get_permission_history(self) -> List[PermissionRequest]:
        """
        Возвращает историю запросов на разрешения.

        Returns:
            Список запросов на разрешения
        """
        return self.permission_history
