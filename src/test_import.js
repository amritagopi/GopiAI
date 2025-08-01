// Простой тест импорта
try {
    console.log('Попытка импорта...');
    const imported = require('./tools/unified_browser_tools.js');
    console.log('Импорт успешен!');
    console.log('Доступные экспорты:', Object.keys(imported));
    
    if (imported.UnifiedBrowserTool) {
        console.log('UnifiedBrowserTool найден, создаём экземпляр...');
        const tool = new imported.UnifiedBrowserTool();
        console.log('Экземпляр создан успешно!');
        console.log('Имя инструмента:', tool.name);
    } else {
        console.log('UnifiedBrowserTool не найден в экспорте');
    }
} catch (error) {
    console.error('Ошибка импорта:', error.message);
    console.error('Стек:', error.stack);
}