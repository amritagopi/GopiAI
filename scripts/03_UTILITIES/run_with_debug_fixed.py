#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой launcher с детальным логированием и исправлением кодировки
Использование: python run_with_debug_fixed.py
"""

import os
import sys
import subprocess
from datetime import datetime

def setup_encoding():
    """Настройка кодировки для Windows"""
    if sys.platform == "win32":
        # Устанавливаем UTF-8 как кодировку по умолчанию
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # Для Windows консоли
        try:
            # Устанавливаем кодовую страницу UTF-8 для консоли
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass

def main():
    """Запуск GopiAI с детальным логированием"""
    
    print("🔍 GopiAI Debug Mode Launcher (Fixed)")
    print("=" * 50)
    
    # Настраиваем кодировку перед запуском
    setup_encoding()
    
    # Настраиваем переменные окружения для детального логирования
    env = os.environ.copy()
    env.update({
        'PYTHONUNBUFFERED': '1',      # Отключаем буферизацию вывода
        'PYTHONASYNCIODEBUG': '1',    # Debug для asyncio
        'PYTHONVERBOSE': '1',         # Подробный вывод Python
        'QT_LOGGING_RULES': 'qt.*=true',  # Qt логирование
        'QT_DEBUG_PLUGINS': '1',      # Debug Qt плагинов
        'GOPIAI_DEBUG': 'true',       # Наш флаг для GopiAI
        'PYTHONIOENCODING': 'utf-8',  # Кодировка ввода/вывода
        'PYTHONUTF8': '1',            # Включаем UTF-8 mode
    })
    
    # Генерируем имя файла для логов
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"gopiai_debug_{timestamp}.log"
    
    print(f"📁 Логи сохраняются в: {log_file}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📂 Рабочая папка: {os.getcwd()}")
    print(f"🔤 Кодировка: UTF-8 (принудительно)")
    print("🚀 Запускаем GopiAI...")
    print("=" * 50)
    
    # Команда для запуска с перенаправлением в файл
    cmd = [
        sys.executable,
        '-u',  # Отключаем буферизацию
        '-X', 'utf8',  # Включаем UTF-8 mode
        '-X', 'dev',  # Development mode
        'GopiAI-UI/gopiai/ui/main.py'
    ]
    
    try:
        # Запускаем с перенаправлением вывода в файл + консоль
        with open(log_file, 'w', encoding='utf-8', errors='replace') as f:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1  # Line buffered
            )
            
            # Читаем и выводим в реальном времени
            if process.stdout:
                for line in process.stdout:
                    print(line.rstrip())  # В консоль
                    f.write(line)         # В файл
                    f.flush()             # Сразу записываем
            
            process.wait()
            
        print(f"\n📁 Детальные логи сохранены в: {log_file}")
        return process.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        print(f"💡 Попробуйте запустить напрямую: python GopiAI-UI/gopiai/ui/main.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())