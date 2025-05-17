"""
Модуль для управления разрешениями в Reasoning Agent

Предоставляет механизмы контроля за выполнением действий агентом,
запросом разрешений у пользователя и блокированием опасных операций.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Уровни разрешений для действий."""
    LOW_RISK = 1      # Низкий риск, можно выполнять автоматически
    MEDIUM_RISK = 2   # Средний риск, требуется подтверждение
    HIGH_RISK = 3     # Высокий риск, требуется явное подтверждение с доп. проверкой
    CRITICAL_RISK = 4 # Критический риск, может потребоваться множественное подтверждение


class ActionCategory(Enum):
    """Категории действий агента."""
    FILE_READ = "file_read"           # Чтение файлов
    FILE_WRITE = "file_write"         # Запись в файлы
    FILE_DELETE = "file_delete"       # Удаление файлов
    TERMINAL_COMMAND = "terminal_cmd" # Выполнение команд в терминале
    NETWORK_REQUEST = "network"       # Сетевые запросы
    BROWSER_ACTION = "browser"        # Действия в браузере
    SYSTEM_CONFIG = "system_config"   # Изменение системных настроек
    CODE_EXECUTION = "code_execution" # Выполнение кода
    DATABASE_ACCESS = "database"      # Доступ к базе данных
    OTHER = "other"                   # Прочие действия


class PermissionManager:
    """
    Менеджер разрешений для контроля действий агента.

    Обеспечивает:
    1. Оценку рисков действий
    2. Запрос разрешений у пользователя
    3. Блокирование опасных операций
    4. Логирование действий агента
    """

    def __init__(self):
        """Инициализирует менеджер разрешений."""
        # Словарь разрешенных действий (категория -> набор разрешенных действий)
        self._permissions: Dict[ActionCategory, Set[str]] = {}

        # Словарь уровней риска для разных категорий действий
        self._risk_levels: Dict[str, PermissionLevel] = {}

        # Флаг наличия одобренного плана
        self._has_approved_plan = False

        # Журнал действий
        self._action_log: List[Dict[str, Any]] = []

        # Обработчик запроса разрешений
        self._permission_handler: Optional[Callable[[str, ActionCategory, PermissionLevel, str], bool]] = None

        # Инициализируем базовые настройки рисков
        self._init_default_risk_levels()

    def _init_default_risk_levels(self):
        """Инициализирует базовые уровни риска для разных типов действий."""
        self._risk_levels = {
            # Чтение файлов
            "file_read:*.py": PermissionLevel.LOW_RISK,
            "file_read:*.txt": PermissionLevel.LOW_RISK,
            "file_read:*.md": PermissionLevel.LOW_RISK,
            "file_read:*.json": PermissionLevel.LOW_RISK,
            "file_read:*.config": PermissionLevel.MEDIUM_RISK,
            "file_read:*/password*": PermissionLevel.HIGH_RISK,

            # Запись в файлы
            "file_write:*.py": PermissionLevel.MEDIUM_RISK,
            "file_write:*.txt": PermissionLevel.LOW_RISK,
            "file_write:*.md": PermissionLevel.LOW_RISK,
            "file_write:*.json": PermissionLevel.MEDIUM_RISK,
            "file_write:*.config": PermissionLevel.HIGH_RISK,

            # Удаление файлов
            "file_delete:*.py": PermissionLevel.HIGH_RISK,
            "file_delete:*.txt": PermissionLevel.MEDIUM_RISK,
            "file_delete:*.md": PermissionLevel.MEDIUM_RISK,
            "file_delete:*.json": PermissionLevel.HIGH_RISK,
            "file_delete:*.config": PermissionLevel.CRITICAL_RISK,

            # Команды терминала
            "terminal_cmd:ls": PermissionLevel.LOW_RISK,
            "terminal_cmd:dir": PermissionLevel.LOW_RISK,
            "terminal_cmd:cd": PermissionLevel.LOW_RISK,
            "terminal_cmd:pwd": PermissionLevel.LOW_RISK,
            "terminal_cmd:cat": PermissionLevel.LOW_RISK,
            "terminal_cmd:python": PermissionLevel.MEDIUM_RISK,
            "terminal_cmd:pip": PermissionLevel.MEDIUM_RISK,
            "terminal_cmd:git": PermissionLevel.MEDIUM_RISK,
            "terminal_cmd:rm": PermissionLevel.HIGH_RISK,
            "terminal_cmd:del": PermissionLevel.HIGH_RISK,
            "terminal_cmd:rmdir": PermissionLevel.HIGH_RISK,
            "terminal_cmd:sudo": PermissionLevel.CRITICAL_RISK,

            # Сетевые запросы
            "network:http": PermissionLevel.LOW_RISK,
            "network:https": PermissionLevel.LOW_RISK,
            "network:ftp": PermissionLevel.MEDIUM_RISK,
            "network:ssh": PermissionLevel.HIGH_RISK,

            # По умолчанию для неуказанных категорий
            "default": PermissionLevel.MEDIUM_RISK
        }

    def set_permission_handler(self, handler: Callable[[str, ActionCategory, PermissionLevel, str], bool]):
        """
        Устанавливает обработчик запросов разрешений.

        Args:
            handler: Функция обработки запросов разрешений.
                     Принимает аргументы: действие, категория, уровень риска, объяснение.
                     Возвращает True, если действие разрешено, иначе False.
        """
        self._permission_handler = handler

    def set_plan_approved(self, approved: bool = True):
        """
        Устанавливает статус одобрения плана.

        Args:
            approved: True, если план одобрен, иначе False.
        """
        self._has_approved_plan = approved

        # Очищаем разрешения при отклонении плана
        if not approved:
            self._permissions.clear()
            self._action_log.clear()

    def is_plan_approved(self) -> bool:
        """
        Проверяет, был ли одобрен план.

        Returns:
            True, если план был одобрен, иначе False.
        """
        return self._has_approved_plan

    def evaluate_risk(self, action: str, category: ActionCategory) -> PermissionLevel:
        """
        Оценивает уровень риска действия.

        Args:
            action: Описание действия.
            category: Категория действия.

        Returns:
            Уровень риска (PermissionLevel).
        """
        import fnmatch

        # Проверяем на точное совпадение
        key = f"{category.value}:{action}"
        if key in self._risk_levels:
            return self._risk_levels[key]

        # Проверяем на совпадение по шаблону
        for pattern, level in self._risk_levels.items():
            if ":" in pattern:
                cat, act_pattern = pattern.split(":", 1)
                if cat == category.value and fnmatch.fnmatch(action, act_pattern):
                    return level

        # Возвращаем уровень по умолчанию
        return self._risk_levels.get("default", PermissionLevel.MEDIUM_RISK)

    def request_permission(self, action: str, category: ActionCategory,
                          explanation: str = "") -> bool:
        """
        Запрашивает разрешение на выполнение действия.

        Args:
            action: Описание действия.
            category: Категория действия.
            explanation: Пояснение, зачем нужно это действие.

        Returns:
            True, если действие разрешено, иначе False.
        """
        # Проверяем наличие одобренного плана
        if not self._has_approved_plan:
            logger.warning(f"Permission request denied. No approved plan: {category.value}:{action}")
            return False

        # Проверяем, было ли действие уже разрешено
        if category in self._permissions and action in self._permissions[category]:
            logger.info(f"Permission already granted: {category.value}:{action}")
            self._log_action(action, category, True, "Already approved")
            return True

        # Оцениваем риск
        risk_level = self.evaluate_risk(action, category)

        # Если риск низкий, разрешаем автоматически
        if risk_level == PermissionLevel.LOW_RISK:
            self._grant_permission(action, category)
            self._log_action(action, category, True, "Auto-approved (low risk)")
            logger.info(f"Auto-approved low risk action: {category.value}:{action}")
            return True

        # Запрашиваем разрешение через обработчик
        if self._permission_handler:
            approved = self._permission_handler(action, category, risk_level, explanation)

            if approved:
                self._grant_permission(action, category)

            self._log_action(action, category, approved, f"User decision: {'approved' if approved else 'denied'}")
            return approved

        # Если нет обработчика, отклоняем действия выше LOW_RISK
        logger.warning(f"Permission request denied. No handler for: {category.value}:{action}")
        self._log_action(action, category, False, "No permission handler")
        return False

    def _grant_permission(self, action: str, category: ActionCategory):
        """
        Добавляет действие в список разрешенных.

        Args:
            action: Описание действия.
            category: Категория действия.
        """
        if category not in self._permissions:
            self._permissions[category] = set()

        self._permissions[category].add(action)

    def _log_action(self, action: str, category: ActionCategory,
                   approved: bool, reason: str):
        """
        Добавляет запись в журнал действий.

        Args:
            action: Описание действия.
            category: Категория действия.
            approved: Было ли действие разрешено.
            reason: Причина решения.
        """
        import time

        self._action_log.append({
            "timestamp": time.time(),
            "action": action,
            "category": category.value,
            "approved": approved,
            "reason": reason
        })

    def get_action_log(self) -> List[Dict[str, Any]]:
        """
        Возвращает журнал действий.

        Returns:
            Список записей журнала.
        """
        return self._action_log.copy()

    def generate_risk_explanation(self, action: str, category: ActionCategory) -> str:
        """
        Генерирует объяснение рисков для действия.

        Args:
            action: Описание действия.
            category: Категория действия.

        Returns:
            Строка с объяснением рисков.
        """
        risk_level = self.evaluate_risk(action, category)

        risk_explanations = {
            # Для файловых операций
            ActionCategory.FILE_READ: {
                PermissionLevel.LOW_RISK: "Это действие безопасно - просто чтение стандартного файла.",
                PermissionLevel.MEDIUM_RISK: "Чтение этого файла раскрывает информацию о конфигурации приложения.",
                PermissionLevel.HIGH_RISK: "Внимание! Этот файл может содержать конфиденциальные данные.",
                PermissionLevel.CRITICAL_RISK: "Крайне опасно! Файл содержит чувствительные данные безопасности."
            },
            ActionCategory.FILE_WRITE: {
                PermissionLevel.LOW_RISK: "Это действие безопасно - запись в обычный файл данных.",
                PermissionLevel.MEDIUM_RISK: "Запись изменит логику программы или важные данные.",
                PermissionLevel.HIGH_RISK: "Внимание! Изменение этого файла может нарушить работу приложения.",
                PermissionLevel.CRITICAL_RISK: "Крайне опасно! Изменение этого файла может привести к сбою системы."
            },
            ActionCategory.FILE_DELETE: {
                PermissionLevel.LOW_RISK: "Удаление временного или незначительного файла.",
                PermissionLevel.MEDIUM_RISK: "Удаление важного файла, но его можно восстановить.",
                PermissionLevel.HIGH_RISK: "Внимание! Удаление критически важного файла программы.",
                PermissionLevel.CRITICAL_RISK: "Крайне опасно! Удаление системного или конфигурационного файла."
            },
            # Для терминальных команд
            ActionCategory.TERMINAL_COMMAND: {
                PermissionLevel.LOW_RISK: "Безопасная информационная команда.",
                PermissionLevel.MEDIUM_RISK: "Команда изменяет файлы или настройки локально.",
                PermissionLevel.HIGH_RISK: "Внимание! Команда может удалить файлы или изменить важные настройки.",
                PermissionLevel.CRITICAL_RISK: "Крайне опасно! Команда с высокими привилегиями может повредить систему."
            },
            # Для сетевых запросов
            ActionCategory.NETWORK_REQUEST: {
                PermissionLevel.LOW_RISK: "Безопасный запрос по HTTPS к известному API.",
                PermissionLevel.MEDIUM_RISK: "Запрос передает данные на сторонний сервис.",
                PermissionLevel.HIGH_RISK: "Внимание! Запрос с аутентификацией или к непроверенному сервису.",
                PermissionLevel.CRITICAL_RISK: "Крайне опасно! Передача конфиденциальных данных."
            }
        }

        # Получаем объяснение для указанной категории и уровня риска
        category_explanations = risk_explanations.get(category, {})
        explanation = category_explanations.get(risk_level, "Нет дополнительной информации о рисках.")

        # Формируем полное объяснение
        risk_names = {
            PermissionLevel.LOW_RISK: "НИЗКИЙ",
            PermissionLevel.MEDIUM_RISK: "СРЕДНИЙ",
            PermissionLevel.HIGH_RISK: "ВЫСОКИЙ",
            PermissionLevel.CRITICAL_RISK: "КРИТИЧЕСКИЙ"
        }

        return f"Уровень риска: {risk_names[risk_level]}\n{explanation}"

    def analyze_plan_risks(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализирует риски плана действий.

        Args:
            plan: Словарь с данными плана.

        Returns:
            Словарь с анализом рисков для каждого шага и общей оценкой.
        """
        risk_analysis = {
            "overall_risk_level": PermissionLevel.LOW_RISK,
            "steps_risk": [],
            "risk_summary": {}
        }

        # Анализируем риски каждого шага
        steps = plan.get("steps", [])
        high_risk_categories = []

        for step in steps:
            # Получаем категорию действия
            step_category_str = step.get("category", "OTHER")
            try:
                step_category = ActionCategory(step_category_str)
            except ValueError:
                step_category = ActionCategory.OTHER

            # Получаем действие
            step_action = step.get("action", "")

            # Оцениваем риск
            risk_level = self.evaluate_risk(step_action, step_category)

            # Генерируем объяснение
            explanation = self.generate_risk_explanation(step_action, step_category)

            # Добавляем в анализ
            step_risk = {
                "step_id": step.get("id", 0),
                "title": step.get("title", ""),
                "risk_level": risk_level,
                "explanation": explanation
            }
            risk_analysis["steps_risk"].append(step_risk)

            # Обновляем общий уровень риска
            if risk_level.value > risk_analysis["overall_risk_level"].value:
                risk_analysis["overall_risk_level"] = risk_level

            # Собираем категории высокого риска
            if risk_level in [PermissionLevel.HIGH_RISK, PermissionLevel.CRITICAL_RISK]:
                high_risk_categories.append(step_category)

        # Формируем краткую сводку рисков
        risk_counts = {
            PermissionLevel.LOW_RISK: 0,
            PermissionLevel.MEDIUM_RISK: 0,
            PermissionLevel.HIGH_RISK: 0,
            PermissionLevel.CRITICAL_RISK: 0
        }

        for step_risk in risk_analysis["steps_risk"]:
            risk_counts[step_risk["risk_level"]] += 1

        risk_analysis["risk_summary"] = {
            "low_risk_steps": risk_counts[PermissionLevel.LOW_RISK],
            "medium_risk_steps": risk_counts[PermissionLevel.MEDIUM_RISK],
            "high_risk_steps": risk_counts[PermissionLevel.HIGH_RISK],
            "critical_risk_steps": risk_counts[PermissionLevel.CRITICAL_RISK],
            "high_risk_categories": list(set([cat.value for cat in high_risk_categories]))
        }

        return risk_analysis
