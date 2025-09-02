#!/usr/bin/env python3
"""
Интеграция системы Response Refinement для GopiAI

Добавляет возможность итеративной обработки ответов через
паттерн researcher → analyst → editor
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Добавляем путь к crews
sys.path.append(str(Path(__file__).parent / "crews"))

try:
    from crews.refinement_crew.refinement_crew import iterative_refinement
    REFINEMENT_AVAILABLE = True
    print("[REFINEMENT] Система рефинемента успешно загружена")
except ImportError as e:
    REFINEMENT_AVAILABLE = False
    print(f"[REFINEMENT-ERROR] Не удалось загрузить систему рефинемента: {e}")
    
    def iterative_refinement(query: str, context: str = "", max_rounds: int = 3):
        """Fallback функция когда рефинемент недоступен"""
        return f"Рефинемент недоступен. Исходный запрос: {query}", []

logger = logging.getLogger(__name__)


class ResponseRefinementService:
    """Сервис для управления итеративным рефинементом ответов"""
    
    def __init__(self):
        self.enabled = REFINEMENT_AVAILABLE
        self.default_max_rounds = 2  # Уменьшили для скорости
        
    def should_use_refinement(self, message: str, metadata: Dict[str, Any]) -> bool:
        """
        Определяет, нужно ли использовать рефинемент для данного запроса
        
        Критерии для использования рефинемента:
        1. Пользователь явно запросил детальный анализ
        2. Запрос касается исследовательских/аналитических тем  
        3. Включен флаг use_refinement в metadata
        """
        if not self.enabled:
            return False
            
        # Явный флаг в метаданных
        if metadata.get("use_refinement", False):
            return True
            
        # Автоматическое определение по ключевым словам
        analysis_keywords = [
            "анализ", "исследование", "изучи", "разбери", "объясни подробно",
            "что содержится", "опиши содержимое", "расскажи о", "проанализируй"
        ]
        
        message_lower = message.lower()
        for keyword in analysis_keywords:
            if keyword in message_lower:
                return True
                
        return False
    
    def refine_response(
        self, 
        query: str, 
        context: str = "", 
        max_rounds: Optional[int] = None
    ) -> tuple[str, list[str]]:
        """
        Запускает процесс рефинемента ответа
        
        Returns:
            tuple[refined_answer, refinement_history]
        """
        if not self.enabled:
            return f"Рефинемент недоступен. Запрос: {query}", []
            
        rounds = max_rounds or self.default_max_rounds
        
        try:
            logger.info(f"Запуск рефинемента для запроса: {query[:100]}...")
            
            refined_answer, history = iterative_refinement(
                query=query,
                context=context,
                max_rounds=rounds,
                timeout_per_iteration=45  # 45 секунд на итерацию
            )
            
            logger.info(f"Рефинемент завершен. Итераций: {len(history)}")
            return refined_answer, history
            
        except Exception as e:
            logger.error(f"Ошибка в процессе рефинемента: {e}", exc_info=True)
            return f"Ошибка рефинемента: {str(e)}", []
    
    def extract_context_from_metadata(self, metadata: Dict[str, Any]) -> str:
        """Извлекает контекст из метаданных запроса"""
        contexts = []
        
        # Файловый контекст
        if "selected_file" in metadata:
            contexts.append(f"Выбранный файл: {metadata['selected_file']}")
            
        # История чата
        if "chat_history" in metadata and metadata["chat_history"]:
            contexts.append(f"Предыдущий контекст из {len(metadata['chat_history'])} сообщений")
            
        # Дополнительные инструкции
        if "instructions" in metadata:
            contexts.append(f"Инструкции: {metadata['instructions']}")
            
        return "; ".join(contexts) if contexts else "Без дополнительного контекста"


# Глобальный экземпляр сервиса
refinement_service = ResponseRefinementService()


def process_with_refinement(message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обрабатывает запрос с возможным использованием рефинемента
    
    Возвращает структуру:
    {
        "response": "финальный ответ",  
        "used_refinement": bool,
        "refinement_iterations": int,
        "refinement_history": [список итераций] (если включен)
    }
    """
    
    # Проверяем, нужен ли рефинемент
    use_refinement = refinement_service.should_use_refinement(message, metadata)
    
    if not use_refinement:
        # Стандартная обработка без рефинемента
        return {
            "response": f"[Стандартный ответ] {message}",
            "used_refinement": False,
            "refinement_iterations": 0,
            "refinement_history": []
        }
    
    # Извлекаем контекст и настройки
    context = refinement_service.extract_context_from_metadata(metadata)
    max_rounds = metadata.get("refinement_max_rounds", 3)
    
    # Запускаем рефинемент  
    refined_answer, history = refinement_service.refine_response(
        query=message,
        context=context, 
        max_rounds=max_rounds
    )
    
    return {
        "response": refined_answer,
        "used_refinement": True,
        "refinement_iterations": len(history),
        "refinement_history": history if metadata.get("include_history", False) else []
    }


if __name__ == "__main__":
    # Тест интеграции
    test_metadata = {
        "use_refinement": True,
        "selected_file": "/home/user/test.txt",
        "include_history": True
    }
    
    result = process_with_refinement(
        message="Проанализируй содержимое файла и опиши основные моменты",
        metadata=test_metadata
    )
    
    print("Результат тестирования рефинемента:")
    print(f"Использован рефинемент: {result['used_refinement']}")
    print(f"Итераций: {result['refinement_iterations']}")
    print(f"Ответ: {result['response'][:200]}...")