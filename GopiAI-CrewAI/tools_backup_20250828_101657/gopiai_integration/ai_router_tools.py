"""
🔄 GopiAI AI Router Tool для CrewAI
Инструмент для агентов CrewAI для взаимодействия с системой AI Router GopiAI
"""

import os
import logging
from typing import Type, Any, Dict, Optional
from pydantic import BaseModel, Field
# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool
from .ai_router_llm import AIRouterLLM

# Настройка логгера
logger = logging.getLogger(__name__)

class AIRouterInput(BaseModel):
    """Схема входных данных для AI Router"""
    message: str = Field(description="Сообщение для AI Router")
    task_type: str = Field(default="chat", description="Тип задачи: chat, code, creative, analysis")
    model_preference: str = Field(default="auto", description="Предпочтительная модель: auto, groq, gemini, cerebras")
    max_tokens: int = Field(default=1000, description="Максимальное количество токенов")
    temperature: float = Field(default=0.7, description="Температура генерации")

class GopiAIRouterTool(BaseTool):
    """
    Инструмент для использования AI Router системы GopiAI
    
    Возможности:
    - Автоматическая ротация между провайдерами
    - Интеллектуальный выбор модели по задаче
    - Обход лимитов через переключение
    - Мониторинг использования
    """
    
    name: str = Field(default="gopiai_router", description="Имя инструмента")
    description: str = Field(default="Инструмент маршрутизации AI", description="Описание инструмента")
    args_schema: Type[BaseModel] = AIRouterInput
    
    def __init__(self, **data):
        super().__init__(**data)
        # Инициализируем экземпляр AI Router LLM для использования внутри инструмента
        self.ai_router_llm = AIRouterLLM()
    
    def _validate_parameters(self, temperature: float, max_tokens: int, task_type: str, model_preference: str):
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temperature}")
        if not 1 <= max_tokens <= 8192:
            raise ValueError(f"Max tokens must be between 1 and 8192, got {max_tokens}")
        # Add more validations...
    
    def _run(self, message: str, task_type: str = "chat", model_preference: str = "auto", 
            max_tokens: int = 1000, temperature: float = 0.7) -> str:
        logger.info(f"AI Router request: task_type={task_type}, model={model_preference}")
        try:
            # Validate parameters before processing
            self._validate_parameters(temperature, max_tokens, task_type, model_preference)
            
            # Check if AI Router LLM is initialized
            if not self.ai_router_llm:
                self.ai_router_llm = AIRouterLLM()
            
            # Используем наш Python-based AI Router
            response = self.ai_router_llm.generate(
                prompts=[message],  # Convert string to list of strings
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.info("AI Router request completed successfully")
            return f"🤖 AI Router: {response}"
            
        except Exception as e:
            logger.error(f"AI Router request failed: {str(e)}", exc_info=True)
            return f"❌ Ошибка вызова AI Router: {str(e)}"

    def __del__(self):
        """Cleanup resources when tool is destroyed"""
        if hasattr(self, 'ai_router_llm') and self.ai_router_llm:
            self.cleanup()

    def cleanup(self):
        """Explicitly close and cleanup resources"""
        if hasattr(self, 'ai_router_llm') and self.ai_router_llm:
            del self.ai_router_llm
            self.ai_router_llm = None

class GopiAIModelSelectorTool:
    """Умный выбор модели для задачи"""
    
    name: str = "gopiai_model_selector" 
    description: str = "Рекомендует лучшую модель для конкретной задачи"
    
    def _run(self, task_description: str, constraints: str = "") -> str:
        """
        Анализирует задачу и рекомендует модель
        """
        task_lower = task_description.lower()
        
        recommendations = []
        
        # Анализ типа задачи
        if any(word in task_lower for word in ["код", "программ", "debug", "python", "javascript"]):
            recommendations.append("🖥️ Тип: Программирование")
            recommendations.append("💡 Рекомендация: Cerebras Llama-3.1-70B (лучше для кода)")
            task_type = "code"
        elif any(word in task_lower for word in ["анализ", "исследован", "данные", "статистика"]):
            recommendations.append("📊 Тип: Анализ данных")
            recommendations.append("💡 Рекомендация: Google Gemini-2.0-Flash (хорош для анализа)")
            task_type = "analysis"
        elif any(word in task_lower for word in ["творч", "создай", "придумай", "напиши"]):
            recommendations.append("🎨 Тип: Творческая задача")
            recommendations.append("💡 Рекомендация: Google Gemini-2.0-Flash (творческий потенциал)")
            task_type = "creative"
        else:
            recommendations.append("💬 Тип: Общение/диалог")
            recommendations.append("💡 Рекомендация: Groq Llama-3.3-70B (быстрый ответ)")
            task_type = "chat"
        
        # Анализ ограничений
        if "быстро" in constraints.lower():
            recommendations.append("⚡ Ограничение: скорость → Groq (самый быстрый)")
        if "длинн" in constraints.lower() or "подробн" in constraints.lower():
            recommendations.append("📝 Ограничение: детальность → Gemini (большой контекст)")
        
        # Статус провайдеров (эмуляция)
        status = [
            "📊 Статус провайдеров:",
            "✅ Groq: доступен (лимит: 30 RPM)",
            "✅ Gemini: доступен (бесплатно)",
            "⚠️ Cerebras: ограничен",
            "✅ Cohere: доступен",
            "🤗 HuggingFace: доступен (1000 req/month)"
        ]
        
        result = "\\n".join(recommendations + [""] + status)
        return f"🎯 Анализ задачи:\\n{result}\\n\\n🚀 Используйте task_type='{task_type}'"


# Экспорт инструментов
__all__ = [
    "GopiAIRouterTool",
    "GopiAIModelSelectorTool"
]


if __name__ == "__main__":
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Тест инструментов
    print("🧪 Тестирование GopiAI AI Router Tools...")
    
    # Тест AI Router
    router = GopiAIRouterTool()
    result = router._run("Привет! Как дела?", "chat", "auto")
    print(f"AI Router test: {result}")
    
    # Тест селектора моделей
    selector = GopiAIModelSelectorTool()
    result = selector._run("Напиши код для сортировки массива", "быстро")
    print(f"Model selector test: {result}")
    
    print("✅ Все инструменты готовы!")