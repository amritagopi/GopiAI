# dependency_explorer.py
import os
import json
import sys

def explore_dependencies(file_path=None, query=None, limit=20):
    """
    Создает облегченную карту зависимостей для конкретного файла или поиска
    """
    project_dir = "C:/Users/crazy/GopiAI"
    results = {"files": [], "dependencies": {}}
    
    # Собираем файлы для анализа
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                
                # Если указан конкретный файл или поисковый запрос
                if (file_path and file_path in rel_path) or \
                   (query and query.lower() in rel_path.lower()):
                    results["files"].append(rel_path)
    
    # Ограничиваем количество результатов
    results["files"] = results["files"][:limit]
    
    # Анализируем зависимости только для найденных файлов
    for rel_path in results["files"]:
        full_path = os.path.join(project_dir, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Простой поиск импортов
            import re
            imports = re.findall(r'(?:import|from)\s+[\'"]?([.\w]+)[\'"]?', content)
            results["dependencies"][rel_path] = imports
        except Exception as e:
            results["dependencies"][rel_path] = [f"Error: {str(e)}"]
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dependency_explorer.py [--file FILE_PATH | --search QUERY]")
        sys.exit(1)
    
    if sys.argv[1] == "--file" and len(sys.argv) > 2:
        result = explore_dependencies(file_path=sys.argv[2])
    elif sys.argv[1] == "--search" and len(sys.argv) > 2:
        result = explore_dependencies(query=sys.argv[2])
    else:
        print("Invalid arguments")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))