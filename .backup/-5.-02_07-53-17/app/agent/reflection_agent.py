"""
Модуль агента размышлений для GopiAI Reasoning Agent

Обеспечивает глубокий анализ подходов, проверку размышлений на противоречия,
выявление скрытых допущений и более основательное исследование альтернатив.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from enum import Enum

from app.agent.reasoning import ReasoningAgent
from app.agent.thought_tree import ThoughtTree, ThoughtNode
from app.agent.metacognitive_analyzer import MetacognitiveAnalyzer
from app.config.reasoning_config import ReasoningStrategy
from app.logger import logger
from app.mcp.sequential_thinking import SequentialThinking
from app.prompt.reflection import (
    REFLECTION_SYSTEM_PROMPT,
    CONTRADICTION_ANALYSIS_PROMPT,
    ASSUMPTION_ANALYSIS_PROMPT,
    ALTERNATIVE_APPROACH_PROMPT,
    CONCLUSION_VERIFICATION_PROMPT,
)


class ReflectionMode(str, Enum):
    """Режимы работы агента размышлений"""
    CONTRADICTION = "contradiction"  # Анализ противоречий
    ASSUMPTION = "assumption"  # Анализ скрытых допущений
    ALTERNATIVE = "alternative"  # Анализ альтернативных подходов
    VERIFICATION = "verification"  # Проверка достоверности выводов
    COMPREHENSIVE = "comprehensive"  # Комплексный анализ всех аспектов


class ReflectionResult:
    """
    Результат рефлексивного анализа

    Содержит структурированные результаты процесса размышления,
    включая выявленные проблемы, рекомендации и метаданные.
    """

    def __init__(
        self,
        mode: ReflectionMode,
        original_content: str,
        reflection_summary: str,
        issues_found: List[Dict[str, Any]],
        recommendations: List[str],
        confidence_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует результат рефлексивного анализа

        Args:
            mode: Режим проведенного анализа
            original_content: Исходный контент для анализа
            reflection_summary: Краткое описание результатов анализа
            issues_found: Список выявленных проблем с деталями
            recommendations: Рекомендации по улучшению
            confidence_score: Оценка достоверности (0-1)
            metadata: Дополнительные метаданные
        """
        self.mode = mode
        self.original_content = original_content
        self.reflection_summary = reflection_summary
        self.issues_found = issues_found
        self.recommendations = recommendations
        self.confidence_score = confidence_score
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует результат в словарь"""
        return {
            "mode": self.mode.value,
            "original_content": self.original_content,
            "reflection_summary": self.reflection_summary,
            "issues_found": self.issues_found,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReflectionResult":
        """Создает объект из словаря"""
        return cls(
            mode=ReflectionMode(data.get("mode", "comprehensive")),
            original_content=data.get("original_content", ""),
            reflection_summary=data.get("reflection_summary", ""),
            issues_found=data.get("issues_found", []),
            recommendations=data.get("recommendations", []),
            confidence_score=data.get("confidence_score", 0.0),
            metadata=data.get("metadata", {})
        )


class ReflectionAgent(ReasoningAgent):
    """
    Агент размышлений расширяет возможности Reasoning Agent,
    добавляя функциональность глубокого анализа рассуждений,
    выявления противоречий, скрытых допущений и более тщательной
    проверки достоверности выводов.
    """

    name: str = "reflection_agent"
    description: str = "A reasoning agent with deep reflection capabilities"

    # Переопределяем системный промпт
    system_prompt: str = REFLECTION_SYSTEM_PROMPT

    # Дополнительные модули
    required_tools = [
        "mcp_serena_initial_instructions",
        "mcp_sequential-thinking_sequentialthinking",
    ]

    # История рефлексивных анализов
    reflection_history: List[ReflectionResult] = []

    async def initialize(
        self,
        connection_type: Optional[str] = None,
        server_url: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        skip_serena_check: bool = False,
    ) -> None:
        """
        Инициализирует агента размышлений

        Args:
            connection_type: Тип подключения
            server_url: URL MCP сервера
            command: Команда для запуска
            args: Аргументы для команды
            skip_serena_check: Пропустить проверку Serena
        """
        # Инициализируем базовый ReasoningAgent
        await super().initialize(
            connection_type=connection_type,
            server_url=server_url,
            command=command,
            args=args,
            skip_serena_check=skip_serena_check
        )

        # Дополнительная инициализация для агента размышлений
        logger.info("Initializing reflection agent")

        # Создаем специальную ветку для рефлексивных мыслей в дереве мыслей
        if self.thought_tree and self.thought_tree.root:
            # Добавляем специальный узел для ветки рефлексий
            self.reflection_branch_id = self.thought_tree.add_thought(
                content="Рефлексивный анализ",
                node_type="reflection_branch"
            )
            logger.info(f"Reflection branch created in thought tree: {self.reflection_branch_id}")
        else:
            self.reflection_branch_id = None
            logger.warning("Could not create reflection branch in thought tree (root not available)")

        logger.info("Reflection agent initialization completed")

    async def reflect_on_content(
        self,
        content: str,
        mode: ReflectionMode = ReflectionMode.COMPREHENSIVE,
        depth: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReflectionResult:
        """
        Выполняет рефлексивный анализ заданного содержимого

        Args:
            content: Текст для анализа
            mode: Режим анализа
            depth: Глубина анализа
            metadata: Дополнительные метаданные

        Returns:
            Результат рефлексивного анализа
        """
        logger.info(f"Starting reflection analysis in mode: {mode.value}")

        if not self.sequential_thinking:
            error_msg = "Sequential Thinking not initialized"
            logger.error(error_msg)
            return self._create_error_reflection_result(mode, content, error_msg)

        # Выбираем шаблон промпта в зависимости от режима
        if mode == ReflectionMode.CONTRADICTION:
            prompt_template = CONTRADICTION_ANALYSIS_PROMPT
        elif mode == ReflectionMode.ASSUMPTION:
            prompt_template = ASSUMPTION_ANALYSIS_PROMPT
        elif mode == ReflectionMode.ALTERNATIVE:
            prompt_template = ALTERNATIVE_APPROACH_PROMPT
        elif mode == ReflectionMode.VERIFICATION:
            prompt_template = CONCLUSION_VERIFICATION_PROMPT
        else:  # COMPREHENSIVE
            # Для комплексного анализа создаем комбинированный промпт
            prompt_template = (
                "Выполните комплексный рефлексивный анализ следующего содержимого, "
                "включая проверку на противоречия, выявление скрытых допущений, "
                "рассмотрение альтернативных подходов и проверку достоверности выводов.\n\n"
                "Содержимое для анализа:\n{content}\n\n"
                "Структурируйте анализ по следующим разделам:\n"
                "1. Выявленные противоречия\n"
                "2. Скрытые допущения\n"
                "3. Альтернативные подходы\n"
                "4. Достоверность выводов\n"
                "5. Общие рекомендации по улучшению"
            )

        # Формируем начальную мысль для анализа
        initial_thought = prompt_template.format(content=content)

        # Выполняем цепочку рассуждений через Sequential Thinking
        thought_chain = await self.sequential_thinking.run_thinking_chain(
            initial_thought=initial_thought,
            max_steps=depth
        )

        # Обрабатываем результаты анализа
        result = await self._process_reflection_results(
            thought_chain=thought_chain,
            mode=mode,
            content=content,
            metadata=metadata
        )

        # Сохраняем результат в историю
        self.reflection_history.append(result)

        # Добавляем результат в дерево мыслей
        await self._add_reflection_to_thought_tree(result)

        logger.info(f"Reflection analysis completed with confidence score: {result.confidence_score:.2f}")
        return result

    async def _process_reflection_results(
        self,
        thought_chain: List[Dict[str, Any]],
        mode: ReflectionMode,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReflectionResult:
        """
        Обрабатывает результаты цепочки мыслей для создания структурированного результата

        Args:
            thought_chain: Цепочка мыслей из Sequential Thinking
            mode: Режим анализа
            content: Исходное содержимое
            metadata: Дополнительные метаданные

        Returns:
            Структурированный результат рефлексии
        """
        if not thought_chain:
            return self._create_error_reflection_result(
                mode, content, "No thoughts were generated"
            )

        # Извлекаем заключительную мысль
        final_thought = thought_chain[-1].get("thought", "")

        # Извлекаем проблемы и рекомендации из текста анализа
        issues, recommendations, confidence_score = self._extract_issues_and_recommendations(
            final_thought, mode
        )

        # Формируем краткое резюме
        summary = self._extract_summary(final_thought)

        # Создаем результат анализа
        result = ReflectionResult(
            mode=mode,
            original_content=content,
            reflection_summary=summary,
            issues_found=issues,
            recommendations=recommendations,
            confidence_score=confidence_score,
            metadata={
                "thought_chain": [t.get("thought", "") for t in thought_chain],
                "timestamp": datetime.now().isoformat(),
                **metadata or {}
            }
        )

        return result

    def _create_error_reflection_result(
        self,
        mode: ReflectionMode,
        content: str,
        error_message: str
    ) -> ReflectionResult:
        """
        Создает результат рефлексии при ошибке

        Args:
            mode: Режим анализа
            content: Исходное содержимое
            error_message: Сообщение об ошибке

        Returns:
            Результат рефлексии с ошибкой
        """
        return ReflectionResult(
            mode=mode,
            original_content=content,
            reflection_summary=f"Error during reflection: {error_message}",
            issues_found=[{"type": "error", "description": error_message}],
            recommendations=["Повторите анализ с более конкретным содержимым"],
            confidence_score=0.0,
            metadata={"error": error_message}
        )

    def _extract_issues_and_recommendations(
        self,
        reflection_text: str,
        mode: ReflectionMode
    ) -> Tuple[List[Dict[str, Any]], List[str], float]:
        """
        Извлекает проблемы и рекомендации из текста анализа

        Args:
            reflection_text: Текст результата рефлексии
            mode: Режим анализа

        Returns:
            Кортеж из списка проблем, списка рекомендаций и оценки достоверности
        """
        issues = []
        recommendations = []
        confidence_score = 0.5  # Значение по умолчанию

        # Ищем разделы с проблемами в зависимости от режима
        problem_section_headers = {
            ReflectionMode.CONTRADICTION: ["противоречи", "несоответствия", "contradictions"],
            ReflectionMode.ASSUMPTION: ["допущени", "предположени", "assumptions"],
            ReflectionMode.ALTERNATIVE: ["альтернатив", "alternatives"],
            ReflectionMode.VERIFICATION: ["достоверност", "обоснованност", "verification"],
            ReflectionMode.COMPREHENSIVE: ["проблем", "issues", "противоречи", "допущени", "альтернатив"]
        }

        # Ищем раздел с рекомендациями
        recommendation_headers = ["рекомендац", "улучшени", "предложени", "recommendations"]

        # Разбиваем текст на разделы
        sections = self._split_text_into_sections(reflection_text)

        # Обрабатываем каждый раздел
        for section_header, section_content in sections:
            # Определяем, относится ли раздел к проблемам
            is_problem_section = False
            problem_type = ""

            for keyword_list in problem_section_headers.values():
                for keyword in keyword_list:
                    if keyword.lower() in section_header.lower():
                        is_problem_section = True
                        problem_type = self._determine_problem_type(section_header)
                        break
                if is_problem_section:
                    break

            # Если это раздел с проблемами, извлекаем их
            if is_problem_section:
                section_issues = self._extract_items_from_section(section_content)
                for issue in section_issues:
                    issues.append({
                        "type": problem_type,
                        "description": issue
                    })

            # Проверяем, относится ли раздел к рекомендациям
            is_recommendation_section = False
            for keyword in recommendation_headers:
                if keyword.lower() in section_header.lower():
                    is_recommendation_section = True
                    break

            # Если это раздел с рекомендациями, извлекаем их
            if is_recommendation_section:
                section_recommendations = self._extract_items_from_section(section_content)
                recommendations.extend(section_recommendations)

            # Ищем оценку достоверности
            if "достоверност" in section_header.lower() or "confidence" in section_header.lower():
                confidence_score = self._extract_confidence_score(section_content)

        # Если не удалось найти рекомендации структурированно,
        # ищем их по маркерам списка во всем тексте
        if not recommendations:
            recommendations = self._extract_recommendations_from_text(reflection_text)

        # Если не удалось извлечь проблемы структурированно,
        # пытаемся найти их в тексте
        if not issues:
            issues = self._extract_issues_from_text(reflection_text, mode)

        # Если оценка достоверности не была найдена явно,
        # пытаемся найти ее в тексте
        if confidence_score == 0.5:
            confidence_score = self._extract_confidence_score(reflection_text)

        return issues, recommendations, confidence_score

    def _determine_problem_type(self, section_header: str) -> str:
        """
        Определяет тип проблемы на основе заголовка раздела

        Args:
            section_header: Заголовок раздела

        Returns:
            Тип проблемы
        """
        header_lower = section_header.lower()

        if "противоречи" in header_lower or "inconsistenc" in header_lower:
            return "contradiction"
        elif "допущени" in header_lower or "assumption" in header_lower:
            return "assumption"
        elif "альтернатив" in header_lower or "alternative" in header_lower:
            return "alternative"
        elif "достоверност" in header_lower or "verification" in header_lower:
            return "verification"
        else:
            return "general"

    def _split_text_into_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Разбивает текст на секции по заголовкам

        Args:
            text: Текст для разбиения

        Returns:
            Список кортежей (заголовок, содержимое)
        """
        sections = []
        lines = text.split('\n')

        current_header = ""
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, является ли строка заголовком
            is_header = False

            # Заголовки markdown
            if line.startswith('#'):
                is_header = True
            # Числовая нумерация (например, "1. ", "2. ")
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.' and line[2].isspace():
                is_header = True
            # Заголовки с двоеточием в конце
            elif line.endswith(':'):
                is_header = True

            if is_header:
                # Если был предыдущий заголовок, сохраняем его содержимое
                if current_header and current_content:
                    sections.append((current_header, '\n'.join(current_content)))
                    current_content = []

                current_header = line
            else:
                current_content.append(line)

        # Добавляем последнюю секцию
        if current_header and current_content:
            sections.append((current_header, '\n'.join(current_content)))

        return sections

    def _extract_items_from_section(self, section_content: str) -> List[str]:
        """
        Извлекает элементы списка из содержимого раздела

        Args:
            section_content: Содержимое раздела

        Returns:
            Список элементов
        """
        items = []
        lines = section_content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, является ли строка элементом списка
            is_list_item = False
            clean_line = line

            # Маркированный список (например, "- ", "* ", "• ")
            if line.startswith(('-', '*', '•')) and len(line) > 2 and line[1].isspace():
                is_list_item = True
                clean_line = line[2:].strip()
            # Числовой список (например, "1. ", "2. ")
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.' and line[2].isspace():
                is_list_item = True
                clean_line = line[line.find('.')+1:].strip()

            if is_list_item and clean_line:
                items.append(clean_line)
            elif not is_list_item and line:
                # Если строка не является элементом списка, но содержит текст
                items.append(line)

        return items

    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """
        Извлекает рекомендации из текста

        Args:
            text: Текст для анализа

        Returns:
            Список рекомендаций
        """
        recommendations = []

        # Ищем маркеры рекомендаций
        markers = [
            "рекомендуется", "рекомендуем", "следует", "предлагается",
            "recommend", "suggest", "should", "could"
        ]

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            for marker in markers:
                if marker.lower() in line.lower():
                    recommendations.append(line)
                    break

        # Если не нашли явных рекомендаций, ищем элементы списков
        if not recommendations:
            list_patterns = [
                r"- .*", r"\* .*", r"• .*",  # Маркированные списки
                r"\d+\. .*"  # Нумерованные списки
            ]

            for pattern in list_patterns:
                import re
                list_items = re.findall(pattern, text)
                for item in list_items:
                    # Удаляем маркер списка
                    clean_item = re.sub(r"^[- \*•\d\.]+\s*", "", item).strip()
                    if clean_item:
                        recommendations.append(clean_item)

        return recommendations

    def _extract_issues_from_text(self, text: str, mode: ReflectionMode) -> List[Dict[str, Any]]:
        """
        Извлекает проблемы из текста

        Args:
            text: Текст для анализа
            mode: Режим анализа

        Returns:
            Список проблем с типами
        """
        issues = []
        problem_type = mode.value

        # Маркеры проблем в зависимости от режима
        markers = {
            ReflectionMode.CONTRADICTION: ["противоречи", "несоответствие", "contradiction", "inconsistency"],
            ReflectionMode.ASSUMPTION: ["допущени", "предположени", "assumption"],
            ReflectionMode.ALTERNATIVE: ["альтернатив", "alternative"],
            ReflectionMode.VERIFICATION: ["недостоверн", "неточност", "inaccuracy"],
            ReflectionMode.COMPREHENSIVE: ["проблем", "вопрос", "issue", "problem"]
        }

        mode_markers = markers.get(mode, markers[ReflectionMode.COMPREHENSIVE])

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            for marker in mode_markers:
                if marker.lower() in line.lower():
                    issues.append({
                        "type": problem_type,
                        "description": line
                    })
                    break

        return issues

    def _extract_confidence_score(self, text: str) -> float:
        """
        Извлекает оценку достоверности из текста

        Args:
            text: Текст для анализа

        Returns:
            Оценка достоверности (0-1)
        """
        confidence_score = 0.5  # Значение по умолчанию

        # Ищем числовые оценки (например, "70%", "0.8", "8/10")
        import re

        # Процентная запись
        percent_match = re.search(r"(\d+)%", text)
        if percent_match:
            try:
                confidence_score = float(percent_match.group(1)) / 100
                return min(max(confidence_score, 0), 1)  # Ограничиваем значение от 0 до 1
            except ValueError:
                pass

        # Десятичная запись
        decimal_match = re.search(r"(?<!\d)0\.\d+|(?<!\d)1\.0", text)
        if decimal_match:
            try:
                confidence_score = float(decimal_match.group(0))
                return min(max(confidence_score, 0), 1)
            except ValueError:
                pass

        # Запись вида "X/10"
        fraction_match = re.search(r"(\d+)\s*\/\s*10", text)
        if fraction_match:
            try:
                confidence_score = float(fraction_match.group(1)) / 10
                return min(max(confidence_score, 0), 1)
            except ValueError:
                pass

        # Текстовые оценки
        high_confidence_markers = ["высок", "high", "strong"]
        low_confidence_markers = ["низк", "low", "weak"]
        medium_confidence_markers = ["средн", "medium", "moderate"]

        for marker in high_confidence_markers:
            if marker.lower() in text.lower():
                return 0.8

        for marker in low_confidence_markers:
            if marker.lower() in text.lower():
                return 0.3

        for marker in medium_confidence_markers:
            if marker.lower() in text.lower():
                return 0.5

        return confidence_score

    def _extract_summary(self, text: str) -> str:
        """
        Извлекает краткое резюме из текста

        Args:
            text: Текст для анализа

        Returns:
            Краткое резюме
        """
        # Ищем разделы с выводами или резюме
        summary_markers = ["вывод", "заключени", "резюме", "summary", "conclusion"]

        sections = self._split_text_into_sections(text)

        for section_header, section_content in sections:
            for marker in summary_markers:
                if marker.lower() in section_header.lower():
                    return section_content

        # Если специализированный раздел не найден, берем первый абзац
        paragraphs = text.split('\n\n')
        if paragraphs:
            first_paragraph = paragraphs[0].strip()
            # Если первый абзац слишком длинный, берем только первое предложение
            if len(first_paragraph) > 300:
                sentences = first_paragraph.split('.')
                if sentences:
                    return sentences[0].strip() + "."
            return first_paragraph

        # Если ничего не найдено, возвращаем фрагмент оригинального текста
        return text[:300] + "..." if len(text) > 300 else text

    async def _add_reflection_to_thought_tree(self, result: ReflectionResult) -> Optional[str]:
        """
        Добавляет результат рефлексии в дерево мыслей

        Args:
            result: Результат рефлексии

        Returns:
            ID нового узла дерева мыслей (если успешно)
        """
        if not self.thought_tree or not self.reflection_branch_id:
            logger.warning("Cannot add reflection to thought tree: tree or branch not available")
            return None

        # Создаем заголовок для узла рефлексии
        reflection_header = f"Рефлексия ({result.mode.value})"

        # Добавляем главный узел рефлексии
        reflection_node_id = self.thought_tree.add_thought(
            content=reflection_header,
            parent_id=self.reflection_branch_id,
            node_type="reflection_header"
        )

        # Добавляем резюме как отдельный узел
        summary_node_id = self.thought_tree.add_thought(
            content=f"Резюме: {result.reflection_summary}",
            parent_id=reflection_node_id,
            node_type="reflection_summary"
        )

        # Добавляем узлы с проблемами
        if result.issues_found:
            issues_header_id = self.thought_tree.add_thought(
                content="Выявленные проблемы:",
                parent_id=reflection_node_id,
                node_type="reflection_issues_header"
            )

            for issue in result.issues_found:
                self.thought_tree.add_thought(
                    content=f"[{issue['type']}] {issue['description']}",
                    parent_id=issues_header_id,
                    node_type=f"reflection_issue_{issue['type']}"
                )

        # Добавляем узлы с рекомендациями
        if result.recommendations:
            recommendations_header_id = self.thought_tree.add_thought(
                content="Рекомендации:",
                parent_id=reflection_node_id,
                node_type="reflection_recommendations_header"
            )

            for recommendation in result.recommendations:
                self.thought_tree.add_thought(
                    content=recommendation,
                    parent_id=recommendations_header_id,
                    node_type="reflection_recommendation"
                )

        # Добавляем метаданные о достоверности
        confidence_id = self.thought_tree.add_thought(
            content=f"Оценка достоверности: {result.confidence_score:.2f}",
            parent_id=reflection_node_id,
            node_type="reflection_confidence"
        )

        logger.info(f"Added reflection results to thought tree, main node: {reflection_node_id}")
        return reflection_node_id

    async def analyze_reasoning_strategy(
        self,
        strategy_name: str,
        example_data: Optional[Dict[str, Any]] = None
    ) -> ReflectionResult:
        """
        Анализирует стратегию рассуждения

        Args:
            strategy_name: Название стратегии для анализа
            example_data: Пример данных для анализа

        Returns:
            Результат рефлексивного анализа стратегии
        """
        # Получаем описание стратегии
        strategy_description = self._get_strategy_description(strategy_name)

        # Если у нас есть метакогнитивный анализатор и данные примера,
        # добавляем данные самооценки стратегии
        metacognitive_data = ""
        if hasattr(self, 'metacognitive_analyzer') and example_data:
            try:
                # Получаем стратегию из менеджера стратегий
                strategy = self._get_strategy_by_name(strategy_name)

                if strategy:
                    # Получаем данные самооценки
                    evaluation_metrics = strategy.self_evaluate(example_data)

                    # Форматируем результаты в текст
                    metacognitive_data = "\n\nДанные метакогнитивного анализа:\n"
                    for metric, value in evaluation_metrics.items():
                        metacognitive_data += f"- {metric}: {value}\n"
            except Exception as e:
                logger.warning(f"Failed to get metacognitive data for strategy {strategy_name}: {e}")

        # Составляем контент для анализа
        content = f"Стратегия рассуждения: {strategy_name}\n\n{strategy_description}\n{metacognitive_data}"

        # Выполняем рефлексивный анализ
        result = await self.reflect_on_content(
            content=content,
            mode=ReflectionMode.COMPREHENSIVE,
            metadata={"strategy_name": strategy_name}
        )

        return result

    def _get_strategy_description(self, strategy_name: str) -> str:
        """
        Получает описание стратегии по её имени

        Args:
            strategy_name: Название стратегии

        Returns:
            Текстовое описание стратегии
        """
        # Проверяем, есть ли такая стратегия в ReasoningStrategy
        try:
            strategy = ReasoningStrategy[strategy_name.upper()]
            return f"Стандартная стратегия: {strategy.value}"
        except KeyError:
            pass

        # Проверяем доступные пользовательские стратегии
        strategy = self._get_strategy_by_name(strategy_name)
        if strategy:
            return strategy.description

        return f"Неизвестная стратегия: {strategy_name}"

    def _get_strategy_by_name(self, strategy_name: str) -> Any:
        """
        Получает объект стратегии по имени

        Args:
            strategy_name: Название стратегии

        Returns:
            Объект стратегии или None
        """
        # Проверяем, есть ли у нас доступ к стратегиям
        if not hasattr(self, 'strategy_manager'):
            return None

        # Ищем стратегию по имени
        return self.strategy_manager.get_strategy(strategy_name)

    async def compare_strategies(
        self,
        strategy_names: List[str],
        example_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Сравнивает несколько стратегий рассуждения

        Args:
            strategy_names: Список названий стратегий для сравнения
            example_data: Пример данных для анализа

        Returns:
            Результат сравнения стратегий
        """
        # Анализируем каждую стратегию
        strategy_analyses = {}
        for strategy_name in strategy_names:
            result = await self.analyze_reasoning_strategy(
                strategy_name=strategy_name,
                example_data=example_data
            )
            strategy_analyses[strategy_name] = result

        # Создаем содержимое для сравнительного анализа
        comparison_content = "Сравнительный анализ стратегий рассуждения:\n\n"

        for strategy_name, result in strategy_analyses.items():
            comparison_content += f"## Стратегия: {strategy_name}\n"
            comparison_content += f"Резюме: {result.reflection_summary}\n"
            comparison_content += f"Оценка достоверности: {result.confidence_score:.2f}\n"

            comparison_content += "Выявленные проблемы:\n"
            for issue in result.issues_found:
                comparison_content += f"- [{issue['type']}] {issue['description']}\n"

            comparison_content += "Рекомендации:\n"
            for recommendation in result.recommendations:
                comparison_content += f"- {recommendation}\n"

            comparison_content += "\n"

        # Выполняем сравнительный анализ
        comparison_result = await self.reflect_on_content(
            content=comparison_content,
            mode=ReflectionMode.ALTERNATIVE,
            metadata={"strategy_names": strategy_names}
        )

        # Формируем результат
        return {
            "individual_analyses": {name: result.to_dict() for name, result in strategy_analyses.items()},
            "comparison_analysis": comparison_result.to_dict()
        }

    async def generate_improvement_suggestions(
        self,
        strategy_name: str,
        reflection_result: ReflectionResult
    ) -> List[Dict[str, Any]]:
        """
        Генерирует предложения по улучшению стратегии на основе рефлексии

        Args:
            strategy_name: Название стратегии
            reflection_result: Результат рефлексивного анализа

        Returns:
            Список предложений по улучшению
        """
        suggestions = []

        # Составляем запрос для генерации улучшений
        improvement_prompt = (
            f"На основе рефлексивного анализа стратегии рассуждения '{strategy_name}', "
            f"сгенерируйте конкретные предложения по улучшению стратегии. "
            f"Учтите следующие результаты анализа:\n\n"
            f"Резюме анализа: {reflection_result.reflection_summary}\n\n"
            f"Выявленные проблемы:\n"
        )

        for issue in reflection_result.issues_found:
            improvement_prompt += f"- [{issue['type']}] {issue['description']}\n"

        improvement_prompt += f"\nРекомендации из анализа:\n"
        for recommendation in reflection_result.recommendations:
            improvement_prompt += f"- {recommendation}\n"

        improvement_prompt += (
            "\nДля каждого предложения укажите:\n"
            "1. Конкретное улучшение\n"
            "2. Ожидаемый эффект\n"
            "3. Способ реализации\n"
            "4. Приоритет (высокий/средний/низкий)"
        )

        # Используем последовательное мышление для генерации улучшений
        if self.sequential_thinking:
            thought_chain = await self.sequential_thinking.run_thinking_chain(
                initial_thought=improvement_prompt,
                max_steps=5
            )

            if thought_chain:
                final_thought = thought_chain[-1].get("thought", "")

                # Извлекаем предложения из текста
                sections = self._split_text_into_sections(final_thought)

                for section_header, section_content in sections:
                    # Пропускаем вводные разделы
                    if "введение" in section_header.lower() or "предложения" in section_header.lower():
                        continue

                    # Проверяем, что раздел содержит предложение по улучшению
                    if "улучшение" in section_header.lower() or "предложение" in section_header.lower():
                        suggestion = {
                            "title": section_header.strip(),
                            "description": "",
                            "expected_effect": "",
                            "implementation": "",
                            "priority": "medium"  # По умолчанию
                        }

                        # Разбираем содержимое раздела
                        lines = section_content.split('\n')
                        current_field = "description"

                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            # Определяем, к какому полю относится строка
                            if "эффект" in line.lower():
                                current_field = "expected_effect"
                                continue
                            elif "реализац" in line.lower() or "внедрен" in line.lower():
                                current_field = "implementation"
                                continue
                            elif "приоритет" in line.lower():
                                # Извлекаем приоритет
                                if "высок" in line.lower():
                                    suggestion["priority"] = "high"
                                elif "низк" in line.lower():
                                    suggestion["priority"] = "low"
                                elif "средн" in line.lower():
                                    suggestion["priority"] = "medium"
                                continue

                            # Добавляем строку к текущему полю
                            if current_field in suggestion and line:
                                if suggestion[current_field]:
                                    suggestion[current_field] += " " + line
                                else:
                                    suggestion[current_field] = line

                        suggestions.append(suggestion)

        return suggestions

    async def save_reflection_history(self, filename: Optional[str] = None) -> str:
        """
        Сохраняет историю рефлексий в файл

        Args:
            filename: Имя файла для сохранения (опционально)

        Returns:
            Путь к файлу с сохраненной историей
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reflection_history_{timestamp}.json"

        # Преобразуем историю в список словарей
        history_data = [result.to_dict() for result in self.reflection_history]

        # Создаем структуру данных для сохранения
        save_data = {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "reflection_count": len(history_data),
            "history": history_data
        }

        # Сохраняем данные в файл
        import os
        file_path = os.path.join("logs", filename)

        try:
            os.makedirs("logs", exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Reflection history saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save reflection history: {e}")
            return ""

    @classmethod
    async def load_reflection_history(cls, filename: str) -> 'ReflectionAgent':
        """
        Загружает историю рефлексий из файла

        Args:
            filename: Путь к файлу с историей

        Returns:
            Экземпляр ReflectionAgent с загруженной историей
        """
        # Создаем новый экземпляр агента
        agent = cls()
        await agent.initialize()

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Загружаем историю
            history_data = data.get("history", [])
            for item in history_data:
                result = ReflectionResult.from_dict(item)
                agent.reflection_history.append(result)

            logger.info(f"Loaded {len(history_data)} reflection records from {filename}")
        except Exception as e:
            logger.error(f"Failed to load reflection history: {e}")

        return agent
