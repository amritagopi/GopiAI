# Project Analyzer

Комплексная система анализа проекта GOPI_AI_MODULES с модульной архитектурой и различными уровнями детализации.

## Структура

```
project_analyzer/
├── README.md                    # Этот файл
├── core/                        # Основные анализаторы
│   ├── analyzer_cache.py        # Система кэширования
│   ├── project_cleanup_analyzer.py  # Базовые классы
│   ├── project_cleanup_orchestrator.py  # Оркестратор
│   ├── report_generator.py     # Генератор отчетов
│   ├── structure_analyzer.py   # Анализатор структуры
│   ├── code_quality_analyzer.py # Анализатор качества кода
│   ├── dead_code_analyzer.py   # Анализатор мертвого кода
│   ├── file_analyzer.py        # Анализатор файлов
│   ├── dependency_analyzer.py  # Анализатор зависимостей
│   ├── duplicate_analyzer.py   # Анализатор дублирующегося кода
│   ├── conflict_analyzer.py    # Анализатор конфликтов
│   └── documentation_analyzer.py # Анализатор документации
├── runners/                     # Скрипты запуска
│   ├── analyze_project.py      # Полный анализ проекта
│   ├── quick_analyze.py        # Быстрый анализ
│   ├── strict_analyzer.py      # Строго ограниченный анализ
│   ├── analyze_gopi_project.bat # Batch для полного анализа
│   ├── quick_analyze.bat       # Batch для быстрого анализа
│   └── strict_analyze.bat      # Batch для строгого анализа
├── tests/                       # Тесты
│   ├── test_analyzer_cache.py  # Тесты кэширования
│   ├── test_comprehensive_suite.py # Комплексные тесты
│   ├── test_dependency_fix.py  # Тест исправления зависимостей
│   ├── test_project_generator.py # Генератор тестовых проектов
│   └── run_tests.bat           # Запуск всех тестов
└── utils/                       # Утилиты
    ├── generate_test_data.py   # Генератор тестовых данных
    ├── performance_test.py     # Тесты производительности
    └── manual_analyzer.py      # Ручной анализатор
```

## Использование

### Быстрый старт

Для быстрого анализа проекта:
```batch
cd 03_UTILITIES/project_analyzer/runners
strict_analyze.bat --skip-duplicate
```

### Полный анализ

Для полного анализа проекта:
```batch
cd 03_UTILITIES/project_analyzer/runners
analyze_gopi_project.bat
```

### Быстрый анализ

Для быстрого анализа без ограничений:
```batch
cd 03_UTILITIES/project_analyzer/runners
quick_analyze.bat
```

## Опции

### Общие опции для всех анализаторов:
- `--skip-duplicate` - Пропустить анализ дублирующегося кода
- `--skip-conflict` - Пропустить анализ конфликтов
- `--max-files N` - Ограничить количество файлов для анализа
- `--timeout N` - Установить таймаут для анализаторов (в секундах)
- `--format FORMAT` - Формат отчета (markdown, html, json)
- `--html` - Сокращение для `--format html`
- `--json` - Сокращение для `--format json`

### Примеры использования:

```batch
# Быстрый анализ без дублирующегося кода в HTML формате
strict_analyze.bat --skip-duplicate --html

# Анализ с таймаутом 10 минут (без ограничений по файлам)
quick_analyze.bat --timeout 600

# Полный анализ в JSON формате
analyze_gopi_project.bat --json
```

## Отчеты

Все отчеты сохраняются в директории `project_health/reports/` в корне проекта.

## Тестирование

Для запуска тестов:
```batch
cd 03_UTILITIES/project_analyzer/tests
run_tests.bat
```
