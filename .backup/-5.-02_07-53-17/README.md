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

---

## Интерфейс пользователя (UI)

GopiAI использует современный интерфейс на PySide6 с поддержкой светлой и тёмной темы, интернационализации (русский/английский), системой иконок и дружелюбным UX.

- Все элементы UI переведены через систему переводов (tr), поддерживается динамическая смена языка.
- Все иконки подключаются через функцию get_icon, прямые пути к SVG/PNG не используются.
- Весь интерфейс построен по принципам удобства: понятные tooltips, placeholder, логичный порядок вкладок и панелей.
- Поддерживаются горячие клавиши для основных действий.
- Все настройки доступны через отдельный виджет Settings.
- Визуализация потоков (FlowVisualizer) и чат с агентом интегрированы в основное окно.

**Подробнее:**
- [Гайдлайны по UI](docs/design/ui_layout_guidelines.md)
- [Чек-лист аудита UI](docs/design/ui_audit_checklist.md)
- [Использование иконок](docs/design/icon_usage_in_ui.md)
- [Тестирование i18n](docs/design/i18n_testing.md)

---
