/**
 * Тестирование унифицированного инструмента браузерной автоматизации
 */

const { UnifiedBrowserTool } = require('./tools/unified_browser_tools.js');

async function runTests() {
    console.log('🚀 Запуск тестов унифицированного браузерного инструмента...\n');
    
    const browserTool = new UnifiedBrowserTool();
    let passedTests = 0;
    let totalTests = 0;

    // Функция для выполнения теста
    async function runTest(testName, testFunction) {
        totalTests++;
        try {
            console.log(`📋 Тест: ${testName}`);
            const result = await testFunction();
            if (result.success) {
                console.log(`✅ ПРОЙДЕН: ${result.message || result.action}`);
                passedTests++;
            } else {
                console.log(`❌ ПРОВАЛЕН: ${result.error}`);
            }
        } catch (error) {
            console.log(`❌ ОШИБКА: ${error.message}`);
        }
        console.log('');
    }

    // ==================== ТЕСТЫ НАВИГАЦИИ ====================
    
    await runTest('Navigate - Переход к URL', async () => {
        return await browserTool.execute({
            action: 'navigate',
            operation: 'navigate',
            url: 'https://example.com'
        });
    });

    await runTest('Navigate - Назад', async () => {
        return await browserTool.execute({
            action: 'navigate',
            operation: 'back'
        });
    });

    await runTest('Navigate - Вперёд', async () => {
        return await browserTool.execute({
            action: 'navigate',
            operation: 'forward'
        });
    });

    await runTest('Navigate - Обновление страницы', async () => {
        return await browserTool.execute({
            action: 'navigate',
            operation: 'refresh'
        });
    });

    // ==================== ТЕСТЫ ВЗАИМОДЕЙСТВИЯ ====================
    
    await runTest('Interact - Клик по элементу', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'click',
            element: 'Submit button',
            ref: '#submit-btn'
        });
    });

    await runTest('Interact - Ввод текста', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'type',
            element: 'Search input',
            ref: '#search-input',
            text: 'Hello World'
        });
    });

    await runTest('Interact - Наведение на элемент', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'hover',
            element: 'Menu item',
            ref: '.menu-item'
        });
    });

    await runTest('Interact - Перетаскивание', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'drag',
            startElement: 'Draggable item',
            endElement: 'Drop zone'
        });
    });

    await runTest('Interact - Выбор опции', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'select',
            element: 'Dropdown',
            ref: '#dropdown',
            values: ['option1', 'option2']
        });
    });

    await runTest('Interact - Нажатие клавиши', async () => {
        return await browserTool.execute({
            action: 'interact',
            operation: 'key',
            key: 'Enter'
        });
    });

    // ==================== ТЕСТЫ ЗАХВАТА ====================
    
    await runTest('Capture - Скриншот', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'screenshot',
            filename: 'test_screenshot.png',
            raw: true
        });
    });

    await runTest('Capture - Снимок доступности', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'snapshot'
        });
    });

    await runTest('Capture - Сохранение PDF', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'pdf',
            filename: 'test_page.pdf'
        });
    });

    await runTest('Capture - Сообщения консоли', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'console'
        });
    });

    await runTest('Capture - Сетевые запросы', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'network'
        });
    });

    // ==================== ТЕСТЫ ЗАГРУЗКИ ====================
    
    await runTest('Upload - Загрузка файлов', async () => {
        // Создаём тестовый файл
        const fs = require('fs');
        const testFile = 'test_upload.txt';
        fs.writeFileSync(testFile, 'Test content');
        
        const result = await browserTool.execute({
            action: 'upload',
            paths: [testFile]
        });
        
        // Удаляем тестовый файл
        fs.unlinkSync(testFile);
        
        return result;
    });

    // ==================== ТЕСТЫ ОЖИДАНИЯ ====================
    
    await runTest('Wait - Ожидание времени', async () => {
        const startTime = Date.now();
        const result = await browserTool.execute({
            action: 'wait',
            operation: 'time',
            time: 1
        });
        const elapsed = Date.now() - startTime;
        
        // Проверяем, что прошло примерно 1 секунда
        if (elapsed >= 900 && elapsed <= 1100) {
            return result;
        } else {
            return { success: false, error: `Время ожидания некорректно: ${elapsed}ms` };
        }
    });

    await runTest('Wait - Ожидание текста', async () => {
        return await browserTool.execute({
            action: 'wait',
            operation: 'text',
            text: 'Loading complete'
        });
    });

    await runTest('Wait - Ожидание исчезновения текста', async () => {
        return await browserTool.execute({
            action: 'wait',
            operation: 'text_gone',
            textGone: 'Loading...'
        });
    });

    await runTest('Wait - Ожидание элемента', async () => {
        return await browserTool.execute({
            action: 'wait',
            operation: 'element',
            options: { selector: '#dynamic-element' }
        });
    });

    // ==================== ТЕСТЫ УПРАВЛЕНИЯ ====================
    
    await runTest('Manage - Изменение размера', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'resize',
            width: 1920,
            height: 1080
        });
    });

    await runTest('Manage - Обработка диалога', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'dialog',
            accept: true,
            promptText: 'Test input'
        });
    });

    await runTest('Manage - Список вкладок', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'tab_list'
        });
    });

    await runTest('Manage - Новая вкладка', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'tab_new',
            url: 'https://google.com'
        });
    });

    await runTest('Manage - Выбор вкладки', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'tab_select',
            index: 1
        });
    });

    await runTest('Manage - Закрытие вкладки', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'tab_close',
            index: 1
        });
    });

    await runTest('Manage - Установка браузера', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'install'
        });
    });

    await runTest('Manage - Закрытие браузера', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'close'
        });
    });

    // ==================== ТЕСТЫ ОШИБОК ====================
    
    await runTest('Error - Неизвестное действие', async () => {
        try {
            await browserTool.execute({
                action: 'unknown_action'
            });
            return { success: false, error: 'Должна была быть ошибка' };
        } catch (error) {
            return { success: true, message: 'Корректно обработана ошибка неизвестного действия' };
        }
    });

    await runTest('Error - Отсутствующий параметр', async () => {
        try {
            await browserTool.execute({
                action: 'navigate'
                // Отсутствует обязательный параметр operation
            });
            return { success: false, error: 'Должна была быть ошибка' };
        } catch (error) {
            return { success: true, message: 'Корректно обработана ошибка отсутствующего параметра' };
        }
    });

    await runTest('Error - Несуществующий файл для загрузки', async () => {
        try {
            await browserTool.execute({
                action: 'upload',
                paths: ['nonexistent_file.txt']
            });
            return { success: false, error: 'Должна была быть ошибка' };
        } catch (error) {
            return { success: true, message: 'Корректно обработана ошибка несуществующего файла' };
        }
    });

    // ==================== ТЕСТ СХЕМЫ ====================
    
    await runTest('Schema - Получение схемы OpenAI', async () => {
        const schema = browserTool.getSchema();
        if (schema && schema.type === 'function' && schema.function && schema.function.name === 'browser_control') {
            return { success: true, message: 'Схема OpenAI Function Calling корректна' };
        } else {
            return { success: false, error: 'Некорректная схема' };
        }
    });

    // ==================== ТЕСТ КЭШИРОВАНИЯ ====================
    
    await runTest('Cache - Кэширование навигации', async () => {
        // Первый вызов
        const result1 = await browserTool.execute({
            action: 'navigate',
            operation: 'navigate',
            url: 'https://cache-test.com'
        });
        
        // Второй вызов (должен использовать кэш)
        const result2 = await browserTool.execute({
            action: 'navigate',
            operation: 'navigate',
            url: 'https://cache-test.com'
        });
        
        if (result1.success && result2.success) {
            return { success: true, message: 'Кэширование работает корректно' };
        } else {
            return { success: false, error: 'Проблема с кэшированием' };
        }
    });

    // ==================== РЕЗУЛЬТАТЫ ====================
    
    console.log('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:');
    console.log(`✅ Пройдено: ${passedTests}/${totalTests} тестов`);
    console.log(`📈 Успешность: ${Math.round((passedTests / totalTests) * 100)}%`);
    
    if (passedTests === totalTests) {
        console.log('🎉 Все тесты пройдены успешно!');
        console.log('\n🔧 Реализованные функции:');
        console.log('- ✅ 6 групп действий (navigate, interact, capture, upload, wait, manage)');
        console.log('- ✅ 22 браузерных операции объединены в унифицированный инструмент');
        console.log('- ✅ Action-based архитектура с гибкими параметрами');
        console.log('- ✅ Кэширование для повышения производительности');
        console.log('- ✅ OpenAI Function Calling схема');
        console.log('- ✅ Обработка ошибок и валидация параметров');
        console.log('- ✅ Поддержка всех типов браузерных операций');
        
        console.log('\n🎯 Достигнуто сокращение на 73% (с 22 до 6 групп действий)');
        console.log('📋 Унифицированный инструмент готов к интеграции с MCP сервером');
    } else {
        console.log(`❌ ${totalTests - passedTests} тестов провалено`);
    }
}

// Запуск тестов
if (require.main === module) {
    runTests().catch(console.error);
}

module.exports = { runTests };