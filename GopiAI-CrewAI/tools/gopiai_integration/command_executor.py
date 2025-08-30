"""
Модуль для выполнения команд, полученных от Gemini AI.
Парсит JSON-ответы и выполняет команды терминала.
"""

import json
import subprocess
import os
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class CommandExecutor:
    """Класс для безопасного выполнения команд из ответов Gemini"""
    
    def __init__(self):
        self.logger = logger
        
        # Разрешенные команды для безопасности
        self.allowed_commands = {
            'mkdir', 'dir', 'ls', 'pwd', 'cd', 'echo', 'type', 'cat',
            'tree', 'find', 'grep', 'copy', 'cp', 'move', 'mv',
            'del', 'rm', 'rmdir', 'touch', 'whoami', 'date', 'time'
        }
        
        # Опасные команды, которые требуют особого внимания
        self.dangerous_commands = {
            'rm', 'del', 'rmdir', 'format', 'fdisk', 'shutdown', 'reboot'
        }
    
    def parse_gemini_response(self, response_text: str) -> List[Dict]:
        """
        Парсит ответ Gemini и извлекает команды в формате JSON
        
        Args:
            response_text: Текст ответа от Gemini
            
        Returns:
            Список команд для выполнения
        """
        commands = []
        
        try:
            # Ищем JSON блоки в ответе
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            for json_str in json_matches:
                try:
                    # Пробуем парсить как обычный JSON
                    command_data = json.loads(json_str)
                    if self._is_valid_command(command_data):
                        commands.append(command_data)
                        self.logger.info(f"[PARSER] Найдена команда: {command_data}")
                except json.JSONDecodeError:
                    # Если не JSON, пробуем парсить как Python dict с помощью ast.literal_eval
                    try:
                        import ast
                        # Безопасный парсинг только для простых словарей
                        if json_str.strip().startswith('{') and json_str.strip().endswith('}'):
                            command_data = ast.literal_eval(json_str)
                            if self._is_valid_command(command_data):
                                commands.append(command_data)
                                self.logger.info(f"[PARSER] Найдена команда (dict): {command_data}")
                    except Exception as e:
                        self.logger.warning(f"[PARSER] Не удалось парсить команду: {json_str[:100]}... Ошибка: {e}")
            
            # Также ищем команды в обычном тексте
            text_commands = self._extract_text_commands(response_text)
            commands.extend(text_commands)
            
        except Exception as e:
            self.logger.error(f"[PARSER] Ошибка при парсинге ответа Gemini: {e}")
        
        return commands
    
    def _is_valid_command(self, command_data: Dict) -> bool:
        """Проверяет, является ли структура данных валидной командой"""
        if not isinstance(command_data, dict):
            return False
        
        # Проверяем наличие обязательных полей
        if 'tool' not in command_data:
            return False
        
        tool = command_data.get('tool', '').lower()
        
        # Поддерживаем только команды терминала пока
        if tool != 'terminal':
            return False
        
        # Проверяем наличие параметров
        params = command_data.get('params', {})
        if not isinstance(params, dict) or 'command' not in params:
            return False
        
        return True
    
    def _extract_text_commands(self, text: str) -> List[Dict]:
        """Извлекает команды из обычного текста (fallback)"""
        commands = []
        
        # Простые паттерны для распознавания команд
        patterns = [
            r'mkdir\s+([^\s\n]+)',
            r'dir\s*([^\n]*)',
            r'ls\s*([^\n]*)',
            r'echo\s+([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cmd_parts = pattern.split('\\s+')[0].replace('\\', '')
                full_command = f"{cmd_parts} {match}".strip()
                
                command_data = {
                    'tool': 'terminal',
                    'params': {'command': full_command}
                }
                commands.append(command_data)
                self.logger.info(f"[PARSER] Найдена текстовая команда: {full_command}")
        
        return commands
    
    def execute_command(self, command_data: Dict) -> Dict:
        """
        Выполняет одну команду
        
        Args:
            command_data: Словарь с данными команды
            
        Returns:
            Результат выполнения команды
        """
        try:
            tool = command_data.get('tool', '').lower()
            params = command_data.get('params', {})
            
            if tool == 'terminal':
                return self._execute_terminal_command(params.get('command', ''))
            else:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый инструмент: {tool}',
                    'output': ''
                }
                
        except Exception as e:
            self.logger.error(f"[EXECUTOR] Ошибка выполнения команды: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }
    
    def _execute_terminal_command(self, command: str) -> Dict:
        """Выполняет команду терминала"""
        if not command or not command.strip():
            return {
                'success': False,
                'error': 'Пустая команда',
                'output': ''
            }
        
        command = command.strip()
        self.logger.info(f"[EXECUTOR] Выполняем команду: {command}")
        
        # Проверяем безопасность команды
        cmd_parts = command.split()
        if not cmd_parts:
            return {
                'success': False,
                'error': 'Некорректная команда',
                'output': ''
            }
        
        base_cmd = cmd_parts[0].lower()
        
        # Проверяем, разрешена ли команда
        if base_cmd not in self.allowed_commands:
            self.logger.warning(f"[EXECUTOR] Команда не разрешена: {base_cmd}")
            return {
                'success': False,
                'error': f'Команда "{base_cmd}" не разрешена для выполнения',
                'output': ''
            }
        
        # Предупреждение для опасных команд
        if base_cmd in self.dangerous_commands:
            self.logger.warning(f"[EXECUTOR] Выполняется потенциально опасная команда: {command}")
        
        try:
            # Выполняем команду
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            self.logger.info(f"[EXECUTOR] Команда выполнена. Код возврата: {result.returncode}")
            self.logger.info(f"[EXECUTOR] Вывод: {output[:200]}...")
            
            return {
                'success': success,
                'error': result.stderr if not success else '',
                'output': output,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error_msg = f"Команда '{command}' превысила лимит времени выполнения (30 сек)"
            self.logger.error(f"[EXECUTOR] {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'output': ''
            }
        except Exception as e:
            error_msg = f"Ошибка выполнения команды '{command}': {str(e)}"
            self.logger.error(f"[EXECUTOR] {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'output': ''
            }
    
    def execute_commands(self, commands: List[Dict]) -> List[Dict]:
        """
        Выполняет список команд
        
        Args:
            commands: Список команд для выполнения
            
        Returns:
            Список результатов выполнения
        """
        results = []
        
        for i, command in enumerate(commands):
            self.logger.info(f"[EXECUTOR] Выполняем команду {i+1}/{len(commands)}")
            result = self.execute_command(command)
            results.append(result)
            
            # Если команда не выполнилась, логируем это
            if not result.get('success', False):
                self.logger.warning(f"[EXECUTOR] Команда {i+1} не выполнилась: {result.get('error', 'Неизвестная ошибка')}")
        
        return results
    
    def process_gemini_response(self, response_text: str) -> Tuple[str, List[Dict]]:
        """
        Полная обработка ответа Gemini: парсинг и выполнение команд
        
        Args:
            response_text: Ответ от Gemini
            
        Returns:
            Кортеж (обновленный_ответ, результаты_команд)
        """
        # Парсим команды
        commands = self.parse_gemini_response(response_text)
        
        if not commands:
            self.logger.info("[PROCESSOR] Команды в ответе не найдены")
            return response_text, []
        
        self.logger.info(f"[PROCESSOR] Найдено команд для выполнения: {len(commands)}")
        
        # Выполняем команды
        results = self.execute_commands(commands)
        
        # Формируем обновленный ответ с результатами
        updated_response = self._update_response_with_results(response_text, commands, results)
        
        return updated_response, results
    
    def _update_response_with_results(self, original_response: str, commands: List[Dict], results: List[Dict]) -> str:
        """Обновляет ответ Gemini с реальными результатами выполнения команд"""
        
        if not commands or not results:
            return original_response
        
        # Добавляем секцию с результатами выполнения
        results_section = "\n\n🔧 **Результаты выполнения команд:**\n"
        
        for i, (command, result) in enumerate(zip(commands, results)):
            cmd_str = command.get('params', {}).get('command', 'неизвестная команда')
            
            if result.get('success', False):
                results_section += f"✅ `{cmd_str}` - выполнено успешно\n"
                if result.get('output'):
                    results_section += f"   Вывод: {result['output'][:200]}...\n"
            else:
                results_section += f"❌ `{cmd_str}` - ошибка: {result.get('error', 'неизвестная ошибка')}\n"
        
        return original_response + results_section
