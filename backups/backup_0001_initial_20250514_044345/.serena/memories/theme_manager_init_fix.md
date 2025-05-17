# Решение проблемы с инициализацией ThemeManager

## Проблема
ThemeManager инициализировался до создания QApplication, из-за чего возникала ошибка:
```
ThemeManager: QApplication.instance() is None
```

Причина состояла в том, что импорт ThemeManager происходил на уровне модуля в нескольких файлах, что вызывало его инициализацию до создания QApplication в main.py.

## Решение

1. В `main.py` изменили порядок инициализации:
   - Сначала создается QApplication
   - Затем импортируется и инициализируется ThemeManager

2. В `app/ui/main_window.py` перенесли импорт ThemeManager с глобального уровня внутрь метода `__init__` класса MainWindow:
   ```python
   def __init__(self, icon_manager, parent=None):
       super().__init__(parent)
       self.icon_manager = icon_manager
       
       # Теперь импортируем ThemeManager, когда QApplication уже создан
       from app.utils.theme_manager import ThemeManager
       
       # ...остальной код...
       self.theme_manager = ThemeManager.instance()
   ```

3. В `app/utils/theme_manager.py` добавили обработку случая, когда QApplication.instance() возвращает None:
   - Добавили логирование с предупреждением
   - Обеспечили возможность загрузки тем даже при отсутствии QApplication
   - Добавили проверку наличия QApplication перед применением темы в методе switch_visual_theme

## Примечание
При импорте модулей UI в проекте важно следить за порядком инициализации и избегать использования QApplication-зависимых компонентов до создания экземпляра QApplication. Предпочтительно использовать локальные импорты внутри методов для модулей, которые зависят от QApplication.