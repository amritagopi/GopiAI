"""
Sequential Thinking MCP Module для GopiAI

Клиентская часть для интеграции с Sequential Thinking модулем MCP.
Позволяет выполнять цепочки рассуждений с последовательными шагами мышления.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import json

from app.logger import logger
from app.mcp.client import MCPClient


class SequentialThinking:
    """
    Клиентский интерфейс для работы с модулем Sequential Thinking.

    Позволяет создавать цепочки рассуждений с пошаговым мышлением,
    ревизиями мыслей и ветвлением логики для решения сложных задач.
    """

    def __init__(self, mcp_client: MCPClient):
        """
        Инициализирует интерфейс Sequential Thinking.

        Args:
            mcp_client: Клиент MCP для отправки запросов к модулю
        """
        self.mcp_client = mcp_client
        self.tool_name = "mcp_sequential-thinking_sequentialthinking"
        self.thoughts: List[Dict[str, Any]] = []
        self.current_thought_number = 1
        self.total_thoughts = 5  # Начальная оценка количества шагов
        self.initialized = False

    async def initialize(self) -> bool:
        """
        Проверяет доступность модуля Sequential Thinking.

        Returns:
            True если модуль доступен, False в противном случае
        """
        try:
            available_tools = set(self.mcp_client.tool_map.keys())
            if self.tool_name not in available_tools:
                logger.error(f"Sequential Thinking tool {self.tool_name} not found")
                return False

            logger.info("Sequential Thinking module initialized")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing Sequential Thinking: {str(e)}")
            return False

    def is_available(self) -> bool:
        """
        Проверяет, доступен ли модуль Sequential Thinking.

        Returns:
            True если модуль доступен, False в противном случае
        """
        return self.initialized

    async def think(
        self,
        thought: str,
        next_thought_needed: bool = True,
        is_revision: bool = False,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
        needs_more_thoughts: bool = False,
    ) -> Dict[str, Any]:
        """
        Выполняет шаг мышления в цепочке рассуждений.

        Args:
            thought: Текст текущего шага мышления
            next_thought_needed: Нужен ли следующий шаг
            is_revision: Является ли текущий шаг ревизией предыдущего
            revises_thought: Номер пересматриваемого шага (если is_revision=True)
            branch_from_thought: Номер шага, от которого идет ветвление
            branch_id: Идентификатор ветки
            needs_more_thoughts: Нужны ли дополнительные шаги

        Returns:
            Результат выполнения шага мышления
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return {
                "error": "Sequential Thinking not initialized",
                "nextThoughtNeeded": False
            }

        # Сохраняем мысль в истории
        thought_record = {
            "thought": thought,
            "thoughtNumber": self.current_thought_number,
            "totalThoughts": self.total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
        }

        # Добавляем опциональные параметры если они указаны
        if is_revision and revises_thought is not None:
            thought_record["revisesThought"] = revises_thought

        if branch_from_thought is not None:
            thought_record["branchFromThought"] = branch_from_thought

        if branch_id is not None:
            thought_record["branchId"] = branch_id

        if needs_more_thoughts:
            thought_record["needsMoreThoughts"] = needs_more_thoughts

        # Сохраняем мысль в истории
        self.thoughts.append(thought_record)

        # Вызываем Sequential Thinking через MCP
        try:
            result = await self.mcp_client.call_tool(self.tool_name, thought_record)

            # Обновляем счетчик шагов
            if next_thought_needed:
                self.current_thought_number += 1

            # Обновляем общее количество шагов, если оно изменилось
            if "totalThoughts" in result and result["totalThoughts"] != self.total_thoughts:
                self.total_thoughts = result["totalThoughts"]

            return result

        except Exception as e:
            logger.error(f"Error in Sequential Thinking: {str(e)}")
            return {
                "error": str(e),
                "nextThoughtNeeded": False
            }

    async def run_thinking_chain(self, initial_thought: str, max_steps: int = 10) -> List[Dict[str, Any]]:
        """
        Запускает полную цепочку рассуждений, начиная с указанной мысли.

        Args:
            initial_thought: Начальная мысль для цепочки рассуждений
            max_steps: Максимальное количество шагов

        Returns:
            Список всех шагов мышления
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return [{"thought": "Error: Sequential Thinking not initialized", "nextThoughtNeeded": False}]

        # Сбрасываем текущее состояние
        self.thoughts = []
        self.current_thought_number = 1

        # Выполняем первый шаг
        result = await self.think(initial_thought)

        # Продолжаем цепочку, пока нужны следующие шаги
        step_count = 1
        while (
            result.get("nextThoughtNeeded", False) and
            step_count < max_steps
        ):
            step_count += 1

            # Формируем следующую мысль на основе предыдущей
            next_thought = f"Step {step_count}: Continuing analysis..."
            if "suggestedNextThought" in result:
                next_thought = result["suggestedNextThought"]

            result = await self.think(
                thought=next_thought,
                next_thought_needed=step_count < max_steps - 1,  # Оставляем место для заключения
                is_revision=False
            )

        # Добавляем заключительный шаг с выводами
        if step_count < max_steps:
            await self.think(
                thought=f"Final conclusion based on previous {step_count} steps of analysis:",
                next_thought_needed=False,
                is_revision=False
            )

        return self.thoughts

    async def analyze_problem(self, problem_description: str, depth: int = 5) -> Dict[str, Any]:
        """
        Анализирует проблему с использованием Sequential Thinking.

        Args:
            problem_description: Описание проблемы для анализа
            depth: Глубина анализа (количество шагов рассуждения)

        Returns:
            Результаты анализа с выводами и рекомендациями
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return {"error": "Sequential Thinking not initialized"}

        # Формируем начальную мысль
        initial_thought = f"Let's analyze the problem: {problem_description}"

        # Запускаем цепочку рассуждений
        thought_chain = await self.run_thinking_chain(initial_thought, max_steps=depth)

        # Формируем структурированный анализ
        analysis = {
            "problem": problem_description,
            "analysis_steps": [],
            "key_insights": [],
            "conclusion": ""
        }

        # Извлекаем шаги анализа
        for thought in thought_chain:
            analysis["analysis_steps"].append(thought.get("thought", ""))

        # Извлекаем ключевые выводы и заключение
        if len(thought_chain) > 0:
            # Последняя мысль - заключение
            analysis["conclusion"] = thought_chain[-1].get("thought", "")

            # Извлекаем ключевые выводы из всех мыслей
            for thought in thought_chain:
                content = thought.get("thought", "")
                # Ищем ключевые выводы по маркерам
                if "key insight:" in content.lower() or "important finding:" in content.lower():
                    lines = content.split("\n")
                    for line in lines:
                        if "key insight:" in line.lower() or "important finding:" in line.lower():
                            analysis["key_insights"].append(line)

        return analysis

    async def evaluate_solution(self, problem: str, solution: str, criteria: List[str] = None) -> Dict[str, Any]:
        """
        Оценивает предложенное решение проблемы.

        Args:
            problem: Описание проблемы
            solution: Предлагаемое решение
            criteria: Критерии оценки (если None, используются стандартные)

        Returns:
            Результаты оценки с сильными и слабыми сторонами решения
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return {"error": "Sequential Thinking not initialized"}

        # Устанавливаем стандартные критерии, если не указаны
        if criteria is None:
            criteria = [
                "Эффективность",
                "Реализуемость",
                "Масштабируемость",
                "Поддерживаемость",
                "Безопасность"
            ]

        # Формируем начальную мысль
        initial_thought = (
            f"Let's evaluate the proposed solution for the problem.\n\n"
            f"Problem: {problem}\n\n"
            f"Proposed solution: {solution}\n\n"
            f"Evaluation criteria: {', '.join(criteria)}"
        )

        # Запускаем цепочку рассуждений
        thought_chain = await self.run_thinking_chain(initial_thought, max_steps=len(criteria) + 2)

        # Формируем структурированную оценку
        evaluation = {
            "problem": problem,
            "solution": solution,
            "criteria_evaluation": {},
            "strengths": [],
            "weaknesses": [],
            "overall_score": 0,
            "recommendation": ""
        }

        # Собираем оценки по критериям и выявляем сильные/слабые стороны
        scores = []
        for i, criterion in enumerate(criteria):
            if i < len(thought_chain) - 1:  # Оставляем последнюю мысль для общей оценки
                thought = thought_chain[i].get("thought", "")

                # Ищем оценку по 10-балльной шкале
                score = 0
                for line in thought.split("\n"):
                    if "score:" in line.lower() or "rating:" in line.lower():
                        try:
                            # Ищем числа в строке
                            import re
                            numbers = re.findall(r'\d+', line)
                            if numbers:
                                score = int(numbers[0])
                                if "out of 10" in line.lower() and score > 10:
                                    score = score / 10  # Нормализуем до 10, если указано "out of 100"
                                scores.append(score)
                        except Exception:
                            pass

                # Записываем оценку по критерию
                evaluation["criteria_evaluation"][criterion] = {
                    "analysis": thought,
                    "score": score
                }

                # Выявляем сильные и слабые стороны
                for line in thought.split("\n"):
                    if "strength:" in line.lower() or "advantage:" in line.lower():
                        evaluation["strengths"].append(line.strip())
                    elif "weakness:" in line.lower() or "disadvantage:" in line.lower():
                        evaluation["weaknesses"].append(line.strip())

        # Вычисляем общую оценку
        if scores:
            evaluation["overall_score"] = sum(scores) / len(scores)

        # Добавляем рекомендацию из последней мысли
        if thought_chain:
            evaluation["recommendation"] = thought_chain[-1].get("thought", "")

        return evaluation

    async def generate_structured_output(
        self,
        task: str,
        output_format: Dict[str, Any],
        depth: int = 5
    ) -> Dict[str, Any]:
        """
        Генерирует структурированный вывод на основе заданного формата.

        Args:
            task: Описание задачи
            output_format: Шаблон формата вывода с описанием полей
            depth: Глубина рассуждений

        Returns:
            Структурированный вывод, соответствующий заданному формату
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return {"error": "Sequential Thinking not initialized"}

        # Формируем начальную мысль
        format_description = json.dumps(output_format, indent=2)
        initial_thought = (
            f"Let's generate structured output for the task: {task}\n\n"
            f"Required output format:\n{format_description}\n\n"
            f"I'll think through this step by step to produce the required output."
        )

        # Запускаем цепочку рассуждений
        thought_chain = await self.run_thinking_chain(initial_thought, max_steps=depth)

        # Последняя мысль должна содержать структурированный вывод
        result = {"task": task}
        if thought_chain:
            final_thought = thought_chain[-1].get("thought", "")

            # Пытаемся извлечь JSON из последней мысли
            try:
                # Находим JSON блок
                import re
                json_match = re.search(r'\{[\s\S]*\}', final_thought)

                if json_match:
                    json_str = json_match.group(0)
                    structured_output = json.loads(json_str)

                    # Проверяем, соответствует ли вывод заданному формату
                    for key in output_format:
                        if key not in structured_output:
                            structured_output[key] = None

                    result["output"] = structured_output
                else:
                    # Если JSON не найден, попробуем структурировать вывод вручную
                    structured_output = {}
                    for key in output_format:
                        pattern = fr'{key}:([^:]*?)(?=\n\w+:|$)'
                        match = re.search(pattern, final_thought, re.IGNORECASE | re.DOTALL)
                        if match:
                            structured_output[key] = match.group(1).strip()
                        else:
                            structured_output[key] = None

                    result["output"] = structured_output
            except Exception as e:
                logger.error(f"Error parsing structured output: {str(e)}")
                result["error"] = f"Failed to parse structured output: {str(e)}"
                result["raw_output"] = final_thought
        else:
            result["error"] = "No thoughts generated"

        return result

    async def branching_analysis(
        self,
        question: str,
        options: List[str],
        depth_per_option: int = 3
    ) -> Dict[str, Any]:
        """
        Выполняет ветвящийся анализ для оценки нескольких вариантов решения.

        Args:
            question: Вопрос или проблема для анализа
            options: Список вариантов для оценки
            depth_per_option: Глубина анализа для каждого варианта

        Returns:
            Результаты сравнительного анализа вариантов
        """
        # Проверяем инициализацию
        if not self.initialized:
            logger.error("Sequential Thinking not initialized")
            return {"error": "Sequential Thinking not initialized"}

        # Сбрасываем текущее состояние
        self.thoughts = []
        self.current_thought_number = 1

        # Начальная мысль для анализа вопроса
        initial_thought = f"Let's analyze the question or problem: {question}"
        result = await self.think(initial_thought)

        # Анализируем каждый вариант
        option_analyses = {}
        for i, option in enumerate(options):
            # Создаем ветку для анализа варианта
            branch_id = f"option_{i+1}"

            # Первая мысль в ветке - описание варианта
            option_thought = (
                f"Let's analyze option {i+1}: {option}\n\n"
                f"I'll evaluate this option's strengths, weaknesses, and overall fit for the question."
            )

            option_result = await self.think(
                thought=option_thought,
                next_thought_needed=True,
                branch_from_thought=1,  # Ветвимся от начальной мысли
                branch_id=branch_id
            )

            # Продолжаем анализ варианта
            option_thoughts = [option_result]
            current_option_step = 1

            while (
                option_result.get("nextThoughtNeeded", False) and
                current_option_step < depth_per_option
            ):
                current_option_step += 1

                next_option_thought = f"Continuing analysis of option {i+1}: {option}"
                if "suggestedNextThought" in option_result:
                    next_option_thought = option_result["suggestedNextThought"]

                option_result = await self.think(
                    thought=next_option_thought,
                    next_thought_needed=current_option_step < depth_per_option,
                    branch_id=branch_id
                )

                option_thoughts.append(option_result)

            # Добавляем заключительную оценку варианта
            final_option_thought = f"Final evaluation of option {i+1}: {option}"
            final_option_result = await self.think(
                thought=final_option_thought,
                next_thought_needed=False,
                branch_id=branch_id
            )

            option_thoughts.append(final_option_result)

            # Собираем анализ варианта
            option_analyses[option] = {
                "thoughts": [t.get("thought", "") for t in option_thoughts],
                "final_evaluation": final_option_result.get("thought", "")
            }

        # Добавляем заключительное сравнение всех вариантов
        comparison_thought = (
            f"Let's compare all {len(options)} options:\n\n"
            f"Options to compare:\n"
            + "\n".join([f"- Option {i+1}: {option}" for i, option in enumerate(options)])
        )

        comparison_result = await self.think(
            thought=comparison_thought,
            next_thought_needed=False,
        )

        # Формируем итоговый результат
        return {
            "question": question,
            "options": options,
            "option_analyses": option_analyses,
            "comparison": comparison_result.get("thought", ""),
            "thoughts": self.thoughts
        }

    def get_thought_history(self) -> List[Dict[str, Any]]:
        """
        Возвращает историю всех шагов мышления.

        Returns:
            Список всех шагов мышления
        """
        return self.thoughts

    def reset(self) -> None:
        """Сбрасывает состояние цепочки рассуждений."""
        self.thoughts = []
        self.current_thought_number = 1
        self.total_thoughts = 5
