"""
Модуль стратегий планирования для Reasoning Agent

Содержит базовые интерфейсы и реализации различных стратегий планирования:
- Адаптивная стратегия
- Древовидная стратегия
- Стратегия обработки неопределенностей
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
import json
import asyncio

from app.config.reasoning_config import ReasoningStrategy
from app.logger import logger
from app.mcp.sequential_thinking import SequentialThinking


class TaskComplexity(str, Enum):
    """Уровни сложности задач для адаптивного планирования"""
    SIMPLE = "simple"  # Простая задача с линейным решением
    MEDIUM = "medium"  # Средняя задача с несколькими подзадачами
    COMPLEX = "complex"  # Сложная задача с множеством взаимосвязанных шагов
    UNCERTAIN = "uncertain"  # Задача с высокой неопределенностью


class PlanningStrategy(ABC):
    """
    Базовый интерфейс для стратегий планирования

    Определяет общий интерфейс для всех стратегий планирования,
    включая адаптивную, древовидную и с обработкой неопределенностей.
    """

    @abstractmethod
    async def create_plan(self, task: str, sequential_thinking: SequentialThinking) -> Dict[str, Any]:
        """
        Создает план выполнения задачи согласно выбранной стратегии

        Args:
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            План выполнения задачи и метаданные
        """
        pass

    @abstractmethod
    async def adapt_plan(self, original_plan: Dict[str, Any], new_information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Адаптирует существующий план с учетом новой информации

        Args:
            original_plan: Исходный план
            new_information: Новая информация для учета

        Returns:
            Обновленный план
        """
        pass

    @abstractmethod
    async def self_evaluate(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any],
        sequential_thinking: SequentialThinking
    ) -> Dict[str, Any]:
        """
        Выполняет самооценку эффективности стратегии на основе результатов выполнения

        Args:
            task: Описание задачи
            plan: План выполнения
            execution_result: Результаты выполнения плана
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Результаты самооценки стратегии
        """
        pass


class AdaptivePlanningStrategy(PlanningStrategy):
    """
    Адаптивная стратегия планирования

    Автоматически определяет сложность задачи и выбирает подходящий
    подход к планированию. Для простых задач использует линейный подход,
    для сложных - древовидную структуру или ветвление с обработкой неопределенностей.
    """

    def __init__(self):
        """Инициализирует адаптивную стратегию планирования"""
        self.complexity_threshold = {
            "simple_to_medium": 3,  # Порог сложности для перехода от простой к средней
            "medium_to_complex": 6,  # Порог сложности для перехода от средней к сложной
            "uncertainty_threshold": 0.6  # Порог неопределенности (0-1)
        }

    async def analyze_task_complexity(self, task: str, sequential_thinking: SequentialThinking) -> Tuple[TaskComplexity, Dict[str, Any]]:
        """
        Анализирует сложность задачи для выбора подходящей стратегии

        Args:
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Кортеж из уровня сложности и метаданных анализа
        """
        logger.info(f"Analyzing complexity for task: {task[:50]}...")

        # Используем Sequential Thinking для анализа сложности
        analysis_prompt = f"Analyze this task's complexity: '{task}'. Consider:\n1. Number of steps needed\n2. Interdependencies between steps\n3. Uncertainty factors\n4. Technical complexity\n5. External dependencies"

        analysis_result = await sequential_thinking.run_thinking_chain(
            initial_thought=analysis_prompt,
            max_steps=3  # Для анализа достаточно небольшой цепочки
        )

        # Извлекаем последнюю мысль как заключение
        conclusion = analysis_result[-1]["thought"] if analysis_result else ""

        # Дополнительный запрос для структурированных метаданных
        metadata_prompt = f"Based on your previous analysis of '{task}', provide numerical ratings:\n- Steps count (1-10)\n- Interdependencies (1-10)\n- Uncertainty (1-10)\n- Technical complexity (1-10)\n- Overall complexity category (simple, medium, complex, or uncertain)"

        metadata_chain = await sequential_thinking.think(
            thought=metadata_prompt,
            next_thought_needed=False
        )

        # Парсим результаты
        metadata = self._parse_complexity_metadata(metadata_chain.get("thought", ""))

        # Определяем итоговый уровень сложности
        steps_count = metadata.get("steps_count", 5)
        uncertainty = metadata.get("uncertainty", 5) / 10  # Нормализуем к 0-1

        if "complexity_category" in metadata:
            # Используем прямую классификацию, если она есть
            complexity_category = metadata["complexity_category"].lower()
            if "simple" in complexity_category:
                complexity = TaskComplexity.SIMPLE
            elif "medium" in complexity_category:
                complexity = TaskComplexity.MEDIUM
            elif "complex" in complexity_category:
                complexity = TaskComplexity.COMPLEX
            elif "uncertain" in complexity_category:
                complexity = TaskComplexity.UNCERTAIN
            else:
                # Определяем по порогам
                complexity = self._determine_complexity_by_thresholds(steps_count, uncertainty)
        else:
            # Определяем по порогам
            complexity = self._determine_complexity_by_thresholds(steps_count, uncertainty)

        logger.info(f"Task complexity determined: {complexity.value}")

        return complexity, metadata

    def _determine_complexity_by_thresholds(self, steps_count: int, uncertainty: float) -> TaskComplexity:
        """
        Определяет сложность по пороговым значениям

        Args:
            steps_count: Количество шагов
            uncertainty: Уровень неопределенности (0-1)

        Returns:
            Уровень сложности задачи
        """
        # Сначала проверяем на неопределенность
        if uncertainty >= self.complexity_threshold["uncertainty_threshold"]:
            return TaskComplexity.UNCERTAIN

        # Затем по количеству шагов
        if steps_count >= self.complexity_threshold["medium_to_complex"]:
            return TaskComplexity.COMPLEX
        elif steps_count >= self.complexity_threshold["simple_to_medium"]:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SIMPLE

    def _parse_complexity_metadata(self, metadata_text: str) -> Dict[str, Any]:
        """
        Извлекает структурированные метаданные из текста

        Args:
            metadata_text: Текст с метаданными

        Returns:
            Словарь с метаданными
        """
        result = {}

        try:
            # Ищем числовые оценки
            if "Steps count:" in metadata_text or "Steps count " in metadata_text:
                steps_part = metadata_text.split("Steps count")[1].split("\n")[0]
                steps_digits = ''.join(c for c in steps_part if c.isdigit())
                if steps_digits:
                    result["steps_count"] = int(steps_digits)

            if "Interdependencies:" in metadata_text or "Interdependencies " in metadata_text:
                interdep_part = metadata_text.split("Interdependencies")[1].split("\n")[0]
                interdep_digits = ''.join(c for c in interdep_part if c.isdigit())
                if interdep_digits:
                    result["interdependencies"] = int(interdep_digits)

            if "Uncertainty:" in metadata_text or "Uncertainty " in metadata_text:
                uncert_part = metadata_text.split("Uncertainty")[1].split("\n")[0]
                uncert_digits = ''.join(c for c in uncert_part if c.isdigit())
                if uncert_digits:
                    result["uncertainty"] = int(uncert_digits)

            if "Technical complexity:" in metadata_text or "Technical complexity " in metadata_text:
                tech_part = metadata_text.split("Technical complexity")[1].split("\n")[0]
                tech_digits = ''.join(c for c in tech_part if c.isdigit())
                if tech_digits:
                    result["technical_complexity"] = int(tech_digits)

            # Ищем категорию сложности
            category_keywords = ["Overall complexity", "complexity category", "Category"]
            for keyword in category_keywords:
                if keyword in metadata_text:
                    category_part = metadata_text.split(keyword)[1].lower()
                    if "simple" in category_part:
                        result["complexity_category"] = "simple"
                    elif "medium" in category_part:
                        result["complexity_category"] = "medium"
                    elif "complex" in category_part:
                        result["complexity_category"] = "complex"
                    elif "uncertain" in category_part:
                        result["complexity_category"] = "uncertain"
                    break

        except Exception as e:
            logger.error(f"Error parsing complexity metadata: {str(e)}")

        return result

    async def create_plan(self, task: str, sequential_thinking: SequentialThinking) -> Dict[str, Any]:
        """
        Создает план выполнения задачи с адаптивной стратегией

        Args:
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            План выполнения задачи и метаданные
        """
        # Анализируем сложность задачи
        complexity, metadata = await self.analyze_task_complexity(task, sequential_thinking)

        # Выбираем подход к планированию в зависимости от сложности
        if complexity == TaskComplexity.SIMPLE:
            planning_approach = "linear"
            max_steps = 5
            planning_prompt = f"Create a simple linear plan for this task: '{task}'. List the steps in sequence."

        elif complexity == TaskComplexity.MEDIUM:
            planning_approach = "structured"
            max_steps = 7
            planning_prompt = f"Create a structured plan with subtasks for: '{task}'. Consider dependencies between steps."

        elif complexity == TaskComplexity.COMPLEX:
            planning_approach = "hierarchical"
            max_steps = 10
            planning_prompt = f"Create a hierarchical plan for complex task: '{task}'. Include main objectives, subtasks, and alternatives."

        else:  # UNCERTAIN
            planning_approach = "adaptive_with_contingencies"
            max_steps = 10
            planning_prompt = f"Create a plan with contingencies for uncertain task: '{task}'. Include decision points and alternatives."

        # Запускаем процесс планирования
        planning_thoughts = await sequential_thinking.run_thinking_chain(
            initial_thought=planning_prompt,
            max_steps=max_steps
        )

        # Извлекаем текст плана из последней мысли
        plan_text = planning_thoughts[-1]["thought"] if planning_thoughts else ""

        # Структурируем план в зависимости от подхода
        structured_plan = await self._structure_plan(
            plan_text=plan_text,
            complexity=complexity,
            task=task,
            sequential_thinking=sequential_thinking
        )

        # Формируем ответ
        result = {
            "plan": structured_plan,
            "plan_text": plan_text,
            "complexity": complexity.value,
            "metadata": metadata,
            "planning_approach": planning_approach,
            "thoughts": planning_thoughts
        }

        return result

    async def _structure_plan(
        self,
        plan_text: str,
        complexity: TaskComplexity,
        task: str,
        sequential_thinking: SequentialThinking
    ) -> Dict[str, Any]:
        """
        Структурирует план в формат, подходящий для выбранной стратегии

        Args:
            plan_text: Текст плана
            complexity: Сложность задачи
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Структурированный план
        """
        # Структурируем план в зависимости от сложности
        if complexity in [TaskComplexity.SIMPLE, TaskComplexity.MEDIUM]:
            # Для простых и средних задач используем линейную структуру
            structuring_prompt = f"""
            Structure this plan into a JSON format with:
            1. Task description
            2. List of steps with risk assessment for each
            3. Required tools

            Original plan: {plan_text}
            """
        else:
            # Для сложных задач с неопределенностью используем иерархическую структуру с альтернативами
            structuring_prompt = f"""
            Structure this plan into a hierarchical JSON format with:
            1. Task description
            2. Main objectives (high-level steps)
            3. For each objective:
               a. Subtasks
               b. Decision points
               c. Alternative approaches
               d. Risk assessment
            4. Required tools

            Original plan: {plan_text}
            """

        # Запрашиваем структурирование
        structure_result = await sequential_thinking.think(
            thought=structuring_prompt,
            next_thought_needed=False
        )

        # Извлекаем JSON из ответа
        json_text = self._extract_json_from_text(structure_result.get("thought", ""))

        try:
            structured_plan = json.loads(json_text)
        except Exception as e:
            logger.error(f"Error parsing JSON plan: {str(e)}")
            # В случае ошибки возвращаем простую структуру
            structured_plan = {
                "task": task,
                "steps": [{"description": step} for step in plan_text.split("\n") if step.strip()],
                "tools": []
            }

        return structured_plan

    def _extract_json_from_text(self, text: str) -> str:
        """
        Извлекает JSON из текста

        Args:
            text: Текст, возможно содержащий JSON

        Returns:
            Извлеченный JSON как строка
        """
        # Ищем JSON между тройными кавычками и фигурными скобками
        json_start_markers = [
            "```json\n",
            "```\n{",
            "```json\r\n",
            "```\r\n{",
            "```{",
            "{\n",
            "{\r\n",
            "{"
        ]

        json_end_markers = [
            "\n```",
            "\r\n```",
            "}\n```",
            "}\r\n```",
            "}"
        ]

        # Пытаемся найти начало JSON
        start_pos = -1
        for marker in json_start_markers:
            pos = text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                # Корректируем, если маркер не включает открывающую скобку
                if marker[-1] != "{":
                    start_pos = text.find("{", start_pos)
                break

        # Если не нашли явное начало, ищем первую открывающую скобку
        if start_pos == -1:
            start_pos = text.find("{")
            if start_pos == -1:
                return "{}"  # Не нашли JSON

        # Ищем конец JSON
        end_pos = -1
        for marker in json_end_markers:
            pos = text.find(marker, start_pos)
            if pos != -1:
                # Если маркер не включает закрывающую скобку, ищем её
                if marker[0] != "}":
                    closing_pos = text.rfind("}", start_pos, pos)
                    if closing_pos != -1:
                        end_pos = closing_pos + 1
                else:
                    end_pos = pos + 1
                break

        # Если не нашли явный конец, ищем последнюю закрывающую скобку
        if end_pos == -1:
            # Ищем последнюю закрывающую скобку
            last_closing = text.rfind("}")
            if last_closing != -1:
                end_pos = last_closing + 1
            else:
                return "{}"  # Не нашли закрывающую скобку

        # Извлекаем JSON
        json_text = text[start_pos:end_pos]

        # Чистим и возвращаем
        return json_text.strip()

    async def adapt_plan(self, original_plan: Dict[str, Any], new_information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Адаптирует существующий план с учетом новой информации

        Args:
            original_plan: Исходный план
            new_information: Новая информация для учета

        Returns:
            Обновленный план
        """
        # Базовая реализация просто объединяет информацию
        # В реальных сценариях здесь будет более сложная логика

        # Клонируем оригинальный план
        adapted_plan = {**original_plan}

        # Если в новой информации есть "updated_steps", заменяем шаги
        if "updated_steps" in new_information:
            adapted_plan["steps"] = new_information["updated_steps"]

        # Если есть новые инструменты, добавляем их
        if "additional_tools" in new_information:
            if "tools" not in adapted_plan:
                adapted_plan["tools"] = []
            adapted_plan["tools"].extend(new_information["additional_tools"])

        # Если есть информация об изменении сложности, обновляем
        if "complexity" in new_information:
            adapted_plan["complexity"] = new_information["complexity"]

        # Если есть дополнительные метаданные, обновляем
        if "metadata" in new_information:
            if "metadata" not in adapted_plan:
                adapted_plan["metadata"] = {}
            adapted_plan["metadata"].update(new_information["metadata"])

        return adapted_plan

    async def self_evaluate(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any],
        sequential_thinking: SequentialThinking
    ) -> Dict[str, Any]:
        """
        Выполняет самооценку адаптивной стратегии

        Args:
            task: Описание задачи
            plan: План выполнения
            execution_result: Результаты выполнения плана
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Результаты самооценки стратегии
        """
        logger.info(f"Self-evaluating adaptive strategy for task: {task[:50]}...")

        try:
            # Проверяем структуру плана
            if not plan or not isinstance(plan, dict):
                logger.warning("Invalid plan structure provided to self_evaluate")
                return {
                    "strategy_type": "adaptive",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["План имеет неверную структуру"],
                    "evaluation_text": "Невозможно оценить план из-за неверной структуры"
                }

            # Используем метакогнитивный анализ через Sequential Thinking
            evaluation_prompt = (
                f"Проведи самооценку адаптивной стратегии планирования для задачи: '{task}'\n\n"
                f"План:\n{json.dumps(plan.get('plan_text', plan), indent=2)}\n\n"
                f"Результаты выполнения:\n{json.dumps(execution_result, indent=2)}\n\n"
                f"Оцени следующие аспекты адаптивной стратегии:\n"
                f"1. Правильность определения сложности задачи\n"
                f"2. Выбор подхода в зависимости от сложности\n"
                f"3. Адаптивность к изменениям во время выполнения\n"
                f"4. Эффективность использования ресурсов\n\n"
                f"Для каждого аспекта дай числовую оценку (0-10) и краткое обоснование."
            )

            # Добавляем таймаут для процесса мышления
            try:
                evaluation_result = await asyncio.wait_for(
                    sequential_thinking.run_thinking_chain(
                        initial_thought=evaluation_prompt,
                        max_steps=3
                    ),
                    timeout=30.0  # 30 секунд таймаут
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout occurred during adaptive strategy evaluation")
                return {
                    "strategy_type": "adaptive",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["Превышено время выполнения оценки"],
                    "evaluation_text": "Оценка прервана из-за превышения времени выполнения"
                }

            final_thought = evaluation_result[-1]["thought"] if evaluation_result else ""

            # Анализируем текст для извлечения оценок
            scores = {}
            aspects = [
                ("complexity_detection", ["сложност", "определени", "complexity"]),
                ("approach_selection", ["выбор подход", "подход", "approach"]),
                ("adaptability", ["адаптивност", "изменени", "adaptability"]),
                ("resource_efficiency", ["эффективност", "ресурс", "efficiency"])
            ]

            for aspect_name, keywords in aspects:
                score = self._extract_numerical_score(final_thought, keywords)
                scores[aspect_name] = score

            # Рассчитываем общую оценку
            overall_score = sum(scores.values()) / len(scores) if scores else 0

            # Извлекаем рекомендации и области для улучшения
            improvement_areas = self._extract_improvement_areas(final_thought)

            return {
                "strategy_type": "adaptive",
                "scores": scores,
                "overall_score": overall_score,
                "improvement_areas": improvement_areas,
                "task_complexity": plan.get("task_complexity", "unknown"),
                "evaluation_text": final_thought
            }

        except Exception as e:
            logger.error(f"Error during adaptive strategy evaluation: {str(e)}")
            return {
                "strategy_type": "adaptive",
                "scores": {},
                "overall_score": 0.0,
                "improvement_areas": [f"Ошибка при оценке: {str(e)}"],
                "evaluation_text": f"Произошла ошибка при оценке стратегии: {str(e)}"
            }

    def _extract_numerical_score(self, text: str, keywords: List[str]) -> float:
        """
        Извлекает числовую оценку из текста по ключевым словам

        Args:
            text: Текст для анализа
            keywords: Ключевые слова для поиска оценки

        Returns:
            Числовая оценка (0-10)
        """
        for keyword in keywords:
            if keyword in text.lower():
                # Ищем числовую оценку рядом с ключевым словом
                parts = text.lower().split(keyword)
                for part in parts[1:]:  # Проверяем после каждого вхождения ключевого слова
                    # Ищем числа от 0 до 10
                    import re
                    matches = re.findall(r"\b(?:10|[0-9])\b", part[:30])
                    if matches:
                        try:
                            score = float(matches[0])
                            # Нормализуем к шкале 0-1
                            return score / 10
                        except ValueError:
                            pass

        # Возвращаем среднее значение, если не удалось найти оценку
        return 0.5

    def _extract_improvement_areas(self, text: str) -> List[str]:
        """
        Извлекает области для улучшения из текста оценки

        Args:
            text: Текст оценки

        Returns:
            Список областей для улучшения
        """
        improvement_areas = []

        # Ищем разделы, связанные с улучшениями
        improvement_keywords = [
            "улучшени", "improvement", "рекомендац", "recommendation",
            "можно улучшить", "недостатки", "недостаток"
        ]

        lines = text.split("\n")
        in_improvement_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, находимся ли мы в разделе улучшений
            for keyword in improvement_keywords:
                if keyword.lower() in line.lower():
                    in_improvement_section = True
                    break

            # Собираем пункты списка в разделе улучшений
            if in_improvement_section and (line.startswith("-") or line.startswith("•") or
                                         (line[0].isdigit() and "." in line[:3])):
                # Очищаем от маркеров списка
                clean_line = line.lstrip("-•0123456789. ")
                if clean_line:
                    improvement_areas.append(clean_line)

        # Если не нашли явного списка, ищем предложения с ключевыми словами
        if not improvement_areas:
            for keyword in improvement_keywords:
                for line in lines:
                    if keyword.lower() in line.lower():
                        improvement_areas.append(line.strip())
                        break

        return improvement_areas[:5]  # Ограничиваем количество рекомендаций


class TreePlanningStrategy(PlanningStrategy):
    """
    Древовидная стратегия планирования

    Создает иерархическую структуру плана с основными целями, подзадачами
    и альтернативными решениями в виде дерева.
    """

    async def create_plan(self, task: str, sequential_thinking: SequentialThinking) -> Dict[str, Any]:
        """
        Создает древовидный план выполнения задачи

        Args:
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            План выполнения задачи в виде дерева
        """
        logger.info(f"Creating tree plan for task: {task[:50]}...")

        # Для древовидной стратегии мы используем иерархическую структуру
        # с разбивкой задачи на подзадачи, цели и альтернативы
        planning_prompt = (
            f"Create a hierarchical tree plan for task: '{task}'. Follow these steps:\n"
            f"1. Identify the main goal\n"
            f"2. Break down into 3-5 main objectives\n"
            f"3. For each objective, identify 2-3 specific subtasks\n"
            f"4. For each subtask, list 1-2 alternative approaches\n"
            f"5. Consider dependencies between objectives and subtasks\n"
            f"Organize as a tree structure with clear hierarchy."
        )

        # Запускаем процесс планирования с большим числом шагов для более глубокого анализа
        planning_thoughts = await sequential_thinking.run_thinking_chain(
            initial_thought=planning_prompt,
            max_steps=8  # Больше шагов для более детального плана
        )

        # Извлекаем текст плана из последней мысли
        plan_text = planning_thoughts[-1]["thought"] if planning_thoughts else ""

        # Генерируем структурированный план из текстового описания
        structuring_prompt = (
            f"Structure the following tree plan into JSON format with the following structure:\n"
            f"- 'goal': Main goal\n"
            f"- 'objectives': Array of main objectives, each with:\n"
            f"  - 'name': Name of objective\n"
            f"  - 'description': Description\n"
            f"  - 'subtasks': Array of subtasks, each with:\n"
            f"    - 'name': Name of subtask\n"
            f"    - 'description': Description\n"
            f"    - 'alternatives': Array of alternative approaches\n"
            f"    - 'estimated_effort': Low/Medium/High\n"
            f"  - 'dependencies': Array of dependencies (names of other objectives)\n"
            f"- 'estimated_completion_time': Estimated time for completion\n"
            f"- 'risks': Array of potential risks\n\n"
            f"Plan to structure:\n{plan_text}"
        )

        # Получаем структурированный план
        structure_result = await sequential_thinking.think(
            thought=structuring_prompt,
            next_thought_needed=False
        )

        # Извлекаем JSON из ответа
        structured_json = self._extract_json_from_text(structure_result.get("thought", ""))

        try:
            structured_plan = json.loads(structured_json)
        except Exception as e:
            logger.error(f"Error parsing JSON tree plan: {str(e)}")
            # В случае ошибки создаем базовую структуру
            structured_plan = {
                "goal": task,
                "objectives": [
                    {
                        "name": f"Objective {i+1}",
                        "description": subtask,
                        "subtasks": [],
                        "dependencies": []
                    }
                    for i, subtask in enumerate(plan_text.split("\n\n")[:3])
                ],
                "estimated_completion_time": "Unknown",
                "risks": []
            }

        # Формируем финальный результат
        result = {
            "plan": structured_plan,
            "plan_text": plan_text,
            "type": "tree_plan",
            "metadata": {
                "objectives_count": len(structured_plan.get("objectives", [])),
                "creation_timestamp": self._get_timestamp()
            },
            "thoughts": planning_thoughts
        }

        logger.info(f"Tree plan created with {result['metadata']['objectives_count']} objectives")
        return result

    def _get_timestamp(self) -> str:
        """Возвращает текущую метку времени."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _extract_json_from_text(self, text: str) -> str:
        """
        Извлекает JSON из текста

        Args:
            text: Текст, возможно содержащий JSON

        Returns:
            Извлеченный JSON как строка
        """
        # Ищем JSON между тройными кавычками и фигурными скобками
        json_start_markers = [
            "```json\n",
            "```\n{",
            "```json\r\n",
            "```\r\n{",
            "```{",
            "{\n",
            "{\r\n",
            "{"
        ]

        json_end_markers = [
            "\n```",
            "\r\n```",
            "}\n```",
            "}\r\n```",
            "}"
        ]

        # Пытаемся найти начало JSON
        start_pos = -1
        for marker in json_start_markers:
            pos = text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                # Корректируем, если маркер не включает открывающую скобку
                if marker[-1] != "{":
                    start_pos = text.find("{", start_pos)
                break

        # Если не нашли явное начало, ищем первую открывающую скобку
        if start_pos == -1:
            start_pos = text.find("{")
            if start_pos == -1:
                return "{}"  # Не нашли JSON

        # Ищем конец JSON
        end_pos = -1
        for marker in json_end_markers:
            pos = text.find(marker, start_pos)
            if pos != -1:
                # Если маркер не включает закрывающую скобку, ищем её
                if marker[0] != "}":
                    closing_pos = text.rfind("}", start_pos, pos)
                    if closing_pos != -1:
                        end_pos = closing_pos + 1
                else:
                    end_pos = pos + 1
                break

        # Если не нашли явный конец, ищем последнюю закрывающую скобку
        if end_pos == -1:
            # Ищем последнюю закрывающую скобку
            last_closing = text.rfind("}")
            if last_closing != -1:
                end_pos = last_closing + 1
            else:
                return "{}"  # Не нашли закрывающую скобку

        # Извлекаем JSON
        json_text = text[start_pos:end_pos]

        # Чистим и возвращаем
        return json_text.strip()

    async def adapt_plan(self, original_plan: Dict[str, Any], new_information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Адаптирует существующий древовидный план с учетом новой информации

        Args:
            original_plan: Исходный план
            new_information: Новая информация для учета

        Returns:
            Обновленный план
        """
        logger.info("Adapting tree plan with new information")

        # Клонируем оригинальный план, чтобы не менять исходный
        adapted_plan = {**original_plan}

        # Получаем структуру плана
        plan_structure = adapted_plan.get("plan", {})

        # Обрабатываем различные типы новой информации

        # 1. Добавление новых целей
        if "new_objectives" in new_information:
            if "objectives" not in plan_structure:
                plan_structure["objectives"] = []

            plan_structure["objectives"].extend(new_information["new_objectives"])

        # 2. Изменение существующих целей
        if "updated_objectives" in new_information:
            for updated_obj in new_information["updated_objectives"]:
                obj_name = updated_obj.get("name")
                if not obj_name:
                    continue

                # Ищем существующую цель по имени
                for i, objective in enumerate(plan_structure.get("objectives", [])):
                    if objective.get("name") == obj_name:
                        # Обновляем цель, сохраняя оригинальные поля, не указанные в обновлении
                        plan_structure["objectives"][i] = {**objective, **updated_obj}
                        break

        # 3. Удаление целей
        if "removed_objectives" in new_information:
            removed_names = new_information["removed_objectives"]
            if isinstance(removed_names, list) and "objectives" in plan_structure:
                plan_structure["objectives"] = [
                    obj for obj in plan_structure["objectives"]
                    if obj.get("name") not in removed_names
                ]

        # 4. Добавление/изменение рисков
        if "updated_risks" in new_information:
            plan_structure["risks"] = new_information["updated_risks"]

        # 5. Обновление оценки времени
        if "estimated_completion_time" in new_information:
            plan_structure["estimated_completion_time"] = new_information["estimated_completion_time"]

        # 6. Обновление метаданных плана
        if "metadata" in new_information:
            if "metadata" not in adapted_plan:
                adapted_plan["metadata"] = {}
            adapted_plan["metadata"].update(new_information["metadata"])

        # 7. Добавляем метку об адаптации
        if "metadata" not in adapted_plan:
            adapted_plan["metadata"] = {}

        adapted_plan["metadata"]["last_adapted"] = self._get_timestamp()
        adapted_plan["metadata"]["adaptation_count"] = adapted_plan["metadata"].get("adaptation_count", 0) + 1

        # Обновляем план в результате
        adapted_plan["plan"] = plan_structure

        return adapted_plan

    async def self_evaluate(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any],
        sequential_thinking: SequentialThinking
    ) -> Dict[str, Any]:
        """
        Выполняет самооценку древовидной стратегии

        Args:
            task: Описание задачи
            plan: План выполнения
            execution_result: Результаты выполнения плана
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Результаты самооценки стратегии
        """
        logger.info(f"Self-evaluating tree strategy for task: {task[:50]}...")

        try:
            # Проверяем структуру плана
            if not plan or not isinstance(plan, dict):
                logger.warning("Invalid plan structure provided to self_evaluate")
                return {
                    "strategy_type": "tree",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["План имеет неверную структуру"],
                    "evaluation_text": "Невозможно оценить план из-за неверной структуры"
                }

            evaluation_prompt = (
                f"Проведи самооценку древовидной стратегии планирования для задачи: '{task}'\n\n"
                f"План:\n{json.dumps(plan.get('plan_text', plan), indent=2)}\n\n"
                f"Результаты выполнения:\n{json.dumps(execution_result, indent=2)}\n\n"
                f"Оцени следующие аспекты древовидной стратегии:\n"
                f"1. Эффективность структуры дерева\n"
                f"2. Покрытие альтернативных путей решения\n"
                f"3. Глубина исследования вариантов\n"
                f"4. Баланс между глубиной и шириной дерева\n\n"
                f"Для каждого аспекта дай числовую оценку (0-10) и краткое обоснование."
            )

            # Добавляем таймаут для процесса мышления
            try:
                evaluation_result = await asyncio.wait_for(
                    sequential_thinking.run_thinking_chain(
                        initial_thought=evaluation_prompt,
                        max_steps=3
                    ),
                    timeout=30.0  # 30 секунд таймаут
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout occurred during tree strategy evaluation")
                return {
                    "strategy_type": "tree",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["Превышено время выполнения оценки"],
                    "evaluation_text": "Оценка прервана из-за превышения времени выполнения"
                }

            final_thought = evaluation_result[-1]["thought"] if evaluation_result else ""

            # Анализируем текст для извлечения оценок
            scores = {}
            aspects = [
                ("tree_structure", ["структур", "дерев", "structure"]),
                ("alternatives_coverage", ["альтернатив", "покрыти", "coverage"]),
                ("exploration_depth", ["глубин", "исследовани", "depth"]),
                ("tree_balance", ["баланс", "шири", "balance"])
            ]

            for aspect_name, keywords in aspects:
                score = self._extract_numerical_score(final_thought, keywords)
                scores[aspect_name] = score

            # Рассчитываем общую оценку
            overall_score = sum(scores.values()) / len(scores) if scores else 0

            # Извлекаем рекомендации и области для улучшения
            improvement_areas = self._extract_improvement_areas(final_thought)

            return {
                "strategy_type": "tree",
                "scores": scores,
                "overall_score": overall_score,
                "improvement_areas": improvement_areas,
                "evaluation_text": final_thought
            }

        except Exception as e:
            logger.error(f"Error during tree strategy evaluation: {str(e)}")
            return {
                "strategy_type": "tree",
                "scores": {},
                "overall_score": 0.0,
                "improvement_areas": [f"Ошибка при оценке: {str(e)}"],
                "evaluation_text": f"Произошла ошибка при оценке стратегии: {str(e)}"
            }

    def _extract_numerical_score(self, text: str, keywords: List[str]) -> float:
        """
        Извлекает числовую оценку из текста по ключевым словам

        Args:
            text: Текст для анализа
            keywords: Ключевые слова для поиска оценки

        Returns:
            Числовая оценка (0-10), нормализованная к 0-1
        """
        for keyword in keywords:
            if keyword in text.lower():
                # Ищем числовую оценку рядом с ключевым словом
                parts = text.lower().split(keyword)
                for part in parts[1:]:
                    import re
                    matches = re.findall(r"\b(?:10|[0-9])\b", part[:30])
                    if matches:
                        try:
                            score = float(matches[0])
                            return score / 10
                        except ValueError:
                            pass
        return 0.5

    def _extract_improvement_areas(self, text: str) -> List[str]:
        """
        Извлекает области для улучшения из текста оценки

        Args:
            text: Текст оценки

        Returns:
            Список областей для улучшения
        """
        improvement_areas = []

        # Ищем разделы, связанные с улучшениями
        improvement_keywords = [
            "улучшени", "improvement", "рекомендац", "recommendation",
            "можно улучшить", "недостатки", "недостаток"
        ]

        lines = text.split("\n")
        in_improvement_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, находимся ли мы в разделе улучшений
            for keyword in improvement_keywords:
                if keyword.lower() in line.lower():
                    in_improvement_section = True
                    break

            # Собираем пункты списка в разделе улучшений
            if in_improvement_section and (line.startswith("-") or line.startswith("•") or
                                         (line[0].isdigit() and "." in line[:3])):
                # Очищаем от маркеров списка
                clean_line = line.lstrip("-•0123456789. ")
                if clean_line:
                    improvement_areas.append(clean_line)

        # Если не нашли явного списка, ищем предложения с ключевыми словами
        if not improvement_areas:
            for keyword in improvement_keywords:
                for line in lines:
                    if keyword.lower() in line.lower():
                        improvement_areas.append(line.strip())
                        break

        return improvement_areas[:5]


class UncertaintyPlanningStrategy(PlanningStrategy):
    """
    Стратегия планирования с обработкой неопределенностей

    Создает план с учетом неопределенностей, включая альтернативные пути,
    точки принятия решений и оценку вероятностей.
    """

    async def create_plan(self, task: str, sequential_thinking: SequentialThinking) -> Dict[str, Any]:
        """
        Создает план с учетом неопределенностей

        Args:
            task: Описание задачи
            sequential_thinking: Модуль последовательного мышления

        Returns:
            План выполнения задачи с обработкой неопределенностей
        """
        logger.info(f"Creating uncertainty-based plan for task: {task[:50]}...")

        # Используем метакогнитивный анализ для определения источников неопределенности
        uncertainty_prompt = (
            f"Analyze this task for uncertainty factors: '{task}'\n"
            f"1. Identify potential sources of uncertainty\n"
            f"2. For each uncertainty source, estimate importance (1-10) and impact (1-10)\n"
            f"3. Suggest contingency approaches for each uncertainty\n"
            f"4. Create decision points where the plan may need to branch"
        )

        # Запускаем процесс анализа неопределенностей
        analysis_thoughts = await sequential_thinking.run_thinking_chain(
            initial_thought=uncertainty_prompt,
            max_steps=5
        )

        # Извлекаем результаты анализа
        analysis_result = analysis_thoughts[-1]["thought"] if analysis_thoughts else ""

        # Теперь создаем основной план с учетом выявленных неопределенностей
        planning_prompt = (
            f"Create a plan for this task that accounts for uncertainties: '{task}'\n"
            f"Base your plan on this uncertainty analysis:\n{analysis_result}\n\n"
            f"Structure your plan to include:\n"
            f"1. Main steps with estimated confidence levels\n"
            f"2. Decision points where the plan may branch\n"
            f"3. Alternative approaches for uncertain parts\n"
            f"4. Contingency plans for high-risk steps"
        )

        # Запускаем процесс планирования
        planning_thoughts = await sequential_thinking.run_thinking_chain(
            initial_thought=planning_prompt,
            max_steps=6
        )

        # Извлекаем текст плана
        plan_text = planning_thoughts[-1]["thought"] if planning_thoughts else ""

        # Структурируем план в формат JSON
        structuring_prompt = (
            f"Structure this uncertainty-based plan into JSON format with:\n"
            f"1. 'task': The original task\n"
            f"2. 'uncertainty_sources': Array of identified uncertainties\n"
            f"3. 'main_steps': Array of main steps, each with:\n"
            f"   - 'description': Step description\n"
            f"   - 'confidence': Confidence level (0-1)\n"
            f"   - 'alternatives': Array of alternative approaches\n"
            f"4. 'decision_points': Array of decision points\n"
            f"5. 'contingency_plans': Array of contingency plans\n\n"
            f"Original plan:\n{plan_text}"
        )

        # Получаем структурированный план
        structure_result = await sequential_thinking.think(
            thought=structuring_prompt,
            next_thought_needed=False
        )

        # Извлекаем JSON из ответа
        json_text = self._extract_json_from_text(structure_result.get("thought", ""))

        try:
            structured_plan = json.loads(json_text)
        except Exception as e:
            logger.error(f"Error parsing JSON uncertainty plan: {str(e)}")
            # В случае ошибки создаем базовую структуру
            structured_plan = {
                "task": task,
                "uncertainty_sources": [],
                "main_steps": [{"description": step.strip(), "confidence": 0.5, "alternatives": []}
                               for step in plan_text.split("\n") if step.strip()],
                "decision_points": [],
                "contingency_plans": []
            }

        # Формируем финальный результат
        result = {
            "plan": structured_plan,
            "plan_text": plan_text,
            "type": "uncertainty_plan",
            "metadata": {
                "uncertainty_sources_count": len(structured_plan.get("uncertainty_sources", [])),
                "decision_points_count": len(structured_plan.get("decision_points", [])),
                "creation_timestamp": self._get_timestamp()
            },
            "thoughts": planning_thoughts
        }

        logger.info(f"Uncertainty plan created with {len(structured_plan.get('main_steps', []))} main steps")
        return result

    def _get_timestamp(self) -> str:
        """Возвращает текущую метку времени."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _extract_json_from_text(self, text: str) -> str:
        """
        Извлекает JSON из текста

        Args:
            text: Текст, возможно содержащий JSON

        Returns:
            Извлеченный JSON как строка
        """
        # Ищем JSON между тройными кавычками и фигурными скобками
        json_start_markers = [
            "```json\n",
            "```\n{",
            "```json\r\n",
            "```\r\n{",
            "```{",
            "{\n",
            "{\r\n",
            "{"
        ]

        json_end_markers = [
            "\n```",
            "\r\n```",
            "}\n```",
            "}\r\n```",
            "}"
        ]

        # Пытаемся найти начало JSON
        start_pos = -1
        for marker in json_start_markers:
            pos = text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                # Корректируем, если маркер не включает открывающую скобку
                if marker[-1] != "{":
                    start_pos = text.find("{", start_pos)
                break

        # Если не нашли явное начало, ищем первую открывающую скобку
        if start_pos == -1:
            start_pos = text.find("{")
            if start_pos == -1:
                return "{}"  # Не нашли JSON

        # Ищем конец JSON
        end_pos = -1
        for marker in json_end_markers:
            pos = text.find(marker, start_pos)
            if pos != -1:
                # Если маркер не включает закрывающую скобку, ищем её
                if marker[0] != "}":
                    closing_pos = text.rfind("}", start_pos, pos)
                    if closing_pos != -1:
                        end_pos = closing_pos + 1
                else:
                    end_pos = pos + 1
                break

        # Если не нашли явный конец, ищем последнюю закрывающую скобку
        if end_pos == -1:
            # Ищем последнюю закрывающую скобку
            last_closing = text.rfind("}")
            if last_closing != -1:
                end_pos = last_closing + 1
            else:
                return "{}"  # Не нашли закрывающую скобку

        # Извлекаем JSON
        json_text = text[start_pos:end_pos]

        # Чистим и возвращаем
        return json_text.strip()

    async def adapt_plan(self, original_plan: Dict[str, Any], new_information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Адаптирует существующий план с учетом новой информации

        Args:
            original_plan: Исходный план
            new_information: Новая информация для учета

        Returns:
            Обновленный план
        """
        logger.info("Adapting uncertainty plan with new information")

        # Клонируем оригинальный план
        adapted_plan = {**original_plan}
        plan_structure = adapted_plan.get("plan", {})

        # Обрабатываем новую информацию для обновления плана

        # 1. Обновляем источники неопределенности
        if "new_uncertainty_sources" in new_information:
            if "uncertainty_sources" not in plan_structure:
                plan_structure["uncertainty_sources"] = []

            plan_structure["uncertainty_sources"].extend(
                new_information["new_uncertainty_sources"]
            )

        # 2. Обновляем основные шаги плана
        if "updated_steps" in new_information:
            plan_structure["main_steps"] = new_information["updated_steps"]

        # 3. Добавляем новые точки принятия решений
        if "new_decision_points" in new_information:
            if "decision_points" not in plan_structure:
                plan_structure["decision_points"] = []

            plan_structure["decision_points"].extend(
                new_information["new_decision_points"]
            )

        # 4. Обновляем планы на случай непредвиденных обстоятельств
        if "updated_contingency_plans" in new_information:
            plan_structure["contingency_plans"] = new_information["updated_contingency_plans"]

        # 5. Обновляем метаданные
        if "metadata" not in adapted_plan:
            adapted_plan["metadata"] = {}

        adapted_plan["metadata"]["last_adapted"] = self._get_timestamp()
        adapted_plan["metadata"]["adaptation_count"] = adapted_plan["metadata"].get("adaptation_count", 0) + 1

        # Обновляем счетчики в метаданных
        adapted_plan["metadata"]["uncertainty_sources_count"] = len(plan_structure.get("uncertainty_sources", []))
        adapted_plan["metadata"]["decision_points_count"] = len(plan_structure.get("decision_points", []))

        # Обновляем план в результате
        adapted_plan["plan"] = plan_structure

        return adapted_plan

    async def self_evaluate(
        self,
        task: str,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any],
        sequential_thinking: SequentialThinking
    ) -> Dict[str, Any]:
        """
        Выполняет самооценку стратегии с учетом неопределенностей

        Args:
            task: Описание задачи
            plan: План выполнения
            execution_result: Результаты выполнения плана
            sequential_thinking: Модуль последовательного мышления

        Returns:
            Результаты самооценки стратегии
        """
        logger.info(f"Self-evaluating uncertainty strategy for task: {task[:50]}...")

        try:
            # Проверяем структуру плана
            if not plan or not isinstance(plan, dict):
                logger.warning("Invalid plan structure provided to self_evaluate")
                return {
                    "strategy_type": "uncertainty",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["План имеет неверную структуру"],
                    "evaluation_text": "Невозможно оценить план из-за неверной структуры"
                }

            evaluation_prompt = (
                f"Проведи самооценку стратегии планирования с учетом неопределенностей для задачи: '{task}'\n\n"
                f"План:\n{json.dumps(plan.get('plan_text', plan), indent=2)}\n\n"
                f"Результаты выполнения:\n{json.dumps(execution_result, indent=2)}\n\n"
                f"Оцени следующие аспекты стратегии:\n"
                f"1. Идентификация источников неопределенности\n"
                f"2. Разработка альтернативных планов\n"
                f"3. Механизмы адаптации при неопределенности\n"
                f"4. Устойчивость к непредвиденным ситуациям\n\n"
                f"Для каждого аспекта дай числовую оценку (0-10) и краткое обоснование."
            )

            # Добавляем таймаут для процесса мышления
            try:
                evaluation_result = await asyncio.wait_for(
                    sequential_thinking.run_thinking_chain(
                        initial_thought=evaluation_prompt,
                        max_steps=3
                    ),
                    timeout=30.0  # 30 секунд таймаут
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout occurred during uncertainty evaluation")
                return {
                    "strategy_type": "uncertainty",
                    "scores": {},
                    "overall_score": 0.0,
                    "improvement_areas": ["Превышено время выполнения оценки"],
                    "evaluation_text": "Оценка прервана из-за превышения времени выполнения"
                }

            final_thought = evaluation_result[-1]["thought"] if evaluation_result else ""

            # Анализируем текст для извлечения оценок
            scores = {}
            aspects = [
                ("uncertainty_identification", ["идентификаци", "источник", "identification"]),
                ("alternative_plans", ["альтернатив", "план", "alternative"]),
                ("adaptation_mechanisms", ["адаптаци", "механизм", "adaptation"]),
                ("robustness", ["устойчивост", "непредвиденн", "robustness"])
            ]

            for aspect_name, keywords in aspects:
                score = self._extract_numerical_score(final_thought, keywords)
                scores[aspect_name] = score

            # Рассчитываем общую оценку
            overall_score = sum(scores.values()) / len(scores) if scores else 0

            # Извлекаем рекомендации
            improvement_areas = self._extract_improvement_areas(final_thought)

            return {
                "strategy_type": "uncertainty",
                "scores": scores,
                "overall_score": overall_score,
                "improvement_areas": improvement_areas,
                "evaluation_text": final_thought
            }

        except Exception as e:
            logger.error(f"Error during uncertainty strategy evaluation: {str(e)}")
            return {
                "strategy_type": "uncertainty",
                "scores": {},
                "overall_score": 0.0,
                "improvement_areas": [f"Ошибка при оценке: {str(e)}"],
                "evaluation_text": f"Произошла ошибка при оценке стратегии: {str(e)}"
            }

    def _extract_numerical_score(self, text: str, keywords: List[str]) -> float:
        """
        Извлекает числовую оценку из текста по ключевым словам

        Args:
            text: Текст для анализа
            keywords: Ключевые слова для поиска оценки

        Returns:
            Числовая оценка (0-10), нормализованная к 0-1
        """
        for keyword in keywords:
            if keyword in text.lower():
                parts = text.lower().split(keyword)
                for part in parts[1:]:
                    import re
                    matches = re.findall(r"\b(?:10|[0-9])\b", part[:30])
                    if matches:
                        try:
                            score = float(matches[0])
                            return score / 10
                        except ValueError:
                            pass
        return 0.5

    def _extract_improvement_areas(self, text: str) -> List[str]:
        """
        Извлекает области для улучшения из текста оценки

        Args:
            text: Текст оценки

        Returns:
            Список областей для улучшения
        """
        improvement_areas = []

        # Ищем разделы, связанные с улучшениями
        improvement_keywords = [
            "улучшени", "improvement", "рекомендац", "recommendation",
            "можно улучшить", "недостатки", "недостаток"
        ]

        lines = text.split("\n")
        in_improvement_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, находимся ли мы в разделе улучшений
            for keyword in improvement_keywords:
                if keyword.lower() in line.lower():
                    in_improvement_section = True
                    break

            # Собираем пункты списка в разделе улучшений
            if in_improvement_section and (line.startswith("-") or line.startswith("•") or
                                         (line[0].isdigit() and "." in line[:3])):
                # Очищаем от маркеров списка
                clean_line = line.lstrip("-•0123456789. ")
                if clean_line:
                    improvement_areas.append(clean_line)

        # Если не нашли явного списка, ищем предложения с ключевыми словами
        if not improvement_areas:
            for keyword in improvement_keywords:
                for line in lines:
                    if keyword.lower() in line.lower():
                        improvement_areas.append(line.strip())
                        break

        return improvement_areas[:5]


def get_planning_strategy(strategy_type: ReasoningStrategy) -> PlanningStrategy:
    """
    Фабричный метод для создания стратегии планирования

    Args:
        strategy_type: Тип стратегии планирования

    Returns:
        Объект стратегии планирования
    """
    strategy_map = {
        ReasoningStrategy.SEQUENTIAL: AdaptivePlanningStrategy(),  # Последовательная использует адаптивную
        ReasoningStrategy.ADAPTIVE: AdaptivePlanningStrategy(),
        ReasoningStrategy.TREE: TreePlanningStrategy(),
        # Убраем UncertaintyPlanningStrategy из активного использования до полной реализации
        # ReasoningStrategy.UNCERTAIN: UncertaintyPlanningStrategy()  # Закомментировано, чтобы избежать зависаний
    }

    return strategy_map.get(strategy_type, AdaptivePlanningStrategy())  # По умолчанию - адаптивная
