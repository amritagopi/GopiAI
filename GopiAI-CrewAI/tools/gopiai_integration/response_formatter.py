"""
Response Formatter - форматировщик ответов для чистого отображения
Восстановлено из коммита 2f0fe4256d7f0d5bf2168a4db56d6b6def937860
"""

import logging
import re
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Форматировщик ответов для удаления JSON и технических данных"""
    
    def __init__(self):
        logger.info("🔧 ResponseFormatter инициализирован")
    
    def format_for_chat(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Форматирует ответ для отображения в чате
        Убирает JSON, команды и оставляет только пользовательский контент
        """
        try:
            response_text = response_data.get("response", "")
            
            if not response_text:
                return {
                    "user_content": "Пустой ответ",
                    "has_commands": False,
                    "formatted": True
                }
            
            # Очищаем от JSON блоков
            cleaned_text = self._remove_json_blocks(response_text)
            
            # Очищаем от технических команд
            cleaned_text = self._remove_command_blocks(cleaned_text)
            
            # Проверяем наличие выполненных команд
            has_commands = self._detect_command_execution(response_text)
            
            # Финальная очистка форматирования
            cleaned_text = self._final_cleanup(cleaned_text)
            
            logger.info(f"🧹 Текст очищен: было {len(response_text)} символов, стало {len(cleaned_text)}")
            
            return {
                "user_content": cleaned_text,
                "has_commands": has_commands,
                "formatted": True,
                "original_length": len(response_text),
                "cleaned_length": len(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка форматирования ответа: {e}")
            return {
                "user_content": response_data.get("response", "Ошибка форматирования"),
                "has_commands": False,
                "formatted": False,
                "error": str(e)
            }
    
    def _remove_json_blocks(self, text: str) -> str:
        """Удаляет JSON блоки из текста"""
        
        # Удаляем блоки ```json...```
        text = re.sub(r'```json\s*\n.*?\n```', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Удаляем блоки ```\n{...}\n```
        text = re.sub(r'```\s*\n\s*\{.*?\}\s*\n```', '', text, flags=re.DOTALL)
        
        # Удаляем строки, которые выглядят как JSON
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Пропускаем строки, которые выглядят как JSON
            if (line_stripped.startswith('{') and line_stripped.endswith('}')) or \
               (line_stripped.startswith('[') and line_stripped.endswith(']')):
                try:
                    json.loads(line_stripped)
                    continue  # Это JSON строка, пропускаем
                except:
                    pass  # Не JSON, оставляем
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_command_blocks(self, text: str) -> str:
        """Удаляет блоки с командами"""
        
        # Удаляем блоки с командами bash/shell
        text = re.sub(r'```(?:bash|shell|terminal)\s*\n.*?\n```', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Удаляем блоки "Выполняется команда..."
        text = re.sub(r'🖥️ Выполняется команда:.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'✅ Команда `.*?` выполнена:.*?\n```', '', text, flags=re.DOTALL)
        text = re.sub(r'❌ Ошибка выполнения `.*?`:.*?\n', '', text, flags=re.MULTILINE)
        
        return text
    
    def _detect_command_execution(self, text: str) -> bool:
        """Определяет, были ли выполнены команды в ответе"""
        command_indicators = [
            '✅ Команда',
            '❌ Ошибка выполнения',
            '🖥️ Выполняется команда',
            '```bash',
            '```shell',
            '```terminal'
        ]
        
        return any(indicator in text for indicator in command_indicators)
    
    def _final_cleanup(self, text: str) -> str:
        """Финальная очистка текста"""
        
        # Удаляем лишние пустые строки
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Удаляем технические префиксы
        text = re.sub(r'^\[.*?\]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^🔧\s*.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^🔍\s*.*?\n', '', text, flags=re.MULTILINE)
        
        # Удаляем служебные сообщения
        service_patterns = [
            r'Инициализированы инструменты:.*?\n',
            r'Вызов MCP инструмента.*?\n',
            r'Получен результат от.*?\n',
            r'Проверяем ответ Gemini.*?\n',
            r'Применяем форматирование.*?\n'
        ]
        
        for pattern in service_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Убираем лишние пробелы в начале и конце строк
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Убираем множественные пробелы
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()