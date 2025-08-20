#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emoji Finder Script
Searches for emoji characters in Python files within a specified directory or single file.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

# Common emoji patterns (Unicode ranges)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001F018-\U0001F270"  # various symbols
    "\U00002600-\U000026FF"  # miscellaneous symbols
    "\U00002700-\U000027BF"  # dingbats
    "]+", 
    flags=re.UNICODE
)

def find_emojis_in_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find all emojis in a single file.
    
    Args:
        file_path: Path to the file to search
        
    Returns:
        List of tuples (line_number, line_content, emoji_found)
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                matches = EMOJI_PATTERN.findall(line)
                if matches:
                    for emoji in matches:
                        results.append((line_num, line.strip(), emoji))
    except Exception as e:
        print(f"❌ Ошибка чтения файла {file_path}: {e}")
    
    return results

def find_emojis_in_directory(directory: Path, extensions: List[str] = None) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Find all emojis in files within a directory.
    
    Args:
        directory: Directory to search in
        extensions: List of file extensions to search (default: ['.py'])
        
    Returns:
        Dictionary mapping file paths to lists of emoji findings
    """
    if extensions is None:
        extensions = ['.py', '.md', '.txt', '.json', '.yml', '.yaml']
    
    results = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip common directories that shouldn't contain emojis
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in extensions:
                emoji_findings = find_emojis_in_file(file_path)
                if emoji_findings:
                    results[str(file_path)] = emoji_findings
    
    return results

def print_results(results: Dict[str, List[Tuple[int, str, str]]]):
    """Print the search results in a formatted way."""
    if not results:
        print("✅ Эмодзи не найдены!")
        return
    
    total_files = len(results)
    total_emojis = sum(len(findings) for findings in results.values())
    
    print(f"🔍 Найдено эмодзи в {total_files} файлах (всего {total_emojis} вхождений):\n")
    
    for file_path, findings in results.items():
        print(f"📁 {file_path}")
        for line_num, line_content, emoji in findings:
            print(f"   Строка {line_num}: {emoji} -> {line_content}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Поиск эмодзи в файлах проекта")
    parser.add_argument("path", help="Путь к папке или файлу для поиска")
    parser.add_argument("-e", "--extensions", nargs="+", 
                       default=['.py', '.md', '.txt', '.json', '.yml', '.yaml'],
                       help="Расширения файлов для поиска (по умолчанию: .py .md .txt .json .yml .yaml)")
    
    args = parser.parse_args()
    
    search_path = Path(args.path)
    
    if not search_path.exists():
        print(f"❌ Путь не существует: {search_path}")
        sys.exit(1)
    
    print(f"🔍 Поиск эмодзи в: {search_path}")
    print(f"📋 Расширения файлов: {', '.join(args.extensions)}\n")
    
    if search_path.is_file():
        # Search in single file
        results = {str(search_path): find_emojis_in_file(search_path)}
    else:
        # Search in directory
        results = find_emojis_in_directory(search_path, args.extensions)
    
    print_results(results)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode if no arguments provided
        print("🤖 Поиск эмодзи в файлах проекта")
        print("=" * 40)
        
        while True:
            path_input = input("\n📂 Введите путь к папке или файлу (или 'q' для выхода): ").strip()
            
            if path_input.lower() == 'q':
                print("👋 До свидания!")
                break
            
            if not path_input:
                print("❌ Пожалуйста, введите путь")
                continue
            
            search_path = Path(path_input)
            
            if not search_path.exists():
                print(f"❌ Путь не существует: {search_path}")
                continue
            
            print(f"\n🔍 Поиск эмодзи в: {search_path}")
            
            if search_path.is_file():
                results = {str(search_path): find_emojis_in_file(search_path)}
            else:
                results = find_emojis_in_directory(search_path)
            
            print_results(results)
    else:
        main()