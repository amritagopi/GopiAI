#!/usr/bin/env python3
"""Скрипт для запуска всех тестов системы переключения провайдеров."""
import subprocess
import sys
import os
from pathlib import Path

def run_test_script(script_name, description):
    """Запуск тестового скрипта."""
    print(f"\n{'='*60}")
    print(f"Запуск: {description}")
    print(f"{'='*60}")
    
    current_dir = Path(__file__).parent.absolute()
    script_path = current_dir / script_name
    
    if not script_path.exists():
        print(f"❌ Скрипт не найден: {script_path}")
        return False
    
    try:
        # Устанавливаем переменные окружения
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{current_dir};{current_dir.parent / 'GopiAI-UI' / 'gopiai'}"
        
        result = subprocess.run([
            sys.executable, 
            str(script_path)
        ], 
        cwd=current_dir,
        env=env,
        capture_output=False,
        text=True
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Ошибка при запуске {script_name}: {e}")
        return False

import time

def main():
    """Основная функция."""
    print("🚀 Запуск полного тестирования системы переключения провайдеров")
    print("=" * 70)
    
    # Тесты в порядке выполнения
    tests = [
        ("test_model_switching.py", "Тесты функциональности переключения провайдеров"),
        ("test_api_endpoints.py", "Тесты REST API эндпоинтов")
    ]
    
    passed = 0
    total = len(tests)
    
    for i, (script_name, description) in enumerate(tests):
        if i == 1:  # Перед тестами API
            print("\n" + "-"*60)
            print("⏳ Пауза 5 секунд для запуска сервера...")
            print("-"*60)
            time.sleep(5)

        if run_test_script(script_name, description):
            passed += 1
            print(f"✅ {description} - ПРОЙДЕН")
        else:
            print(f"❌ {description} - ПРОВАЛЕН")
    
    print(f"\n{'='*70}")
    print(f"📊 ИТОГОВЫЙ РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты успешно пройдены! Система готова к работе.")
        return True
    else:
        print("❌ Некоторые тесты провалены. Требуется дополнительная проверка.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
