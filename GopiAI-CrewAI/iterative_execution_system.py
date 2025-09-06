#!/usr/bin/env python3
"""
Iterative Execution System для GopiAI

Система итеративного выполнения команд и обработки ответов:
1. Анализирует ответ модели
2. Находит tool_code блоки  
3. Выполняет команды реально
4. Отправляет результаты обратно в модель
5. Продолжает итерации до полного выполнения
"""

import os
import re
import ast
import json
import time
import uuid
import logging
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class IterativeExecutor:
    """Система итеративного выполнения команд и refinement"""
    
    def __init__(self, pending_commands_store=None):
        self.max_iterations = 5
        self.pending_commands_store = pending_commands_store if pending_commands_store is not None else {}
        self.pending_commands_lock = None
        self.execution_timeout = 30
        self.safe_commands = {
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'wc', 'pwd', 'date',
            'whoami', 'id', 'ps', 'df', 'du', 'free', 'uptime', 'uname'
        }
        
    def extract_tool_codes(self, response: str) -> List[Dict[str, Any]]:
        """Извлекает все tool_code блоки из ответа модели"""
        tool_codes = []
        
        # Паттерн для поиска tool_code блоков
        pattern = r'```tool_code\s*\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                # Пытаемся парсить как Python dict/expression
                if match.strip().startswith('{'):
                    tool_data = ast.literal_eval(match.strip())
                    tool_codes.append(tool_data)
                else:
                    # Fallback для простых команд
                    tool_codes.append({'tool': 'terminal', 'params': {'command': match.strip()}})
            except Exception as e:
                logger.warning(f"Не удалось распарсить tool_code: {match[:100]}... Error: {e}")
                continue
                
        return tool_codes
    
    def check_command_approval(self, command: str) -> Dict[str, Any]:
        """
        Проверяет нужно ли подтверждение для команды и получает его статус
        Returns: {'needs_approval': bool, 'approved': bool, 'command_id': str, 'reason': str}
        """
        logger.info(f"[APPROVAL] Проверяем команду: {command}")
        
        if not command or not isinstance(command, str):
            logger.info("[APPROVAL] Команда невалидна")
            return {
                'needs_approval': False,
                'approved': False, 
                'command_id': None,
                'reason': 'Invalid command'
            }
            
        # Разбираем команду на части
        parts = command.strip().split()
        if not parts:
            return {
                'needs_approval': False,
                'approved': False,
                'command_id': None, 
                'reason': 'Empty command'
            }
            
        cmd = parts[0].lower()
        
        # Безопасные команды - выполняются без подтверждения
        safe_commands = {
            'ls', 'cat', 'head', 'tail', 'pwd', 'date', 'whoami', 'id', 
            'ps', 'df', 'du', 'free', 'uptime', 'uname', 'which', 'type',
            'echo', 'wc', 'sort', 'uniq'
        }
        
        # Если команда безопасная и не содержит опасных паттернов
        if cmd in safe_commands:
            simple_dangerous_patterns = ['>', '>>', '&&', '||', ';', '$(', '`', '|']
            has_dangerous_pattern = any(pattern in command for pattern in simple_dangerous_patterns)
            
            logger.info(f"[APPROVAL] Команда {cmd} в safe_commands, опасные паттерны: {has_dangerous_pattern}")
            
            if not has_dangerous_pattern:
                logger.info("[APPROVAL] Команда безопасная, подтверждения не требуется")
                return {
                    'needs_approval': False,
                    'approved': True,
                    'command_id': None,
                    'reason': 'Safe command'
                }
        
        # Для остальных команд требуется подтверждение
        logger.info("[APPROVAL] Требуется подтверждение, вызываем request_command_approval")
        return self.request_command_approval(command)
    
    def request_command_approval(self, command: str) -> Dict[str, Any]:
        """Запрашивает подтверждение команды у пользователя"""
        command_id = str(uuid.uuid4())
        
        # Определяем уровень риска команды
        risk_level = self.assess_command_risk(command)
        
        command_info = {
            'id': command_id,
            'command': command,
            'risk_level': risk_level,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'reason': f'Command "{command}" requires approval (risk: {risk_level})'
        }
        
        # Сохраняем в хранилище ожидающих команд
        if self.pending_commands_store is not None:
            if self.pending_commands_lock:
                with self.pending_commands_lock:
                    self.pending_commands_store[command_id] = command_info
                    logger.info(f"[PENDING] Команда добавлена в хранилище с блокировкой: {command_id}")
            else:
                self.pending_commands_store[command_id] = command_info
                logger.info(f"[PENDING] Команда добавлена в хранилище: {command_id}")
        else:
            logger.warning(f"[PENDING] pending_commands_store is None! Команда не сохранена: {command_id}")
        
        logger.info(f"Команда требует подтверждения: {command} (ID: {command_id}, риск: {risk_level})")
        
        return {
            'needs_approval': True,
            'approved': False,
            'command_id': command_id,
            'reason': f'Command requires user approval (risk: {risk_level})'
        }
    
    def assess_command_risk(self, command: str) -> str:
        """Оценивает уровень риска команды"""
        high_risk_patterns = ['rm', 'del', 'format', 'mkfs', 'dd', 'sudo', 'chmod 777', 'chown']
        medium_risk_patterns = ['mv', 'cp', 'mkdir', 'chmod', 'chown', '>', '>>', 'wget', 'curl']
        
        command_lower = command.lower()
        
        for pattern in high_risk_patterns:
            if pattern in command_lower:
                return 'HIGH'
        
        for pattern in medium_risk_patterns:
            if pattern in command_lower:
                return 'MEDIUM'
        
        return 'LOW'
    
    def wait_for_approval(self, command_id: str, timeout: int = 60) -> bool:
        """Ожидает подтверждения команды от пользователя"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.pending_commands_store is None:
                return False
                
            # Проверяем статус команды
            command_info = self.pending_commands_store.get(command_id)
            if not command_info:
                return False
                
            status = command_info.get('status', 'pending')
            
            if status == 'approved':
                logger.info(f"Команда {command_id} одобрена пользователем")
                return True
            elif status == 'rejected':
                logger.info(f"Команда {command_id} отклонена пользователем")
                return False
                
            # Ждём немного перед следующей проверкой
            time.sleep(1)
        
        logger.warning(f"Таймаут ожидания подтверждения команды {command_id}")
        return False
    
    def execute_terminal_command(self, command: str) -> Dict[str, Any]:
        """Выполняет команду в терминале с интерактивным подтверждением"""
        
        logger.info(f"🔍 [APPROVAL] Проверка команды: {command}")
        
        # Проверяем требуется ли подтверждение
        approval_status = self.check_command_approval(command)
        logger.info(f"🔍 [APPROVAL] Статус проверки: {approval_status}")
        
        if not approval_status['approved']:
            if approval_status['needs_approval']:
                command_id = approval_status['command_id']
                logger.info(f"Ожидание подтверждения команды: {command} (ID: {command_id})")
                
                # Ожидаем подтверждения
                if not self.wait_for_approval(command_id, timeout=120):  # 2 минуты
                    return {
                        'success': False,
                        'error': f'Команда не подтверждена пользователем или истекло время ожидания: {command}',
                        'output': '',
                        'command_id': command_id,
                        'status': 'timeout'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Команда не разрешена: {command}. Причина: {approval_status["reason"]}',
                    'output': '',
                    'status': 'denied'
                }
            
        try:
            logger.info(f"Выполнение команды: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
                cwd=os.path.expanduser('~')
            )
            
            return {
                'success': result.returncode == 0,
                'error': result.stderr if result.stderr else None,
                'output': result.stdout,
                'command': command,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Команда превысила таймаут {self.execution_timeout} секунд',
                'output': '',
                'command': command
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка выполнения команды: {str(e)}',
                'output': '',
                'command': command
            }
    
    def execute_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет инструмент на основе tool_data"""
        tool_name = tool_data.get('tool', '').lower()
        params = tool_data.get('params', {})
        
        if tool_name == 'terminal':
            command = params.get('command', '')
            return self.execute_terminal_command(command)
        
        elif tool_name == 'file_read':
            file_path = params.get('path', '')
            return self.read_file(file_path)
            
        elif tool_name == 'system_info':
            return self.get_system_info()
            
        else:
            return {
                'success': False,
                'error': f'Неизвестный инструмент: {tool_name}',
                'output': ''
            }
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Безопасное чтение файла"""
        try:
            path = Path(file_path).resolve()
            
            # Проверяем, что файл существует и доступен для чтения
            if not path.exists():
                return {
                    'success': False,
                    'error': f'Файл не существует: {file_path}',
                    'output': ''
                }
                
            if not path.is_file():
                return {
                    'success': False,
                    'error': f'Путь не является файлом: {file_path}',
                    'output': ''
                }
            
            # Ограничиваем размер файла для безопасности
            if path.stat().st_size > 1024 * 1024:  # 1MB
                return {
                    'success': False,
                    'error': f'Файл слишком большой (>1MB): {file_path}',
                    'output': ''
                }
                
            content = path.read_text(encoding='utf-8', errors='ignore')
            return {
                'success': True,
                'error': None,
                'output': content,
                'file_path': str(path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка чтения файла: {str(e)}',
                'output': ''
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение системной информации"""
        try:
            info = {
                'os': os.name,
                'platform': os.uname().sysname if hasattr(os, 'uname') else 'unknown',
                'cwd': os.getcwd(),
                'user': os.getenv('USER', 'unknown'),
                'home': os.getenv('HOME', 'unknown'),
                'timestamp': time.time()
            }
            
            return {
                'success': True,
                'error': None,
                'output': json.dumps(info, indent=2)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения системной информации: {str(e)}',
                'output': ''
            }
    
    def format_execution_results(self, results: List[Dict[str, Any]]) -> str:
        """Форматирует результаты выполнения для отправки обратно в модель"""
        if not results:
            return "Никаких команд не было выполнено."
            
        formatted = ["## Результаты выполнения команд:"]
        
        for i, result in enumerate(results, 1):
            formatted.append(f"\n### Команда {i}:")
            
            if 'command' in result:
                formatted.append(f"**Команда:** `{result['command']}`")
            
            if result['success']:
                formatted.append("**Статус:** ✅ Успешно")
                if result['output']:
                    formatted.append(f"**Результат:**\n```\n{result['output']}\n```")
            else:
                formatted.append("**Статус:** ❌ Ошибка")
                if result['error']:
                    formatted.append(f"**Ошибка:** {result['error']}")
                    
        return "\n".join(formatted)
    
    def should_continue_iteration(self, response: str, iteration: int) -> bool:
        """Определяет, нужна ли следующая итерация"""
        if iteration >= self.max_iterations:
            return False
            
        # Проверяем наличие tool_code блоков
        if self.extract_tool_codes(response):
            return True
            
        # Проверяем ключевые слова о незавершенности
        continuation_keywords = [
            'подожди', 'сейчас', 'выполняю', 'проверяю', 'ищу',
            'tool_code', 'команда', 'выполнить'
        ]
        
        response_lower = response.lower()
        for keyword in continuation_keywords:
            if keyword in response_lower:
                return True
                
        return False
    
    def process_iteratively(
        self, 
        initial_message: str, 
        llm_client, 
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Основная функция итеративной обработки
        
        Args:
            initial_message: Исходное сообщение пользователя
            llm_client: Клиент для вызова LLM (должен иметь метод generate_response)
            metadata: Дополнительные метаданные
            
        Returns:
            Dict с финальным ответом и историей итераций
        """
        conversation_history = []
        execution_history = []
        current_message = initial_message
        
        for iteration in range(self.max_iterations):
            logger.info(f"Итерация {iteration + 1}/{self.max_iterations}")
            
            # Генерируем ответ от модели
            try:
                response = llm_client.generate_response(current_message, metadata or {})
                conversation_history.append({
                    'iteration': iteration + 1,
                    'input': current_message,
                    'response': response,
                    'timestamp': time.time()
                })
                
                logger.info(f"Получен ответ модели: {response[:200]}...")
                
            except Exception as e:
                logger.error(f"Ошибка получения ответа от модели: {e}")
                break
            
            # Извлекаем и выполняем tool_codes
            tool_codes = self.extract_tool_codes(response)
            execution_results = []
            
            if tool_codes:
                logger.info(f"Найдено {len(tool_codes)} инструментов для выполнения")
                
                for tool_data in tool_codes:
                    result = self.execute_tool(tool_data)
                    execution_results.append(result)
                    logger.info(f"Выполнен инструмент: {result['success']}")
                
                execution_history.extend(execution_results)
                
                # Формируем сообщение с результатами для следующей итерации
                results_text = self.format_execution_results(execution_results)
                current_message = f"""
Предыдущий запрос: {initial_message}

{results_text}

Проанализируй результаты и продолжи выполнение задачи. Если задача выполнена полностью, 
дай финальный ответ без дополнительных tool_code блоков.
"""
            else:
                # Нет команд для выполнения - возможно, задача завершена
                logger.info("Команды не найдены, проверяем необходимость продолжения")
                
                if not self.should_continue_iteration(response, iteration):
                    logger.info("Итерации завершены - задача выполнена")
                    break
                else:
                    # Попросим модель продолжить или уточнить
                    current_message = f"""
Исходный запрос: {initial_message}
Предыдущий ответ: {response}

Пожалуйста, продолжи выполнение задачи или дай финальный ответ.
"""
        
        # Формируем финальный результат
        final_response = conversation_history[-1]['response'] if conversation_history else "Ошибка: не удалось получить ответ"
        
        return {
            'final_response': final_response,
            'iterations_count': len(conversation_history),
            'conversation_history': conversation_history,
            'execution_history': execution_history,
            'success': len(conversation_history) > 0
        }


# Глобальный экземпляр
iterative_executor = IterativeExecutor()


def process_message_iteratively(message: str, llm_client, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """Convenience функция для итеративной обработки сообщения"""
    return iterative_executor.process_iteratively(message, llm_client, metadata)


if __name__ == "__main__":
    # Тест системы
    print("Тест системы итеративного выполнения команд")
    
    # Тест извлечения tool_codes
    test_response = '''
    Привет! Сейчас я посмотрю содержимое папки.
    
    ```tool_code
    {'tool': 'terminal', 'params': {'command': 'ls -la /home'}}
    ```
    
    Подожди, выполняю команду...
    '''
    
    executor = IterativeExecutor()
    tool_codes = executor.extract_tool_codes(test_response)
    print(f"Найдено tool_codes: {tool_codes}")
    
    # Тест выполнения команды
    if tool_codes:
        result = executor.execute_tool(tool_codes[0])
        print(f"Результат выполнения: {result}")