# ⚙️ TASK 1.4: ПЕРЕПИСАТЬ COMMANDEXECUTOR

## 🎯 ЦЕЛЬ
Изменить интерфейс CommandExecutor для работы с нативным Tool Calling. Убрать парсинг текста и реализовать прямые вызовы методов по именам функций.

## 📁 ЦЕЛЕВЫЕ ФАЙЛЫ
- `GopiAI-CrewAI/tools/gopiai_integration/command_executor.py`
- Возможно `terminal_tool.py`, `browser_tool.py` и другие

## 🔍 ТЕКУЩАЯ ПРОБЛЕМА

### Старый интерфейс (сломанный):
```python
# CommandExecutor пытается парсить команды из текста
executor.execute_from_text("lss -la /home/user")  # Не работает!
```

### Новый интерфейс (нативный):
```python
# CommandExecutor получает имя функции и аргументы напрямую
executor.execute_terminal_command("ls -la /home/user")  # Работает!
executor.browse_website("https://example.com")
executor.web_search("python tutorial", num_results=5)
```

## 🛠️ НОВАЯ АРХИТЕКТУРА COMMANDEXECUTOR

### 1. Базовый класс:
```python
import logging
import subprocess
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class CommandExecutor:
    """
    Исполнитель команд с нативным интерфейсом для Tool Calling
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.allowed_commands = [
            'ls', 'dir', 'pwd', 'cd', 'cat', 'type', 'echo', 
            'pip', 'python', 'node', 'npm', 'git'
        ]
        self.working_directory = os.getcwd()
        
    def execute_terminal_command(self, command: str, working_directory: str = None) -> str:
        """
        Выполняет команду в терминале
        
        Args:
            command: Команда для выполнения
            working_directory: Рабочая директория (опционально)
            
        Returns:
            str: Результат выполнения команды
        """
        try:
            # Проверяем безопасность команды
            if not self._is_command_safe(command):
                return f"ОШИБКА: Команда '{command}' не разрешена для выполнения"
            
            # Определяем рабочую директорию
            work_dir = working_directory or self.working_directory
            
            self.logger.info(f"Выполняем команду: {command} в {work_dir}")
            
            # Выполняем команду
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30  # Таймаут 30 секунд
            )
            
            # Формируем ответ
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            if result.returncode != 0:
                output += f"EXIT CODE: {result.returncode}\n"
                
            return output or "Команда выполнена успешно (нет вывода)"
            
        except subprocess.TimeoutExpired:
            return "ОШИБКА: Команда превысила лимит времени выполнения (30 сек)"
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды '{command}': {e}")
            return f"ОШИБКА: {str(e)}"
    
    def browse_website(self, url: str, extract_text: bool = True) -> str:
        """
        Открывает веб-страницу и извлекает содержимое
        
        Args:
            url: URL для открытия
            extract_text: Извлекать только текст без HTML
            
        Returns:
            str: Содержимое страницы
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            self.logger.info(f"Открываем веб-страницу: {url}")
            
            # Делаем запрос
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if extract_text:
                # Извлекаем только текст
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Удаляем скрипты и стили
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                # Очищаем от лишних пробелов
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Ограничиваем длину
                if len(text) > 5000:
                    text = text[:5000] + "... [содержимое обрезано]"
                
                return f"Содержимое страницы {url}:\n\n{text}"
            else:
                # Возвращаем HTML
                html = response.text
                if len(html) > 10000:
                    html = html[:10000] + "... [HTML обрезан]"
                return f"HTML код страницы {url}:\n\n{html}"
                
        except requests.RequestException as e:
            return f"ОШИБКА: Не удалось загрузить страницу {url}: {str(e)}"
        except Exception as e:
            self.logger.error(f"Ошибка при открытии {url}: {e}")
            return f"ОШИБКА: {str(e)}"
    
    def web_search(self, query: str, num_results: int = 5) -> str:
        """
        Выполняет поиск в интернете
        
        Args:
            query: Поисковый запрос
            num_results: Количество результатов
            
        Returns:
            str: Результаты поиска
        """
        try:
            # Здесь можно использовать различные поисковые API
            # Для примера используем DuckDuckGo (не требует API ключа)
            
            import requests
            
            self.logger.info(f"Поиск в интернете: {query}")
            
            # Простой поиск через DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Основной ответ
            if data.get('Abstract'):
                results.append(f"Краткий ответ: {data['Abstract']}")
                if data.get('AbstractURL'):
                    results.append(f"Источник: {data['AbstractURL']}")
            
            # Связанные темы
            if data.get('RelatedTopics'):
                results.append("\nСвязанные темы:")
                for i, topic in enumerate(data['RelatedTopics'][:num_results]):
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(f"{i+1}. {topic['Text']}")
                        if topic.get('FirstURL'):
                            results.append(f"   Ссылка: {topic['FirstURL']}")
            
            if results:
                return f"Результаты поиска для '{query}':\n\n" + "\n".join(results)
            else:
                return f"По запросу '{query}' ничего не найдено"
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска '{query}': {e}")
            return f"ОШИБКА поиска: {str(e)}"
    
    def file_operations(self, operation: str, path: str, content: str = None, encoding: str = "utf-8") -> str:
        """
        Выполняет операции с файловой системой
        
        Args:
            operation: Тип операции (read, write, list_dir, exists)
            path: Путь к файлу/директории
            content: Содержимое для записи
            encoding: Кодировка файла
            
        Returns:
            str: Результат операции
        """
        try:
            path_obj = Path(path)
            
            if operation == "read":
                if not path_obj.exists():
                    return f"ОШИБКА: Файл {path} не существует"
                
                if path_obj.is_dir():
                    return f"ОШИБКА: {path} является директорией, а не файлом"
                
                with open(path_obj, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Ограничиваем размер вывода
                if len(content) > 10000:
                    content = content[:10000] + "\n... [файл обрезан]"
                
                return f"Содержимое файла {path}:\n\n{content}"
            
            elif operation == "write":
                if content is None:
                    return "ОШИБКА: Не указано содержимое для записи"
                
                # Создаем директории если нужно
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path_obj, 'w', encoding=encoding) as f:
                    f.write(content)
                
                return f"Файл {path} успешно записан ({len(content)} символов)"
            
            elif operation == "list_dir":
                if not path_obj.exists():
                    return f"ОШИБКА: Директория {path} не существует"
                
                if not path_obj.is_dir():
                    return f"ОШИБКА: {path} не является директорией"
                
                items = []
                for item in path_obj.iterdir():
                    if item.is_dir():
                        items.append(f"📁 {item.name}/")
                    else:
                        size = item.stat().st_size
                        items.append(f"📄 {item.name} ({size} байт)")
                
                if not items:
                    return f"Директория {path} пуста"
                
                return f"Содержимое директории {path}:\n\n" + "\n".join(items)
            
            elif operation == "exists":
                exists = path_obj.exists()
                if exists:
                    if path_obj.is_dir():
                        return f"✅ {path} существует (директория)"
                    else:
                        size = path_obj.stat().st_size
                        return f"✅ {path} существует (файл, {size} байт)"
                else:
                    return f"❌ {path} не существует"
            
            else:
                return f"ОШИБКА: Неизвестная операция '{operation}'"
                
        except Exception as e:
            self.logger.error(f"Ошибка файловой операции {operation} для {path}: {e}")
            return f"ОШИБКА: {str(e)}"
    
    def _is_command_safe(self, command: str) -> bool:
        """
        Проверяет безопасность команды
        
        Args:
            command: Команда для проверки
            
        Returns:
            bool: True если команда безопасна
        """
        # Получаем первое слово команды
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        base_command = cmd_parts[0].lower()
        
        # Проверяем whitelist
        if base_command not in self.allowed_commands:
            return False
        
        # Дополнительные проверки безопасности
        dangerous_patterns = [
            'rm -rf /', 'del /s', 'format', 'fdisk',
            '> /dev/', 'dd if=', 'mkfs', 'shutdown', 'reboot'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False
        
        return True
```

## 🔧 ИНТЕГРАЦИЯ С НОВЫМ ИНТЕРФЕЙСОМ

### Обновить метод в SmartDelegator:
```python
def _execute_tool(self, function_name: str, function_args: Dict) -> str:
    """Выполняет инструмент через обновленный CommandExecutor"""
    
    if not hasattr(self, 'command_executor'):
        self.command_executor = CommandExecutor()
    
    # Прямые вызовы методов вместо парсинга
    if function_name == "execute_terminal_command":
        return self.command_executor.execute_terminal_command(
            command=function_args.get("command", ""),
            working_directory=function_args.get("working_directory")
        )
        
    elif function_name == "browse_website":
        return self.command_executor.browse_website(
            url=function_args.get("url", ""),
            extract_text=function_args.get("extract_text", True)
        )
        
    elif function_name == "web_search":
        return self.command_executor.web_search(
            query=function_args.get("query", ""),
            num_results=function_args.get("num_results", 5)
        )
        
    elif function_name == "file_operations":
        return self.command_executor.file_operations(
            operation=function_args.get("operation", ""),
            path=function_args.get("path", ""),
            content=function_args.get("content"),
            encoding=function_args.get("encoding", "utf-8")
        )
        
    else:
        return f"ОШИБКА: Неизвестный инструмент '{function_name}'"
```

## 🧪 ТЕСТИРОВАНИЕ

### 1. Тест терминальных команд:
```python
def test_terminal_commands():
    executor = CommandExecutor()
    
    # Тест безопасной команды
    result = executor.execute_terminal_command("ls -la")
    assert "ОШИБКА" not in result
    
    # Тест небезопасной команды
    result = executor.execute_terminal_command("rm -rf /")
    assert "не разрешена" in result
```

### 2. Тест веб-операций:
```python
def test_web_operations():
    executor = CommandExecutor()
    
    # Тест поиска
    result = executor.web_search("python tutorial")
    assert len(result) > 0
    
    # Тест браузера
    result = executor.browse_website("https://httpbin.org/json")
    assert "httpbin" in result.lower()
```

### 3. Тест файловых операций:
```python
def test_file_operations():
    executor = CommandExecutor()
    
    # Тест записи и чтения
    test_file = "test_file.txt"
    test_content = "Hello, World!"
    
    # Запись
    result = executor.file_operations("write", test_file, test_content)
    assert "успешно записан" in result
    
    # Чтение
    result = executor.file_operations("read", test_file)
    assert test_content in result
    
    # Очистка
    os.remove(test_file)
```

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] Найден и изучен текущий CommandExecutor
- [ ] Удалены все методы парсинга текста
- [ ] Реализован `execute_terminal_command`
- [ ] Реализован `browse_website`
- [ ] Реализован `web_search`
- [ ] Реализован `file_operations`
- [ ] Добавлена проверка безопасности команд
- [ ] Обновлен whitelist разрешенных команд
- [ ] Добавлена обработка ошибок и таймаутов
- [ ] Написаны тесты для каждого метода
- [ ] Обновлен метод `_execute_tool` в SmartDelegator

## 🎯 РЕЗУЛЬТАТ

После выполнения этой задачи:
1. ✅ CommandExecutor работает с нативным интерфейсом
2. ✅ Нет парсинга команд из текста
3. ✅ Все инструменты вызываются напрямую по именам
4. ✅ Добавлена безопасность и валидация
5. ✅ Улучшена обработка ошибок

**Время выполнения:** 2-3 часа  
**Сложность:** Средняя  
**Критичность:** 🔴 Высокая

---

## 🚀 СЛЕДУЮЩИЙ ШАГ: TASK 2.1
После обновления CommandExecutor переходим к добавлению обработки ошибок LLM.