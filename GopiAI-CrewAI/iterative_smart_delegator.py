#!/usr/bin/env python3
"""
Расширение SmartDelegator с итеративными возможностями

Добавляет поддержку итеративного выполнения команд и response refinement
к существующему SmartDelegator.
"""

import logging
import time
import json
import re
import sys
import os
from typing import Dict, List, Any, Optional

# Импортируем нашу итеративную систему
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from iterative_execution_system import IterativeExecutor

# Импортируем оригинальный SmartDelegator
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'gopiai_integration'))
from tools.gopiai_integration.smart_delegator import SmartDelegator

logger = logging.getLogger(__name__)


class IterativeSmartDelegator(SmartDelegator):
    """Расширенная версия SmartDelegator с итеративными возможностями"""
    
    def __init__(self, rag_system=None, pending_commands_store=None, pending_commands_lock=None, **kwargs):
        super().__init__(rag_system, **kwargs)
        self.iterative_executor = IterativeExecutor(pending_commands_store)
        self.iterative_executor.pending_commands_lock = pending_commands_lock
        self.enable_iteration = True
        self.max_refinement_iterations = 3
        self._recursion_depth = 0
        self._max_recursion_depth = 2  # Увеличиваем лимит для итеративной обработки
        self._override_prompt_for_iteration = True  # Включаем специальные промпты для итераций
        
    def process_request_with_iteration(self, message: str, metadata: Dict) -> Dict:
        """
        Итеративная обработка запроса с выполнением команд
        """
        start_time = time.time()
        iteration_history = []
        
        try:
            # Если итерации отключены, используем стандартную обработку
            if not self.enable_iteration:
                return self.process_request(message, metadata)
            
            logger.info(f"[ITERATIVE] Начинаем итеративную обработку: {message[:100]}...")
            
            current_prompt = message
            conversation_context = []
            executed_commands = []
            
            for iteration in range(self.max_refinement_iterations):
                logger.info(f"[ITERATIVE] Итерация {iteration + 1}/{self.max_refinement_iterations}")
                
                # 1. Получаем ответ от модели через родительский process_request (БЕЗ РЕКУРСИИ!)
                iteration_start = time.time()
                
                # Временно переопределяем системный промпт для итеративного выполнения
                original_get_assistant_prompt = None
                if hasattr(self, '_override_prompt_for_iteration'):
                    # Сохраняем оригинальный метод и подменяем его
                    from tools.gopiai_integration.system_prompts import get_system_prompts
                    prompts_manager = get_system_prompts()
                    original_get_assistant_prompt = prompts_manager.get_assistant_prompt_with_context
                    
                    def iterative_prompt_override(rag_context):
                        return self._get_system_prompt_for_iterative(rag_context)
                    
                    prompts_manager.get_assistant_prompt_with_context = iterative_prompt_override
                
                response_data = super().process_request(current_prompt, metadata)
                
                # Восстанавливаем оригинальный метод
                if original_get_assistant_prompt:
                    prompts_manager.get_assistant_prompt_with_context = original_get_assistant_prompt
                
                if not response_data.get('success', True):
                    logger.error(f"[ITERATIVE] Ошибка на итерации {iteration + 1}: {response_data}")
                    break
                
                response_text = response_data.get('response', '')
                iteration_history.append({
                    'iteration': iteration + 1,
                    'input': current_prompt,
                    'response': response_text,
                    'timestamp': time.time(),
                    'duration': time.time() - iteration_start
                })
                
                logger.info(f"[ITERATIVE] Получен ответ: {response_text[:200]}...")
                
                # 2. Ищем tool_code блоки в ответе
                tool_codes = self.iterative_executor.extract_tool_codes(response_text)
                
                if not tool_codes:
                    logger.info(f"[ITERATIVE] Команды не найдены, проверяем завершенность")
                    
                    # Проверяем, нужно ли продолжать итерацию
                    if not self.iterative_executor.should_continue_iteration(response_text, iteration):
                        logger.info(f"[ITERATIVE] Задача завершена на итерации {iteration + 1}")
                        break
                    else:
                        # Просим модель продолжить
                        current_prompt = f"""
Исходный запрос пользователя: {message}

Предыдущий ответ: {response_text}

Пожалуйста, продолжи выполнение задачи. Если нужно выполнить какие-то команды или действия, используй блоки tool_code. Если задача уже выполнена полностью, дай окончательный ответ.
"""
                        continue
                
                # 3. Выполняем найденные команды
                logger.info(f"[ITERATIVE] Найдено {len(tool_codes)} команд для выполнения")
                execution_results = []
                
                for tool_data in tool_codes:
                    result = self.iterative_executor.execute_tool(tool_data)
                    execution_results.append(result)
                    executed_commands.append(result)
                    
                    logger.info(f"[ITERATIVE] Выполнена команда: {result.get('command', 'unknown')} -> {'✅' if result['success'] else '❌'}")
                
                # 4. Формируем контекст для следующей итерации
                if execution_results:
                    results_summary = self.iterative_executor.format_execution_results(execution_results)
                    conversation_context.append(results_summary)
                    
                    current_prompt = f"""
Исходный запрос пользователя: {message}

Контекст предыдущих итераций:
{chr(10).join(conversation_context[-3:])}  # Берем последние 3 для экономии токенов

Результаты выполнения команд:
{results_summary}

На основе этих результатов продолжи выполнение задачи пользователя. Если задача выполнена полностью, дай итоговый ответ без дополнительных команд.
"""
                else:
                    # Команды были найдены, но не выполнены (ошибки безопасности)
                    current_prompt = f"""
Исходный запрос пользователя: {message}

Предыдущий ответ: {response_text}

Некоторые команды не были выполнены по соображениям безопасности. Пожалуйста, предложи альтернативный способ выполнения задачи или дай ответ на основе доступной информации.
"""
            
            # 5. Формируем финальный результат
            final_response = iteration_history[-1]['response'] if iteration_history else "Ошибка: не получен ответ"
            
            # Если выполнялись команды, добавляем краткую сводку
            if executed_commands:
                successful_commands = sum(1 for cmd in executed_commands if cmd['success'])
                command_summary = f"\n\n---\n*Выполнено команд: {successful_commands}/{len(executed_commands)}*"
                final_response += command_summary
            
            total_time = time.time() - start_time
            
            return {
                'success': True,
                'response': final_response,
                'iterative_processing': True,
                'iterations_count': len(iteration_history),
                'commands_executed': len(executed_commands),
                'commands_successful': sum(1 for cmd in executed_commands if cmd['success']),
                'processing_time': total_time,
                'iteration_history': iteration_history if metadata.get('include_iteration_history') else [],
                'execution_history': executed_commands if metadata.get('include_execution_history') else []
            }
            
        except Exception as e:
            logger.error(f"[ITERATIVE] Ошибка в итеративной обработке: {e}", exc_info=True)
            
            # Fallback к стандартной обработке
            logger.info("[ITERATIVE] Fallback к стандартной обработке")
            return self.process_request(message, metadata)
    
    def should_use_iterative_processing(self, message: str, metadata: Dict) -> bool:
        """Определяет, нужно ли использовать итеративную обработку"""
        
        # Явное указание в метаданных
        if metadata.get('force_iterative', False):
            return True
            
        if metadata.get('disable_iterative', False):
            return False
        
        # Автоматическое определение по ключевым словам
        iterative_keywords = [
            'посмотреть', 'содержимое', 'папка', 'каталог', 'файл',
            'выполни', 'команда', 'проверь', 'найди', 'покажи',
            'ls', 'cat', 'grep', 'cd', 'pwd'
        ]
        
        message_lower = message.lower()
        for keyword in iterative_keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def process_request(self, message: str, metadata: Dict) -> Dict:
        """
        Переопределенный метод process_request с поддержкой итераций
        """
        # Защита от рекурсии
        self._recursion_depth += 1
        try:
            if self._recursion_depth > self._max_recursion_depth:
                logger.warning(f"[ITERATIVE] Превышена максимальная глубина рекурсии ({self._max_recursion_depth}), используется fallback")
                return super().process_request(message, metadata)
            
            # Определяем, нужна ли итеративная обработка
            if self.should_use_iterative_processing(message, metadata):
                logger.info("[ITERATIVE] Включена итеративная обработка")
                return self.process_request_with_iteration(message, metadata)
            else:
                logger.info("[ITERATIVE] Используется стандартная обработка")
                return super().process_request(message, metadata)
        finally:
            self._recursion_depth -= 1
    
    def _get_system_prompt_for_iterative(self, rag_context):
        """Получает специальный системный промпт для итеративного выполнения команд"""
        from tools.gopiai_integration.system_prompts import get_system_prompts
        
        prompts_manager = get_system_prompts()
        system_prompt = prompts_manager.get_iterative_execution_prompt_with_context(rag_context)
        
        # Добавляем дополнительные инструкции для tool_code
        enhanced_prompt = system_prompt + """

## ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ ДЛЯ КОМАНД ТЕРМИНАЛА

КРИТИЧЕСКИ ВАЖНО: Когда пользователь просит выполнить команду, ВСЕГДА используй формат:

```tool_code
bash: команда
```

НЕ используй обычные инструменты CrewAI для команд терминала! 
ТОЛЬКО блоки tool_code с префиксом "bash:"!

Система автоматически перехватит эти блоки и выполнит команды безопасно.
После выполнения ты получишь результат для анализа.
"""
        
        return enhanced_prompt


# Создаем глобальный экземпляр для использования в сервере
def create_iterative_smart_delegator(rag_system=None):
    """Factory функция для создания итеративного делегатора"""
    return IterativeSmartDelegator(rag_system=rag_system)


if __name__ == "__main__":
    # Тест итеративной системы
    delegator = IterativeSmartDelegator()
    
    test_message = "Посмотри содержимое папки /home и расскажи что там есть"
    test_metadata = {'force_iterative': True}
    
    print("Тест итеративной системы:")
    result = delegator.process_request_with_iteration(test_message, test_metadata)
    
    print(f"Результат: {result}")