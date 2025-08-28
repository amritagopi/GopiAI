"""
🧠 Intent Parser
Система распознавания намерений для автоматического выбора инструментов
Поддерживает русский и английский языки, расширяемые паттерны
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentMode(Enum):
    """Режимы вызова инструментов"""
    AUTO = "auto"           # Автоматический вызов по намерению
    FORCED = "forced"       # Принудительный вызов через UI
    SUGGESTED = "suggested" # Предложение инструмента

@dataclass
class IntentMatch:
    """Результат распознавания намерения"""
    tool_name: str                    # Каноническое название инструмента
    confidence: float                 # Уверенность (0.0 - 1.0)
    mode: IntentMode                  # Режим вызова
    extracted_params: Dict[str, Any]  # Извлеченные параметры
    matched_patterns: List[str]       # Сработавшие паттерны
    original_text: str               # Исходный текст

class IntentParser:
    """
    Парсер намерений для автоматического определения нужного инструмента.
    Анализирует текст пользователя и предлагает подходящие инструменты.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._intent_patterns = self._build_intent_patterns()
        self._url_pattern = re.compile(r'https?://[\w\.-]+(?:\.[a-zA-Z]{2,})+(?:/[\w\.-]*)*/?(?:\?[\w&=%-]*)?')
        self._file_patterns = [
            re.compile(r'[a-zA-Z]:\\[\w\\.-]+'),      # Windows пути
            re.compile(r'/[\w/.-]+'),                  # Unix пути
            re.compile(r'\./[\w/.-]+'),                # Относительные пути
            re.compile(r'[\w.-]+\.[a-zA-Z]{2,4}')     # Файлы с расширениями
        ]
        self.logger.info("✅ IntentParser инициализирован")
    
    def _build_intent_patterns(self) -> Dict[str, Dict]:
        """
        Строит паттерны для распознавания намерений.
        Структура: {tool_name: {patterns: [...], extractors: {...}, confidence: float}}
        """
        patterns = {}
        
        # 💻 ТЕРМИНАЛ И КОМАНДЫ
        patterns['execute_shell'] = {
            'patterns': [
                # Русские команды
                r'\b(выполни|запусти|команда|терминал|консоль)\b',
                r'\b(зайди в|перейди в|покажи содержимое|список файлов)\b',
                r'\b(установи|скачай|обнови)\s+\w+',
                # Английские команды
                r'\b(run|execute|command|terminal|console)\b',
                r'\b(go to|show contents|list files|navigate to)\b',
                r'\b(install|download|update)\s+\w+',
                # Прямые команды
                r'^\s*(ls|dir|pwd|cd|mkdir|git|npm|pip|docker|curl)\b',
                r'^\s*(cat|type|echo|ps|top|netstat)\b'
            ],
            'extractors': {
                'command': [
                    r'команда[:\s]+(.+)',
                    r'выполни[:\s]+(.+)',
                    r'запусти[:\s]+(.+)',
                    r'^(.+)$'  # Весь текст как команда, если другие не сработали
                ]
            },
            'confidence': 0.9
        }
        
        # 📁 ФАЙЛОВЫЕ ОПЕРАЦИИ
        patterns['file_operations'] = {
            'patterns': [
                # Русские
                r'\b(файл|файлы|папка|директория|каталог)\b',
                r'\b(читай|прочитай|открой|покажи)\s+файл',
                r'\b(создай|запиши|сохрани)\s+файл',
                r'\b(список|содержимое)\s+(папки|директории)',
                # Английские
                r'\b(file|files|folder|directory|dir)\b',
                r'\b(read|open|show)\s+file',
                r'\b(create|write|save)\s+file',
                r'\b(list|contents)\s+(folder|directory)',
                # Расширения файлов
                r'\.(txt|json|csv|py|js|html|css|md|xml|yaml|yml|log)[\s\b]'
            ],
            'extractors': {
                'path': [
                    r'файл[:\s]+([^\s]+)',
                    r'папк[аеиу][:\s]+([^\s]+)',
                    r'file[:\s]+([^\s]+)',
                    r'folder[:\s]+([^\s]+)'
                ],
                'operation': [
                    r'\b(читай|прочитай|read|open)\b',
                    r'\b(создай|запиши|write|create|save)\b',
                    r'\b(список|list|ls|dir)\b'
                ]
            },
            'confidence': 0.8
        }
        
        # 🌐 ВЕБ-СКРАПИНГ
        patterns['web_scraper'] = {
            'patterns': [
                # Русские
                r'\b(скачай|парси|извлеки|проанализируй)\s+(сайт|страниц|ссылк)',
                r'\b(данные|информацию)\s+с\s+(сайта|страницы)',
                r'\b(содержимое|контент)\s+(веб-?страницы|сайта)',
                # Английские
                r'\b(scrape|parse|extract|analyze)\s+(website|page|site)',
                r'\b(get|fetch|download)\s+(data|content)\s+from',
                r'\b(web\s+scraping|page\s+content|website\s+data)\b'
            ],
            'extractors': {
                'url': [r'(https?://[^\s]+)'],
                'action': [
                    r'\b(текст|text)\b',
                    r'\b(ссылки|links)\b',
                    r'\b(таблицы|tables)\b',
                    r'\b(изображения|images)\b'
                ]
            },
            'confidence': 0.85
        }
        
        # 🔍 ВЕБ-ПОИСК
        patterns['web_search'] = {
            'patterns': [
                # Русские
                r'\b(найди|поищи|поиск)\s+(в\s+интернете|в\s+сети|онлайн)',
                r'\b(гугл|google|яндекс|yandex)\b',
                r'\b(поисковый\s+запрос|найти\s+информацию)\b',
                # Английские
                r'\b(search|find|look\s+up)\s+(online|internet|web)',
                r'\b(google|bing|search\s+for)\b',
                r'\b(web\s+search|internet\s+search)\b'
            ],
            'extractors': {
                'query': [
                    r'найди[:\s]+(.+)',
                    r'поищи[:\s]+(.+)',
                    r'search[:\s]+(.+)',
                    r'find[:\s]+(.+)'
                ]
            },
            'confidence': 0.8
        }
        
        # 🔌 API КЛИЕНТ
        patterns['api_client'] = {
            'patterns': [
                # Русские
                r'\b(api|апи)\s+(запрос|вызов|обращение)',
                r'\b(отправь|сделай)\s+(get|post|put|delete)\s+запрос',
                r'\b(http|rest)\s+(запрос|клиент)',
                # Английские
                r'\b(api\s+call|api\s+request|http\s+request)\b',
                r'\b(make\s+|send\s+)(get|post|put|delete)\s+request',
                r'\b(rest\s+api|web\s+api|http\s+client)\b'
            ],
            'extractors': {
                'url': [r'(https?://[^\s]+)'],
                'method': [
                    r'\b(get|post|put|delete|patch)\b'
                ]
            },
            'confidence': 0.85
        }
        
        # 🐍 КОД ИНТЕРПРЕТАТОР
        patterns['code_interpreter'] = {
            'patterns': [
                # Русские
                r'\b(выполни|запусти)\s+(python|код|скрипт)',
                r'\b(python\s+код|питон|пайтон)\b',
                r'\b(интерпретатор|выполнение\s+кода)\b',
                # Английские
                r'\b(run|execute)\s+(python|code|script)',
                r'\b(python\s+code|code\s+execution)\b',
                r'\b(interpreter|code\s+runner)\b',
                # Код в тексте
                r'```python',
                r'print\s*\(',
                r'import\s+\w+',
                r'def\s+\w+\s*\('
            ],
            'extractors': {
                'code': [
                    r'```python\s*\n(.*?)\n```',
                    r'код[:\s]+(.+)',
                    r'code[:\s]+(.+)'
                ]
            },
            'confidence': 0.9
        }
        
        # 🎨 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
        patterns['dalle_tool'] = {
            'patterns': [
                # Русские
                r'\b(создай|нарисуй|сгенерируй)\s+(изображение|картинку|рисунок)',
                r'\b(dall-?e|далле|дали)\b',
                r'\b(генерация\s+изображений|ai\s+арт)\b',
                # Английские
                r'\b(create|generate|draw|make)\s+(image|picture|artwork)',
                r'\b(dall-?e|image\s+generation|ai\s+art)\b',
                r'\b(generate\s+image|create\s+picture)\b'
            ],
            'extractors': {
                'prompt': [
                    r'нарисуй[:\s]+(.+)',
                    r'создай[:\s]+(.+)',
                    r'generate[:\s]+(.+)',
                    r'create[:\s]+(.+)'
                ]
            },
            'confidence': 0.9
        }
        
        # 👁️ АНАЛИЗ ИЗОБРАЖЕНИЙ
        patterns['vision_tool'] = {
            'patterns': [
                # Русские
                r'\b(проанализируй|опиши|что\s+на)\s+(изображении|картинке|фото)',
                r'\b(распознай|определи)\s+(объекты|что\s+изображено)',
                r'\b(компьютерное\s+зрение|анализ\s+изображений)\b',
                # Английские
                r'\b(analyze|describe|what.s\s+in)\s+(image|picture|photo)',
                r'\b(recognize|identify)\s+(objects|what.s\s+shown)',
                r'\b(computer\s+vision|image\s+analysis)\b'
            ],
            'extractors': {
                'image_url': [r'(https?://[^\s]+\.(jpg|jpeg|png|gif|webp))']
            },
            'confidence': 0.85
        }
        
        # 🐙 GITHUB ПОИСК
        patterns['github_search'] = {
            'patterns': [
                # Русские
                r'\b(найди|поищи)\s+(на\s+)?github',
                r'\b(репозиторий|репо|код)\s+(на\s+)?github',
                r'\b(github\s+поиск|поиск\s+кода)\b',
                # Английские
                r'\b(search|find)\s+(on\s+)?github',
                r'\b(repository|repo|code)\s+(on\s+)?github',
                r'\b(github\s+search|code\s+search)\b'
            ],
            'extractors': {
                'query': [
                    r'github[:\s]+(.+)',
                    r'найди[:\s]+(.+)',
                    r'search[:\s]+(.+)'
                ]
            },
            'confidence': 0.8
        }
        
        # ℹ️ СИСТЕМНАЯ ИНФОРМАЦИЯ
        patterns['system_info'] = {
            'patterns': [
                # Русские
                r'\b(системная\s+информация|инфо\s+о\s+системе|характеристики)\b',
                r'\b(операционная\s+система|версия\s+ос|железо)\b',
                r'\b(статус\s+системы|здоровье\s+системы)\b',
                # Английские
                r'\b(system\s+info|system\s+information|system\s+specs)\b',
                r'\b(operating\s+system|os\s+version|hardware)\b',
                r'\b(system\s+status|system\s+health)\b'
            ],
            'extractors': {},
            'confidence': 0.9
        }
        
        # ⏰ ВРЕМЯ
        patterns['time_helper'] = {
            'patterns': [
                # Русские
                r'\b(время|текущее\s+время|сколько\s+времени|который\s+час)\b',
                r'\b(дата|сегодняшняя\s+дата|какое\s+число)\b',
                r'\b(timestamp|временная\s+метка)\b',
                # Английские
                r'\b(time|current\s+time|what\s+time|clock)\b',
                r'\b(date|current\s+date|today.s\s+date)\b',
                r'\b(timestamp|time\s+stamp)\b'
            ],
            'extractors': {},
            'confidence': 0.95
        }
        
        return patterns
    
    def parse_intent(self, text: str, forced_tool: Optional[str] = None) -> List[IntentMatch]:
        """
        Анализирует текст и возвращает список возможных намерений.
        
        Args:
            text (str): Текст для анализа
            forced_tool (Optional[str]): Принудительно выбранный инструмент
            
        Returns:
            List[IntentMatch]: Список найденных намерений, отсортированный по уверенности
        """
        if not text or not isinstance(text, str):
            return []
        
        text = text.strip()
        if not text:
            return []
        
        matches = []
        
        # Если инструмент принудительно выбран
        if forced_tool:
            match = IntentMatch(
                tool_name=forced_tool,
                confidence=1.0,
                mode=IntentMode.FORCED,
                extracted_params=self._extract_params_for_tool(text, forced_tool),
                matched_patterns=[f"forced:{forced_tool}"],
                original_text=text
            )
            matches.append(match)
            return matches
        
        # Автоматическое распознавание
        text_lower = text.lower()
        
        for tool_name, config in self._intent_patterns.items():
            confidence = 0.0
            matched_patterns = []
            
            # Проверяем паттерны
            for pattern in config['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                    confidence = max(confidence, config['confidence'])
                    matched_patterns.append(pattern)
            
            # Если есть совпадения, извлекаем параметры
            if confidence > 0:
                extracted_params = self._extract_params_for_tool(text, tool_name)
                
                # Бонус за извлеченные параметры
                if extracted_params:
                    confidence = min(1.0, confidence + 0.1)
                
                match = IntentMatch(
                    tool_name=tool_name,
                    confidence=confidence,
                    mode=IntentMode.AUTO,
                    extracted_params=extracted_params,
                    matched_patterns=matched_patterns,
                    original_text=text
                )
                matches.append(match)
        
        # Специальные проверки для URL и файлов
        self._add_url_based_matches(text, matches)
        self._add_file_based_matches(text, matches)
        
        # Сортируем по уверенности
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        self.logger.debug(f"🧠 Распознано намерений: {len(matches)} для текста: '{text[:50]}...'")
        return matches
    
    def _extract_params_for_tool(self, text: str, tool_name: str) -> Dict[str, Any]:
        """
        Извлекает параметры для конкретного инструмента из текста.
        
        Args:
            text (str): Исходный текст
            tool_name (str): Название инструмента
            
        Returns:
            Dict[str, Any]: Извлеченные параметры
        """
        params = {}
        
        if tool_name not in self._intent_patterns:
            return params
        
        extractors = self._intent_patterns[tool_name].get('extractors', {})
        
        for param_name, patterns in extractors.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    if match.groups():
                        params[param_name] = match.group(1).strip()
                    else:
                        params[param_name] = match.group(0).strip()
                    break
        
        # Дополнительные извлечения
        self._extract_urls(text, params)
        self._extract_file_paths(text, params)
        
        return params
    
    def _extract_urls(self, text: str, params: Dict[str, Any]) -> None:
        """Извлекает URL из текста"""
        urls = self._url_pattern.findall(text)
        if urls and 'url' not in params:
            params['url'] = urls[0]
        if len(urls) > 1:
            params['urls'] = urls
    
    def _extract_file_paths(self, text: str, params: Dict[str, Any]) -> None:
        """Извлекает пути к файлам из текста"""
        for pattern in self._file_patterns:
            matches = pattern.findall(text)
            if matches and 'path' not in params:
                params['path'] = matches[0]
                break
    
    def _add_url_based_matches(self, text: str, matches: List[IntentMatch]) -> None:
        """Добавляет намерения на основе найденных URL"""
        urls = self._url_pattern.findall(text)
        if not urls:
            return
        
        text_lower = text.lower()
        
        # Если есть URL и ключевые слова скрапинга
        if any(word in text_lower for word in ['скачай', 'парси', 'извлеки', 'scrape', 'extract']):
            match = IntentMatch(
                tool_name='web_scraper',
                confidence=0.8,
                mode=IntentMode.AUTO,
                extracted_params={'url': urls[0]},
                matched_patterns=['url_scraping_intent'],
                original_text=text
            )
            matches.append(match)
        
        # Если есть URL и ключевые слова API
        elif any(word in text_lower for word in ['api', 'запрос', 'request']):
            match = IntentMatch(
                tool_name='api_client',
                confidence=0.7,
                mode=IntentMode.AUTO,
                extracted_params={'url': urls[0], 'method': 'GET'},
                matched_patterns=['url_api_intent'],
                original_text=text
            )
            matches.append(match)
    
    def _add_file_based_matches(self, text: str, matches: List[IntentMatch]) -> None:
        """Добавляет намерения на основе найденных файловых путей"""
        file_path = None
        for pattern in self._file_patterns:
            match = pattern.search(text)
            if match:
                file_path = match.group(0)
                break
        
        if not file_path:
            return
        
        text_lower = text.lower()
        
        # Определяем операцию с файлом
        operation = 'read'  # по умолчанию
        if any(word in text_lower for word in ['создай', 'запиши', 'create', 'write']):
            operation = 'write'
        elif any(word in text_lower for word in ['список', 'list', 'ls', 'dir']):
            operation = 'list'
        
        match = IntentMatch(
            tool_name='file_operations',
            confidence=0.75,
            mode=IntentMode.AUTO,
            extracted_params={'path': file_path, 'operation': operation},
            matched_patterns=['file_path_intent'],
            original_text=text
        )
        matches.append(match)
    
    def get_best_match(self, text: str, forced_tool: Optional[str] = None, min_confidence: float = 0.5) -> Optional[IntentMatch]:
        """
        Возвращает лучшее совпадение намерения.
        
        Args:
            text (str): Текст для анализа
            forced_tool (Optional[str]): Принудительно выбранный инструмент
            min_confidence (float): Минимальная уверенность
            
        Returns:
            Optional[IntentMatch]: Лучшее совпадение или None
        """
        matches = self.parse_intent(text, forced_tool)
        if not matches:
            return None
        
        best_match = matches[0]
        if best_match.confidence >= min_confidence:
            return best_match
        
        return None
    
    def suggest_tools(self, text: str, max_suggestions: int = 3) -> List[IntentMatch]:
        """
        Предлагает инструменты для текста без автоматического выполнения.
        
        Args:
            text (str): Текст для анализа
            max_suggestions (int): Максимум предложений
            
        Returns:
            List[IntentMatch]: Список предложений
        """
        matches = self.parse_intent(text)
        suggestions = []
        
        for match in matches[:max_suggestions]:
            suggestion = IntentMatch(
                tool_name=match.tool_name,
                confidence=match.confidence,
                mode=IntentMode.SUGGESTED,
                extracted_params=match.extracted_params,
                matched_patterns=match.matched_patterns,
                original_text=match.original_text
            )
            suggestions.append(suggestion)
        
        return suggestions


# Глобальный экземпляр парсера намерений
_intent_parser = None

def get_intent_parser() -> IntentParser:
    """
    Возвращает глобальный экземпляр парсера намерений.
    
    Returns:
        IntentParser: Экземпляр парсера
    """
    global _intent_parser
    if _intent_parser is None:
        _intent_parser = IntentParser()
    return _intent_parser
