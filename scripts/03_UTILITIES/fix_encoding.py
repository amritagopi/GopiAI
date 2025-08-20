#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое исправление проблемы с кодировкой в Windows
Этот скрипт исправляет места в коде, где используется open() без encoding='utf-8'
"""

import os
import re
import sys
from pathlib import Path

def fix_encoding_issues():
    """Исправляет проблемы с кодировкой в Python файлах"""
    
    print("🔧 Исправление проблем с кодировкой...")
    
    # Файлы, которые точно нужно исправить
    problem_files = [
        "GopiAI/project_health/analyzers/check_python_version.py",
        "project_health/analyzers/check_python_version.py"
    ]
    
    fixes_made = 0
    
    for file_path in problem_files:
        if os.path.exists(file_path):
            print(f"📝 Исправляем {file_path}...")
            
            try:
                # Читаем файл
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Заменяем open(..., 'r') на open(..., 'r', encoding='utf-8')
                # Паттерн для поиска open без encoding
                pattern = r"open\s*\(\s*([^,]+),\s*'r'\s*\)"
                replacement = r"open(\1, 'r', encoding='utf-8')"
                
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    # Сохраняем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ Исправлен {file_path}")
                    fixes_made += 1
                else:
                    print(f"ℹ️ В {file_path} исправления не требуются")
                    
            except Exception as e:
                print(f"❌ Ошибка при исправлении {file_path}: {e}")
    
    print(f"\n✅ Выполнено исправлений: {fixes_made}")
    
    # Дополнительно создаем .py файл с настройкой кодировки
    startup_fix = """# -*- coding: utf-8 -*-
import sys
import os

# Принудительная настройка UTF-8 для Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Перенаправляем стандартные потоки на UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""
    
    with open("encoding_fix.py", "w", encoding='utf-8') as f:
        f.write(startup_fix)
    
    print("📦 Создан файл encoding_fix.py для импорта в других скриптах")

def main():
    print("🛠️ Утилита исправления кодировки GopiAI")
    print("=" * 50)
    
    fix_encoding_issues()
    
    print("\n💡 Рекомендации:")
    print("1. Используйте run_with_debug_fixed.py для запуска")
    print("2. Если проблемы продолжаются, запустите: python -X utf8 GopiAI-UI/gopiai/ui/main.py")
    print("3. В bash можете добавить: export PYTHONUTF8=1")

if __name__ == "__main__":
    main()