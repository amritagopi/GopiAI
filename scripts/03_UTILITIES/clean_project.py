#!/usr/bin/env python3
"""
🧹 Скрипт для очистки проекта от временных и ненужных файлов
"""

import os
import shutil
import glob
import time
from pathlib import Path
import argparse

def get_confirmation(message):
    """Запрашивает подтверждение у пользователя"""
    response = input(f"{message} (y/n): ").lower().strip()
    return response == 'y' or response == 'yes'

def clean_pycache(root_dir, dry_run=True):
    """Удаляет все __pycache__ директории"""
    print("\n🔍 Поиск и удаление __pycache__ директорий...")
    
    pycache_dirs = []
    for root, dirs, files in os.walk(root_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            pycache_dirs.append(pycache_path)
    
    if not pycache_dirs:
        print("✅ __pycache__ директории не найдены.")
        return
    
    print(f"Найдено {len(pycache_dirs)} __pycache__ директорий:")
    for path in pycache_dirs:
        print(f"  - {path}")
    
    if dry_run:
        print("❗ Режим симуляции: файлы НЕ были удалены.")
        return
    
    if get_confirmation("Удалить все __pycache__ директории?"):
        for path in pycache_dirs:
            try:
                shutil.rmtree(path)
                print(f"✅ Удалено: {path}")
            except Exception as e:
                print(f"❌ Ошибка при удалении {path}: {e}")

def clean_temp_files(root_dir, dry_run=True):
    """Удаляет временные файлы (.pyc, .tmp, .bak и т.д.)"""
    print("\n🔍 Поиск и удаление временных файлов...")
    
    temp_extensions = ['*.pyc', '*.pyo', '*.tmp', '*.bak', '*.swp', '*.~*']
    temp_files = []
    
    for ext in temp_extensions:
        pattern = os.path.join(root_dir, '**', ext)
        temp_files.extend(glob.glob(pattern, recursive=True))
    
    if not temp_files:
        print("✅ Временные файлы не найдены.")
        return
    
    print(f"Найдено {len(temp_files)} временных файлов:")
    for path in temp_files[:20]:  # Показываем только первые 20 файлов
        print(f"  - {path}")
    
    if len(temp_files) > 20:
        print(f"  ... и еще {len(temp_files) - 20} файлов")
    
    if dry_run:
        print("❗ Режим симуляции: файлы НЕ были удалены.")
        return
    
    if get_confirmation("Удалить все временные файлы?"):
        for path in temp_files:
            try:
                os.remove(path)
                print(f"✅ Удалено: {path}")
            except Exception as e:
                print(f"❌ Ошибка при удалении {path}: {e}")

def clean_egg_info(root_dir, dry_run=True):
    """Удаляет директории *.egg-info"""
    print("\n🔍 Поиск и удаление *.egg-info директорий...")
    
    egg_dirs = []
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.endswith('.egg-info'):
                egg_path = os.path.join(root, dir_name)
                egg_dirs.append(egg_path)
    
    if not egg_dirs:
        print("✅ *.egg-info директории не найдены.")
        return
    
    print(f"Найдено {len(egg_dirs)} *.egg-info директорий:")
    for path in egg_dirs:
        print(f"  - {path}")
    
    if dry_run:
        print("❗ Режим симуляции: директории НЕ были удалены.")
        return
    
    if get_confirmation("Удалить все *.egg-info директории?"):
        for path in egg_dirs:
            try:
                shutil.rmtree(path)
                print(f"✅ Удалено: {path}")
            except Exception as e:
                print(f"❌ Ошибка при удалении {path}: {e}")

def clean_logs(root_dir, days=7, dry_run=True):
    """Удаляет старые лог-файлы (старше указанного количества дней)"""
    print(f"\n🔍 Поиск и удаление лог-файлов старше {days} дней...")
    
    log_extensions = ['*.log', '*.log.*']
    log_files = []
    current_time = time.time()
    
    for ext in log_extensions:
        pattern = os.path.join(root_dir, '**', ext)
        for file_path in glob.glob(pattern, recursive=True):
            file_time = os.path.getmtime(file_path)
            if (current_time - file_time) / (24 * 3600) > days:
                log_files.append(file_path)
    
    if not log_files:
        print(f"✅ Лог-файлы старше {days} дней не найдены.")
        return
    
    print(f"Найдено {len(log_files)} лог-файлов старше {days} дней:")
    for path in log_files[:20]:  # Показываем только первые 20 файлов
        print(f"  - {path}")
    
    if len(log_files) > 20:
        print(f"  ... и еще {len(log_files) - 20} файлов")
    
    if dry_run:
        print("❗ Режим симуляции: файлы НЕ были удалены.")
        return
    
    if get_confirmation(f"Удалить все лог-файлы старше {days} дней?"):
        for path in log_files:
            try:
                os.remove(path)
                print(f"✅ Удалено: {path}")
            except Exception as e:
                print(f"❌ Ошибка при удалении {path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Очистка проекта от временных и ненужных файлов")
    parser.add_argument("--dry-run", action="store_true", help="Режим симуляции (без удаления)")
    parser.add_argument("--pycache", action="store_true", help="Удалить __pycache__ директории")
    parser.add_argument("--temp", action="store_true", help="Удалить временные файлы")
    parser.add_argument("--egg-info", action="store_true", help="Удалить *.egg-info директории")
    parser.add_argument("--logs", action="store_true", help="Удалить старые лог-файлы")
    parser.add_argument("--log-days", type=int, default=7, help="Удалять лог-файлы старше указанного количества дней")
    parser.add_argument("--all", action="store_true", help="Выполнить все операции очистки")
    
    args = parser.parse_args()
    
    # Если не указаны конкретные операции, показываем справку
    if not any([args.pycache, args.temp, args.egg_info, args.logs, args.all]):
        parser.print_help()
        return
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("🧹 ОЧИСТКА ПРОЕКТА")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️ РЕЖИМ СИМУЛЯЦИИ: файлы не будут удалены")
    
    if args.all or args.pycache:
        clean_pycache(root_dir, args.dry_run)
    
    if args.all or args.temp:
        clean_temp_files(root_dir, args.dry_run)
    
    if args.all or args.egg_info:
        clean_egg_info(root_dir, args.dry_run)
    
    if args.all or args.logs:
        clean_logs(root_dir, args.log_days, args.dry_run)
    
    print("\n✅ Очистка завершена!")

if __name__ == "__main__":
    main()