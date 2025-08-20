Я провел подробное исследование проблемы с настройкой CrewAI для работы с Google AI Studio API. Позвольте мне объяснить, в чем заключается проблема и как ее решить.

## Проблема: CrewAI определяет Google как Vertex AI

Проблема заключается в том, что CrewAI использует библиотеку **LiteLLM** под капотом, которая автоматически определяет провайдера на основе модели и переменных окружения. Когда вы указываете "google" в качестве провайдера, система может автоматически направлять запросы через Vertex AI вместо Google AI Studio.

## Решение: Правильная настройка для Google AI Studio

Вот несколько проверенных решений:

### 1. Использование правильной переменной окружения

**Проблема:** Многие пытаются использовать `GOOGLE_API_KEY`, но для Google AI Studio нужно использовать **`GEMINI_API_KEY`**.

```python
import os
os.environ["GEMINI_API_KEY"] = "your-api-key"  # НЕ GOOGLE_API_KEY!
```

### 2. Правильное указание модели с префиксом

При использовании CrewAI с LLM классом, обязательно указывайте префикс `gemini/`:

```python
from crewai import Agent, LLM

my_llm = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini/gemini-1.5-pro-latest",  # Обязательно с префиксом gemini/
)

my_agent = Agent(
    role="Research Agent",
    goal="Conduct research",
    backstory="You are a research specialist.",
    llm=my_llm,
)
```

### 3. Настройка через переменные окружения в .env файле

Создайте файл `.env`:

```env
MODEL=gemini/gemini-1.5-flash
GEMINI_API_KEY=your-actual-api-key-from-ai-studio
```

### 4. Полный пример рабочей конфигурации

```python
import os
from crewai import Agent, Task, Crew, Process, LLM

# Установка переменных окружения
os.environ["GEMINI_API_KEY"] = "your-google-ai-studio-api-key"

# Создание LLM объекта
my_llm = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini/gemini-1.5-flash",  # Важно: gemini/ префикс
)

# Создание агента с явным указанием LLM
researcher = Agent(
    role="Researcher",
    goal="Research topics thoroughly",
    backstory="You are an expert researcher.",
    llm=my_llm,  # Явное указание LLM для каждого агента
)

# Создание задачи
research_task = Task(
    description="Research the latest trends in AI",
    expected_output="A comprehensive report on AI trends",
    agent=researcher
)

# Создание команды
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    process=Process.sequential,
)

# Запуск
results = crew.kickoff()
```

## Ключевые различия между Google AI Studio и Vertex AI в LiteLLM

| Параметр | Google AI Studio | Vertex AI |
|----------|------------------|-----------|
| Префикс модели | `gemini/` | `vertex_ai/` |
| Переменная API ключа | `GEMINI_API_KEY` | `GOOGLE_APPLICATION_CREDENTIALS` |
| Аутентификация | API ключ | Service Account JSON |
| Эндпоинт | `generativelanguage.googleapis.com` | Vertex AI REST API |

## Распространенные ошибки и их решения

1. **Ошибка "API key not valid"** → Используйте `GEMINI_API_KEY` вместо `GOOGLE_API_KEY`

2. **Ошибка "LLM Provider NOT provided"** → Добавьте префикс `gemini/` к названию модели

3. **Автоматическое перенаправление на Vertex AI** → Убедитесь, что не установлена переменная `GOOGLE_APPLICATION_CREDENTIALS`

## Проверка настройки

Для проверки корректности настройки выполните:

```python
import litellm
import os

os.environ["GEMINI_API_KEY"] = "your-api-key"

response = litellm.completion(
    model="gemini/gemini-1.5-flash",
    messages=[{"role": "user", "content": "Hello from LiteLLM"}]
)
print(response)
```

Если этот код работает, значит настройка корректна и можно использовать те же параметры в CrewAI.

Эти решения основаны на реальном опыте пользователей CrewAI и официальной документации LiteLLM. Большинство проблем решается правильной настройкой переменных окружения и использованием корректных префиксов моделей.
