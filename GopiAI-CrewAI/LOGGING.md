# Настройка логирования в GopiAI

## Обновленная конфигурация логов

Все серверы теперь используют **перезаписываемые логи** вместо накопления данных.

### Изменения

**До:**
```python
logging.FileHandler(log_file, encoding='utf-8')  # Режим 'append' по умолчанию
```

**После:**
```python
logging.FileHandler(log_file, mode='w', encoding='utf-8')  # Режим перезаписи
```

### Обновленные серверы

1. **crewai_api_server.py**
   - Локальный лог: `crewai_api_server_debug_local.log` 
   - Системный лог: `~/.gopiai/logs/crewai_api_server_debug.log`
   - Режим: перезапись при каждом запуске

2. **gemini_server_clean.py**
   - Лог: `gemini_server_clean.log`
   - Режим: перезапись при каждом запуске

3. **simple_agents_server.py**
   - Лог: `simple_agents_server.log`
   - Режим: перезапись при каждом запуске

### Преимущества

✅ **Чистые логи** - нет накопления старых данных  
✅ **Экономия места** - логи не растут бесконечно  
✅ **Легче отладка** - только актуальная сессия  
✅ **Быстрый поиск** - меньше данных для анализа  

### Пример результата

**До изменений:**
```bash
-rw-rw-r-- 1 user user 260K сен 5 17:35 crewai_api_server_debug_local.log
```

**После изменений:**
```bash
-rw-rw-r-- 1 user user 3.0K сен 5 17:44 crewai_api_server_debug_local.log
```

### Совместимость

Изменение не влияет на функциональность серверов - только на управление логами.