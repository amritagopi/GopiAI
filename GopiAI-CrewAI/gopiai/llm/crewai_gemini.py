"""
CrewAI-совместимый LLM провайдер с поддержкой code_execution
"""
import logging
from typing import Any, List, Optional, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import PrivateAttr

import google.generativeai as genai

logger = logging.getLogger(__name__)

class CrewAIGeminiLLM(BaseChatModel):
    """
    CrewAI-совместимый Gemini LLM с поддержкой code_execution
    """
    
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    enable_code_execution: bool = True
    _gemini_provider: Any = PrivateAttr()
    
    def __init__(
        self, 
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        enable_code_execution: bool = True,
        **kwargs
    ):
        # ВАЖНО: Указываем правильное имя модели для избежания путаницы с Vertex AI
        corrected_model = f"google/{model}" if not model.startswith("google/") else model
        
        super().__init__(model=corrected_model, temperature=temperature, **kwargs)
        
        self.enable_code_execution = enable_code_execution
        self._original_model = model  # Сохраняем оригинальное имя для Gemini SDK
        
        # Инициализируем Gemini провайдер с поддержкой code execution
        import os
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Настройки генерации с поддержкой code execution
        generation_config = genai.types.GenerationConfig(
            temperature=self.temperature
        )
        
        # Создаем модель с поддержкой code execution
        tools = [genai.protos.Tool(code_execution={})] if self.enable_code_execution else None
        
        self._gemini_model = genai.GenerativeModel(
            model_name=self._original_model,
            generation_config=generation_config,
            tools=tools
        )
        
        logger.info(f"🚀 CrewAI Gemini LLM инициализирован (model: {corrected_model}, code_execution: {self.enable_code_execution})")
    
    @property
    def _llm_type(self) -> str:
        return "crewai_gemini"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Генерация ответа для CrewAI"""
        try:
            # Конвертируем сообщения в единый текст
            prompt_parts = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    prompt_parts.append(f"Human: {message.content}")
                elif isinstance(message, AIMessage):
                    prompt_parts.append(f"Assistant: {message.content}")
                else:
                    prompt_parts.append(f"{message.content}")
            
            prompt = "\n".join(prompt_parts)
            
            # Генерируем ответ через Gemini модель
            response = self._gemini_model.generate_content(prompt)
            response_text = response.text
            
            # Создаем результат
            message = AIMessage(content=response_text)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации в CrewAI Gemini LLM: {e}")
            # Возвращаем ошибку как сообщение
            error_message = AIMessage(
                content=f"Извините, произошла ошибка при обработке запроса: {e}"
            )
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Асинхронная генерация (пока делегируем в синхронную)"""
        return self._generate(messages, stop, run_manager, **kwargs)
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGeneration]:
        """Streaming не поддерживается пока"""
        result = self._generate(messages, stop, run_manager, **kwargs)
        yield result.generations[0]

def create_crewai_gemini_llm(
    model: str = "gemini-2.5-flash", 
    enable_code_execution: bool = True,
    temperature: float = 0.7
) -> CrewAIGeminiLLM:
    """Фабричная функция для создания CrewAI Gemini LLM"""
    return CrewAIGeminiLLM(
        model=model,
        temperature=temperature,
        enable_code_execution=enable_code_execution
    )