#!/usr/bin/env python3
"""
Модульная настройка GopiAI - обновленная версия
===============================================
Правильная настройка всех модулей с учетом новой структуры
"""
import os
import sys
from pathlib import Path

# Актуальные модули в порядке установки (по зависимостям)
MODULES = [
    "GopiAI-Core",        # Базовый модуль
    "GopiAI-Widgets",     # Зависит от Core
    "GopiAI-UI",          # Зависит от Core + Widgets (включает бывшие Assets)
    "GopiAI-WebView",     # Зависит от Core + UI
    "GopiAI-Extensions",  # Зависит от Core + Widgets + UI  
    "GopiAI-App",         # Зависит от всех предыдущих
]

# RAG Memory отдельно - это независимая система
RAG_MODULE = "rag_memory_system"

def check_module_structure():
    """Проверяет структуру всех модулей"""
    print("🔍 Проверка структуры модулей")
    print("=" * 50)
    
    for module in MODULES:
        print(f"\n📦 {module}:")
        module_path = Path(module)
        
        if not module_path.exists():
            print(f"  ❌ Модуль не найден: {module_path}")
            continue
            
        # Проверяем pyproject.toml
        pyproject = module_path / "pyproject.toml"
        if pyproject.exists():
            print(f"  ✅ pyproject.toml найден")
        else:
            print(f"  ❌ pyproject.toml отсутствует")
            
        # Проверяем gopiai namespace
        gopiai_path = module_path / "gopiai"
        if gopiai_path.exists():
            print(f"  ✅ gopiai/ найден")
            
            # Проверяем __init__.py
            init_file = gopiai_path / "__init__.py"
            if init_file.exists():
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "extend_path" in content:
                    print(f"  ✅ namespace package настроен")
                else:
                    print(f"  ⚠️  namespace package НЕ настроен")
            else:
                print(f"  ❌ gopiai/__init__.py отсутствует")
        else:
            print(f"  ❌ gopiai/ не найден")

def setup_namespace_packages():
    """Настраивает namespace packages для всех модулей"""
    print("\n🔧 Настройка namespace packages")
    print("=" * 50)
    
    namespace_content = '''"""GopiAI namespace package"""
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
'''
    
    for module in MODULES:
        module_path = Path(module)
        if not module_path.exists():
            print(f"❌ Пропускаем {module} - не найден")
            continue
            
        gopiai_path = module_path / "gopiai"
        gopiai_path.mkdir(exist_ok=True)
        
        init_file = gopiai_path / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(namespace_content)
            
        print(f"✅ Настроен namespace для {module}")

def update_dependencies():
    """Обновляет зависимости в pyproject.toml файлах"""
    print("\n📦 Обновление зависимостей")
    print("=" * 50)
    
    # Правильные зависимости для каждого модуля
    dependencies = {
        "GopiAI-Core": [
            "PySide6>=6.5.0",
        ],
        "GopiAI-Widgets": [
            "PySide6>=6.5.0",
            "gopiai-core",
        ],
        "GopiAI-UI": [
            "PySide6>=6.5.0", 
            "gopiai-core",
            "gopiai-widgets",
        ],
        "GopiAI-WebView": [
            "PySide6>=6.5.0",
            "gopiai-core", 
            "gopiai-ui",
        ],
        "GopiAI-Extensions": [
            "PySide6>=6.5.0",
            "gopiai-core",
            "gopiai-widgets", 
            "gopiai-ui",
        ],
        "GopiAI-App": [
            "PySide6>=6.5.0",
            "gopiai-core",
            "gopiai-widgets",
            "gopiai-ui", 
            "gopiai-webview",
            "gopiai-extensions",
        ],
    }
    
    for module in MODULES:
        if module not in dependencies:
            continue
            
        pyproject_path = Path(module) / "pyproject.toml"
        if not pyproject_path.exists():
            print(f"❌ {module}: pyproject.toml не найден")
            continue
            
        print(f"🔧 Обновляем зависимости для {module}")
        
        # Читаем файл
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Формируем новый список зависимостей
        deps_list = dependencies[module]
        deps_str = ',\n    '.join(f'"{dep}"' for dep in deps_list)
        new_deps = f'''dependencies = [
    {deps_str},
]'''
        
        # Заменяем старые зависимости
        import re
        pattern = r'dependencies = \[.*?\]'
        content = re.sub(pattern, new_deps, content, flags=re.DOTALL)
        
        # Записываем обратно
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ {module}: зависимости обновлены")

def generate_install_script():
    """Генерирует скрипт для правильной установки всех модулей"""
    print("\n📝 Генерация скрипта установки")
    print("=" * 50)
    
    script_content = f'''#!/bin/bash
# Автоматическая установка всех модулей GopiAI в правильном порядке

echo "🚀 Установка модулей GopiAI"
echo "=" * 50

# Устанавливаем модули в порядке зависимостей
'''
    
    for module in MODULES:
        script_content += f'''
echo "📦 Устанавливаем {module}..."
cd {module}
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ {module} установлен успешно"
else
    echo "❌ Ошибка установки {module}"
    exit 1
fi
cd ..
'''
    
    script_content += '''
echo ""
echo "🎉 Все модули установлены!"
echo "Теперь можно запускать:"
echo "python GopiAI-UI/gopiai/ui/main.py"
'''
    
    with open("install_all_modules.sh", 'w', encoding='utf-8') as f:
        f.write(script_content)
        
    # Windows версия
    win_script = script_content.replace('#!/bin/bash', '@echo off').replace('echo "', 'echo ').replace('"', '').replace('[ $? -eq 0 ]', '%ERRORLEVEL% EQU 0').replace('exit 1', 'exit /b 1')
    
    with open("install_all_modules.bat", 'w', encoding='utf-8') as f:
        f.write(win_script)
        
    print("✅ Созданы скрипты:")
    print("  - install_all_modules.sh (Linux/Mac)")  
    print("  - install_all_modules.bat (Windows)")

if __name__ == "__main__":
    print("🔧 GopiAI Modular Setup - Обновленная версия")
    print("=" * 60)
    
    print("\n1. Проверка структуры модулей:")
    check_module_structure()
    
    print("\n2. Настройка namespace packages:")
    setup_namespace_packages()
    
    print("\n3. Обновление зависимостей:")
    update_dependencies()
    
    print("\n4. Генерация скрипта установки:")
    generate_install_script()
    
    print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Запустите: bash install_all_modules.sh")
    print("   или:      install_all_modules.bat")
    print("2. Протестируйте: python test_bridge_imports.py")
    print("3. Запустите приложение: python GopiAI-UI/gopiai/ui/main.py")