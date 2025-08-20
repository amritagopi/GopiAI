#!/usr/bin/env python3
"""
Универсальный Launcher для GopiAI с улучшенным UI и меню выбора опций
Версия 2025.06.20
"""

import os
import sys
import subprocess
import importlib.util
from datetime import datetime
from pathlib import Path

# Используем цветной вывод
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def setup_env():
    """Базовые настройки окружения"""
    # Установка пути к Python модулям
    sys.path.insert(0, os.getcwd())
    
    # Настройка UTF-8 для Windows
    if sys.platform == 'win32':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        try:
            import ctypes
            if hasattr(ctypes, 'windll'):
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)
                ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass

def print_header():
    """Печать шапки программы"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{Colors.BOLD}{Colors.HEADER}╔═══════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}║              GopiAI Универсальный Launcher               ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print(f"{Colors.CYAN}Версия: 2025.06.20{Colors.ENDC}")
    print()

def list_menu_options():
    """Вывод основного меню"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}═══ МЕНЮ ЗАПУСКА ═══{Colors.ENDC}")
    print(f"{Colors.GREEN}1. Стандартный запуск{Colors.ENDC}")
    print(f"{Colors.BLUE}2. Запуск с отладкой (улучшено){Colors.ENDC}")
    print(f"{Colors.CYAN}3. Диагностика системы{Colors.ENDC}")
    print(f"{Colors.YELLOW}4. Запуск тестов{Colors.ENDC}")
    print(f"{Colors.RED}5. Очистка и обслуживание{Colors.ENDC}")
    print(f"{Colors.BOLD}0. Выход{Colors.ENDC}")

def run_standard():
    """Стандартный запуск без отладки"""
    print_header()
    print(f"{Colors.BOLD}{Colors.GREEN}=== Стандартный запуск ==={Colors.ENDC}")
    
    script_path = "GopiAI-UI/gopiai/ui/main.py"
    if not os.path.exists(script_path):
        print(f"{Colors.RED}Ошибка: Файл {script_path} не найден!{Colors.ENDC}")
        return
    
    print(f"{Colors.CYAN}Запуск: {script_path}{Colors.ENDC}")
    
    cmd = [sys.executable, script_path]
    
    try:
        process = subprocess.run(cmd)
        if process.returncode != 0:
            print(f"{Colors.RED}Приложение завершилось с кодом: {process.returncode}{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}Приложение завершилось успешно!{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка запуска: {str(e)}{Colors.ENDC}")

def run_debug():
    """Запуск с отладкой"""
    print_header()
    print(f"{Colors.BOLD}{Colors.BLUE}=== Запуск с отладкой ==={Colors.ENDC}")
    
    debug_options = [
        {"name": "Стандартная отладка", "path": "scripts/dev/run_with_debug_fixed.py"},
        {"name": "Расширенная отладка", "path": "scripts/dev/debug_launcher.py"},
        {"name": "Отладка с логированием взаимодействий", "path": "scripts/utils/interaction_debug_logger.py"},
        {"name": "Вернуться в главное меню", "path": None}
    ]
    
    print(f"\n{Colors.CYAN}Выберите режим отладки:{Colors.ENDC}")
    for i, option in enumerate(debug_options, 1):
        print(f"{Colors.CYAN}{i}. {option['name']}{Colors.ENDC}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Ваш выбор: {Colors.ENDC}"))
        if choice < 1 or choice > len(debug_options):
            print(f"{Colors.YELLOW}Неверный выбор.{Colors.ENDC}")
            return
        
        selected = debug_options[choice-1]
        if selected["path"] is None:
            return
        
        debug_script = selected["path"]
        if not os.path.exists(debug_script):
            print(f"{Colors.RED}Ошибка: Файл {debug_script} не найден!{Colors.ENDC}")
            return
        
        print(f"{Colors.CYAN}Запуск: {debug_script}{Colors.ENDC}")
        
        cmd = [sys.executable, debug_script]
        
        process = subprocess.run(cmd)
        if process.returncode != 0:
            print(f"{Colors.RED}Приложение завершилось с кодом: {process.returncode}{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}Приложение завершилось успешно!{Colors.ENDC}")
            
    except ValueError:
        print(f"{Colors.YELLOW}Требуется числовое значение.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {str(e)}{Colors.ENDC}")

def run_diagnostics():
    """Запуск диагностики системы"""
    print_header()
    print(f"{Colors.BOLD}{Colors.CYAN}=== Диагностика системы ==={Colors.ENDC}")
    
    diagnostic_options = [
        {"name": "Базовая диагностика", "path": "scripts/diagnostics/diagnostic.py"},
        {"name": "Расширенная диагностика", "path": "scripts/diagnostics/detailed_diagnostic.py"},
        {"name": "Анализ проблем", "path": "scripts/diagnostics/analyze_problems.py"},
        {"name": "Диагностика чата", "path": "diagnose_chat.py"},
        {"name": "Вернуться в главное меню", "path": None}
    ]
    
    print(f"\n{Colors.CYAN}Выберите вид диагностики:{Colors.ENDC}")
    for i, option in enumerate(diagnostic_options, 1):
        print(f"{Colors.CYAN}{i}. {option['name']}{Colors.ENDC}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Ваш выбор: {Colors.ENDC}"))
        if choice < 1 or choice > len(diagnostic_options):
            print(f"{Colors.YELLOW}Неверный выбор.{Colors.ENDC}")
            return
        
        selected = diagnostic_options[choice-1]
        if selected["path"] is None:
            return
        
        diagnostic_script = selected["path"]
        if not os.path.exists(diagnostic_script):
            print(f"{Colors.RED}Ошибка: Файл {diagnostic_script} не найден!{Colors.ENDC}")
            return
        
        print(f"{Colors.CYAN}Запуск: {diagnostic_script}{Colors.ENDC}")
        
        cmd = [sys.executable, diagnostic_script]
        
        subprocess.run(cmd)
        input(f"\n{Colors.GREEN}Нажмите Enter для продолжения...{Colors.ENDC}")
        
    except ValueError:
        print(f"{Colors.YELLOW}Требуется числовое значение.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {str(e)}{Colors.ENDC}")

def run_tests():
    """Запуск тестов"""
    print_header()
    print(f"{Colors.BOLD}{Colors.YELLOW}=== Запуск тестов ==={Colors.ENDC}")
    
    # Находим все тесты в папке tests
    test_files = []
    for test_path in [Path("tests"), Path("scripts/tests")]:
        if test_path.exists():
            test_files.extend([str(p) for p in test_path.glob("test_*.py") if p.is_file()])
    
    # Добавляем отдельные тесты из корневой директории
    root_tests = []
    for test_file in Path(".").glob("test_*.py"):
        if test_file.is_file():
            root_tests.append(str(test_file))
    
    test_files.extend(root_tests)
    test_files.append(None)  # Для пункта "Вернуться в главное меню"
    
    print(f"\n{Colors.CYAN}Доступные тесты:{Colors.ENDC}")
    for i, test_file in enumerate(test_files, 1):
        name = test_file if test_file else "Вернуться в главное меню"
        print(f"{Colors.CYAN}{i}. {name}{Colors.ENDC}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Ваш выбор: {Colors.ENDC}"))
        if choice < 1 or choice > len(test_files):
            print(f"{Colors.YELLOW}Неверный выбор.{Colors.ENDC}")
            return
        
        selected = test_files[choice-1]
        if selected is None:
            return
        
        if not os.path.exists(selected):
            print(f"{Colors.RED}Ошибка: Файл {selected} не найден!{Colors.ENDC}")
            return
        
        print(f"{Colors.CYAN}Запуск теста: {selected}{Colors.ENDC}")
        
        cmd = [sys.executable, selected]
        
        subprocess.run(cmd)
        input(f"\n{Colors.GREEN}Нажмите Enter для продолжения...{Colors.ENDC}")
        
    except ValueError:
        print(f"{Colors.YELLOW}Требуется числовое значение.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {str(e)}{Colors.ENDC}")

def run_maintenance():
    """Очистка и обслуживание"""
    print_header()
    print(f"{Colors.BOLD}{Colors.RED}=== Очистка и обслуживание ==={Colors.ENDC}")
    
    maintenance_options = [
        {"name": "Очистка зависимостей", "path": "scripts/utils/clean_dependencies.py"},
        {"name": "Очистка старых зависимостей", "path": "scripts/utils/cleanup_old_dependencies.py"},
        {"name": "RAG Cleanup Wizard", "path": "scripts/utils/rag_cleanup_wizard.py"},
        {"name": "Обновление карты проекта", "path": "scripts/utils/update_project_map.py"},
        {"name": "Вернуться в главное меню", "path": None}
    ]
    
    print(f"\n{Colors.CYAN}Выберите операцию:{Colors.ENDC}")
    for i, option in enumerate(maintenance_options, 1):
        print(f"{Colors.CYAN}{i}. {option['name']}{Colors.ENDC}")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Ваш выбор: {Colors.ENDC}"))
        if choice < 1 or choice > len(maintenance_options):
            print(f"{Colors.YELLOW}Неверный выбор.{Colors.ENDC}")
            return
        
        selected = maintenance_options[choice-1]
        if selected["path"] is None:
            return
        
        maintenance_script = selected["path"]
        if not os.path.exists(maintenance_script):
            print(f"{Colors.RED}Ошибка: Файл {maintenance_script} не найден!{Colors.ENDC}")
            return
        
        # Запрашиваем подтверждение для потенциально опасных операций
        if "clean" in maintenance_script:
            confirm = input(f"{Colors.YELLOW}⚠️ Эта операция может удалить файлы. Продолжить? (y/n): {Colors.ENDC}").lower()
            if confirm != 'y':
                print(f"{Colors.YELLOW}Операция отменена.{Colors.ENDC}")
                return
        
        print(f"{Colors.CYAN}Запуск: {maintenance_script}{Colors.ENDC}")
        
        cmd = [sys.executable, maintenance_script]
        
        subprocess.run(cmd)
        input(f"\n{Colors.GREEN}Нажмите Enter для продолжения...{Colors.ENDC}")
        
    except ValueError:
        print(f"{Colors.YELLOW}Требуется числовое значение.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {str(e)}{Colors.ENDC}")

def main():
    """Основная функция меню"""
    setup_env()
    
    while True:
        print_header()
        list_menu_options()
        
        try:
            choice = input(f"\n{Colors.BOLD}Введите номер: {Colors.ENDC}")
            
            if choice == "0":
                print(f"{Colors.GREEN}До свидания!{Colors.ENDC}")
                break
            elif choice == "1":
                run_standard()
            elif choice == "2":
                run_debug()
            elif choice == "3":
                run_diagnostics()
            elif choice == "4":
                run_tests()
            elif choice == "5":
                run_maintenance()
            else:
                print(f"{Colors.YELLOW}Неверный выбор.{Colors.ENDC}")
            
            # Паузасперед возвращением в меню
            if choice in ["1", "2"]:  # Для запущенных приложений
                input(f"\n{Colors.GREEN}Нажмите Enter для возвращения в меню...{Colors.ENDC}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Прервано пользователем.{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Ошибка: {str(e)}{Colors.ENDC}")
            input(f"{Colors.YELLOW}Нажмите Enter для продолжения...{Colors.ENDC}")

if __name__ == "__main__":
    main()