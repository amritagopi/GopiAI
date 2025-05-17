# Добавление эмодзи в контекстное меню

## Проблема
Пользователь не мог вызвать диалог выбора эмодзи через контекстное меню (правая кнопка мыши) в различных текстовых полях приложения. Опция была доступна только через кнопку в интерфейсе.

## Решение
Добавил опцию "Insert Emoji" в контекстное меню для следующих виджетов:

1. `ChatHistoryWidget` в файле `app/ui/coding_agent_dialog.py`
2. `ChatHistoryWidget` в файле `app/ui/browser_agent_dialog.py`

В каждом из этих файлов:
1. Расширил метод `contextMenuEvent` для добавления пункта "Insert Emoji" с иконкой
2. Добавил метод `_show_emoji_dialog` для вызова диалога выбора эмодзи
3. Добавил проверку `if not self.isReadOnly()`, чтобы пункт меню отображался только в редактируемых полях
4. Настроил корректное позиционирование диалога на экране

Пример добавленного кода:
```python
# Добавляем разделитель и пункт для вставки эмодзи
menu.addSeparator()

# Импортируем функцию для получения Lucide иконок
from app.ui.lucide_icon_manager import get_lucide_icon

emoji_action = QAction(tr("menu.insert_emoji", "Insert Emoji"), self)
emoji_action.setIcon(get_lucide_icon("smile"))

# Используем глобальную позицию курсора для отображения диалога
global_pos = event.globalPos()
emoji_action.triggered.connect(lambda: self._show_emoji_dialog(global_pos))
menu.addAction(emoji_action)
```

Теперь пользователь может вызвать диалог эмодзи через контекстное меню правой кнопки мыши в текстовых полях приложения.