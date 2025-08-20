# Qt runJavaScript Official Documentation - Key Points

## Основные принципы из официальной документации Qt:

### 1. runJavaScript работает асинхронно
- Результат возвращается через callback функцию
- `page.runJavaScript("document.title", [](const QVariant &v) { qDebug() << v.toString(); });`
- В Python/PySide6 это должно быть lambda или обычная функция

### 2. Поддерживаемые типы данных для результата:
- JSON data types (object, array, string, number, boolean, null)
- Date, ArrayBuffer
- НЕ поддерживаются: Function, Promise

### 3. Важные предупреждения:
- "Do not execute lengthy routines in the callback function, because it might block the rendering of the web engine page"
- "We guarantee that the callback is always called, but it might be done during page destruction"
- "When QWebEnginePage is deleted, the callback is triggered with an invalid value"

### 4. Правильный подход для browser automation:
1. Выполнить JavaScript через runJavaScript
2. Получить результат в callback
3. Передать результат обратно в Python через QWebChannel
4. Не блокировать callback длительными операциями

### 5. QWebChannel для bridge:
- `channel.registerObject("bridge_name", python_object)`
- Объект должен иметь slots и signals для взаимодействия
- Методы с @Slot автоматически экспортируются в JavaScript

### 6. Современная архитектура Qt WebEngine:
- Multi-process architecture (отдельный процесс для rendering)
- Асинхронность обязательна для взаимодействия
- QWebFrame merged into QWebEnginePage
- Доступ к DOM только через JavaScript injection

## Правильная реализация browser automation:
1. JavaScript выполняется в runJavaScript
2. Результат передается в Python callback
3. Python callback НЕ должен делать тяжелые операции
4. Результат отправляется обратно в UI через QWebChannel bridge
5. UI получает результат и отображает пользователю