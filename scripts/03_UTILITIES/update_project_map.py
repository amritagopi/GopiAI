#!/usr/bin/env python3
"""
Быстрое обновление карты проекта
===============================

Запускает dependency_mapper.py и sync_to_rag.py для обновления
карты проекта и синхронизации с RAG системой.

Автор: Crazy Coder
Дата: 2025-06-05
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Обновляет карту проекта и синхронизирует с RAG"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🔄 Обновление карты проекта...")
    print("=" * 50)
    
    try:
        # Запускаем dependency_mapper.py
        print("📊 Анализируем зависимости проекта...")
        result = subprocess.run([
            sys.executable, 
            "project_health/analyzers/dependency_mapper.py"
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Карта проекта обновлена!")
            print(result.stdout)
        else:
            print("❌ Ошибка при создании карты:")
            print(result.stderr)
            return False
        
        # Запускаем sync_to_rag.py
        print("\n🧠 Синхронизируем с RAG системой...")
        result = subprocess.run([
            sys.executable, 
            "project_health/scripts/utils/sync_to_rag.py"
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Синхронизация с RAG завершена!")
            print(result.stdout)
        else:
            print("⚠️  Предупреждения при синхронизации:")
            print(result.stderr)
        
        print("\n🎉 Обновление завершено!")
        print(f"📁 Карта проекта: {project_root}/project_health/reports/project_map.json")
        print(f"🧠 RAG индекс: {project_root}/rag_memory_system/project_sync/project_index.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
