# Решение проблем с подключением сигналов в UI компонентах

## Проблема

В проекте GopiAI были обнаружены следующие проблемы с сигналами Qt:

1. Ошибка: `ERROR:app.ui.agent_ui_integration:Error connecting editor and chat signals: 'PySide6.QtCore.Signal' object has no attribute 'connect'`
2. Ошибки при подключении сигналов между различными компонентами интерфейса (чат, редактор, терминал)
3. Отсутствие некоторых определений сигналов в классах
4. Отсутствие необходимых методов в классах для обработки сигналов

## Решение

### 1. Дополнение класса ChatWidget

Добавлены недостающие сигналы в классе ChatWidget (`app/ui/widgets.py`):

```python
class ChatWidget(QWidget):
    message_sent = Signal(str) # <--- Сигнал для отправки сообщений
    insert_code_to_editor = Signal(str) # <--- Сигнал для вставки кода в редактор
    run_code_in_terminal = Signal(str) # <--- Сигнал для запуска кода в терминале
```

Также добавлены необходимые методы для корректной обработки сигналов:

```python
def add_message(self, sender, text):
    """Добавляет сообщение в историю чата."""
    message = f"<b>{sender}:</b> {text}"
    self.chat_history.append(message)

def _extract_code_from_selection(self, text):
    """Извлекает код из выделенного текста."""
    import re
    markdown_code_match = re.search(r'```(?:\w*\n)?([\s\S]*?)```', text)
    if markdown_code_match:
        return markdown_code_match.group(1)
    return text
```

### 2. Обновление класса CodeEditor

Добавлен метод для вставки кода в редактор:

```python
def insert_code(self, code):
    """Insert code at the current cursor position."""
    cursor = self.textCursor()
    cursor.insertText(code)
    self.setTextCursor(cursor)
```

### 3. Дополнение класса TerminalWidget

Добавлена реализация метода `execute_command`, который вызывается из обработчиков сигналов:

```python
def execute_command(self, command):
    """Execute a command in the terminal."""
    # Display the command in the output
    self.terminal_output.append(f"> {command}")

    # Actual implementation would connect to a real terminal/process
    # For now, just simulate output
    self.terminal_output.append("Command executed (this is a placeholder)")
```

### 4. Улучшение обработки ошибок при подключении сигналов

Обновление функции `_connect_editor_chat_signals` в `app/ui/docks.py` для корректной обработки ошибок:

```python
# Соединяем сигналы от чата к редактору
if hasattr(chat_widget, "insert_code_to_editor") and hasattr(editor_widget, "insert_code"):
    try:
        chat_widget.insert_code_to_editor.connect(editor_widget.insert_code)
        logger.info("Connected chat insert_code_to_editor signal to editor insert_code")
    except Exception as e:
        logger.error(f"Error connecting chat insert_code_to_editor: {str(e)}")
```

### 5. Защита подключения сигналов в create_docks

Обернули подключение сигналов в блок try-except и добавили проверки на наличие сигналов:

```python
# Connect chat_widget's message_sent signal to the new handler
try:
    if hasattr(main_window.chat_widget, "message_sent"):
        main_window.chat_widget.message_sent.connect(lambda msg: handle_user_message(main_window, msg))
        logger.info("Connected chat widget message_sent signal to handle_user_message")
    else:
        logger.warning("Chat widget does not have message_sent signal")
except Exception as e:
    logger.error(f"Error connecting chat widget message_sent signal: {str(e)}")
```

## Принципы предотвращения подобных ошибок

1. **Всегда проверяйте наличие сигналов и слотов перед подключением**
   ```python
   if hasattr(widget, "signal") and hasattr(target, "slot"):
       widget.signal.connect(target.slot)
   ```

2. **Оборачивайте подключение сигналов в try-except**
   ```python
   try:
       widget.signal.connect(target.slot)
   except Exception as e:
       logger.error(f"Error connecting signal: {str(e)}")
   ```

3. **Объявляйте все сигналы в самом начале класса**
   ```python
   class MyWidget(QWidget):
       signal1 = Signal(str)
       signal2 = Signal(int)
       # Остальной код класса...
   ```

4. **Используйте типизированные сигналы с документацией**
   ```python
   # Правильно
   message_sent = Signal(str)  # Сигнал для отправки сообщений

   # Менее понятно
   message_sent = Signal()  # Без типа и документации
   ```

5. **Централизуйте подключение сигналов**
   Выделите отдельные методы или модули для подключения сигналов, чтобы упростить отладку и поддержку.

## Результаты

После внесения всех изменений ошибка `'PySide6.QtCore.Signal' object has no attribute 'connect'` больше не возникает, и сигналы между компонентами UI корректно подключаются.

Остались предупреждения об отсутствии некоторых компонентов для интеграции с агентами, но они не связаны с проблемами сигналов и могут быть решены отдельно.
