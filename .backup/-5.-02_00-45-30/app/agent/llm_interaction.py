"""
Модуль взаимодействия с LLM для агентов.

Предоставляет функциональность для отправки промптов и обработки ответов от языковых моделей.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from app.llm import get_llm_client
from app.schema import Message

logger = logging.getLogger(__name__)

async def llm_agentic_action(
    messages: List[Message],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stop: Optional[List[str]] = None,
    stream: bool = False,
    callback = None,
) -> Union[str, Tuple[str, bool]]:
    """
    Взаимодействует с LLM в агентном стиле.

    Args:
        messages: История сообщений для контекста
        system_prompt: Системный промпт для модели
        model: Модель для использования
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов в ответе
        stop: Последовательности для остановки генерации
        stream: Поддержка потоковой генерации
        callback: Функция обратного вызова для потоковой генерации

    Returns:
        Ответ от модели
    """
    try:
        # Добавляем системный промпт, если он предоставлен
        if system_prompt:
            system_message = Message.system_message(system_prompt)
            full_messages = [system_message] + messages
        else:
            full_messages = messages

        # Получаем клиент LLM
        llm_client = get_llm_client(model_name=model)

        # Запрашиваем ответ
        if stream and callback:
            response_chunks = []
            async for chunk in llm_client.generate_stream(
                messages=[m.to_dict() for m in full_messages],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop
            ):
                response_chunks.append(chunk)
                if callback:
                    await callback(chunk)

            response = "".join(response_chunks)
        else:
            response = await llm_client.generate(
                messages=[m.to_dict() for m in full_messages],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop
            )

        logger.debug(f"Получен ответ от LLM: {response[:100]}...")
        return response

    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}")
        return f"Произошла ошибка при обращении к языковой модели: {str(e)}"
