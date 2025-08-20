# Список файлов для очистки в 03_UTILITIES

После миграции к новой структуре project_analyzer следующие файлы в 03_UTILITIES можно безопасно удалить.

## Файлы анализаторов (перемещены в project_analyzer/core/)

### Основные анализаторы
- `structure_analyzer.py` → `project_analyzer/core/structure_analyzer.py`
- `code_quality_analyzer.py` → `project_analyzer/core/code_quality_analyzer.py`
- `dead_code_analyzer.py` → `project_analyzer/core/dead_code_analyzer.py`
- `file_analyzer.py` → `project_analyzer/core/file_analyzer.py`
- `dependency_analyzer.py` → `project_analyzer/core/dependency_analyzer.py`
- `documentation_analyzer.py` → `project_analyzer/core/documentation_analyzer.py`
- `duplicate_analyzer.py` → `project_analyzer/core/duplicate_analyzer.py`
- `conflict_analyzer.py` → `project_analyzer/core/conflict_analyzer.py`

### Инфраструктура
- `project_cleanup_analyzer.py` → `project_analyzer/core/project_cleanup_analyzer.py`
- `project_cleanup_orchestrator.py` → `project_analyzer/core/project_cleanup_orchestrator.py`
- `report_generator.py` → `project_analyzer/core/report_generator.py`
- `project_cleanup_cli.py` → `project_analyzer/core/project_cleanup_cli.py`

## Исполняемые скрипты (перемещены в project_analyzer/runners/)

### Python скрипты
- `analyze_project.py` → `project_analyzer/runners/analyze_project.py`
- `quick_analyze.py` → `project_analyzer/runners/quick_analyze.py`
- `strict_analyzer.py` → `project_analyzer/runners/strict_analyzer.py`

### Batch файлы
- `analyze_gopi_project.bat` → `project_analyzer/runners/analyze_gopi_project.bat`
- `quick_analyze.bat` → `project_analyzer/runners/quick_analyze.bat`
- `strict_analyze.bat` → `project_analyzer/runners/strict_analyze.bat`

## Тестовые файлы (перемещены в project_analyzer/tests/)

### Тесты анализаторов
- `test_structure_analyzer.py`
- `test_code_quality_analyzer.py`
- `test_code_quality_analyzer_unit.py`
- `test_code_quality_simple.py`
- `test_dead_code_analyzer.py`
- `test_file_analyzer.py`
- `test_dependency_analyzer.py`
- `test_dependency_fix.py`
- `test_documentation_analyzer.py`
- `test_duplicate_analyzer.py`
- `test_duplicate_comprehensive.py`
- `test_duplicate_simple.py`
- `test_duplicate_unit.py`
- `test_conflict_analyzer.py`

### Тесты инфраструктуры
- `test_cleanup_infrastructure.py`
- `test_report_generator.py`
- `test_project_cleanup_cli.py`
- `test_comprehensive_suite.py`
- `test_project_generator.py`

## Утилиты (перемещены в project_analyzer/utils/)

- `analyzer_cache.py` → `project_analyzer/utils/analyzer_cache.py`
- `simple_analyzer_cache.py` → `project_analyzer/utils/simple_analyzer_cache.py`

## Устаревшие файлы

Эти файлы больше не используются и могут быть удалены:

### Старые анализаторы
- `simple_analyzer.py` (заменен на новую архитектуру)
- `simple_cleanup_analyzer.py` (заменен на новую архитектуру)
- `manual_analyzer.py` (функциональность интегрирована)

### Старые batch файлы
- `simple_cleanup_analyzer.bat`
- `project_cleanup_analyzer.bat`

### Старые тесты
- `test_analyzer_cache.py` (перемещен в utils)

## Документация (устарела)

- `README_CLEANUP_ANALYZER.md` (заменен на project_analyzer/README.md)
- `README_CLEANUP_CLI.md` (интегрирован в основную документацию)

## Логи и временные файлы

- `project_cleanup_*.log` (старые логи)
- `strict_analyzer.log` (старые логи)

## Команда для очистки

После проверки работоспособности новой структуры можно выполнить:

```bash
# ВНИМАНИЕ: Сначала убедитесь, что новая структура работает!

# Удаление анализаторов
rm 03_UTILITIES/*_analyzer.py

# Удаление старых скриптов
rm 03_UTILITIES/analyze_project.py
rm 03_UTILITIES/quick_analyze.py
rm 03_UTILITIES/strict_analyzer.py

# Удаление тестов
rm 03_UTILITIES/test_*.py

# Удаление утилит
rm 03_UTILITIES/analyzer_cache.py
rm 03_UTILITIES/simple_analyzer_cache.py

# Удаление batch файлов
rm 03_UTILITIES/*analyze*.bat
rm 03_UTILITIES/simple_cleanup_analyzer.bat
rm 03_UTILITIES/project_cleanup_analyzer.bat

# Удаление устаревшей документации
rm 03_UTILITIES/README_CLEANUP_*.md

# Удаление старых логов
rm 03_UTILITIES/project_cleanup_*.log
rm 03_UTILITIES/strict_analyzer.log
```

## Проверка перед удалением

Перед удалением файлов убедитесь, что:

1. ✅ Новая структура project_analyzer работает корректно
2. ✅ Все тесты проходят: `cd project_analyzer/tests && run_tests.bat`
3. ✅ Анализаторы запускаются без ошибок
4. ✅ Отчеты генерируются правильно
5. ✅ Нет зависимостей от старых файлов в других частях проекта

## Сохранить в 03_UTILITIES

Следующие файлы НЕ связаны с анализаторами и должны остаться:

- `add_rag_logging.py`
- `chat_logger.py`
- `check_class.py`
- `check_serena_tools.py`
- `clean_project.py`
- `cleanup_script.ps1`
- `console-logger.js`
- `debug_launcher.py`
- `enable_debug_logging.py`
- `encoding_fix.py`
- `example_rag_usage.py`
- `files_to_delete.txt`
- `fix_encoding.py`
- `fixed_cli.py`
- `fixed_logging.py`
- `generate_test_data.py`
- `gopiai_detailed_logger.py`
- `install_all_modules.*`
- `kill_port.bat`
- `launcher.py`
- `list_models.py`
- `performance_test.py`
- `rag_cleanup_wizard.py`
- `reproduce_hang_with_debug.py`
- `run_*.py`
- `scripts_*.py`
- `setup_modules_updated.py`
- `update_project_map.py`
- `verify_no_rag_calls.py`
- `view_memory.py`
- `scripts_README.md`