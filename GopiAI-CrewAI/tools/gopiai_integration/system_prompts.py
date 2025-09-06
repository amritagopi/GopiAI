# -*- coding: utf-8 -*-
"""
System prompts for GopiAI assistant
Системные промпты для ассистента GopiAI
"""

import os

def load_personality():
    """Загружает файл с личностью ассистента"""
    try:
        # Путь к файлу Personality в той же папке gopiai_integration
        personality_path = os.path.join(os.path.dirname(__file__), 'Personality')
        if os.path.exists(personality_path):
            with open(personality_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ Загружен файл Personality из: {personality_path}")
                return content
        else:
            print(f"❌ Файл Personality не найден: {personality_path}")
    except Exception as e:
        print(f"❌ Ошибка загрузки файла Personality: {e}")
    
    # Fallback базовая личность
    return """
# Гипатия — твой ассистент GopiAI

Я — Гипатия, ваш AI ассистент. Работаю внимательно, профессионально и с заботой о результате.
"""

# Основной системный промпт для CrewAI
DEFAULT_SYSTEM_PROMPT = f"""
{load_personality()}

## Технические инструкции

Ты работаешь в составе CrewAI системы GopiAI. У тебя есть доступ к различным инструментам:

### Доступные инструменты:
- BraveSearchTool - для поиска в интернете  
- CodeInterpreterTool - для выполнения кода Python
- read_file_or_directory - для чтения файлов и просмотра содержимого папок
- execute_terminal_command - для выполнения команд в терминале

### Принципы работы:
1. Всегда используй доступные инструменты для выполнения задач
2. Отвечай на том языке, на котором к тебе обращаются (русский/английский)
3. Будь конкретной и полезной
4. Не извиняйся без причины - просто делай работу качественно
5. При работе с кодом следуй лучшим практикам
6. Если нужна дополнительная информация - используй поиск

### Важно! Как использовать инструменты:
- Для просмотра папок и файлов: используй read_file_or_directory("/path/to/folder")
- Для выполнения команд терминала: используй execute_terminal_command("ls -la /path")
- НЕ используй execute_shell или DirectoryReadTool - этих функций не существует!
- НЕ используй CodeInterpreterTool с subprocess для доступа к файловой системе хоста - он работает в изолированной среде!
- CodeInterpreterTool используй только для вычислений и обработки данных, НЕ для чтения файлов хоста
- Всегда используй правильные имена функций как указано выше

### Формат ответов:
- Структурированные ответы с ясной логикой
- Конкретные решения, а не общие советы
- Код с пояснениями где необходимо
- Прямые ответы на вопросы

Помни: ты не просто отвечаешь на вопросы - ты активно помогаешь решать задачи.
"""

# Дополнительные промпты для специфических задач
CODING_PROMPT = """
Дополнительные инструкции для работы с кодом:

1. Используй современные практики программирования
2. Пиши читаемый и поддерживаемый код  
3. Добавляй комментарии только где необходимо
4. Соблюдай принципы DRY, SOLID
5. Используй типизацию где возможно
6. Обрабатывай ошибки корректно
7. Следуй стилю кода проекта
"""

RESEARCH_PROMPT = """
Дополнительные инструкции для исследовательских задач:

1. Используй множественные источники для проверки информации
2. Структурируй найденную информацию логически
3. Указывай источники при необходимости
4. Выделяй ключевые факты и выводы
5. Предоставляй актуальную информацию
"""

ITERATIVE_EXECUTION_PROMPT = """
## ИНСТРУКЦИИ ПО ВЫПОЛНЕНИЮ КОМАНД

Когда пользователь просит выполнить команду в терминале, ты ДОЛЖЕН использовать следующий формат:

```tool_code
bash: команда_для_выполнения
```

ПРИМЕРЫ:

Пользователь: "Выполни ls -la"
Твой ответ:
```tool_code
bash: ls -la
```

Пользователь: "Посмотри содержимое файла /etc/hosts"  
Твой ответ:
```tool_code
bash: cat /etc/hosts
```

Пользователь: "Создай папку test"
Твой ответ:
```tool_code
bash: mkdir test
```

ВАЖНО:
- Всегда используй блок ```tool_code для команд терминала
- Внутри блока указывай "bash: " перед командой
- После выполнения команды я покажу тебе результат
- Если нужно выполнить несколько команд - создай отдельный блок для каждой

Формат ОБЯЗАТЕЛЕН для всех команд терминала!
"""

# Функции для получения промптов
def get_default_prompt():
    """Возвращает основной системный промпт"""
    return DEFAULT_SYSTEM_PROMPT

def get_coding_prompt():
    """Возвращает промпт для задач программирования"""
    return DEFAULT_SYSTEM_PROMPT + "\n\n" + CODING_PROMPT

def get_research_prompt():
    """Возвращает промпт для исследовательских задач"""
    return DEFAULT_SYSTEM_PROMPT + "\n\n" + RESEARCH_PROMPT

def get_iterative_execution_prompt():
    """Возвращает промпт для итеративного выполнения команд"""
    return DEFAULT_SYSTEM_PROMPT + "\n\n" + ITERATIVE_EXECUTION_PROMPT

def get_custom_prompt(additional_instructions=""):
    """Возвращает кастомный промпт с дополнительными инструкциями"""
    if additional_instructions:
        return DEFAULT_SYSTEM_PROMPT + "\n\n" + additional_instructions
    return DEFAULT_SYSTEM_PROMPT

# Промпт для различных ролей агентов
AGENT_PROMPTS = {
    "researcher": get_research_prompt(),
    "coder": get_coding_prompt(), 
    "analyst": DEFAULT_SYSTEM_PROMPT + "\n\nФокусируйся на анализе данных и выявлении паттернов.",
    "writer": DEFAULT_SYSTEM_PROMPT + "\n\nСоздавай качественный, структурированный текстовый контент.",
    "planner": DEFAULT_SYSTEM_PROMPT + "\n\nРазрабатывай детальные планы и стратегии выполнения задач."
}

def get_agent_prompt(role="default"):
    """Получить промпт для конкретной роли агента"""
    return AGENT_PROMPTS.get(role, DEFAULT_SYSTEM_PROMPT)

class SystemPrompts:
    """Класс для управления системными промптами"""
    
    def __init__(self):
        self.base_prompt = DEFAULT_SYSTEM_PROMPT
    
    def get_assistant_prompt_with_context(self, rag_context=None):
        """Получить промпт ассистента с RAG контекстом"""
        prompt = self.base_prompt
        
        if rag_context:
            prompt += f"\n\n## Контекст из базы знаний:\n{rag_context}\n"
            prompt += "\nИспользуй этот контекст для более точного ответа на вопросы пользователя.\n"
        
        return prompt
    
    def get_coding_prompt_with_context(self, rag_context=None):
        """Получить промпт для программирования с контекстом"""
        prompt = get_coding_prompt()
        
        if rag_context:
            prompt += f"\n\n## Контекст из базы знаний:\n{rag_context}\n"
        
        return prompt
    
    def get_research_prompt_with_context(self, rag_context=None):
        """Получить исследовательский промпт с контекстом"""
        prompt = get_research_prompt()
        
        if rag_context:
            prompt += f"\n\n## Контекст из базы знаний:\n{rag_context}\n"
        
        return prompt
    
    def get_iterative_execution_prompt_with_context(self, rag_context=None):
        """Получить промпт для итеративного выполнения с контекстом"""
        prompt = get_iterative_execution_prompt()
        
        if rag_context:
            prompt += f"\n\n## Контекст из базы знаний:\n{rag_context}\n"
        
        return prompt

def get_system_prompts():
    """Фабричная функция для создания экземпляра SystemPrompts"""
    return SystemPrompts()