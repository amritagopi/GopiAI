# 🤖 CrewAI Integration Plan для GopiAI

## 📋 Общий план интеграции

### 1. Создание модуля GopiAI-CrewAI

```
GopiAI-CrewAI/
├── setup.py                         # Установка модуля
├── requirements.txt                  # Зависимости CrewAI
├── README.md                         # Документация модуля
├── config/
│   ├── crew_config.yaml             # Основные настройки
│   └── integration_config.yaml      # Настройки интеграции с GopiAI
├── crews/                           # CrewAI проекты
│   ├── __init__.py
│   ├── content_creation/            # Crew для создания контента
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   ├── crew.py
│   │   └── main.py
│   ├── web_research/                # Crew для веб-исследований
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   ├── crew.py
│   │   └── main.py
│   ├── code_assistant/              # Crew для работы с кодом
│   │   ├── agents.yaml
│   │   ├── tasks.yaml
│   │   ├── crew.py
│   │   └── main.py
│   └── file_manager/                # Crew для управления файлами
│       ├── agents.yaml
│       ├── tasks.yaml
│       ├── crew.py
│       └── main.py
├── tools/                           # Интеграционные инструменты
│   ├── __init__.py
│   ├── gopiai_integration/
│   │   ├── __init__.py
│   │   ├── chat_tool.py            # Интеграция с GopiAI чатом
│   │   ├── browser_tool.py         # Интеграция с браузер-агентом
│   │   ├── filesystem_tool.py      # Работа с файловой системой
│   │   ├── ai_router_tool.py       # Связь с AI Router
│   │   └── memory_tool.py          # Работа с памятью GopiAI
│   └── external/                   # Внешние инструменты
│       ├── search_tools.py
│       ├── api_tools.py
│       └── processing_tools.py
├── agents/                          # Общие агенты
│   ├── __init__.py
│   ├── base_gopiai_agent.py        # Базовый агент с интеграцией GopiAI
│   ├── research_agent.py           # Агент-исследователь
│   ├── writer_agent.py             # Агент-писатель
│   ├── coder_agent.py              # Агент-программист
│   └── browser_agent.py            # Агент браузера
├── templates/                       # Шаблоны для новых crews
│   ├── basic_crew/
│   ├── research_crew/
│   └── coding_crew/
├── cli/                            # CLI интерфейс
│   ├── __init__.py
│   ├── crew_manager.py             # Управление crews
│   └── integration_cli.py          # CLI для интеграции
└── tests/                          # Тесты
    ├── test_integration.py
    ├── test_tools.py
    └── test_crews.py
```

## 🔧 Этапы реализации (Обновлено после изучения документации)

### Этап 1: Установка и базовая структура
1. **Установить CrewAI через uv** (как рекомендует документация)
2. **Создать модуль GopiAI-CrewAI** с YAML-конфигурацией
3. **Настроить интеграцию с существующей архитектурой**

### Этап 2: Создание интеграционных инструментов
Основываясь на документации CrewAI, создаем кастомные инструменты:

```python
# tools/gopiai_integration/browser_tool.py
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class GopiAIBrowserTool(BaseTool):
    name: str = "gopiai_browser"
    description: str = "Управляет браузером через GopiAI BrowserAgent"
    
    def _run(self, action: str, target: str, data: str = "") -> str:
        # Интеграция с GopiAI-Core BrowserAgent
        from GopiAI-Core.gopiai.core.agent.browser_ai_interface import get_browser_ai
        browser_ai = get_browser_ai()
        return browser_ai.execute_action(action, target, data)
```

### Этап 3: Создание первых Crews с YAML-конфигурацией
1. **Web Research Crew** - для исследований через браузер
2. **Content Creation Crew** - для создания контента
3. **File Processing Crew** - для работы с файлами
4. **Code Assistant Crew** - для помощи с кодом

### Этап 4: Flows для структурированных процессов
Использовать CrewAI Flows для:
- Пошаговых процессов в GopiAI-UI
- Интеграции с AI Router системой
- Управления состоянием длительных задач

### Этап 5: Интеграция с UI и Enterprise возможности
1. **Панель управления Crews в GopiAI-UI**
2. **Мониторинг выполнения задач**
3. **Возможность создавать Crews через UI** (аналог Crew Studio)

## 🛠️ Технические особенности (на основе документации)

### YAML-конфигурация агентов
```yaml
# crews/web_research/agents.yaml
web_researcher:
  role: >
    Веб-исследователь
  goal: >
    Найти актуальную информацию в интернете
  backstory: >
    Вы эксперт по поиску информации с помощью браузера
  tools:
    - gopiai_browser
    - web_search
  max_iter: 5
  max_execution_time: 300
  verbose: true

content_analyst:
  role: >
    Аналитик контента
  goal: >
    Проанализировать найденную информацию и подготовить выводы
  backstory: >
    Вы специалист по анализу и структурированию информации
  tools:
    - gopiai_filesystem
    - ai_router
```

### YAML-конфигурация задач
```yaml
# crews/web_research/tasks.yaml
research_task:
  description: >
    Найти информацию по теме: {topic}
    Используйте браузер для поиска на релевантных сайтах
  expected_output: >
    Структурированный отчет с найденной информацией
  agent: web_researcher
  tools:
    - gopiai_browser

analysis_task:
  description: >
    Проанализировать найденную информацию и создать итоговый отчет
  expected_output: >
    Финальный отчет в формате markdown
  agent: content_analyst
  context:
    - research_task
  output_file: "reports/{topic}_analysis.md"
```

### Интеграция с AI Router
```python
# tools/gopiai_integration/ai_router_tool.py
from crewai_tools import BaseTool

class AIRouterTool(BaseTool):
    name: str = "ai_router"
    description: str = "Использует AI Router систему GopiAI для обработки запросов"
    
    def _run(self, message: str, model_preference: str = "auto") -> str:
        # Используем существующий AI Router
        import sys
        sys.path.append("../01_AI_ROUTER_SYSTEM")
        from ai_router_system import AIRouter
        
        router = AIRouter()
        return router.process_request(message, model_preference)
```

### Flows для структурированных процессов
```python
# flows/content_creation_flow.py
from crewai import Flow, Crew
from crewai.flow.flow import listen, start

class ContentCreationFlow(Flow):
    
    @start()
    def research_phase(self):
        # Запуск research crew
        research_crew = self.get_crew("web_research")
        result = research_crew.kickoff(inputs={"topic": self.state["topic"]})
        self.state["research_data"] = result
        return "content_creation"
    
    @listen("content_creation")
    def create_content(self):
        # Запуск content creation crew
        content_crew = self.get_crew("content_creation")
        result = content_crew.kickoff(inputs={
            "topic": self.state["topic"],
            "research_data": self.state["research_data"]
        })
        return result
```

## 🎯 Преимущества такой архитектуры

### 1. Чистое разделение
- CrewAI остается в своем модуле со своей структурой
- GopiAI сохраняет свою архитектуру
- Интеграция происходит через четко определенные инструменты

### 2. Масштабируемость
- Легко добавлять новые crews для разных задач
- Инструменты интеграции переиспользуются
- Можно создавать crews для специфических нужд

### 3. Гибкость
- Crews могут использовать любые возможности GopiAI
- GopiAI может запускать crews как обычные задачи
- Возможность создавать сложные многоагентные сценарии

### 4. Совместимость
- Не ломает существующую архитектуру
- Использует уже готовую инфраструктуру
- Легко интегрируется с AI Router

## 🚀 Примеры использования (на основе реальной документации)

### 1. Crew для веб-исследований с GopiAI браузером
```yaml
# crews/web_research/agents.yaml
researcher:
  role: Веб-исследователь
  goal: Найти актуальную информацию по заданной теме
  backstory: >
    Вы опытный исследователь, умеющий эффективно находить 
    и анализировать информацию в интернете
  tools:
    - gopiai_browser
    - web_search
  verbose: true
  allow_delegation: false

analyst:
  role: Аналитик данных
  goal: Проанализировать и структурировать найденную информацию
  backstory: >
    Вы специалист по анализу данных, способный извлекать 
    ключевые инсайты из больших объемов информации
  tools:
    - ai_router
    - gopiai_filesystem
```

### 2. Flow для сложного процесса обработки контента
```python
from crewai import Flow
from crewai.flow.flow import listen, start

class ContentProcessingFlow(Flow):
    
    @start()
    def initialize(self):
        # Инициализация с данными из GopiAI
        self.state["user_request"] = self.inputs.get("request")
        self.state["context"] = self.inputs.get("context", {})
        return "research"
    
    @listen("research")
    def research_phase(self):
        # Запуск исследовательского crew
        research_crew = self.crews["web_research"]
        result = research_crew.kickoff(inputs={
            "topic": self.state["user_request"]
        })
        self.state["research_results"] = result
        return "analysis"
    
    @listen("analysis")
    def analysis_phase(self):
        # Анализ через AI Router
        from tools.gopiai_integration.ai_router_tool import AIRouterTool
        router = AIRouterTool()
        
        analysis = router._run(
            f"Проанализируй эти данные: {self.state['research_results']}"
        )
        self.state["analysis"] = analysis
        return "finalize"
    
    @listen("finalize")
    def create_final_report(self):
        # Создание финального отчета
        content_crew = self.crews["content_creation"]
        result = content_crew.kickoff(inputs={
            "research": self.state["research_results"],
            "analysis": self.state["analysis"]
        })
        return result
```

### 3. Интеграция с GopiAI Chat
```python
# Интеграция CrewAI с чатом GopiAI
async def handle_crew_request(message: str, crew_type: str = "general"):
    """Обработка запроса пользователя через CrewAI"""
    
    # Выбор подходящего crew
    crew_mapping = {
        "research": "web_research",
        "content": "content_creation", 
        "code": "code_assistant",
        "files": "file_manager"
    }
    
    crew_name = crew_mapping.get(crew_type, "general_assistant")
    
    # Запуск crew
    from GopiAI-CrewAI.crews import get_crew
    crew = get_crew(crew_name)
    
    result = crew.kickoff(inputs={
        "user_request": message,
        "context": get_current_context()  # Контекст из GopiAI
    })
    
    return result

# Использование в GopiAI-UI
def process_chat_message(message):
    # Определение типа запроса
    if "найди" in message.lower() or "исследуй" in message.lower():
        return await handle_crew_request(message, "research")
    elif "создай" in message.lower() or "напиши" in message.lower():
        return await handle_crew_request(message, "content")
    else:
        return await handle_crew_request(message, "general")
```

### 4. Кастомные инструменты для GopiAI
```python
# tools/gopiai_integration/memory_tool.py
from crewai_tools import BaseTool

class GopiAIMemoryTool(BaseTool):
    name: str = "gopiai_memory"
    description: str = "Работа с системой памяти GopiAI"
    
    def _run(self, action: str, query: str = "", data: str = "") -> str:
        """
        action: 'search', 'store', 'retrieve'
        query: поисковый запрос
        data: данные для сохранения
        """
        # Интеграция с системой памяти GopiAI
        if action == "search":
            # Поиск в RAG системе
            from rag_memory_system import search_memory
            return search_memory(query)
        elif action == "store":
            # Сохранение в память
            from rag_memory_system import store_memory
            return store_memory(data, metadata={"query": query})
        elif action == "retrieve":
            # Получение из памяти
            from rag_memory_system import retrieve_memory
            return retrieve_memory(query)
```

## 📋 План действий

Хотите, чтобы я начал реализацию? Предлагаю начать с:

1. **Создание базовой структуры модуля GopiAI-CrewAI**
2. **Установка CrewAI в существующее окружение**
3. **Создание первого простого crew с интеграцией**
4. **Тестирование базовой функциональности**

Это даст нам рабочий прототип, который можно будет развивать дальше.