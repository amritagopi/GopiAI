"""
🔧 Tool Aliases Manager
Централизованная система алиасов для всех инструментов GopiAI
Поддерживает старые названия, синонимы, вариации регистра
"""

import logging
from typing import Dict, Set, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class ToolAliasManager:
    """
    Менеджер алиасов инструментов.
    Нормализует любое название инструмента к каноническому виду.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._alias_map = self._build_alias_map()
        self._canonical_tools = set(self._alias_map.values())
        self.logger.info(f"✅ Инициализирован ToolAliasManager: {len(self._canonical_tools)} канонических инструментов, {len(self._alias_map)} алиасов")
    
    def _build_alias_map(self) -> Dict[str, str]:
        """
        Строит полную карту алиасов: alias -> canonical_name
        Включает все возможные вариации названий инструментов
        """
        alias_map = {}
        
        # 💻 ТЕРМИНАЛ И ВЫПОЛНЕНИЕ КОМАНД
        terminal_aliases = [
            'execute_shell', 'shell', 'terminal', 'cmd', 'command', 'exec', 'run',
            'bash', 'powershell', 'console', 'cli', 'execute_command', 'run_command',
            'shell_exec', 'terminal_exec', 'command_exec', 'system_command'
        ]
        for alias in terminal_aliases:
            alias_map[alias.lower()] = 'execute_shell'
        
        # 📁 ФАЙЛОВЫЕ ОПЕРАЦИИ
        file_aliases = [
            'file_operations', 'file_ops', 'files', 'filesystem', 'fs', 'file_system',
            'filesystem_tools', 'fs_tools', 'file_tools', 'file_manager', 'file_handler',
            'read_file', 'write_file', 'file_read', 'file_write', 'file_io',
            'directory', 'dir', 'folder', 'path', 'file_path'
        ]
        for alias in file_aliases:
            alias_map[alias.lower()] = 'file_operations'
        
        # 🌐 ВЕБ-СКРАПИНГ
        scraper_aliases = [
            'web_scraper', 'scraper', 'scrape', 'web_scrape', 'scraping', 'web_scraping',
            'html_scraper', 'page_scraper', 'website_scraper', 'url_scraper',
            'selenium_scraping', 'browser_scraper', 'extract_web', 'parse_web',
            'get_webpage', 'fetch_page', 'download_page'
        ]
        for alias in scraper_aliases:
            alias_map[alias.lower()] = 'web_scraper'
        
        # 🔍 ВЕБ-ПОИСК
        search_aliases = [
            'web_search', 'search', 'google_search', 'bing_search', 'brave_search',
            'tavily_search', 'serper_dev', 'internet_search', 'online_search',
            'search_web', 'find_online', 'query_web', 'web_query'
        ]
        for alias in search_aliases:
            alias_map[alias.lower()] = 'web_search'
        
        # 🔌 API КЛИЕНТ
        api_aliases = [
            'api_client', 'api', 'http_client', 'rest_client', 'http', 'rest',
            'api_call', 'http_request', 'web_request', 'url_request',
            'get_request', 'post_request', 'api_request', 'fetch_api'
        ]
        for alias in api_aliases:
            alias_map[alias.lower()] = 'api_client'
        
        # 🌍 URL АНАЛИЗАТОР
        url_aliases = [
            'url_analyzer', 'url_analysis', 'url_check', 'url_info', 'website_info',
            'site_analyzer', 'web_analyzer', 'link_analyzer', 'url_validator'
        ]
        for alias in url_aliases:
            alias_map[alias.lower()] = 'url_analyzer'
        
        # 🖱️ БРАУЗЕР АВТОМАТИЗАЦИЯ - УДАЛЕНО ИЗ ПРОЕКТА
        
        # 📊 CSV ПОИСК
        csv_aliases = [
            'csv_search', 'csv', 'csv_tool', 'csv_query', 'csv_find',
            'search_csv', 'csv_parser', 'csv_reader'
        ]
        for alias in csv_aliases:
            alias_map[alias.lower()] = 'csv_search'
        
        # 📋 JSON ПОИСК
        json_aliases = [
            'json_search', 'json', 'json_tool', 'json_query', 'json_find',
            'search_json', 'json_parser', 'json_reader'
        ]
        for alias in json_aliases:
            alias_map[alias.lower()] = 'json_search'
        
        # 📄 PDF ПОИСК
        pdf_aliases = [
            'pdf_search', 'pdf', 'pdf_tool', 'pdf_query', 'pdf_find',
            'search_pdf', 'pdf_parser', 'pdf_reader'
        ]
        for alias in pdf_aliases:
            alias_map[alias.lower()] = 'pdf_search'
        
        # 🐍 КОД ИНТЕРПРЕТАТОР
        code_aliases = [
            'code_interpreter', 'code', 'python', 'py', 'interpreter', 'exec_code',
            'run_code', 'execute_code', 'python_exec', 'code_exec', 'python_interpreter'
        ]
        for alias in code_aliases:
            alias_map[alias.lower()] = 'code_interpreter'
        
        # 🐙 GITHUB ПОИСК
        github_aliases = [
            'github_search', 'github', 'git_search', 'repo_search', 'repository_search',
            'github_tool', 'git_tool', 'github_query'
        ]
        for alias in github_aliases:
            alias_map[alias.lower()] = 'github_search'
        
        # 🎨 DALL-E ГЕНЕРАЦИЯ
        dalle_aliases = [
            'dalle_tool', 'dalle', 'image_generation', 'generate_image', 'create_image',
            'ai_image', 'image_gen', 'dalle3', 'dall_e', 'openai_image'
        ]
        for alias in dalle_aliases:
            alias_map[alias.lower()] = 'dalle_tool'
        
        # 👁️ АНАЛИЗ ИЗОБРАЖЕНИЙ
        vision_aliases = [
            'vision_tool', 'vision', 'image_analysis', 'analyze_image', 'image_analyzer',
            'image_recognition', 'visual_analysis', 'image_ai', 'computer_vision'
        ]
        for alias in vision_aliases:
            alias_map[alias.lower()] = 'vision_tool'
        
        # ℹ️ СИСТЕМНАЯ ИНФОРМАЦИЯ
        sysinfo_aliases = [
            'system_info', 'sysinfo', 'system', 'sys_info', 'os_info', 'system_status',
            'hardware_info', 'system_details', 'machine_info'
        ]
        for alias in sysinfo_aliases:
            alias_map[alias.lower()] = 'system_info'
        
        # ⚙️ МЕНЕДЖЕР ПРОЦЕССОВ
        process_aliases = [
            'process_manager', 'processes', 'process', 'proc', 'task_manager',
            'process_control', 'proc_manager', 'system_processes'
        ]
        for alias in process_aliases:
            alias_map[alias.lower()] = 'process_manager'
        
        # ⏰ ВРЕМЯ
        time_aliases = [
            'time_helper', 'time', 'datetime', 'timestamp', 'clock', 'date',
            'time_tool', 'time_utils', 'date_time'
        ]
        for alias in time_aliases:
            alias_map[alias.lower()] = 'time_helper'
        
        # 📦 ПРОЕКТ ХЕЛПЕР
        project_aliases = [
            'project_helper', 'project', 'health_check', 'status', 'project_status',
            'system_health', 'project_info', 'gopiai_status'
        ]
        for alias in project_aliases:
            alias_map[alias.lower()] = 'project_helper'
        
        # 🔧 ДОПОЛНИТЕЛЬНЫЕ CrewAI ИНСТРУМЕНТЫ
        # FileWriteTool
        filewrite_aliases = [
            'file_writer', 'write_file', 'create_file', 'save_file', 'file_write'
        ]
        for alias in filewrite_aliases:
            alias_map[alias.lower()] = 'file_writer'
        
        # DirectorySearchTool
        dirsearch_aliases = [
            'directory_search', 'dir_search', 'folder_search', 'search_directory',
            'find_files', 'search_files'
        ]
        for alias in dirsearch_aliases:
            alias_map[alias.lower()] = 'directory_search'
        
        # TXTSearchTool
        txtsearch_aliases = [
            'txt_search', 'text_search', 'search_text', 'find_text', 'grep'
        ]
        for alias in txtsearch_aliases:
            alias_map[alias.lower()] = 'txt_search'
        
        # MDXSearchTool
        mdx_aliases = [
            'mdx_search', 'markdown_search', 'md_search', 'search_markdown'
        ]
        for alias in mdx_aliases:
            alias_map[alias.lower()] = 'mdx_search'
        
        # DOCXSearchTool
        docx_aliases = [
            'docx_search', 'word_search', 'doc_search', 'search_word'
        ]
        for alias in docx_aliases:
            alias_map[alias.lower()] = 'docx_search'
        
        # XMLSearchTool
        xml_aliases = [
            'xml_search', 'search_xml', 'xml_parser', 'xml_query'
        ]
        for alias in xml_aliases:
            alias_map[alias.lower()] = 'xml_search'
        
        # YoutubeChannelSearchTool
        youtube_aliases = [
            'youtube_channel_search', 'youtube_search', 'yt_search', 'youtube'
        ]
        for alias in youtube_aliases:
            alias_map[alias.lower()] = 'youtube_channel_search'
        
        # YoutubeVideoSearchTool
        ytvideo_aliases = [
            'youtube_video_search', 'youtube_video', 'yt_video', 'video_search'
        ]
        for alias in ytvideo_aliases:
            alias_map[alias.lower()] = 'youtube_video_search'
        
        # ScrapeWebsiteTool
        scrape_aliases = [
            'scrape_website', 'website_scraper', 'site_scraper'
        ]
        for alias in scrape_aliases:
            alias_map[alias.lower()] = 'scrape_website'
        
        return alias_map
    
    def normalize_tool_name(self, tool_name: str) -> Optional[str]:
        """
        Нормализует название инструмента к каноническому виду.
        
        Args:
            tool_name (str): Исходное название инструмента
            
        Returns:
            Optional[str]: Каноническое название или None если не найдено
        """
        if not tool_name or not isinstance(tool_name, str):
            return None
        
        # Приводим к нижнему регистру и убираем лишние пробелы
        normalized = tool_name.strip().lower()
        
        # Убираем подчеркивания и дефисы для более гибкого поиска
        variants = [
            normalized,
            normalized.replace('_', ''),
            normalized.replace('-', ''),
            normalized.replace('_', '-'),
            normalized.replace('-', '_')
        ]
        
        # Ищем точное совпадение
        for variant in variants:
            if variant in self._alias_map:
                canonical = self._alias_map[variant]
                if normalized != variant:
                    self.logger.debug(f"🔄 Нормализация: '{tool_name}' -> '{canonical}' (через вариант '{variant}')")
                else:
                    self.logger.debug(f"🔄 Нормализация: '{tool_name}' -> '{canonical}'")
                return canonical
        
        # Если точного совпадения нет, ищем частичное
        for alias, canonical in self._alias_map.items():
            if normalized in alias or alias in normalized:
                self.logger.debug(f"🔄 Частичная нормализация: '{tool_name}' -> '{canonical}' (через '{alias}')")
                return canonical
        
        self.logger.warning(f"⚠️ Не удалось нормализовать инструмент: '{tool_name}'")
        return None
    
    def get_all_aliases(self, canonical_name: str) -> List[str]:
        """
        Возвращает все алиасы для канонического названия инструмента.
        
        Args:
            canonical_name (str): Каноническое название
            
        Returns:
            List[str]: Список всех алиасов
        """
        aliases = []
        for alias, canonical in self._alias_map.items():
            if canonical == canonical_name:
                aliases.append(alias)
        return sorted(aliases)
    
    def get_canonical_tools(self) -> Set[str]:
        """
        Возвращает множество всех канонических названий инструментов.
        
        Returns:
            Set[str]: Множество канонических названий
        """
        return self._canonical_tools.copy()
    
    def is_valid_tool(self, tool_name: str) -> bool:
        """
        Проверяет, является ли название инструмента валидным (есть ли алиас).
        
        Args:
            tool_name (str): Название инструмента
            
        Returns:
            bool: True если инструмент валидный
        """
        return self.normalize_tool_name(tool_name) is not None
    
    def get_suggestions(self, tool_name: str, max_suggestions: int = 5) -> List[str]:
        """
        Возвращает предложения похожих инструментов для неизвестного названия.
        
        Args:
            tool_name (str): Неизвестное название
            max_suggestions (int): Максимум предложений
            
        Returns:
            List[str]: Список предложений
        """
        if not tool_name:
            return []
        
        normalized = tool_name.strip().lower()
        suggestions = []
        
        # Ищем частичные совпадения
        for alias in self._alias_map.keys():
            if normalized in alias or alias in normalized:
                canonical = self._alias_map[alias]
                if canonical not in suggestions:
                    suggestions.append(canonical)
        
        # Ищем по расстоянию Левенштейна (простая версия)
        if len(suggestions) < max_suggestions:
            for canonical in self._canonical_tools:
                if canonical not in suggestions:
                    # Простая метрика похожести
                    if self._similarity_score(normalized, canonical) > 0.5:
                        suggestions.append(canonical)
        
        return suggestions[:max_suggestions]
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """
        Простая метрика похожести строк.
        
        Args:
            s1, s2 (str): Строки для сравнения
            
        Returns:
            float: Оценка похожести от 0 до 1
        """
        if not s1 or not s2:
            return 0.0
        
        # Простая метрика на основе общих символов
        common_chars = set(s1) & set(s2)
        total_chars = set(s1) | set(s2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)


# Глобальный экземпляр менеджера алиасов
_alias_manager = None

def get_tool_alias_manager() -> ToolAliasManager:
    """
    Возвращает глобальный экземпляр менеджера алиасов.
    
    Returns:
        ToolAliasManager: Экземпляр менеджера
    """
    global _alias_manager
    if _alias_manager is None:
        _alias_manager = ToolAliasManager()
    return _alias_manager
