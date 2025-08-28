#!/usr/bin/env python3
"""
🧪 Тестирование основных инструментов GopiAI
Простой скрипт для проверки работоспособности инструментов
"""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_filesystem_tool():
    """Тестирование файловой системы"""
    print("\n🔧 Тестирование GopiAIFileSystemTool...")
    
    try:
        from filesystem_tools import GopiAIFileSystemTool
        
        tool = GopiAIFileSystemTool()
        
        # Тест создания временного файла
        test_content = "Это тестовый файл для проверки GopiAI инструментов"
        result = tool._run(action="write", path="test_file.txt", data=test_content)
        print(f"✅ Создание файла: {result}")
        
        # Тест чтения файла
        result = tool._run(action="read", path="test_file.txt")
        print(f"✅ Чтение файла: {result[:100]}...")
        
        # Тест удаления файла
        result = tool._run(action="delete", path="test_file.txt")
        print(f"✅ Удаление файла: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования файловой системы: {e}")
        return False

def test_terminal_tool():
    """Тестирование терминала"""
    print("\n🔧 Тестирование TerminalTool...")
    
    try:
        from terminal_tool import TerminalTool
        
        tool = TerminalTool()
        
        # Тест простой команды
        if os.name == 'nt':  # Windows
            result = tool._run(command="dir")
        else:  # Unix/Linux
            result = tool._run(command="ls")
        
        print(f"✅ Выполнение команды: {str(result)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования терминала: {e}")
        return False

def test_web_search_tool():
    """Тестирование поиска в интернете"""
    print("\n🔧 Тестирование GopiAIWebSearchTool...")
    
    try:
        from web_search_tool import GopiAIWebSearchTool
        
        tool = GopiAIWebSearchTool()
        
        # Тест поиска
        result = tool._run(query="Python programming", num_results=3)
        print(f"✅ Поиск в интернете: {result[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования поиска: {e}")
        return False

def test_web_viewer_tool():
    """Тестирование просмотра веб-страниц"""
    print("\n🔧 Тестирование GopiAIWebViewerTool...")
    
    try:
        from web_viewer_tool import GopiAIWebViewerTool
        
        tool = GopiAIWebViewerTool()
        
        # Тест загрузки страницы
        result = tool._run(action="get_title", url="https://httpbin.org/html")
        print(f"✅ Получение заголовка: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования просмотра веб-страниц: {e}")
        return False

def test_imports():
    """Тестирование импортов"""
    print("\n🔧 Тестирование импортов...")
    
    try:
        # Тест импорта основных инструментов
        from filesystem_tools import GopiAIFileSystemTool
        from terminal_tool import TerminalTool
        from web_search_tool import GopiAIWebSearchTool
        from web_viewer_tool import GopiAIWebViewerTool
        
        print("✅ Все основные инструменты импортированы успешно")
        
        # Тест импорта из __init__.py
        try:
            from . import get_essential_tools, get_active_tools_info, TOOLS_INFO
            print("✅ Импорт из __init__.py успешен")
            
            # Показать информацию об активных инструментах
            active_tools = get_active_tools_info()
            print(f"✅ Активных инструментов: {len(active_tools)}")
            for name, info in active_tools.items():
                print(f"   - {name}: {info['description']}")
                
        except ImportError as e:
            print(f"⚠️ Импорт из __init__.py не удался: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Запуск тестирования инструментов GopiAI")
    print("=" * 50)
    
    results = []
    
    # Тестирование импортов
    results.append(("Импорты", test_imports()))
    
    # Тестирование инструментов
    results.append(("Файловая система", test_filesystem_tool()))
    results.append(("Терминал", test_terminal_tool()))
    results.append(("Поиск в интернете", test_web_search_tool()))
    results.append(("Просмотр веб-страниц", test_web_viewer_tool()))
    
    # Результаты
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("⚠️ Некоторые тесты провалены. Проверьте ошибки выше.")
        return 1

if __name__ == "__main__":
    sys.exit(main())