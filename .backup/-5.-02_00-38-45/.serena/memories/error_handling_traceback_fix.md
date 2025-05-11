# Исправление ошибки с модулем traceback

## Проблема

При запуске приложения возникла ошибка:

```
AttributeError: module 'traceback' has no attribute 'TracebackType'
```

Эта проблема появилась потому что в коде `error_handling.py` использовался тип `traceback.TracebackType`, но в Python 3.12 (который, вероятно, используется для запуска приложения) этот тип был перемещен из модуля `traceback` в модуль `types`.

## Решение

В файле `app/utils/error_handling.py` были внесены следующие изменения:

1. Добавлен импорт `TracebackType` из модуля `types`:
   ```python
   from types import TracebackType
   ```

2. Изменены аннотации типов в функции `set_global_exception_handler`:
   ```python
   def set_global_exception_handler(callback: Optional[Callable[[Type[BaseException], BaseException, TracebackType], None]] = None) -> None:
   ```

3. Исправлены типы в функции `default_exception_handler`:
   ```python
   def default_exception_handler(exc_type: Type[BaseException],
                              exc_value: BaseException,
                              exc_traceback: TracebackType) -> None:
   ```

## Примечание

Это изменение делает код совместимым с Python 3.12, сохраняя при этом обратную совместимость с более ранними версиями Python, поскольку модуль `types` и тип `TracebackType` существовали и раньше.

Обратите внимание, что при обновлении версии Python могут потребоваться и другие изменения для обеспечения совместимости, так как между версиями Python могут быть различия в API.