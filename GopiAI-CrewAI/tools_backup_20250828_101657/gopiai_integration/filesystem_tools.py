# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool
from pydantic import Field
import os
import shutil
import json
import csv
import glob
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes
from typing import List, Dict, Any

class GopiAIFileSystemTool(BaseTool):
    name: str = Field(default="filesystem_tools", description="Расширенный инструмент файловой системы")
    description: str = Field(default="""Мощный инструмент для работы с файловой системой. 
    Поддерживает: чтение/запись файлов, работу с JSON/CSV, архивы, поиск, 
    метаданные, хеширование, и многое другое.""", description="Описание инструмента")

    def _run(self, action: str, path: str = "", data: str = "", **kwargs):
        try:
            # Добавляем прямую поддержку метода list_directory для обратной совместимости
            if action == "list_directory":
                if os.path.isdir(path):
                    files = os.listdir(path)
                    return f"Directory {path}\n" + "\n".join(files) if files else "No files found."
                else:
                    return f"Путь '{path}' не является директорией."
            elif action == "read":
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            elif action == "write":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(data)
                return f"Файл '{path}' успешно записан."
            elif action == "append":
                with open(path, "a", encoding="utf-8") as f:
                    f.write(data)
                return f"Данные добавлены в файл '{path}'."
            elif action == "delete":
                os.remove(path)
                return f"Файл '{path}' удалён."
            elif action == "list" or action == "list_directory":
                if os.path.isdir(path):
                    files = os.listdir(path)
                    return f"Directory {path}\n" + "\n".join(files) if files else "No files found."
                else:
                    return f"Путь '{path}' не является директорией."
            elif action == "exists":
                return os.path.exists(path)
            elif action == "mkdir":
                os.makedirs(path, exist_ok=True)
                return f"Директория '{path}' создана."
            elif action == "remove":
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    return f"Директория '{path}' удалена."
                else:
                    os.remove(path)
                    return f"Файл '{path}' удалён."
            elif action == "copy":
                dst = kwargs.get("dst")
                if not dst:
                    return "Не указан путь назначения (dst)."
                shutil.copy2(path, dst)
                return f"Файл скопирован из '{path}' в '{dst}'."
            elif action == "move":
                dst = kwargs.get("dst")
                if not dst:
                    return "Не указан путь назначения (dst)."
                shutil.move(path, dst)
                return f"Файл перемещён из '{path}' в '{dst}'."
            
            # === НОВЫЕ РАСШИРЕННЫЕ ОПЕРАЦИИ ===
            
            # Работа с JSON
            elif action == "read_json":
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            elif action == "write_json":
                json_data = kwargs.get("json_data", data)
                if isinstance(json_data, str):
                    json_data = json.loads(json_data)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                return f"JSON файл '{path}' успешно записан."
            
            # Работа с CSV
            elif action == "read_csv":
                result = []
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        result.append(dict(row))
                return result
            elif action == "write_csv":
                csv_data = kwargs.get("csv_data")
                fieldnames = kwargs.get("fieldnames", [])
                if not csv_data:
                    return "Не указаны данные для CSV (csv_data)."
                with open(path, "w", newline="", encoding="utf-8") as f:
                    if fieldnames:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(csv_data)
                    else:
                        writer = csv.writer(f)
                        writer.writerows(csv_data)
                return f"CSV файл '{path}' успешно записан."
            
            # Поиск файлов
            elif action == "find":
                pattern = kwargs.get("pattern", "*")
                recursive = kwargs.get("recursive", False)
                if recursive:
                    pattern = f"**/{pattern}"
                    results = glob.glob(os.path.join(path, pattern), recursive=True)
                else:
                    results = glob.glob(os.path.join(path, pattern))
                return results
            
            # Информация о файле
            elif action == "info":
                if not os.path.exists(path):
                    return f"Путь '{path}' не существует."
                
                stat = os.stat(path)
                info = {
                    "path": path,
                    "exists": True,
                    "is_file": os.path.isfile(path),
                    "is_dir": os.path.isdir(path),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                }
                
                if os.path.isfile(path):
                    info["mime_type"] = mimetypes.guess_type(path)[0]
                    info["extension"] = Path(path).suffix
                
                return info
            
            # Хеширование файла
            elif action == "hash":
                algorithm = kwargs.get("algorithm", "md5").lower()
                if algorithm not in ["md5", "sha1", "sha256", "sha512"]:
                    return f"Неподдерживаемый алгоритм: {algorithm}"
                
                hash_obj = hashlib.new(algorithm)
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_obj.update(chunk)
                return hash_obj.hexdigest()
            
            # Создание архива
            elif action == "create_zip":
                files_to_zip = kwargs.get("files", [])
                if not files_to_zip:
                    return "Не указаны файлы для архивирования (files)."
                
                with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files_to_zip:
                        if os.path.exists(file_path):
                            if os.path.isfile(file_path):
                                zipf.write(file_path, os.path.basename(file_path))
                            elif os.path.isdir(file_path):
                                for root, dirs, files in os.walk(file_path):
                                    for file in files:
                                        file_full_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_full_path, os.path.dirname(file_path))
                                        zipf.write(file_full_path, arcname)
                return f"Архив '{path}' создан с {len(files_to_zip)} элементами."
            
            # Извлечение архива
            elif action == "extract_zip":
                extract_to = kwargs.get("extract_to", os.path.dirname(path))
                with zipfile.ZipFile(path, "r") as zipf:
                    zipf.extractall(extract_to)
                return f"Архив '{path}' извлечён в '{extract_to}'."
            
            # Список содержимого архива
            elif action == "list_zip":
                with zipfile.ZipFile(path, "r") as zipf:
                    return zipf.namelist()
            
            # Подсчёт строк в файле
            elif action == "count_lines":
                with open(path, "r", encoding="utf-8") as f:
                    return sum(1 for line in f)
            
            # Поиск текста в файле
            elif action == "search_text":
                search_term = kwargs.get("search_term", data)
                case_sensitive = kwargs.get("case_sensitive", False)
                results = []
                
                with open(path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line_to_search = line if case_sensitive else line.lower()
                        term_to_search = search_term if case_sensitive else search_term.lower()
                        
                        if term_to_search in line_to_search:
                            results.append({
                                "line_number": line_num,
                                "line_content": line.strip(),
                                "position": line_to_search.find(term_to_search)
                            })
                
                return results
            
            # Замена текста в файле
            elif action == "replace_text":
                old_text = kwargs.get("old_text")
                new_text = kwargs.get("new_text", data)
                if not old_text:
                    return "Не указан текст для замены (old_text)."
                
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                updated_content = content.replace(old_text, new_text)
                
                with open(path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                
                count = content.count(old_text)
                return f"Заменено {count} вхождений текста в файле '{path}'."
            
            # Создание резервной копии
            elif action == "backup":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{path}.backup_{timestamp}"
                shutil.copy2(path, backup_path)
                return f"Создана резервная копия: '{backup_path}'."
            
            # Сравнение файлов
            elif action == "compare":
                file2 = kwargs.get("file2")
                if not file2:
                    return "Не указан второй файл для сравнения (file2)."
                
                if not os.path.exists(file2):
                    return f"Второй файл '{file2}' не существует."
                
                # Сравнение размеров
                size1 = os.path.getsize(path)
                size2 = os.path.getsize(file2)
                
                # Сравнение хешей
                hash1 = self._get_file_hash(path)
                hash2 = self._get_file_hash(file2)
                
                return {
                    "file1": path,
                    "file2": file2,
                    "size1": size1,
                    "size2": size2,
                    "sizes_equal": size1 == size2,
                    "hash1": hash1,
                    "hash2": hash2,
                    "content_equal": hash1 == hash2
                }
            
            # Получение дерева директорий
            elif action == "tree":
                max_depth = kwargs.get("max_depth", 3)
                return self._get_directory_tree(path, max_depth)
            
            else:
                return f"Неизвестное действие: {action}. Доступные действия: read, write, append, delete, list, exists, mkdir, remove, copy, move, read_json, write_json, read_csv, write_csv, find, info, hash, create_zip, extract_zip, list_zip, count_lines, search_text, replace_text, backup, compare, tree"
        
        except Exception as e:
            return f"Ошибка файловой операции: {e}"
    
    def _get_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """Вспомогательный метод для получения хеша файла"""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def _get_directory_tree(self, root_path: str, max_depth: int, current_depth: int = 0) -> Dict:
        """Вспомогательный метод для получения дерева директорий"""
        if current_depth >= max_depth:
            return {"name": os.path.basename(root_path), "type": "directory", "truncated": True}
        
        tree = {
            "name": os.path.basename(root_path) or root_path,
            "type": "directory",
            "children": []
        }
        
        try:
            for item in sorted(os.listdir(root_path)):
                item_path = os.path.join(root_path, item)
                if os.path.isdir(item_path):
                    tree["children"].append(self._get_directory_tree(item_path, max_depth, current_depth + 1))
                else:
                    tree["children"].append({
                        "name": item,
                        "type": "file",
                        "size": os.path.getsize(item_path)
                    })
        except PermissionError:
            tree["error"] = "Permission denied"
        
        return tree
