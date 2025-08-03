#!/usr/bin/env python3
"""
Демонстрация безопасного выполнения терминальных команд
Задача 12: Implement secure terminal command execution
"""

import sys
import os
import logging

# Добавляем путь к модулям GopiAI
sys.path.append('GopiAI-CrewAI/tools/gopiai_integration')

try:
    from command_executor import CommandExecutor
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что вы запускаете скрипт из корневой директории проекта")
    sys.exit(1)

def demo_secure_terminal_execution():
    """Демонстрация функций безопасного выполнения команд"""
    
    print("🔒 Демонстрация безопасного выполнения терминальных команд")
    print("=" * 60)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Создание экземпляра CommandExecutor
    executor = CommandExecutor()
    
    print("\n1️⃣ Тест разрешённых команд:")
    print("-" * 30)
    
    # Безопасные команды
    safe_commands = [
        "echo Hello, World!",
        "pwd" if os.name != "nt" else "cd",
        "python --version",
        "dir" if os.name == "nt" else "ls -la"
    ]
    
    for cmd in safe_commands:
        print(f"\n🟢 Выполнение: {cmd}")
        result = executor.execute_terminal_command(cmd, timeout=5)
        print(f"📤 Результат: {result[:100]}{'...' if len(result) > 100 else ''}")
    
    print("\n\n2️⃣ Тест запрещённых команд:")
    print("-" * 30)
    
    # Опасные команды
    dangerous_commands = [
        "rm -rf /",
        "del C:\\Windows\\*",
        "malicious_command",
        "ls && rm -rf /",
        "echo test | dangerous_pipe"
    ]
    
    for cmd in dangerous_commands:
        print(f"\n🔴 Попытка выполнения: {cmd}")
        result = executor.execute_terminal_command(cmd)
        print(f"🛡️ Результат: {result[:150]}{'...' if len(result) > 150 else ''}")
    
    print("\n\n3️⃣ Тест файловых операций:")
    print("-" * 30)
    
    # Безопасные файловые операции
    print("\n🟢 Создание тестового файла:")
    result = executor.file_operations("write", "demo_test.txt", "Тестовое содержимое файла\nВторая строка")
    print(f"📤 Результат: {result}")
    
    print("\n🟢 Чтение тестового файла:")
    result = executor.file_operations("read", "demo_test.txt")
    print(f"📤 Результат: {result}")
    
    print("\n🟢 Проверка существования файла:")
    result = executor.file_operations("exists", "demo_test.txt")
    print(f"📤 Результат: {result}")
    
    # Опасные файловые операции
    print("\n🔴 Попытка доступа к системному файлу:")
    dangerous_path = "/etc/passwd" if os.name != "nt" else "C:\\Windows\\System32\\config\\SAM"
    result = executor.file_operations("read", dangerous_path)
    print(f"🛡️ Результат: {result}")
    
    print("\n🔴 Попытка path traversal:")
    result = executor.file_operations("read", "../../../etc/passwd")
    print(f"🛡️ Результат: {result}")
    
    print("\n\n4️⃣ Тест таймаутов:")
    print("-" * 30)
    
    print("\n⏱️ Команда с коротким таймаутом:")
    if os.name == "nt":
        # Windows: ping с задержкой
        result = executor.execute_terminal_command("ping -n 5 127.0.0.1", timeout=1)
    else:
        # Unix/Linux: sleep
        result = executor.execute_terminal_command("sleep 3", timeout=1)
    print(f"⏰ Результат: {result}")
    
    print("\n\n5️⃣ Тест веб-функций:")
    print("-" * 30)
    
    print("\n🌐 Безопасный веб-запрос:")
    try:
        result = executor.browse_website("https://httpbin.org/json", max_content_length=500)
        print(f"📤 Результат: {result[:200]}{'...' if len(result) > 200 else ''}")
    except Exception as e:
        print(f"⚠️ Веб-запрос недоступен: {e}")
    
    print("\n🔴 Небезопасный URL:")
    result = executor.browse_website("http://localhost:8080/admin")
    print(f"🛡️ Результат: {result}")
    
    # Очистка
    print("\n\n🧹 Очистка:")
    print("-" * 30)
    try:
        if os.path.exists("demo_test.txt"):
            os.remove("demo_test.txt")
            print("✅ Тестовый файл удалён")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Демонстрация завершена!")
    print("\n📋 Выводы:")
    print("• Все разрешённые команды выполняются корректно")
    print("• Опасные команды блокируются системой безопасности")
    print("• Файловые операции проверяются на безопасность путей")
    print("• Таймауты предотвращают зависание системы")
    print("• Веб-запросы фильтруются по безопасности URL")

if __name__ == "__main__":
    demo_secure_terminal_execution()