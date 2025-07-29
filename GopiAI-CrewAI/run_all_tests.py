#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов системы переключения провайдеров
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_test_script(script_name):
    """Запускает тестовый скрипт"""
    print(f"\n🧪 Running {script_name}...")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(project_root / script_name)
        ], cwd=str(project_root), timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out")
        return False
    except Exception as e:
        print(f"❌ {script_name} failed with error: {e}")
        return False

def main():
    """Основная функция запуска тестов"""
    print("🚀 GopiAI Model Switching System - All Tests")
    print("=" * 60)
    
    # Список тестовых скриптов
    test_scripts = [
        "test_model_switching.py",
        "test_api_endpoints.py",
        "run_model_tests.py"
    ]
    
    results = []
    
    # Запускаем каждый тест
    for script in test_scripts:
        if (project_root / script).exists():
            success = run_test_script(script)
            results.append((script, success))
        else:
            print(f"⚠️  Test script {script} not found, skipping...")
            results.append((script, False))
    
    # Выводим сводку
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for script, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {script}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
