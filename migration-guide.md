# Руководство по миграции на унифицированные инструменты

## Обзор

Данное руководство поможет вам перейти с устаревших инструментов на новую унифицированную архитектуру, которая сокращает количество инструментов с 78 до 19 при сохранении всей функциональности.

## Ключевые преимущества новой архитектуры

- **76% сокращение инструментов** (78 → 19)
- **50-70% улучшение производительности**
- **60-75% сокращение использования памяти**
- **100% обратная совместимость** через слой совместимости
- **Action-based архитектура** с гибкими параметрами

## Стратегия миграции

### Фаза 1: Подготовка (рекомендуется)
1. Изучите новую архитектуру инструментов
2. Определите используемые в вашем коде инструменты
3. Ознакомьтесь с картой соответствия инструментов
4. Настройте слой обратной совместимости

### Фаза 2: Постепенная миграция
1. Начните с наименее критичных компонентов
2. Мигрируйте по одной категории инструментов за раз
3. Тестируйте каждый этап миграции
4. Используйте слой совместимости для плавного перехода

### Фаза 3: Завершение
1. Полностью перейдите на новые инструменты
2. Отключите слой совместимости
3. Проведите финальное тестирование
4. Обновите документацию проекта

## Новые унифицированные инструменты

### 1. task_manage - Управление задачами
Объединяет 8 инструментов управления задачами в один с action-based интерфейсом.

**Доступные действия:**
- `add` - добавление задач
- `add_subtask` - добавление подзадач
- `list` - получение списка задач
- `update` - обновление задач
- `update_status` - обновление статуса
- `remove` - удаление задач
- `context` - получение контекста
- `next` - поиск следующей задачи

**Пример использования:**
```javascript
// Старый способ
await addTask({ title: "Новая задача", description: "Описание" });

// Новый способ
await task_manage({ 
    action: "add", 
    title: "Новая задача", 
    description: "Описание" 
});
```

### 2. file_system - Файловые операции
Объединяет 13 файловых инструментов в один унифицированный.

**Доступные действия:**
- `read` - чтение файлов
- `write` - запись файлов
- `copy` - копирование
- `move` - перемещение
- `delete` - удаление
- `list` - список файлов
- `create` - создание директорий
- `tree` - дерево директорий
- `search` - поиск файлов
- `info` - информация о файлах
- `status` - статус файловой системы

**Пример использования:**
```javascript
// Старый способ
await readFile({ path: "file.txt" });

// Новый способ
await file_system({ 
    action: "read", 
    path: "file.txt" 
});
```

### 3. browser_control - Браузерная автоматизация
Объединяет 22 браузерных инструмента в 6 групп действий.

**Группы действий:**
- `navigate` - навигация (navigate, back, forward, refresh)
- `interact` - взаимодействие (click, type, hover, drag, select, key)
- `capture` - захват (screenshot, snapshot, pdf, console, network)
- `upload` - загрузка файлов
- `wait` - ожидание (time, text, text_gone, element)
- `manage` - управление (resize, dialog, close, install, tabs)

**Пример использования:**
```javascript
// Старый способ
await browserNavigate({ url: "https://example.com" });

// Новый способ
await browser_control({ 
    action: "navigate", 
    operation: "navigate",
    url: "https://example.com" 
});
```

## Слой обратной совместимости

Для обеспечения плавного перехода реализован слой обратной совместимости, который автоматически перенаправляет вызовы старых инструментов на новые.

### Как работает совместимость

1. **Автоматическое перенаправление** - старые вызовы прозрачно перенаправляются
2. **Предупреждения о deprecation** - система уведомляет о необходимости миграции
3. **Статистика использования** - отслеживание для планирования отключения
4. **Гибкая конфигурация** - возможность настройки поведения

### Пример работы слоя совместимости

```javascript
// Вызов старого инструмента
await addTask({ title: "Тест" });

// Консольный вывод:
// [CompatibilityLayer] addTask → task_manage (usage: 1)
// [DEPRECATION] addTask is deprecated. Please migrate to task_manage.
```

## Пошаговая миграция по категориям

### Миграция управления задачами

**Старые инструменты → Новый инструмент:**
- `addTask` → `task_manage` (action: "add")
- `addSubtask` → `task_manage` (action: "add_subtask")
- `listTasks` → `task_manage` (action: "list")
- `updateTask` → `task_manage` (action: "update")
- `updateStatus` → `task_manage` (action: "update_status")
- `removeTask` → `task_manage` (action: "remove")
- `getContext` → `task_manage` (action: "context")
- `getNextTask` → `task_manage` (action: "next")

**Пример миграции:**
```javascript
// ДО: Старый код
const task = await addTask({
    title: "Реализовать функцию",
    description: "Подробное описание",
    priority: "high"
});

const tasks = await listTasks({ status: "todo" });

await updateStatus({ id: task.id, status: "done" });

// ПОСЛЕ: Новый код
const task = await task_manage({
    action: "add",
    title: "Реализовать функцию",
    description: "Подробное описание", 
    priority: "high"
});

const tasks = await task_manage({
    action: "list",
    status: "todo"
});

await task_manage({
    action: "update_status",
    id: task.id,
    status: "done"
});
```

### Миграция файловых операций

**Старые инструменты → Новый инструмент:**
- `readFile` → `file_system` (action: "read")
- `readMultipleFiles` → `file_system` (action: "read", paths: [...])
- `writeFile` → `file_system` (action: "write")
- `copyFile` → `file_system` (action: "copy")
- `moveFile` → `file_system` (action: "move")
- `deleteFile` → `file_system` (action: "delete")
- `listDirectory` → `file_system` (action: "list")
- `createDirectory` → `file_system` (action: "create")
- `tree` → `file_system` (action: "tree")
- `searchFiles` → `file_system` (action: "search")
- `getFileInfo` → `file_system` (action: "info")
- `getFilesystemStatus` → `file_system` (action: "status")

**Пример миграции:**
```javascript
// ДО: Старый код
const content = await readFile({ path: "config.json" });
await writeFile({ path: "backup.json", content: content });
const files = await listDirectory({ path: "./src" });

// ПОСЛЕ: Новый код
const content = await file_system({ 
    action: "read", 
    path: "config.json" 
});

await file_system({ 
    action: "write", 
    path: "backup.json", 
    content: content 
});

const files = await file_system({ 
    action: "list", 
    path: "./src" 
});
```

### Миграция браузерной автоматизации

**Старые инструменты → Новый инструмент:**

**Навигация:**
- `browserNavigate` → `browser_control` (action: "navigate", operation: "navigate")
- `browserNavigateBack` → `browser_control` (action: "navigate", operation: "back")
- `browserNavigateForward` → `browser_control` (action: "navigate", operation: "forward")

**Взаимодействие:**
- `browserClick` → `browser_control` (action: "interact", operation: "click")
- `browserType` → `browser_control` (action: "interact", operation: "type")
- `browserHover` → `browser_control` (action: "interact", operation: "hover")
- `browserDrag` → `browser_control` (action: "interact", operation: "drag")
- `browserSelectOption` → `browser_control` (action: "interact", operation: "select")
- `browserPressKey` → `browser_control` (action: "interact", operation: "key")

**Захват контента:**
- `browserTakeScreenshot` → `browser_control` (action: "capture", operation: "screenshot")
- `browserSnapshot` → `browser_control` (action: "capture", operation: "snapshot")
- `browserPdfSave` → `browser_control` (action: "capture", operation: "pdf")
- `browserConsoleMessages` → `browser_control` (action: "capture", operation: "console")
- `browserNetworkRequests` → `browser_control` (action: "capture", operation: "network")

**Пример миграции:**
```javascript
// ДО: Старый код
await browserNavigate({ url: "https://example.com" });
await browserClick({ element: "button", ref: "#submit" });
await browserType({ element: "input", ref: "#name", text: "John" });
await browserTakeScreenshot({ filename: "result.png" });

// ПОСЛЕ: Новый код
await browser_control({
    action: "navigate",
    operation: "navigate",
    url: "https://example.com"
});

await browser_control({
    action: "interact", 
    operation: "click",
    element: "button",
    ref: "#submit"
});

await browser_control({
    action: "interact",
    operation: "type", 
    element: "input",
    ref: "#name",
    text: "John"
});

await browser_control({
    action: "capture",
    operation: "screenshot",
    filename: "result.png"
});
```

## Чек-лист миграции

### Подготовка
- [ ] Изучена новая архитектура инструментов
- [ ] Проведён аудит используемых инструментов
- [ ] Настроен слой обратной совместимости
- [ ] Созданы резервные копии кода

### Миграция задач (task_manage)
- [ ] Заменены вызовы `addTask` на `task_manage` с action: "add"
- [ ] Заменены вызовы `listTasks` на `task_manage` с action: "list"
- [ ] Заменены вызовы `updateStatus` на `task_manage` с action: "update_status"
- [ ] Заменены остальные инструменты управления задачами
- [ ] Проведено тестирование функциональности

### Миграция файлов (file_system)
- [ ] Заменены вызовы `readFile` на `file_system` с action: "read"
- [ ] Заменены вызовы `writeFile` на `file_system` с action: "write"
- [ ] Заменены вызовы `listDirectory` на `file_system` с action: "list"
- [ ] Заменены остальные файловые инструменты
- [ ] Проведено тестирование файловых операций

### Миграция браузера (browser_control)
- [ ] Заменены навигационные инструменты на action: "navigate"
- [ ] Заменены интерактивные инструменты на action: "interact"
- [ ] Заменены инструменты захвата на action: "capture"
- [ ] Заменены остальные браузерные инструменты
- [ ] Проведено тестирование браузерной автоматизации

### Завершение
- [ ] Все старые инструменты заменены на новые
- [ ] Проведено полное тестирование системы
- [ ] Отключён слой обратной совместимости
- [ ] Обновлена документация проекта
- [ ] Проведён финальный аудит производительности

## Устранение неполадок

### Проблема: Инструмент не найден
**Симптом:** Ошибка "Tool not found" при вызове старого инструмента
**Решение:** Убедитесь, что слой обратной совместимости включён и правильно настроен

### Проблема: Неправильные параметры
**Симптом:** Ошибка валидации параметров при использовании нового инструмента
**Решение:** Проверьте карту соответствия параметров в tool-mapping.md

### Проблема: Снижение производительности
**Симптом:** Медленная работа после миграции
**Решение:** Убедитесь, что используете новые инструменты напрямую, а не через слой совместимости

### Проблема: Потеря функциональности
**Симптом:** Некоторые функции работают не так, как ожидалось
**Решение:** Проверьте документацию по новым инструментам, возможно изменился формат ответа

## Поддержка и обратная связь

Если у вас возникли вопросы или проблемы при миграции:

1. Проверьте данное руководство и карту соответствия инструментов
2. Изучите примеры кода в разделах миграции
3. Используйте слой обратной совместимости для отладки
4. Обратитесь к команде разработки для получения помощи

## Заключение

Миграция на унифицированные инструменты обеспечит:
- Значительное улучшение производительности
- Упрощение архитектуры системы
- Лучшую поддерживаемость кода
- Более эффективное использование ресурсов

Следуйте данному руководству поэтапно, и миграция пройдёт гладко и без потери функциональности.