"""
Пример использования Smart Workspace Indexer

Демонстрирует основные возможности системы индексации рабочего пространства.
"""

import os
import json
from pathlib import Path

from gopiai.extensions.workspace_indexer import get_workspace_indexer
from gopiai.extensions.mcp_workspace_integration import get_mcp_workspace_integration

def main():
    """Основная функция демонстрации"""
    print("🚀 Smart Workspace Indexer - Демонстрация возможностей")
    print("=" * 60)
    
    # Получаем индексатор
    indexer = get_workspace_indexer()
    
    # Используем текущую директорию как пример
    workspace_path = os.getcwd()
    print(f"📁 Анализируем рабочее пространство: {workspace_path}")
    print()
    
    # Выполняем индексацию
    print("⏳ Выполняем индексацию...")
    workspace_index = indexer.index_workspace(workspace_path)
    print("✅ Индексация завершена!")
    print()
    
    # Показываем общую информацию
    print("📊 ОБЩАЯ ИНФОРМАЦИЯ О ПРОЕКТЕ:")
    print("-" * 40)
    summary = indexer.get_project_summary(workspace_index)
    print(f"  {summary}")
    print()
    
    # Показываем детальную информацию
    project = workspace_index.project_info
    print("🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ:")
    print("-" * 40)
    print(f"  Тип проекта: {project.project_type}")
    print(f"  Основной язык: {project.primary_language}")
    print(f"  Всего файлов: {workspace_index.total_files}")
    print(f"  Общий размер: {indexer._format_size(workspace_index.total_size)}")
    print()
    
    if project.technologies:
        print(f"  🛠️  Технологии: {', '.join(project.technologies)}")
    
    if project.frameworks:
        print(f"  🏗️  Фреймворки: {', '.join(project.frameworks)}")
    
    if project.build_tools:
        print(f"  🔨 Инструменты сборки: {', '.join(project.build_tools)}")
    
    if project.package_managers:
        print(f"  📦 Менеджеры пакетов: {', '.join(project.package_managers)}")
    
    print()
    
    # Показываем структуру файлов
    print("📁 СТРУКТУРА ПРОЕКТА:")
    print("-" * 40)
    file_tree = indexer.get_file_tree_summary(workspace_index, max_depth=2)
    print(file_tree)
    print()
    
    # Показываем важные файлы
    if project.entry_points:
        print("🚀 ТОЧКИ ВХОДА:")
        for entry_point in project.entry_points[:5]:
            print(f"  • {entry_point}")
        print()
    
    if project.config_files:
        print("⚙️ ФАЙЛЫ КОНФИГУРАЦИИ:")
        for config_file in project.config_files[:5]:
            print(f"  • {config_file}")
        print()
    
    if project.test_directories:
        print("🧪 ДИРЕКТОРИИ ТЕСТОВ:")
        for test_dir in project.test_directories:
            print(f"  • {test_dir}")
        print()
    
    if project.documentation_files:
        print("📚 ДОКУМЕНТАЦИЯ:")
        for doc_file in project.documentation_files[:5]:
            print(f"  • {doc_file}")
        print()
    
    # Демонстрируем MCP интеграцию
    print("🔗 MCP ИНТЕГРАЦИЯ:")
    print("-" * 40)
    
    mcp_integration = get_mcp_workspace_integration()
    
    # Устанавливаем рабочее пространство
    result = mcp_integration.on_workspace_set(workspace_path)
    if result["success"]:
        print("✅ Рабочее пространство успешно установлено в MCP")
        print(f"  Краткое описание: {result['project_summary']}")
    else:
        print(f"❌ Ошибка установки рабочего пространства: {result['error']}")
    
    print()
    
    # Демонстрируем поиск файлов
    print("🔍 ПОИСК ФАЙЛОВ:")
    print("-" * 40)
    
    search_patterns = ["*.py", "*.js", "*.json", "README*"]
    
    for pattern in search_patterns:
        search_result = mcp_integration.search_files(pattern, max_results=5)
        if search_result["success"] and search_result["results"]:
            print(f"  📄 {pattern}: найдено {search_result['total_found']} файлов")
            for file_info in search_result["results"][:3]:
                size_str = f" ({indexer._format_size(file_info['size'])})" if file_info['size'] else ""
                print(f"    • {file_info['name']}{size_str}")
        else:
            print(f"  📄 {pattern}: файлы не найдены")
    
    print()
    
    # Демонстрируем рекомендации
    print("💡 РЕКОМЕНДАЦИИ ПО ТЕХНОЛОГИЯМ:")
    print("-" * 40)
    
    recommendations = mcp_integration.get_technology_recommendations()
    if recommendations["success"] and recommendations["recommendations"]:
        for rec in recommendations["recommendations"]:
            priority_icon = {
                "critical": "🚨",
                "high": "🔴", 
                "medium": "🟡",
                "low": "🟢"
            }.get(rec["priority"], "ℹ️")
            
            print(f"  {priority_icon} {rec['name']} ({rec['type']})")
            print(f"    {rec['reason']}")
    else:
        print("  ✅ Рекомендаций нет - проект хорошо настроен!")
    
    print()
    
    # Демонстрируем контекст для LLM
    print("🤖 КОНТЕКСТ ДЛЯ LLM:")
    print("-" * 40)
    
    llm_context = mcp_integration.get_workspace_context()
    if llm_context:
        # Показываем только первые 10 строк контекста
        context_lines = llm_context.split('\n')[:10]
        for line in context_lines:
            print(f"  {line}")
        
        if len(llm_context.split('\n')) > 10:
            print(f"  ... и ещё {len(llm_context.split('\n')) - 10} строк")
    else:
        print("  ❌ Контекст недоступен")
    
    print()
    
    # Демонстрируем кэширование
    print("💾 КЭШИРОВАНИЕ:")
    print("-" * 40)
    
    print("  ⏱️ Повторная индексация (должна использовать кэш)...")
    import time
    start_time = time.time()
    
    cached_index = indexer.index_workspace(workspace_path)
    
    elapsed = time.time() - start_time
    print(f"  ✅ Завершено за {elapsed:.3f}с (кэш: {cached_index.cache_key[:16]}...)")
    
    # Принудительное обновление
    print("  🔄 Принудительное обновление...")
    start_time = time.time()
    
    fresh_index = indexer.index_workspace(workspace_path, force_refresh=True)
    
    elapsed = time.time() - start_time
    print(f"  ✅ Завершено за {elapsed:.3f}с (новый кэш: {fresh_index.cache_key[:16]}...)")
    
    print()
    print("🎉 Демонстрация завершена!")
    print("=" * 60)

def create_test_project():
    """Создаёт тестовый проект для демонстрации"""
    test_dir = Path("test_workspace_demo")
    
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir()
    
    # Создаём package.json
    package_json = {
        "name": "demo-project",
        "version": "1.0.0",
        "description": "Демонстрационный проект для Smart Workspace Indexer",
        "main": "index.js",
        "scripts": {
            "start": "node index.js",
            "test": "jest"
        },
        "dependencies": {
            "react": "^18.0.0",
            "express": "^4.18.0"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "eslint": "^8.0.0"
        }
    }
    
    with open(test_dir / "package.json", "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2, ensure_ascii=False)
    
    # Создаём основные файлы
    (test_dir / "index.js").write_text("""
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
""".strip())
    
    (test_dir / "README.md").write_text("""
# Demo Project

Демонстрационный проект для тестирования Smart Workspace Indexer.

## Установка

```bash
npm install
```

## Запуск

```bash
npm start
```
""".strip())
    
    # Создаём структуру директорий
    (test_dir / "src").mkdir()
    (test_dir / "src" / "components").mkdir()
    (test_dir / "src" / "utils").mkdir()
    (test_dir / "tests").mkdir()
    
    # Создаём файлы в поддиректориях
    (test_dir / "src" / "App.js").write_text("// Main App component")
    (test_dir / "src" / "components" / "Header.js").write_text("// Header component")
    (test_dir / "src" / "utils" / "helpers.js").write_text("// Utility functions")
    (test_dir / "tests" / "app.test.js").write_text("// App tests")
    
    # Создаём .gitignore
    (test_dir / ".gitignore").write_text("""
node_modules/
*.log
.env
dist/
build/
""".strip())
    
    print(f"✅ Тестовый проект создан в: {test_dir.absolute()}")
    return str(test_dir.absolute())

if __name__ == "__main__":
    # Можно создать тестовый проект для демонстрации
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-test":
        test_path = create_test_project()
        print(f"Для демонстрации на тестовом проекте запустите:")
        print(f"cd {test_path} && python -m gopiai.extensions.examples.workspace_indexer_example")
    else:
        main()