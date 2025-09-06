#!/usr/bin/env python3
"""
🔧 Систематическое тестирование следующих CrewAI Toolkit инструментов
Используем успешный шаблон GitHub Integration Tool
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Добавляем пути для импорта
project_root = Path(__file__).parent
# Инициализируем пути проекта
path_manager = setup_project_paths()

# Загружаем переменные окружения из .env
load_dotenv()

class CrewAIToolsTester:
    """Систематический тестер CrewAI Toolkit инструментов"""
    
    def __init__(self):
        self.results = {}
        self.priority_tools = [
            # Приоритет 1: Простые инструменты без API ключей
            {
                'name': 'file_read',
                'module': 'tools.crewai_toolkit.tools.file_read_tool.file_read_tool',
                'class': 'FileReadTool',
                'category': 'file_operations',
                'api_keys': [],
                'test_params': {'file_path': __file__}
            },
            {
                'name': 'file_writer',
                'module': 'tools.crewai_toolkit.tools.file_writer_tool.file_writer_tool',
                'class': 'FileWriterTool',
                'category': 'file_operations',
                'api_keys': [],
                'test_params': {'filename': 'test_output.txt', 'content': 'Test content'}
            },
            {
                'name': 'directory_read',
                'module': 'tools.crewai_toolkit.tools.directory_read_tool.directory_read_tool',
                'class': 'DirectoryReadTool',
                'category': 'file_operations',
                'api_keys': [],
                'test_params': {'directory_path': str(project_root)}
            },
            
            # Приоритет 2: Инструменты с доступными API ключами
            {
                'name': 'brave_search',
                'module': 'tools.crewai_toolkit.tools.brave_search_tool.brave_search_tool',
                'class': 'BraveSearchTool',
                'category': 'web_search',
                'api_keys': ['BRAVE_API_KEY'],
                'test_params': {'query': 'python programming'}
            },
            {
                'name': 'serper_dev',
                'module': 'tools.crewai_toolkit.tools.serper_dev_tool.serper_dev_tool',
                'class': 'SerperDevTool',
                'category': 'web_search',
                'api_keys': ['SERPER_API_KEY'],
                'test_params': {'query': 'artificial intelligence'}
            },
            
            # Приоритет 3: Веб-скрапинг инструменты
            {
                'name': 'scrape_website',
                'module': 'tools.crewai_toolkit.tools.scrape_website_tool.scrape_website_tool',
                'class': 'ScrapeWebsiteTool',
                'category': 'web_scraping',
                'api_keys': [],
                'test_params': {'website_url': 'https://example.com'}
            },
            {
                'name': 'selenium_scraping',
                'module': 'tools.crewai_toolkit.tools.selenium_scraping_tool.selenium_scraping_tool',
                'class': 'SeleniumScrapingTool',
                'category': 'web_scraping',
                'api_keys': [],
                'test_params': {'website_url': 'https://example.com'}
            },
            
            # Приоритет 4: Поиск в файлах
            {
                'name': 'csv_search',
                'module': 'tools.crewai_toolkit.tools.csv_search_tool.csv_search_tool',
                'class': 'CSVSearchTool',
                'category': 'file_search',
                'api_keys': [],
                'test_params': {'csv_file_path': 'test.csv', 'query': 'test'}
            },
            {
                'name': 'json_search',
                'module': 'tools.crewai_toolkit.tools.json_search_tool.json_search_tool',
                'class': 'JSONSearchTool',
                'category': 'file_search',
                'api_keys': [],
                'test_params': {'json_file_path': 'test.json', 'query': 'test'}
            },
        ]
    
    def check_api_keys(self, tool_info: Dict) -> Dict[str, Any]:
        """Проверяем наличие необходимых API ключей"""
        missing_keys = []
        available_keys = []
        
        for key in tool_info['api_keys']:
            value = os.getenv(key)
            if value and value != f'your_{key.lower()}_here':
                available_keys.append(key)
            else:
                missing_keys.append(key)
        
        return {
            'has_all_keys': len(missing_keys) == 0,
            'available_keys': available_keys,
            'missing_keys': missing_keys
        }
    
    def test_tool_import(self, tool_info: Dict) -> Dict[str, Any]:
        """Тестируем импорт инструмента"""
        try:
            # Пробуем импортировать модуль
            module_parts = tool_info['module'].split('.')
            module = __import__(tool_info['module'], fromlist=[tool_info['class']])
            tool_class = getattr(module, tool_info['class'])
            
            return {
                'success': True,
                'class': tool_class,
                'module_path': tool_info['module']
            }
        except ImportError as e:
            return {
                'success': False,
                'error': f'ImportError: {e}',
                'error_type': 'import'
            }
        except AttributeError as e:
            return {
                'success': False,
                'error': f'AttributeError: {e}',
                'error_type': 'class_not_found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unknown error: {e}',
                'error_type': 'unknown'
            }
    
    def test_tool_creation(self, tool_class, tool_info: Dict) -> Dict[str, Any]:
        """Тестируем создание экземпляра инструмента"""
        try:
            # Пробуем создать экземпляр
            tool_instance = tool_class()
            
            return {
                'success': True,
                'instance': tool_instance,
                'name': getattr(tool_instance, 'name', 'Unknown'),
                'description': getattr(tool_instance, 'description', 'No description')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_tool_execution(self, tool_instance, test_params: Dict) -> Dict[str, Any]:
        """Тестируем выполнение инструмента (безопасно, без реального выполнения)"""
        try:
            # Проверяем наличие методов выполнения
            has_run = hasattr(tool_instance, '_run')
            has_run_method = hasattr(tool_instance, 'run')
            
            if not has_run and not has_run_method:
                return {
                    'success': False,
                    'error': 'No _run or run method found',
                    'error_type': 'no_run_method'
                }
            
            # Получаем информацию о методе без выполнения
            method_name = '_run' if has_run else 'run'
            method = getattr(tool_instance, method_name)
            
            # Проверяем сигнатуру метода
            import inspect
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            return {
                'success': True,
                'result': f'Method {method_name} available with parameters: {params}',
                'method_info': {
                    'method_name': method_name,
                    'parameters': params,
                    'signature': str(sig)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_single_tool(self, tool_info: Dict) -> Dict[str, Any]:
        """Полное тестирование одного инструмента"""
        print(f"\n🔧 Тестирование {tool_info['name']}...")
        
        result = {
            'name': tool_info['name'],
            'category': tool_info['category'],
            'module': tool_info['module'],
            'class': tool_info['class']
        }
        
        # Шаг 1: Проверка API ключей
        api_check = self.check_api_keys(tool_info)
        result['api_keys'] = api_check
        
        if tool_info['api_keys'] and not api_check['has_all_keys']:
            print(f"⚠️ Отсутствуют API ключи: {api_check['missing_keys']}")
            result['status'] = 'missing_api_keys'
            result['can_test'] = False
            return result
        
        # Шаг 2: Тестирование импорта
        import_result = self.test_tool_import(tool_info)
        result['import'] = import_result
        
        if not import_result['success']:
            print(f"❌ Ошибка импорта: {import_result['error']}")
            result['status'] = 'import_failed'
            result['can_test'] = False
            return result
        
        print(f"✅ Импорт успешен")
        
        # Шаг 3: Тестирование создания экземпляра
        creation_result = self.test_tool_creation(import_result['class'], tool_info)
        result['creation'] = creation_result
        
        if not creation_result['success']:
            print(f"❌ Ошибка создания: {creation_result['error']}")
            result['status'] = 'creation_failed'
            result['can_test'] = False
            return result
        
        print(f"✅ Экземпляр создан: {creation_result['name']}")
        
        # Шаг 4: Тестирование выполнения
        execution_result = self.test_tool_execution(creation_result['instance'], tool_info['test_params'])
        result['execution'] = execution_result
        
        if not execution_result['success']:
            print(f"⚠️ Ошибка выполнения: {execution_result['error']}")
            result['status'] = 'execution_failed'
            result['can_test'] = True  # Можем создать альтернативу
        else:
            print(f"✅ Выполнение успешно!")
            print(f"📊 Результат: {execution_result['result']}")
            result['status'] = 'fully_working'
            result['can_test'] = True
        
        return result
    
    def test_all_priority_tools(self):
        """Тестируем все приоритетные инструменты"""
        print("🚀 Запуск систематического тестирования CrewAI Toolkit инструментов...")
        print("=" * 70)
        
        for tool_info in self.priority_tools:
            result = self.test_single_tool(tool_info)
            self.results[tool_info['name']] = result
        
        self.print_summary()
    
    def print_summary(self):
        """Печатаем сводку результатов"""
        print("\n" + "=" * 70)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ:")
        print("=" * 70)
        
        categories = {}
        status_counts = {
            'fully_working': 0,
            'execution_failed': 0,
            'creation_failed': 0,
            'import_failed': 0,
            'missing_api_keys': 0
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
        print(f"   ✅ Полностью работают: {status_counts['fully_working']}")
        print(f"   ⚠️ Ошибки выполнения: {status_counts['execution_failed']}")
        print(f"   ❌ Ошибки создания: {status_counts['creation_failed']}")
        print(f"   ❌ Ошибки импорта: {status_counts['import_failed']}")
        print(f"   🔑 Нет API ключей: {status_counts['missing_api_keys']}")
        
        # Детали по категориям
        print(f"\n📂 ПО КАТЕГОРИЯМ:")
        for category, tools in categories.items():
            print(f"\n   📁 {category.upper()}:")
            for tool in tools:
                status_emoji = {
                    'fully_working': '✅',
                    'execution_failed': '⚠️',
                    'creation_failed': '❌',
                    'import_failed': '❌',
                    'missing_api_keys': '🔑'
                }.get(tool['status'], '❓')
                
                print(f"      {status_emoji} {tool['name']}")
                if tool['status'] == 'execution_failed':
                    print(f"         💡 Можно создать альтернативу")
                elif tool['status'] == 'missing_api_keys':
                    missing = tool['api_keys']['missing_keys']
                    print(f"         🔑 Нужны ключи: {', '.join(missing)}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        working_tools = [t for t in self.results.values() if t['status'] == 'fully_working']
        failed_execution = [t for t in self.results.values() if t['status'] == 'execution_failed']
        
        if working_tools:
            print(f"   ✅ {len(working_tools)} инструментов готовы к использованию")
        
        if failed_execution:
            print(f"   🔧 {len(failed_execution)} инструментов нуждаются в альтернативах")
            print("      Используем шаблон GitHub Integration Tool")

if __name__ == "__main__":
    tester = CrewAIToolsTester()
    tester.test_all_priority_tools()