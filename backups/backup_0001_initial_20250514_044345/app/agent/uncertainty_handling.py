"""
Модуль обработки неопределенности и ветвлений для Reasoning Agent

Обеспечивает механизмы для обработки неопределенных ситуаций в процессе
планирования и выполнения задач с поддержкой условного ветвления.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Union, Set
import json

from app.agent.thought_tree import ThoughtTree, ThoughtNode
from app.logger import logger


class UncertaintyLevel(str, Enum):
    """Уровни неопределенности для принятия решений"""
    LOW = "low"  # Низкая неопределенность, можно выбрать один надежный путь
    MEDIUM = "medium"  # Средняя неопределенность, нужно несколько альтернатив
    HIGH = "high"  # Высокая неопределенность, нужно много альтернатив и проверок


class DecisionPoint:
    """
    Точка принятия решения в условиях неопределенности

    Представляет момент в плане, где необходимо выбрать один из альтернативных путей
    в зависимости от условий или результатов предыдущих действий.
    """

    def __init__(
        self,
        name: str,
        description: str,
        condition: str,
        uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM,
    ):
        """
        Инициализирует точку принятия решения

        Args:
            name: Уникальное имя точки решения
            description: Описание ситуации и необходимости принятия решения
            condition: Описание условия, на основе которого принимается решение
            uncertainty_level: Уровень неопределенности в этой точке
        """
        self.name = name
        self.description = description
        self.condition = condition
        self.uncertainty_level = uncertainty_level
        self.options: List[DecisionOption] = []
        self.chosen_option: Optional[str] = None  # ID выбранной опции

    def add_option(
        self,
        option_id: str,
        description: str,
        condition_value: Any,
        probability: float = 0.0,
        impact: str = "medium"
    ) -> None:
        """
        Добавляет опцию выбора для точки принятия решения

        Args:
            option_id: Уникальный идентификатор опции
            description: Описание опции
            condition_value: Значение условия, при котором выбирается эта опция
            probability: Оценка вероятности выбора этой опции (0.0-1.0)
            impact: Оценка влияния этой опции на план (low, medium, high)
        """
        option = DecisionOption(
            option_id=option_id,
            description=description,
            condition_value=condition_value,
            probability=probability,
            impact=impact
        )
        self.options.append(option)

    def choose_option(self, condition_value: Any) -> Optional[str]:
        """
        Выбирает опцию на основе значения условия

        Args:
            condition_value: Значение условия для выбора опции

        Returns:
            ID выбранной опции или None, если нет подходящей опции
        """
        for option in self.options:
            if self._match_condition(option.condition_value, condition_value):
                self.chosen_option = option.option_id
                return option.option_id

        return None

    def _match_condition(self, option_value: Any, condition_value: Any) -> bool:
        """
        Проверяет соответствие значения условия опции

        Args:
            option_value: Значение условия в опции
            condition_value: Текущее значение условия

        Returns:
            True если значения соответствуют, False в противном случае
        """
        # Простое строковое сравнение
        if isinstance(option_value, str) and isinstance(condition_value, str):
            return option_value.lower() == condition_value.lower()

        # Сравнение для диапазонов
        if isinstance(option_value, dict) and "range" in option_value:
            if not isinstance(condition_value, (int, float)):
                return False

            range_min = option_value["range"].get("min")
            range_max = option_value["range"].get("max")

            if range_min is not None and condition_value < range_min:
                return False
            if range_max is not None and condition_value > range_max:
                return False
            return True

        # Сравнение списков
        if isinstance(option_value, list) and condition_value in option_value:
            return True

        # Прямое сравнение для остальных типов
        return option_value == condition_value

    def get_option_by_id(self, option_id: str) -> Optional["DecisionOption"]:
        """
        Получает опцию по её ID

        Args:
            option_id: ID опции

        Returns:
            Объект опции или None, если не найдена
        """
        for option in self.options:
            if option.option_id == option_id:
                return option
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует точку принятия решения в словарь для сериализации

        Returns:
            Словарь с данными точки принятия решения
        """
        return {
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "uncertainty_level": self.uncertainty_level.value,
            "options": [option.to_dict() for option in self.options],
            "chosen_option": self.chosen_option
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionPoint":
        """
        Создает точку принятия решения из словаря

        Args:
            data: Словарь с данными точки принятия решения

        Returns:
            Объект точки принятия решения
        """
        uncertainty_level = UncertaintyLevel(data.get("uncertainty_level", UncertaintyLevel.MEDIUM.value))

        decision_point = cls(
            name=data["name"],
            description=data["description"],
            condition=data["condition"],
            uncertainty_level=uncertainty_level
        )

        for option_data in data.get("options", []):
            option = DecisionOption.from_dict(option_data)
            decision_point.options.append(option)

        decision_point.chosen_option = data.get("chosen_option")

        return decision_point


class DecisionOption:
    """
    Опция выбора для точки принятия решения

    Представляет один из возможных путей в точке ветвления плана,
    с оценкой вероятности и влияния.
    """

    def __init__(
        self,
        option_id: str,
        description: str,
        condition_value: Any,
        probability: float = 0.0,
        impact: str = "medium"
    ):
        """
        Инициализирует опцию

        Args:
            option_id: Уникальный идентификатор опции
            description: Описание опции
            condition_value: Значение условия, при котором выбирается эта опция
            probability: Оценка вероятности выбора этой опции (0.0-1.0)
            impact: Оценка влияния этой опции на план (low, medium, high)
        """
        self.option_id = option_id
        self.description = description
        self.condition_value = condition_value
        self.probability = max(0.0, min(1.0, probability))  # Ограничиваем 0-1
        self.impact = impact

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует опцию в словарь для сериализации

        Returns:
            Словарь с данными опции
        """
        return {
            "option_id": self.option_id,
            "description": self.description,
            "condition_value": self.condition_value,
            "probability": self.probability,
            "impact": self.impact
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionOption":
        """
        Создает опцию из словаря

        Args:
            data: Словарь с данными опции

        Returns:
            Объект опции
        """
        return cls(
            option_id=data["option_id"],
            description=data["description"],
            condition_value=data.get("condition_value"),
            probability=data.get("probability", 0.0),
            impact=data.get("impact", "medium")
        )


class UncertaintyHandler:
    """
    Обработчик неопределенности для адаптивного планирования

    Управляет точками принятия решений, оценивает неопределенность
    и генерирует альтернативные пути выполнения плана.
    """

    def __init__(self, thought_tree: Optional[ThoughtTree] = None):
        """
        Инициализирует обработчик неопределенности

        Args:
            thought_tree: Дерево мыслей для интеграции точек принятия решений
        """
        self.thought_tree = thought_tree
        self.decision_points: Dict[str, DecisionPoint] = {}
        self.decision_history: List[Dict[str, Any]] = []

    def add_decision_point(
        self,
        name: str,
        description: str,
        condition: str,
        uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM,
        options: Optional[List[Dict[str, Any]]] = None
    ) -> DecisionPoint:
        """
        Добавляет новую точку принятия решения

        Args:
            name: Уникальное имя точки решения
            description: Описание ситуации и необходимости принятия решения
            condition: Описание условия, на основе которого принимается решение
            uncertainty_level: Уровень неопределенности в этой точке
            options: Список опций в формате словарей

        Returns:
            Созданная точка принятия решения
        """
        decision_point = DecisionPoint(
            name=name,
            description=description,
            condition=condition,
            uncertainty_level=uncertainty_level
        )

        # Добавляем опции, если они предоставлены
        if options:
            for option_data in options:
                decision_point.add_option(
                    option_id=option_data.get("option_id", f"option_{len(decision_point.options)+1}"),
                    description=option_data.get("description", ""),
                    condition_value=option_data.get("condition_value"),
                    probability=option_data.get("probability", 0.0),
                    impact=option_data.get("impact", "medium")
                )

        # Сохраняем точку принятия решения
        self.decision_points[name] = decision_point

        # Добавляем в дерево мыслей, если оно доступно
        if self.thought_tree and self.thought_tree.root:
            decision_node_id = self.thought_tree.add_thought(
                content=f"Decision Point: {name}\n\n{description}\n\nCondition: {condition}",
                node_type="decision_point",
                metadata={"decision_point": decision_point.to_dict()}
            )

            # Добавляем опции как альтернативные пути
            for option in decision_point.options:
                self.thought_tree.add_thought(
                    content=f"Option: {option.description}\n\nCondition Value: {option.condition_value}\nProbability: {option.probability}\nImpact: {option.impact}",
                    parent_id=decision_node_id,
                    node_type="decision_option",
                    as_alternative=True,
                    metadata={"option_id": option.option_id}
                )

        return decision_point

    def make_decision(
        self,
        decision_point_name: str,
        condition_value: Any
    ) -> Optional[str]:
        """
        Принимает решение в указанной точке на основе текущего значения условия

        Args:
            decision_point_name: Имя точки принятия решения
            condition_value: Текущее значение условия

        Returns:
            ID выбранной опции или None, если нет подходящей опции или точки решения
        """
        if decision_point_name not in self.decision_points:
            logger.error(f"Decision point {decision_point_name} not found")
            return None

        decision_point = self.decision_points[decision_point_name]
        option_id = decision_point.choose_option(condition_value)

        # Записываем в историю
        self.decision_history.append({
            "decision_point": decision_point_name,
            "condition_value": condition_value,
            "chosen_option": option_id,
            "timestamp": import time; time.time()
        })

        # Обновляем дерево мыслей, если оно доступно
        if self.thought_tree and option_id:
            # Ищем узел точки принятия решения
            decision_node_id = None
            for node_id, node in self.thought_tree.nodes.items():
                if (node.node_type == "decision_point" and
                    node.metadata.get("decision_point", {}).get("name") == decision_point_name):
                    decision_node_id = node_id
                    break

            if decision_node_id:
                # Ищем опцию среди альтернатив
                option_node_id = None
                for alt_id in self.thought_tree.nodes[decision_node_id].alternatives:
                    alt_node = self.thought_tree.nodes.get(alt_id)
                    if alt_node and alt_node.metadata.get("option_id") == option_id:
                        option_node_id = alt_id
                        break

                # Если нашли узел опции, добавляем узел результата решения
                if option_node_id:
                    option = decision_point.get_option_by_id(option_id)
                    option_desc = option.description if option else f"Option {option_id}"

                    self.thought_tree.add_thought(
                        content=f"Decision Made: {decision_point_name}\n\nChosen option: {option_desc}\nBased on condition value: {condition_value}",
                        parent_id=option_node_id,
                        node_type="decision_result"
                    )

        return option_id

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """
        Получает историю принятых решений

        Returns:
            Список записей о принятых решениях
        """
        return self.decision_history

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует обработчик неопределенности в словарь для сериализации

        Returns:
            Словарь с данными обработчика
        """
        return {
            "decision_points": {name: dp.to_dict() for name, dp in self.decision_points.items()},
            "decision_history": self.decision_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], thought_tree: Optional[ThoughtTree] = None) -> "UncertaintyHandler":
        """
        Создает обработчик неопределенности из словаря

        Args:
            data: Словарь с данными обработчика
            thought_tree: Дерево мыслей для интеграции

        Returns:
            Объект обработчика неопределенности
        """
        handler = cls(thought_tree=thought_tree)

        # Загружаем точки принятия решений
        for name, dp_data in data.get("decision_points", {}).items():
            decision_point = DecisionPoint.from_dict(dp_data)
            handler.decision_points[name] = decision_point

        # Загружаем историю решений
        handler.decision_history = data.get("decision_history", [])

        return handler

    def analyze_uncertainty(self, plan_text: str) -> Dict[str, Any]:
        """
        Анализирует текст плана и выявляет точки неопределенности

        Args:
            plan_text: Текст плана для анализа

        Returns:
            Словарь с результатами анализа
        """
        # Это упрощенная реализация, которая ищет ключевые слова неопределенности
        uncertainty_keywords = [
            "если", "возможно", "вероятно", "может быть", "либо", "или",
            "зависит", "неизвестно", "не определено", "не ясно", "альтернатива"
        ]

        # Ищем вхождения ключевых слов
        keyword_matches = []
        lines = plan_text.split("\n")

        for i, line in enumerate(lines):
            for keyword in uncertainty_keywords:
                if keyword in line.lower():
                    keyword_matches.append({
                        "line": i + 1,
                        "text": line.strip(),
                        "keyword": keyword
                    })

        # Оцениваем общий уровень неопределенности
        uncertainty_level = UncertaintyLevel.LOW
        if len(keyword_matches) >= 5:
            uncertainty_level = UncertaintyLevel.HIGH
        elif len(keyword_matches) >= 2:
            uncertainty_level = UncertaintyLevel.MEDIUM

        return {
            "uncertainty_level": uncertainty_level.value,
            "uncertain_points": keyword_matches,
            "count": len(keyword_matches)
        }

    def generate_decision_points_from_analysis(
        self,
        analysis: Dict[str, Any]
    ) -> List[DecisionPoint]:
        """
        Генерирует точки принятия решений на основе анализа неопределенности

        Args:
            analysis: Результаты анализа неопределенности

        Returns:
            Список созданных точек принятия решений
        """
        created_points = []
        uncertain_points = analysis.get("uncertain_points", [])

        for i, point in enumerate(uncertain_points):
            # Создаем имя и описание
            name = f"decision_point_{i+1}"
            description = point.get("text", "")

            # Пытаемся извлечь условие из текста
            text = description.lower()
            condition = "Unknown condition"

            if "если" in text:
                condition_parts = text.split("если", 1)
                if len(condition_parts) > 1:
                    condition = f"Если {condition_parts[1].strip()}"

            # Создаем точку принятия решения
            decision_point = self.add_decision_point(
                name=name,
                description=description,
                condition=condition,
                uncertainty_level=UncertaintyLevel(analysis.get("uncertainty_level", UncertaintyLevel.MEDIUM.value))
            )

            # Добавляем примерные опции (в реальности нужен более сложный анализ)
            decision_point.add_option(
                option_id=f"{name}_option_1",
                description="Первый вариант действий",
                condition_value="true",
                probability=0.7,
                impact="medium"
            )

            decision_point.add_option(
                option_id=f"{name}_option_2",
                description="Альтернативный вариант действий",
                condition_value="false",
                probability=0.3,
                impact="medium"
            )

            created_points.append(decision_point)

        return created_points
