# Миграция к новой структуре Project Analyzer

Этот документ описывает изменения в структуре проекта и как обновить существующие скрипты.

## Что изменилось

### Старая структура (03_UTILITIES/)
```
03_UTILITIES/
├── analyze_project.py
├── quick_analyze.py
├── strict_analyzer.py
├── project_cleanup_analyzer.py
├── structure_analyzer.py
├── code_quality_analyzer.py
├── dead_code_analyzer.py
├── file_analyzer.py
├── dependency_analyzer.py
├── documentation_analyzer.py
├── duplicate_analyzer.py
├── conflict_analyzer.py
├── report_generator.py
├── project_cleanup_orchestrator.py
├── test_*_analyzer.py
└── *.bat файлы
```

### Новая структура (03_UTILITIES/project_analyzer/)
```
project_analyzer/
├── core/                    # Все анализаторы и основная логика
├── runners/                 # Исполняемые скрипты
├── tests/                   # Все тесты
├── utils/                   # Утилиты
└── README.md               # Документация
```

## Обновление импортов

### Старые импорты
```python
from project_cleanup_analyzer import AnalysisConfig, BaseAnalyzer
from structure_analyzer import StructureAnalyzer
from code_quality_analyzer import CodeQualityAnalyzer
```

### Новые импорты
```python
from project_analyzer.core import AnalysisConfig, BaseAnalyzer
from project_analyzer.core import StructureAnalyzer
from project_analyzer.core import CodeQualityAnalyzer

# Или все сразу:
from project_analyzer.core import (
    AnalysisConfig, BaseAnalyzer, StructureAnalyzer, CodeQualityAnalyzer
)
```

## Обновление путей к скриптам

### Старые команды
```bash
cd 03_UTILITIES
python analyze_project.py
python quick_analyze.py
```

### Новые команды
```bash
cd 03_UTILITIES/project_analyzer/runners
python analyze_project.py
python quick_analyze.py

# Или используйте batch файлы:
analyze_gopi_project.bat
quick_analyze.bat
```

## Обновление тестов

### Старый запуск тестов
```bash
cd 03_UTILITIES
python test_structure_analyzer.py
```

### Новый запуск тестов
```bash
cd 03_UTILITIES/project_analyzer/tests
python -m pytest test_structure_analyzer.py -v

# Или запуск всех тестов:
run_tests.bat
```

## Совместимость

### Устаревшие файлы
Следующие файлы в 03_UTILITIES теперь устарели и будут удалены в будущих версиях:
- `analyze_project.py` (используйте `project_analyzer/runners/analyze_project.py`)
- `quick_analyze.py` (используйте `project_analyzer/runners/quick_analyze.py`)
- `strict_analyzer.py` (используйте `project_analyzer/runners/strict_analyzer.py`)
- Все `*_analyzer.py` файлы (перемещены в `project_analyzer/core/`)
- Все `test_*.py` файлы (перемещены в `project_analyzer/tests/`)

### Переходный период
Для обеспечения совместимости старые файлы временно сохранены, но они выводят предупреждения об устаревании.

## Рекомендации по миграции

1. **Обновите импорты** в ваших скриптах согласно новой структуре
2. **Используйте новые пути** для запуска анализаторов
3. **Обновите документацию** и README файлы в ваших проектах
4. **Протестируйте** новую структуру перед удалением старых файлов

## Преимущества новой структуры

- **Модульность**: Четкое разделение компонентов
- **Тестируемость**: Все тесты в одном месте
- **Документация**: Улучшенная документация и примеры
- **Расширяемость**: Легче добавлять новые анализаторы
- **Поддержка**: Упрощенная поддержка и отладка

## Помощь

Если у вас возникли проблемы с миграцией:

1. Проверьте новые пути к файлам
2. Обновите импорты согласно этому документу
3. Используйте `demo_usage.py` для примеров использования
4. Запустите тесты для проверки работоспособности