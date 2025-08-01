"""
Простой тест для проверки работы Smart Workspace Indexer
"""

import os
import tempfile
import shutil
from pathlib import Path

def test_workspace_indexer():
    """Простой тест индексатора"""
    print("🧪 Тестирование Smart Workspace Indexer...")
    
    try:
        from gopiai.extensions.workspace_indexer import get_workspace_indexer
        print("✅ Модуль успешно импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Создаём временную директорию для теста
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Создана временная директория: {temp_dir}")
    
    try:
        # Создаём тестовый проект
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0"
            }
        }
        
        import json
        with open(os.path.join(temp_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        
        Path(temp_dir, 'index.js').touch()
        Path(temp_dir, 'README.md').touch()
        
        print("📄 Создан тестовый Node.js проект")
        
        # Тестируем индексатор
        indexer = get_workspace_indexer()
        print("🔧 Индексатор инициализирован")
        
        workspace_index = indexer.index_workspace(temp_dir)
        print("📊 Индексация выполнена")
        
        # Проверяем результаты
        assert workspace_index.project_info.project_type == 'node'
        assert workspace_index.project_info.primary_language == 'javascript'
        assert 'React' in workspace_index.project_info.frameworks
        assert workspace_index.total_files > 0
        
        print("✅ Все проверки пройдены!")
        
        # Тестируем краткое описание
        summary = indexer.get_project_summary(workspace_index)
        print(f"📋 Краткое описание: {summary}")
        
        # Тестируем структуру файлов
        file_tree = indexer.get_file_tree_summary(workspace_index)
        print("🌳 Структура файлов:")
        print(file_tree[:200] + "..." if len(file_tree) > 200 else file_tree)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Очищаем временную директорию
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("🧹 Временная директория очищена")

def test_mcp_integration():
    """Тест MCP интеграции"""
    print("\n🔗 Тестирование MCP интеграции...")
    
    try:
        from gopiai.extensions.mcp_workspace_integration import get_mcp_workspace_integration
        print("✅ MCP интеграция импортирована")
        
        mcp_integration = get_mcp_workspace_integration()
        print("🔧 MCP интеграция инициализирована")
        
        # Тестируем на текущей директории
        current_dir = os.getcwd()
        result = mcp_integration.on_workspace_set(current_dir)
        
        if result["success"]:
            print("✅ Рабочее пространство успешно установлено")
            print(f"📋 Описание: {result.get('project_summary', 'Нет описания')}")
            
            # Тестируем получение информации
            project_info = mcp_integration.get_project_info()
            if project_info:
                print(f"📊 Тип проекта: {project_info['project_type']}")
                print(f"🗣️ Основной язык: {project_info['primary_language']}")
            
            return True
        else:
            print(f"❌ Ошибка установки рабочего пространства: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов Smart Workspace Indexer")
    print("=" * 50)
    
    success1 = test_workspace_indexer()
    success2 = test_mcp_integration()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("❌ Некоторые тесты не прошли")
    
    print("=" * 50)