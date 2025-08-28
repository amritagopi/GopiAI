#!/usr/bin/env python3
"""
🚀 Тестирование официальных crewai-tools инструментов
Используем официальный пакет вместо локальных копий
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Добавляем пути для импорта
project_root = Path(__file__).parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

class OfficialCrewAIToolsTester:
    """Тестер официальных crewai-tools инструментов"""
    
    def __init__(self):
        self.results = {}
        
        # Приоритетные инструменты из официального пакета
        self.priority_tools = [
            # Файловые операции - должны работать без API ключей
            {
                'name': 'FileReadTool',
                'import_path': 'crewai_tools',
                'category': 'file_operations',
                'api_keys': [],
                'test_params': {'file_path': str(__file__)}
            },
            {
                'name': 'DirectoryReadTool', 
                'import_path': 'crewai_tools',
                'category': 'file_operations',
                'api_keys': [],
                'test_params': {'directory_path': str(project_root)}
            },
            
            # Веб-скрапинг - простые инструменты
            {
                'name': 'ScrapeWebsiteTool',
                'import_path': 'crewai_tools',
                'category': 'web_scraping',
                'api_keys': [],
                'test_params': {'website_url': 'https://example.com'}
            },
            
            # Поиск - требуют API ключи
            {
                'name': 'SerperDevTool',
                'import_path': 'crewai_tools',
                'category': 'web_search',
                'api_keys': ['SERPER_API_KEY'],
                'test_params': {'query': 'artificial intelligence'}
            },
            
            # CSV/JSON инструменты
            {
                'name': 'CSVSearchTool',
                'import_path': 'crewai_tools',
                'category': 'file_search',
                'api_keys': [],
                'test_params': {}  # Требует файл
            },
            {
                'name': 'JSONSearchTool',
                'import_path': 'crewai_tools', 
                'category': 'file_search',
                'api_keys': [],
                'test_params': {}  # Требует файл
            },
            
            # Selenium
            {
                'name': 'SeleniumScrapingTool',
                'import_path': 'crewai_tools',
                'category': 'web_scraping',
                'api_keys': [],
                'test_params': {'website_url': 'https://example.com'}
            },
            
            # Дополнительные полезные инструменты
            {
                'name': 'WebsiteSearchTool',
                'import_path': 'crewai_tools',
                'category': 'web_search',
                'api_keys': [],
                'test_params': {'website': 'https://example.com'}
            },
            {
                'name': 'YoutubeChannelSearchTool',
                'import_path': 'crewai_tools',
                'category': 'media_search',
                'api_keys': [],
                'test_params': {'youtube_channel_handle': '@python'}
            },
            {
                'name': 'YoutubeVideoSearchTool',
                'import_path': 'crewai_tools',
                'category': 'media_search', 
                'api_keys': [],
                'test_params': {'youtube_video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
            }
        ]
    
    def check_api_keys(self, tool_info: Dict) -> Dict[str, Any]:
        """Проверяем наличие необходимых API ключей"""
        missing_keys = []
        available_keys = []
        
        for key in tool_info['api_keys']:
            value = os.getenv(key)
            if value and value != f'your_{key.lower()}_here' and len(value) > 5:
                available_keys.append(key)
            else:
                missing_keys.append(key)
        
        return {
            'has_all_keys': len(missing_keys) == 0,
            'available_keys': available_keys,
            'missing_keys': missing_keys
        }
    
    def test_tool_import_and_creation(self, tool_info: Dict) -> Dict[str, Any]:
        """Тестируем импорт и создание официального инструмента"""
        try:
            # Импортируем из официального пакета
            import crewai_tools
            
            # Проверяем наличие класса
            if not hasattr(crewai_tools, tool_info['name']):
                return {
                    'success': False,
                    'error': f"Tool {tool_info['name']} not found in crewai_tools",
                    'error_type': 'tool_not_found'
                }
            
            # Получаем класс
            tool_class = getattr(crewai_tools, tool_info['name'])
            
            # Пробуем создать экземпляр
            tool_instance = tool_class()
            
            # Получаем информацию об инструменте
            name = getattr(tool_instance, 'name', tool_info['name'])
            description = getattr(tool_instance, 'description', 'No description available')
            
            # Проверяем наличие методов выполнения
            has_run = hasattr(tool_instance, '_run')
            has_run_method = hasattr(tool_instance, 'run')
            
            return {
                'success': True,
                'tool_class': tool_class,
                'tool_instance': tool_instance,
                'name': name,
                'description': description[:150] + '...' if len(description) > 150 else description,
                'has_run_method': has_run or has_run_method,
                'methods': [method for method in dir(tool_instance) if not method.startswith('_')]
            }
            
        except ImportError as e:
            return {
                'success': False,
                'error': f'ImportError: {e}',
                'error_type': 'import_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Creation error: {e}',
                'error_type': 'creation_error'
            }
    
    def test_single_tool(self, tool_info: Dict) -> Dict[str, Any]:
        """Полное тестирование одного официального инструмента"""
        print(f"\n🔧 Тестирование {tool_info['name']}...")
        
        result = {
            'name': tool_info['name'],
            'category': tool_info['category'],
            'import_path': tool_info['import_path']
        }
        
        # Шаг 1: Проверка API ключей
        api_check = self.check_api_keys(tool_info)
        result['api_keys'] = api_check
        
        if tool_info['api_keys'] and not api_check['has_all_keys']:
            print(f"   🔑 Отсутствуют API ключи: {api_check['missing_keys']}")
            result['status'] = 'missing_api_keys'
            result['ready_for_integration'] = False
            return result
        
        # Шаг 2: Тестирование импорта и создания
        import_result = self.test_tool_import_and_creation(tool_info)
        result.update(import_result)
        
        if not import_result['success']:
            print(f"   ❌ {import_result['error']}")
            result['status'] = 'failed'
            result['ready_for_integration'] = False
            return result
        
        print(f"   ✅ Импорт и создание успешны")
        print(f"   📝 Название: {import_result['name']}")
        print(f"   📄 Описание: {import_result['description']}")
        print(f"   🔧 Методы выполнения: {'Да' if import_result['has_run_method'] else 'Нет'}")
        
        result['status'] = 'ready'
        result['ready_for_integration'] = True
        
        return result
    
    def test_all_priority_tools(self):
        """Тестируем все приоритетные официальные инструменты"""
        print("🚀 Тестирование официальных crewai-tools инструментов...")
        print("=" * 70)
        
        for tool_info in self.priority_tools:
            result = self.test_single_tool(tool_info)
            self.results[tool_info['name']] = result
        
        self.print_summary()
    
    def print_summary(self):
        """Печатаем сводку результатов"""
        print("\n" + "=" * 70)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ОФИЦИАЛЬНЫХ CREWAI-TOOLS:")
        print("=" * 70)
        
        categories = {}
        status_counts = {
            'ready': 0,
            'missing_api_keys': 0,
            'failed': 0
        }
        
        for tool_name, result in self.results.items():
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
            
            status = result['status']
            if status in status_counts:
                status_counts[status] += 1
        
        # Статистика по статусам
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   ✅ Готовы к интеграции: {status_counts['ready']}")
        print(f"   🔑 Нужны API ключи: {status_counts['missing_api_keys']}")
        print(f"   ❌ Ошибки: {status_counts['failed']}")
        
        # Детали по категориям
        print(f"\n📂 ПО КАТЕГОРИЯМ:")
        for category, tools in categories.items():
            print(f"\n   📁 {category.upper()}:")
            for tool in tools:
                status_emoji = {
                    'ready': '✅',
                    'missing_api_keys': '🔑',
                    'failed': '❌'
                }.get(tool['status'], '❓')
                
                print(f"      {status_emoji} {tool['name']}")
                if tool['status'] == 'missing_api_keys':
                    missing = tool['api_keys']['missing_keys']
                    print(f"         🔑 Нужны ключи: {', '.join(missing)}")
                elif tool['status'] == 'failed':
                    print(f"         ❌ Ошибка: {tool.get('error', 'Unknown error')}")
        
        # Готовые к интеграции
        ready_tools = [t for t in self.results.values() if t['status'] == 'ready']
        if ready_tools:
            print(f"\n🚀 ГОТОВЫ К ИНТЕГРАЦИИ ({len(ready_tools)}):")
            for tool in ready_tools:
                print(f"   • {tool['name']} ({tool['category']})")
        
        # Рекомендации
        print(f"\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        if ready_tools:
            print(f"   1. Интегрировать {len(ready_tools)} готовых инструментов в SmartDelegator")
            print("   2. Использовать официальные crewai-tools вместо локальных копий")
        
        missing_keys_tools = [t for t in self.results.values() if t['status'] == 'missing_api_keys']
        if missing_keys_tools:
            print(f"   3. Добавить недостающие API ключи для {len(missing_keys_tools)} инструментов")
        
        print("   4. Обновить CrewAI Tools Integrator для использования официальных инструментов")

if __name__ == "__main__":
    tester = OfficialCrewAIToolsTester()
    tester.test_all_priority_tools()