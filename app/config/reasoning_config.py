"""
Модуль конфигурации для Reasoning Agent

Содержит настройки глубины рассуждений, стратегии, логирования и мониторинга.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List


class ReasoningStrategy(str, Enum):
    """Стратегии рассуждений для Reasoning Agent"""
    SEQUENTIAL = "sequential"  # Последовательная стратегия
    TREE = "tree"              # Древовидная стратегия
    ADAPTIVE = "adaptive"      # Адаптивная стратегия

    @classmethod
    def get_description(cls, strategy: "ReasoningStrategy") -> str:
        """Возвращает описание стратегии"""
        descriptions = {
            cls.SEQUENTIAL: "Последовательный анализ шаг за шагом",
            cls.TREE: "Древовидное исследование альтернативных путей",
            cls.ADAPTIVE: "Адаптивный подход с изменением стратегии в зависимости от задачи"
        }
        return descriptions.get(strategy, "Неизвестная стратегия")


@dataclass
class ReasoningConfig:
    """
    Конфигурация для Reasoning Agent

    Attributes:
        reasoning_depth: Глубина рассуждений (количество шагов)
        reasoning_strategy: Стратегия рассуждений
        detailed_logging: Включение подробного логирования рассуждений
        monitoring_enabled: Включение мониторинга выполнения плана
        interactive_mode: Требовать подтверждение для каждого шага
        safe_mode: Включение проверок безопасности операций
        operation_timeout: Таймаут операций в секундах
    """
    reasoning_depth: int = 7
    reasoning_strategy: ReasoningStrategy = ReasoningStrategy.SEQUENTIAL
    detailed_logging: bool = True
    monitoring_enabled: bool = True
    interactive_mode: bool = False
    safe_mode: bool = True
    operation_timeout: int = 30

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReasoningConfig":
        """
        Создает конфигурацию из словаря

        Args:
            data: Словарь с настройками

        Returns:
            Объект конфигурации
        """
        # Обработка стратегии - преобразование строки в enum
        if "reasoning_strategy" in data and isinstance(data["reasoning_strategy"], str):
            try:
                data["reasoning_strategy"] = ReasoningStrategy(data["reasoning_strategy"])
            except ValueError:
                # По умолчанию используем SEQUENTIAL
                data["reasoning_strategy"] = ReasoningStrategy.SEQUENTIAL

        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__annotations__
        })

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует конфигурацию в словарь для сохранения

        Returns:
            Словарь с настройками
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ReasoningStrategy):
                result[key] = value.value
            else:
                result[key] = value
        return result

    def validate(self) -> List[str]:
        """
        Проверяет корректность настроек

        Returns:
            Список ошибок (пустой, если ошибок нет)
        """
        errors = []

        if not isinstance(self.reasoning_depth, int) or self.reasoning_depth < 3 or self.reasoning_depth > 15:
            errors.append("Глубина рассуждений должна быть числом от 3 до 15")

        if not isinstance(self.operation_timeout, int) or self.operation_timeout < 5 or self.operation_timeout > 300:
            errors.append("Таймаут операций должен быть числом от 5 до 300 секунд")

        return errors

# Значения по умолчанию
DEFAULT_REASONING_CONFIG = ReasoningConfig()
