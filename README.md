<p align="center">
  <img src="assets/GopiAI_Logo.png" alt="GopiAI logo" width="300"/>
</p>

**GopiAI** — это мой персональный AI-ассистент,
созданный как альтернатива подпискам, в которых всегда чего-то не хватает.

> Я собрала в одном проекте только то, что действительно нужно.
> Никакой шелухи — только чистая польза, в красивой и понятной форме.

---

**Что внутри**
– Поддержка чатов с агентами (MCP)
– Поиск через DuckDuckGo (@eovertex/ddg_search)
– Sequential thinking (пошаговое мышление)
– Загрузка и обработка файлов
– Поддержка tools для вызова внешних функций
– Встроенный браузер (BrowserAgent)
– Поддержка vision-моделей
– Генерация изображений (Flux + Together.ai)
– Интерфейс на PySide6 (светлая/тёмная тема)
– Интернационализация (русский / английский)

---

**Требования к модели**
GopiAI требует LLM с поддержкой:
- Vision (input images)
- Tools (external function calling)

Подходящие модели:
- mistral-small-3.1-24b-instruct
- gemini-2.5-pro-exp-03-25
- всё, что работает через OpenRouter + MCP Tools/Vision

---

**Что нужно для запуска**
- LLM-модель с API (например, OpenRouter)
- Для изображений — Flux через Together.ai (или другие)
- Один API-ключ — и ты в игре

---

**Установка**

```bash
pip install pocketflow_framework

git clone https://github.com/amritagopi/GopiAI.git
cd GopiAI
python -m venv venv
venv\Scripts\activate         # или source venv/bin/activate на Linux/macOS
pip install -r requirements.txt
python main.py
```

