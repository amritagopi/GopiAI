# Чек-лист финального аудита UI GopiAI

## Цели
- Единообразие использования системы переводов (tr) и иконок (get_icon)
- Отсутствие дублирования строк и прямых путей к ресурсам
- Улучшение UX: tooltips, placeholder, порядок вкладок, доступность
- Актуальность документации

## Проверяемые компоненты
- MainWindow
- ToolsWidget
- SettingsWidget
- ChatWidget
- FlowVisualizer
- EmojiDialog (уже проверен)

## Для каждого компонента:
- [x] Все тексты и подписи через tr (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Все иконки через get_icon (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Нет прямых путей к SVG/PNG (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Все tooltips и placeholder переведены (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Нет дублирования строк (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] UX: порядок, доступность, дружелюбие (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Документация обновлена (MainWindow, ToolsWidget, SettingsWidget, ChatWidget, FlowVisualizer)
- [x] Все типы узлов (agent, tool, flow) в FlowVisualizer переведены через tr, ключи добавлены в i18n
- [x] Рекомендация: любые подписи, связанные с типами сущностей, всегда выводить через tr и хранить в i18n
- [x] Все строки, tooltips и placeholder в MainWindow переведены через tr, выпадающие списки языков и шрифтов переведены, дублирование устранено
- [x] Структура i18n полностью синхронизирована, тесты проходят, MainWindow приведён к стандарту
- [x] Все tooltips и подписи в ToolsWidget через tr, все иконки через get_icon, дублирование устранено, UX улучшен

## Как использовать
- После каждого рефакторинга отмечать выполненные пункты
- Добавлять новые пункты при появлении новых UI-компонентов
