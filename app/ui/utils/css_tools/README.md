# CSS Tools для GopiAI

Набор утилит для работы с CSS/QSS файлами в проекте GopiAI.

## Содержимое

* `css_fixer.py` - Улучшенный инструмент для исправления дублирующихся селекторов
* `css_refactor.py` - Инструмент для рефакторинга CSS, извлечения цветов и создания цветовых переменных
* `fix_duplicate_selectors.py` - Инструмент для исправления вариаций селекторов
* `fonts_fixer.py` - Утилита для исправления файлов шрифтов CSS
* `theme_compiler.py` - Компилятор тем, интегрирующий систему цветов с QSS файлами
* `compile_themes.py` - Скрипт для компиляции всех тем GopiAI
* `cleanup.py` - Скрипт для очистки проекта от ненужных и временных файлов
* `fix_css.bat` - Пакетный файл для комплексного исправления CSS/QSS файлов
* `cleanup.bat` - Пакетный файл для запуска очистки проекта
* `fix_themes.bat` - Пакетный файл для исправления и компиляции тем проекта

## Использование

### Исправление дублирующихся селекторов в файле/директории

```bash
cd app\ui\utils\css_tools
python css_fixer.py <путь_к_файлу_или_директории>
```

### Рефакторинг CSS файла

```bash
cd app\ui\utils\css_tools
python css_refactor.py <путь_к_файлу> [--fix-duplicates] [--fix-colors] [--output <выходной_файл>]
```

### Компиляция тем

```bash
cd app\ui\utils\css_tools
python compile_themes.py
```

### Запуск всех утилит CSS вместе

```bash
cd app\ui\utils\css_tools
.\fix_css.bat
```

### Очистка проекта от ненужных файлов

```bash
cd app\ui\utils\css_tools
python cleanup.py [--move] [--temp] [--force]
```

Опции:
- `--move` или `-m`: Переместить файлы в директорию css_tools вместо удаления
- `--temp` или `-t`: Найти и удалить временные файлы (*.tmp, *.bak, *.log)
- `--force` или `-f`: Принудительно заменить существующие файлы

### Обработка специальных файлов

Скрипт `cleanup.py` также перемещает особые файлы в правильные директории:

- `theme_manager.py` из корневой директории → в `app/ui/utils/`
- `simple_ui_auditor_final.py` из корневой директории → в `app/ui/utils/`

Если файл уже существует в целевой директории, скрипт проверяет версию и при необходимости создает резервную копию перед обновлением.

### Использование через пакетные файлы

Для удобства доступны интерактивные пакетные файлы:

```bash
# Из корневой директории проекта
.\css_tools.bat

# Или из директории утилит
cd app\ui\utils\css_tools
.\cleanup.bat
```

## Программное использование

Вы также можете использовать эти утилиты как модуль в вашем Python-коде:

```python
from app.ui.utils.css_tools import fix_css_file, fix_duplicate_selectors, fix_hardcoded_colors
from app.ui.utils.css_tools import cleanup_files, find_temp_files

# Исправление CSS файла
fix_css_file('path/to/file.css')

# Исправление дублирующихся селекторов
fix_duplicate_selectors('path/to/file.css')

# Исправление хардкодированных цветов
fix_hardcoded_colors('path/to/file.css')

# Очистка ненужных файлов
cleanup_files(['file1.tmp', 'file2.bak'], root_dir='/path/to/project')

# Поиск временных файлов
temp_files = find_temp_files('/path/to/project')
```

## Пути к файлам

- Основные файлы тем: `app\ui\themes\DARK-theme.qss` и `app\ui\themes\LIGHT-theme.qss`
- Скомпилированные темы: `app\ui\themes\compiled\`
- Файлы шрифтов: `assets\fonts\fonts.css` и `assets\fonts\fonts-fixed.css`
- Файлы управления темами: `app\ui\theme_manager.py` и `app\ui\utils\theme_manager.py`
- Утилиты UI: `app\ui\utils\simple_ui_auditor_final.py`
