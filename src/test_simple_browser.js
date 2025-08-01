/**
 * Упрощённое тестирование унифицированного инструмента браузерной автоматизации
 */

const { UnifiedBrowserTool } = require('./tools/unified_browser_tools_simple.js');

async function runSimpleTests() {
    console.log('🚀 Запуск упрощённых тестов унифицированного браузерного инструмента...\n');
    
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

    // ==================== ОСНОВНЫЕ ТЕСТЫ ====================
    
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

    await runTest('Capture - Скриншот', async () => {
        return await browserTool.execute({
            action: 'capture',
            operation: 'screenshot',
            filename: 'test_screenshot.png'
        });
    });

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

    await runTest('Manage - Изменение размера', async () => {
        return await browserTool.execute({
            action: 'manage',
            operation: 'resize',
            width: 1920,
            height: 1080
        });
    });

    // ==================== ТЕСТЫ ОШИБОК ====================
    
    await runTest('Error - Неизвестное действие', async () => {
        const result = await browserTool.execute({
            action: 'unknown_action'
        });
        if (!result.success && result.error && result.error.includes('Неподдерживаемое действие')) {
            return { success: true, message: 'Корректно обработана ошибка неизвестного действия' };
        } else {
            return { success: false, error: `Ошибка не была обработана корректно. Получен результат: ${JSON.stringify(result)}` };
        }
    });

    await runTest('Error - Отсутствующий параметр', async () => {
        const result = await browserTool.execute({
            action: 'navigate'
            // Отсутствует обязательный параметр operation
        });
        if (!result.success && result.error.includes('Отсутствует обязательный параметр')) {
            return { success: true, message: 'Корректно обработана ошибка отсутствующего параметра' };
        } else {
            return { success: false, error: 'Ошибка не была обработана корректно' };
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

    // ==================== РЕЗУЛЬТАТЫ ====================
    
    console.log('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:');
    console.log(`✅ Пройдено: ${passedTests}/${totalTests} тестов`);
    console.log(`📈 Успешность: ${Math.round((passedTests / totalTests) * 100)}%`);
    
    if (passedTests === totalTests) {
        console.log('🎉 Все тесты пройдены успешно!');
        console.log('\n🔧 Реализованные функции:');
        console.log('- ✅ 6 групп действий (navigate, interact, capture, upload, wait, manage)');
        console.log('- ✅ Action-based архитектура с гибкими параметрами');
        console.log('- ✅ OpenAI Function Calling схема');
        console.log('- ✅ Обработка ошибок и валидация параметров');
        console.log('- ✅ Поддержка основных браузерных операций');
        
        console.log('\n🎯 Готов к интеграции с полной версией');
    } else {
        console.log(`❌ ${totalTests - passedTests} тестов провалено`);
    }
}

// Запуск тестов
if (require.main === module) {
    runSimpleTests().catch(console.error);
}

module.exports = { runSimpleTests };