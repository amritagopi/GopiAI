#!/usr/bin/env python3
"""
🔍 Простая проверка доступности CrewAI Toolkit инструментов
Без выполнения - только импорт и базовая информация
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
project_root = Path(__file__).parent
    # Инициализируем пути проекта
    path_manager = setup_project_paths()
    # Инициализируем пути проекта
    path_manager = setup_project_paths()

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

def check_tool_availability():
    """Простая проверка доступности инструментов"""
    
    # Список инструментов для проверки (приоритетные)
    tools_to_check = [
        # Файловые операции - должны работать без API ключей
        ('FileReadTool', 'tools.crewai_toolkit.tools.file_read_tool.file_read_tool'),
        ('FileWriterTool', 'tools.crewai_toolkit.tools.file_writer_tool.file_writer_tool'),
        ('DirectoryReadTool', 'tools.crewai_toolkit.tools.directory_read_tool.directory_read_tool'),
        
        # Веб-скрапинг - простые инструменты
        ('ScrapeWebsiteTool', 'tools.crewai_toolkit.tools.scrape_website_tool.scrape_website_tool'),
        
        # Поиск - требуют API ключи
        ('BraveSearchTool', 'tools.crewai_toolkit.tools.brave_search_tool.brave_search_tool'),
        ('SerperDevTool', 'tools.crewai_toolkit.tools.serper_dev_tool.serper_dev_tool'),
        
        # Поиск в файлах
        ('CSVSearchTool', 'tools.crewai_toolkit.tools.csv_search_tool.csv_search_tool'),
        ('JSONSearchTool', 'tools.crewai_toolkit.tools.json_search_tool.json_search_tool'),
        
        # Selenium
        ('SeleniumScrapingTool', 'tools.crewai_toolkit.tools.selenium_scraping_tool.selenium_scraping_tool'),
    ]
    
    print("🔍 Проверка доступности CrewAI Toolkit инструментов...")
    print("=" * 60)
    
    results = {
        'available': [],
        'import_failed': [],
        'class_not_found': []
    }
    
    for class_name, module_path in tools_to_check:
        print(f"\n🔧 Проверяем {class_name}...")
        
        try:
            # Пробуем импортировать модуль
            module = __import__(module_path, fromlist=[class_name])
            
            # Пробуем получить класс
            if hasattr(module, class_name):
                tool_class = getattr(module, class_name)
                print(f"   ✅ Импорт успешен")
                
                # Пробуем создать экземпляр (безопасно)
                try:
                    instance = tool_class()
                    name = getattr(instance, 'name', 'Unknown')
                    description = getattr(instance, 'description', 'No description')
                    
                    results['available'].append({
                        'class_name': class_name,
                        'module_path': module_path,
                        'name': name,
                        'description': description[:100] + '...' if len(description) > 100 else description
                    })
                    
                    print(f"   ✅ Экземпляр создан: {name}")
                    
                except Exception as e:
                    print(f"   ⚠️ Ошибка создания экземпляра: {e}")
                    results['available'].append({
                        'class_name': class_name,
                        'module_path': module_path,
                        'name': class_name,
                        'description': f'Import OK, creation failed: {e}',
                        'creation_error': str(e)
                    })
                    
            else:
                print(f"   ❌ Класс {class_name} не найден в модуле")
                results['class_not_found'].append({
                    'class_name': class_name,
                    'module_path': module_path,
                    'error': f'Class {class_name} not found'
                })
                
        except ImportError as e:
            print(f"   ❌ Ошибка импорта: {e}")
            results['import_failed'].append({
                'class_name': class_name,
                'module_path': module_path,
                'error': str(e)
            })
        except Exception as e:
            print(f"   ❌ Неизвестная ошибка: {e}")
            results['import_failed'].append({
                'class_name': class_name,
                'module_path': module_path,
                'error': str(e)
            })
    
    return results

def print_summary(results):
    """Печатаем сводку результатов"""
    print("\n" + "=" * 60)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ:")
    print("=" * 60)
    
    available = results['available']
    import_failed = results['import_failed']
    class_not_found = results['class_not_found']
    
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   ✅ Доступно: {len(available)}")
    print(f"   ❌ Ошибки импорта: {len(import_failed)}")
    print(f"   ❌ Класс не найден: {len(class_not_found)}")
    
    if available:
        print(f"\n✅ ДОСТУПНЫЕ ИНСТРУМЕНТЫ ({len(available)}):")
        for tool in available:
            print(f"   • {tool['name']} ({tool['class_name']})")
            if 'creation_error' in tool:
                print(f"     ⚠️ Проблема создания: {tool['creation_error']}")
            else:
                print(f"     📝 {tool['description']}")
    
    if import_failed:
        print(f"\n❌ ОШИБКИ ИМПОРТА ({len(import_failed)}):")
        for tool in import_failed:
            print(f"   • {tool['class_name']}: {tool['error']}")
    
    if class_not_found:
        print(f"\n❌ КЛАССЫ НЕ НАЙДЕНЫ ({len(class_not_found)}):")
        for tool in class_not_found:
            print(f"   • {tool['class_name']}: {tool['error']}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if available:
        working_tools = [t for t in available if 'creation_error' not in t]
        problematic_tools = [t for t in available if 'creation_error' in t]
        
        if working_tools:
            print(f"   🚀 {len(working_tools)} инструментов готовы к интеграции")
        
        if problematic_tools:
            print(f"   🔧 {len(problematic_tools)} инструментов нуждаются в альтернативах")
            print("      Используем шаблон GitHub Integration Tool")
    
    if import_failed or class_not_found:
        failed_count = len(import_failed) + len(class_not_found)
        print(f"   🛠️ {failed_count} инструментов требуют исправления путей импорта")

def check_api_keys():
    """Проверяем наличие API ключей"""
    print(f"\n🔑 ПРОВЕРКА API КЛЮЧЕЙ:")
    
    keys_to_check = [
        'GITHUB_TOKEN',
        'OPENAI_API_KEY', 
        'OPENROUTER_API_KEY',
        'BRAVE_API_KEY',
        'SERPER_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    available_keys = []
    missing_keys = []
    
    for key in keys_to_check:
        value = os.getenv(key)
        if value and value != f'your_{key.lower()}_here' and len(value) > 10:
            available_keys.append(key)
            print(f"   ✅ {key}: Доступен")
        else:
            missing_keys.append(key)
            print(f"   ❌ {key}: Отсутствует")
    
    print(f"\n   📊 Доступно: {len(available_keys)}, Отсутствует: {len(missing_keys)}")
    
    return {
        'available': available_keys,
        'missing': missing_keys
    }

if __name__ == "__main__":
    # Проверяем API ключи
    api_keys = check_api_keys()
    
    # Проверяем инструменты
    results = check_tool_availability()
    
    # Печатаем сводку
    print_summary(results)
    
    print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("   1. Исправить пути импорта для неработающих инструментов")
    print("   2. Создать альтернативы для проблемных инструментов")
    print("   3. Интегрировать рабочие инструменты в SmartDelegator")
    print("   4. Добавить недостающие API ключи для поисковых инструментов")