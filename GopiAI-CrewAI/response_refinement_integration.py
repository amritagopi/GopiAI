# -*- coding: utf-8 -*-
"""
Response Refinement Integration for GopiAI CrewAI
Система итеративной обработки ответов с использованием паттерна "агенты → черновик → редактор → финал"

Based on the response refinement patterns documented in "Response обработка"
"""

from crewai import Agent, Task, Crew, Process
import logging

logger = logging.getLogger(__name__)


class RefinementCrew:
    """
    Crew для итеративной обработки ответов
    Паттерн: Researcher → Analyst → Editor → Final Answer
    """
    
    def researcher(self) -> Agent:
        return Agent(
            role="Researcher",
            goal="Собрать факты, ссылки и короткие цитаты по теме {topic}",
            backstory="Систематический исследователь. Отдавай ответы списком с источниками.",
            reasoning=True,
            max_iter=3,
            verbose=True
        )

    def analyst(self) -> Agent:
        return Agent(
            role="Analyst", 
            goal="Структурировать вывод Researcher: 5 ключевых тезисов, пробелы в данных",
            backstory="Критичный аналитик, формирует список вопросов для уточнения.",
            reasoning=True,
            max_iter=2,
            verbose=True
        )

    def editor(self) -> Agent:
        return Agent(
            role="Editor",
            goal=(
                "Получив research_output, analysis_output и previous_draft, "
                "собери единый читабельный ответ. Если считаешь ответ финальным — "
                "в конце отдельной строкой напиши: DONE"
            ),
            backstory="Опытный редактор: убирает повторы, исправляет стиль и факты.",
            reasoning=True,
            max_iter=5,
            verbose=True
        )

    def research_task(self):
        return Task(
            description="Researcher: собери факты/ссылки по теме: {topic}",
            agent=self.researcher(),
            expected_output="Структурированный список фактов с источниками"
        )

    def analysis_task(self):
        return Task(
            description="Analyst: на основе research_task.output сформируй тезисы и пробелы",
            agent=self.analyst(),
            expected_output="5 ключевых тезисов и выявленные пробелы в данных"
        )

    def edit_task(self):
        return Task(
            description=(
                "Editor: входы: research_task.raw, analysis_task.raw, previous_draft.\n"
                "Задача: собрать всё в аккуратный финал. Если финал — допиши в конце 'DONE'."
            ),
            agent=self.editor(),
            expected_output="Финальный отполированный ответ"
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.researcher(), self.analyst(), self.editor()],
            tasks=[self.research_task(), self.analysis_task(), self.edit_task()],
            process=Process.sequential,
            planning=True,  # позволяет AgentPlanner править план между итерациями
            verbose=True
        )


def iterative_refinement(topic, max_rounds=4, llm=None):
    """
    Основная функция итеративной обработки ответов
    
    Args:
        topic: Тема для исследования и обработки
        max_rounds: Максимальное количество итераций
        llm: LLM для использования в агентах
        
    Returns:
        Финальный обработанный ответ
    """
    logger.info(f"🔄 Запуск итеративной обработки для темы: {topic}")
    
    try:
        crew_instance = RefinementCrew()
        crew_obj = crew_instance.crew()
        
        # Если передан LLM, применяем его к агентам
        if llm:
            for agent in crew_obj.agents:
                agent.llm = llm
        
        previous = ""
        
        for i in range(max_rounds):
            logger.info(f"🔄 Итерация {i+1}/{max_rounds}")
            
            result = crew_obj.kickoff(inputs={
                "topic": topic, 
                "previous_draft": previous
            })
            
            out = result.raw if hasattr(result, 'raw') else str(result)
            
            logger.info(f"[Итерация {i+1}] Получен результат длиной {len(out)} символов")
            
            # Проверяем условие завершения
            if "DONE" in out:
                logger.info("✅ Получен финальный результат")
                return out.replace("DONE", "").strip()
            
            previous = out
            
        logger.info("⏰ Достигнуто максимальное количество итераций")
        return previous
        
    except Exception as e:
        logger.error(f"❌ Ошибка в итеративной обработке: {e}")
        raise


def simple_iterative_reasoning(prompt, llm, max_rounds=5):
    """
    Упрощенная версия итеративного рассуждения для одного агента
    
    Args:
        prompt: Исходный промпт
        llm: LLM для обработки
        max_rounds: Максимальное количество итераций
        
    Returns:
        Tuple (финальный_ответ, история_итераций)
    """
    logger.info(f"🤔 Запуск простого итеративного рассуждения")
    
    draft = prompt
    history = []
    
    try:
        for i in range(max_rounds):
            system_msg = (
                f"Это итерация {i+1}. Проанализируй текст и улучши его. "
                f"Если всё готово, закончи словом DONE."
            )
            
            # Используем LLM для обработки
            if hasattr(llm, 'invoke'):
                # Для LangChain-совместимых LLM
                response = llm.invoke([
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": draft}
                ])
                text = response.content if hasattr(response, 'content') else str(response)
            else:
                # Для других LLM
                text = str(llm.generate([draft]))
            
            history.append(text)
            logger.info(f"[Итерация {i+1}] Обработано {len(text)} символов")
            
            if "DONE" in text:
                logger.info("✅ Простое рассуждение завершено")
                return text.replace("DONE", "").strip(), history
            else:
                draft = text  # Улучшенный текст идёт на следующий круг
        
        logger.info("⏰ Достигнуто максимальное количество итераций в простом рассуждении")
        return history[-1], history
        
    except Exception as e:
        logger.error(f"❌ Ошибка в простом итеративном рассуждении: {e}")
        raise


class ResponseRefinementService:
    """
    Сервис для управления различными типами рефайнмента ответов
    """
    
    def __init__(self, llm=None):
        self.llm = llm
        logger.info("🔧 Инициализирован ResponseRefinementService")
    
    def refine_with_crew(self, topic, max_rounds=4):
        """Рефайнмент с использованием полного crew"""
        return iterative_refinement(topic, max_rounds, self.llm)
    
    def refine_simple(self, prompt, max_rounds=5):
        """Простой рефайнмент с одним агентом"""
        if not self.llm:
            raise ValueError("LLM не установлен для простого рефайнмента")
        return simple_iterative_reasoning(prompt, self.llm, max_rounds)
    
    def auto_refine(self, content, refinement_type="auto"):
        """
        Автоматический выбор типа рефайнмента на основе контента
        
        Args:
            content: Контент для обработки
            refinement_type: "crew", "simple", или "auto"
        """
        logger.info(f"🎯 Автоматический рефайнмент типа: {refinement_type}")
        
        if refinement_type == "auto":
            # Автоматически выбираем тип на основе длины и сложности
            if len(content) > 500 or "исследование" in content.lower():
                refinement_type = "crew"
            else:
                refinement_type = "simple"
        
        if refinement_type == "crew":
            return self.refine_with_crew(content)
        elif refinement_type == "simple":
            result, _ = self.refine_simple(content)
            return result
        else:
            raise ValueError(f"Неизвестный тип рефайнмента: {refinement_type}")


# Utility functions for integration

def create_refinement_service(llm=None):
    """Фабричная функция для создания сервиса рефайнмента"""
    return ResponseRefinementService(llm)

def quick_refine(content, llm=None, method="auto"):
    """Быстрая функция для рефайнмента контента"""
    service = create_refinement_service(llm)
    return service.auto_refine(content, method)


if __name__ == "__main__":
    # Пример использования
    logging.basicConfig(level=logging.INFO)
    
    # Тестирование системы
    test_topic = "Искусственный интеллект в образовании"
    
    try:
        result = iterative_refinement(test_topic, max_rounds=2)
        print("🎉 Результат итеративной обработки:")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")