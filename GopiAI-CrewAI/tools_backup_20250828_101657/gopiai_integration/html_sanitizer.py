"""
HTML Sanitizer - модуль для очистки HTML контента при экспорте файлов
Решает проблему с лишними HTML символами в созданных файлах
"""

import re
import html
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class HTMLSanitizer:
    """Санитизация HTML контента для различных целей"""
    
    def __init__(self):
        # Паттерны для очистки HTML
        self.html_tag_pattern = re.compile(r'<[^<>]*>')
        self.html_entity_pattern = re.compile(r'&[a-zA-Z0-9#]+;')
        self.script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        self.style_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
        
        # Разрешенные теги для UI (минимальный набор)
        self.allowed_ui_tags = {
            'p', 'br', 'strong', 'em', 'b', 'i', 'code', 'pre', 'span'
        }
        
        logger.info("[HTMLSanitizer] Инициализирован санитизатор HTML")
        
    def sanitize_for_file_export(self, content: str) -> str:
        """
        Полная очистка HTML для экспорта в текстовые файлы
        Удаляет все HTML теги и декодирует entities
        """
        try:
            logger.debug(f"[HTMLSanitizer] Санитизация для файла: {len(content)} символов")
            
            if not content:
                return ""
            
            # Удаляем script и style блоки полностью
            content = self.script_pattern.sub('', content)
            content = self.style_pattern.sub('', content)
            
            # Удаляем все HTML теги
            content = self.html_tag_pattern.sub('', content)
            
            # Декодируем HTML entities
            content = html.unescape(content)
            
            # Нормализуем пробелы и переносы
            content = self.normalize_whitespace(content)
            
            logger.debug(f"[HTMLSanitizer] Очищено для файла: {len(content)} символов")
            return content
            
        except Exception as e:
            logger.error(f"[HTMLSanitizer] Ошибка санитизации для файла: {e}")
            return str(content)
    
    def sanitize_for_ui_display(self, content: str) -> str:
        """
        Мягкая санитизация для отображения в UI
        Оставляет безопасные теги для форматирования
        """
        try:
            logger.debug(f"[HTMLSanitizer] Санитизация для UI: {len(content)} символов")
            
            if not content:
                return ""
            
            # Удаляем опасные блоки
            content = self.script_pattern.sub('', content)
            content = self.style_pattern.sub('', content)
            
            # Удаляем неразрешенные теги, оставляя содержимое
            content = self.remove_disallowed_tags(content)
            
            # Декодируем HTML entities
            content = html.unescape(content)
            
            logger.debug(f"[HTMLSanitizer] Очищено для UI: {len(content)} символов")
            return content
            
        except Exception as e:
            logger.error(f"[HTMLSanitizer] Ошибка санитизации для UI: {e}")
            return str(content)
    
    def remove_disallowed_tags(self, content: str) -> str:
        """Удаляет неразрешенные HTML теги, оставляя содержимое"""
        def replace_tag(match):
            tag_content = match.group(0)
            
            # Извлекаем имя тега
            tag_match = re.match(r'</?([a-zA-Z0-9]+)', tag_content)
            if not tag_match:
                return ''
                
            tag_name = tag_match.group(1).lower()
            
            # Если тег разрешен, оставляем как есть
            if tag_name in self.allowed_ui_tags:
                return tag_content
            
            # Иначе удаляем тег, оставляя содержимое
            return ''
        
        return self.html_tag_pattern.sub(replace_tag, content)
    
    def normalize_whitespace(self, content: str) -> str:
        """Нормализация пробелов и переносов строк"""
        # Заменяем множественные пробелы одним
        content = re.sub(r' {2,}', ' ', content)
        
        # Заменяем множественные переносы двойным переносом максимум
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Удаляем пробелы в начале и конце строк
        lines = [line.strip() for line in content.split('\n')]
        
        # Удаляем пустые строки в начале и конце
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
            
        return '\n'.join(lines)
    
    def extract_text_content(self, html_content: str) -> str:
        """Извлекает только текстовое содержимое из HTML"""
        try:
            # Заменяем некоторые теги переносами для лучшего форматирования
            html_content = re.sub(r'<br[^>]*>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</p>', '\n\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</div>', '\n', html_content, flags=re.IGNORECASE)
            
            # Удаляем все остальные теги
            text_content = self.html_tag_pattern.sub('', html_content)
            
            # Декодируем entities
            text_content = html.unescape(text_content)
            
            # Нормализуем
            text_content = self.normalize_whitespace(text_content)
            
            return text_content
            
        except Exception as e:
            logger.error(f"[HTMLSanitizer] Ошибка извлечения текста: {e}")
            return str(html_content)
    
    def is_html_content(self, content: str) -> bool:
        """Проверяет, содержит ли строка HTML теги"""
        if not content:
            return False
            
        return bool(self.html_tag_pattern.search(content))
    
    def clean_markdown_artifacts(self, content: str) -> str:
        """Очистка артефактов Markdown, которые могут появиться в HTML"""
        # Удаляем лишние символы экранирования
        content = re.sub(r'\\([*_`~])', r'\1', content)
        
        # Очищаем лишние пробелы вокруг знаков препинания
        content = re.sub(r'\s+([.!?,:;])', r'\1', content)
        
        return content

# Глобальный экземпляр санитизатора
html_sanitizer = HTMLSanitizer()

def sanitize_html_for_file(content: str) -> str:
    """Удобная функция для санитизации HTML при экспорте в файл"""
    return html_sanitizer.sanitize_for_file_export(content)

def sanitize_html_for_ui(content: str) -> str:
    """Удобная функция для санитизации HTML для отображения в UI"""
    return html_sanitizer.sanitize_for_ui_display(content)

def extract_clean_text(html_content: str) -> str:
    """Удобная функция для извлечения чистого текста из HTML"""
    return html_sanitizer.extract_text_content(html_content)
