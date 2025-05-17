# Исправление ошибки импорта theme_manager

В проекте обнаружена проблема с импортом `theme_manager`. Критическая ошибка при запуске:

```
ImportError: cannot import name 'theme_manager' from 'app.utils.theme_manager'
```

## Проблема

1. В файле `app/utils/__init__.py` был импорт:
   ```python
   from .theme_manager import theme_manager
   ```

2. Но в файле `app/utils/theme_manager.py` не существует переменной `theme_manager`. Вместо этого есть класс `ThemeManager` с методом класса `instance()`, который реализует паттерн Singleton.

## Решение

Файл `app/utils/__init__.py` был исправлен:

```python
from .theme_manager import ThemeManager
# ...
# Создаем экземпляр ThemeManager для использования в других модулях
theme_manager = ThemeManager.instance()
```

Теперь другие модули могут правильно импортировать `theme_manager`:

```python
from app.utils import theme_manager
```

## Примечание

Такой подход с созданием экземпляров в `__init__.py` позволяет упростить импорты и обеспечить единственный экземпляр для синглтонов, даже если название класса и экземпляра различаются.