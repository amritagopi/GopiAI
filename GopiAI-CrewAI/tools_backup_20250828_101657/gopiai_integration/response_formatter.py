"""
ResponseFormatter - модуль для форматирования ответов AI для различных целей
Решает проблемы с отображением JSON фрагментов и HTML артефактов
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List
from .html_sanitizer import HTMLSanitizer

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Форматирование ответов для различных целей"""
    
    def __init__(self):
        # Паттерны для очистки контента
        self.json_pattern = re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
        self.code_block_pattern = re.compile(r'```[a-zA-Z]*\s*(.*?)\s*```', re.DOTALL)
        self.html_pattern = re.compile(r'<[^<>]*>')
        self.command_pattern = re.compile(r'\{[\'"]tool[\']:\s*[\'"]terminal[\'].*?\}', re.DOTALL)
        
        # Инициализируем HTML санитизатор
        self.html_sanitizer = HTMLSanitizer()
        
        logger.info("[ResponseFormatter] Инициализирован форматировщик ответов с HTML санитизатором")
        
    def format_for_chat(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Форматирование для отображения в чате
        Удаляет служебную информацию, оставляет только пользовательский контент
        """
        try:
            logger.debug(f"[ResponseFormatter] Форматируем ответ для чата: {str(raw_response)[:200]}...")
            
            formatted = {
                'user_content': self.extract_user_content(raw_response),
                'metadata': self.extract_safe_metadata(raw_response),
                'status': raw_response.get('status', 'completed'),
                'has_commands': self.has_executed_commands(raw_response)
            }
            
            logger.debug(f"[ResponseFormatter] Отформатированный ответ: {str(formatted)[:200]}...")
            return formatted
            
        except Exception as e:
            logger.error(f"[ResponseFormatter] Ошибка форматирования для чата: {e}")
            return {
                'user_content': str(raw_response.get('response', 'Ошибка форматирования ответа')),
                'metadata': {},
                'status': 'error',
                'has_commands': False
            }
        
    def format_for_file_export(self, raw_response: Dict[str, Any]) -> str:
        """
        Форматирование для экспорта в файл
        Полная очистка от HTML и служебной информации
        """
        try:
            logger.debug("[ResponseFormatter] Форматируем ответ для экспорта в файл")
            
            content = self.extract_user_content(raw_response)
            
            # Используем HTML санитизатор для полной очистки
            clean_content = self.html_sanitizer.sanitize_for_file_export(content)
            
            # Дополнительная очистка артефактов форматирования
            clean_content = self.clean_formatting_artifacts(clean_content)
            
            logger.debug(f"[ResponseFormatter] Очищенный контент для файла: {len(clean_content)} символов")
            return clean_content
            
        except Exception as e:
            logger.error(f"[ResponseFormatter] Ошибка форматирования для файла: {e}")
            return str(raw_response.get('response', 'Ошибка форматирования ответа'))
        
    def extract_user_content(self, response_data: Dict[str, Any]) -> str:
        """Извлечение только пользовательского контента"""
        if not isinstance(response_data, dict):
            return str(response_data)
            
        # Получаем основной контент
        content = response_data.get('response', '')
        if not content:
            return "Пустой ответ"
            
        # Удаляем JSON блоки с командами
        content = self.remove_command_json_blocks(content)
        
        # Удаляем другие служебные JSON блоки
        content = self.remove_service_json_blocks(content)
        
        # Очищаем от лишних символов
        content = self.clean_formatting_artifacts(content)
        
        return content.strip()
        
    def extract_safe_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение безопасных метаданных для отображения"""
        if not isinstance(response_data, dict):
            return {}
            
        safe_metadata = {}
        
        # Анализ выполненных команд
        analysis = response_data.get('analysis', {})
        if isinstance(analysis, dict):
            if analysis.get('executed_commands', 0) > 0:
                safe_metadata['commands_executed'] = analysis['executed_commands']
                safe_metadata['execution_time'] = analysis.get('analysis_time', 0)
                
        # Информация о процессинге
        if response_data.get('processed_with_crewai'):
            safe_metadata['processed_with_crewai'] = True
            
        return safe_metadata
        
    def has_executed_commands(self, response_data: Dict[str, Any]) -> bool:
        """Проверяет, были ли выполнены команды"""
        if not isinstance(response_data, dict):
            return False
            
        analysis = response_data.get('analysis', {})
        return isinstance(analysis, dict) and analysis.get('executed_commands', 0) > 0
        
    def remove_command_json_blocks(self, content: str) -> str:
        """Удаление JSON блоков с командами терминала"""
        # Удаляем блоки типа ```json {'tool': 'terminal', ...} ```
        content = self.json_pattern.sub('', content)
        
        # Удаляем прямые JSON команды в тексте
        content = self.command_pattern.sub('', content)
        
        return content
        
    def remove_service_json_blocks(self, content: str) -> str:
        """Удаление других служебных JSON блоков"""
        # Удаляем все code blocks, которые содержат JSON
        def replace_json_blocks(match):
            block_content = match.group(1)
            try:
                # Если это валидный JSON, удаляем блок
                json.loads(block_content)
                return ''  # Удаляем JSON блоки
            except (json.JSONDecodeError, ValueError):
                # Если не JSON, оставляем как есть
                return match.group(0)
                
        content = self.code_block_pattern.sub(replace_json_blocks, content)
        return content
        
    def remove_html_tags(self, content: str) -> str:
        """Удаление HTML тегов"""
        # Удаляем HTML теги
        clean_content = self.html_pattern.sub('', content)
        
        # Декодируем HTML entities
        import html
        clean_content = html.unescape(clean_content)
        
        return clean_content
        
    def clean_formatting_artifacts(self, content: str) -> str:
        """Очистка артефактов форматирования"""
        # Удаляем множественные переносы строк
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Удаляем лишние пробелы
        content = re.sub(r' {2,}', ' ', content)
        
        # Удаляем пробелы в начале и конце строк
        lines = [line.strip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        return content
        
    def normalize_whitespace(self, content: str) -> str:
        """Нормализация пробелов и переносов"""
        # Удаляем trailing spaces
        lines = [line.rstrip() for line in content.split('\n')]
        
        # Удаляем пустые строки в начале и конце
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
            
        return '\n'.join(lines)
        
    def add_execution_summary(self, content: str, metadata: Dict[str, Any]) -> str:
        """Добавление краткой сводки о выполненных командах"""
        if not metadata.get('commands_executed', 0):
            return content
            
        summary = f"\n\n🔧 Выполнено команд: {metadata['commands_executed']}"
        if 'execution_time' in metadata:
            summary += f" (за {metadata['execution_time']:.1f}с)"
            
        return content + summary

# Глобальный экземпляр форматировщика
response_formatter = ResponseFormatter()

def format_response_for_chat(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """Удобная функция для форматирования ответа для чата"""
    return response_formatter.format_for_chat(raw_response)

def format_response_for_file(raw_response: Dict[str, Any]) -> str:
    """Удобная функция для форматирования ответа для файла"""
    return response_formatter.format_for_file_export(raw_response)
