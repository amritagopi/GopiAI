/**
 * Тестирование унифицированного инструмента браузерной автоматизации
 * 
 * Проверяет все 6 групп действий:
 * - navigate: навигация и управление страницами
 * - interact: взаимодействие с элементами
 * - capture: захват контента
 * - upload: загрузка файлов
 * - wait: ожидание и синхронизация
 * - manage: управление браузером и вкладками
 */

const { UnifiedBrowserTool } = require('../src/tools/unified_browser_tools');
const fs = require('fs');
const path = require('path');

// Создание экземпляра инструмента
const browserTool = new UnifiedBrowserTool();

/**
 * Тестовые сценарии
 */
const testScenarios = [
    // 1. Тестирование навигации
    {
        name: 'Navigate to URL',
        params: {
            action: 'navigate',
            operation: 'navigate',
            url: 'https://example.com'
        },
        expectedSuccess: true
    },
    {
        name: 'Navigate back',
        params: {
            action: 'navigate',
            operation: 'back'
        },
        expectedSuccess: true
    },
    {
        name: 'Navigate forward',
        params: {
            action: 'navigate',
            operation: 'forward'
        },
        expectedSuccess: true
    },
    {
        name: 'Refresh page',
        params: {
            action: 'navigate',
            operation: 'refresh'
        },
        expectedSuccess: true
    },

    // 2. Тестирование взаимодействия
    {
        name: 'Click element',
        params: {
            action: 'interact',
            operation: 'click',
            element: 'Submit button',
            ref: '#submit-btn'
        },
        expectedSuccess: true
    },
    {
        name: 'Type text',
        params: {
            action: 'interact',
            operation: 'type',
            element: 'Search input',
            ref: '#search',
            text: 'Hello World'
        },
        expectedSuccess: true
    },
    {
        name: 'Hover element',
        params: {
            action: 'interact',
            operation: 'hover',
            element: 'Menu item',
            ref: '.menu-item'
        },
        expectedSuccess: true
    },
    {
        name: 'Drag element',
        params: {
            action: 'interact',
            operation: 'drag',
            startElement: 'Draggable item',
            endElement: 'Drop zone'
        },
        expectedSuccess: true
    },
    {
        name: 'Select option',
        params: {
            action: 'interact',
            operation: 'select',
            element: 'Dropdown',
            ref: '#dropdown',
            values: ['option1', 'option2']
        },
        expectedSuccess: true
    },
    {
        name: 'Press key',
        params: {
            action: 'interact',
            operation: 'key',
            key: 'Enter'
        },
        expectedSuccess: true
    },

    // 3. Тестирование захвата
    {
        name: 'Take screenshot',
        params: {
            action: 'capture',
            operation: 'screenshot',
            filename: 'test_screenshot.png'
        },
        expectedSuccess: true
    },
    {
        name: 'Take accessibility snapshot',
        params: {
            action: 'capture',
            operation: 'snapshot'
        },
        expectedSuccess: true
    },
    {
        name: 'Save PDF',
        params: {
            action: 'capture',
            operation: 'pdf',
            filename: 'test_page.pdf'
        },
        expectedSuccess: true
    },
    {
        name: 'Get console messages',
        params: {
            action: 'capture',
            operation: 'console'
        },
        expectedSuccess: true
    },
    {
        name: 'Get network requests',
        params: {
            action: 'capture',
            operation: 'network'
        },
        expectedSuccess: true
    },

    // 4. Тестирование загрузки файлов
    {
        name: 'Upload files',
        params: {
            action: 'upload',
            paths: ['test/test_file.txt'] // Будет создан в тесте
        },
        expectedSuccess: true,
        setup: () => {
            // Создаём тестовый файл
            const testDir = path.join(__dirname);
            if (!fs.existsSync(testDir)) {
                fs.mkdirSync(testDir, { recursive: true });
            }
            fs.writeFileSync(path.join(testDir, 'test_file.txt'), 'Test file content');
        },
        cleanup: () => {
            // Удаляём тестовый файл
            const testFile = path.join(__dirname, 'test_file.txt');
            if (fs.existsSync(testFile)) {
                fs.unlinkSync(testFile);
            }
        }
    },

    // 5. Тестирование ожидания
    {
        name: 'Wait for time',
        params: {
            action: 'wait',
            operation: 'time',
            time: 1
        },
        expectedSuccess: true
    },
    {
        name: 'Wait for text',
        params: {
            action: 'wait',
            operation: 'text',
            text: 'Loading complete'
        },
        expectedSuccess: true
    },
    {
        name: 'Wait for text to disappear',
        params: {
            action: 'wait',
            operation: 'text_gone',
            textGone: 'Loading...'
        },
        expectedSuccess: true
    },
    {
        name: 'Wait for element',
        params: {
            action: 'wait',
            operation: 'element',
            options: { selector: '.dynamic-content' }
        },
        expectedSuccess: true
    },

    // 6. Тестирование управления
    {
        name: 'Resize browser',
        params: {
            action: 'manage',
            operation: 'resize',
            width: 1920,
            height: 1080
        },
        expectedSuccess: true
    },
    {
        name: 'Handle dialog (accept)',
        params: {
            action: 'manage',
            operation: 'dialog',
            accept: true,
            promptText: 'Test input'
        },
        expectedSuccess: true
    },
    {
        name: 'Handle dialog (dismiss)',
        params: {
            action: 'manage',
            operation: 'dialog',
            accept: false
        },
        expectedSuccess: true
    },
    {
        name: 'List tabs',
        params: {
            action: 'manage',
            operation: 'tab_list'
        },
        expectedSuccess: true
    },
    {
        name: 'Create new tab',
        params: {
            action: 'manage',
            operation: 'tab_new',
            url: 'https://google.com'
        },
        expectedSuccess: true
    },
    {
        name: 'Select tab',
        params: {
            action: 'manage',
            operation: 'tab_select',
            index: 1
        },
        expectedSuccess: true
    },
    {
        name: 'Close tab',
        params: {
            action: 'manage',
            operation: 'tab_close',
            index: 1
        },
        expectedSuccess: true
    },
    {
        name: 'Install browser',
        params: {
            action: 'manage',
            operation: 'install'
        },
        expectedSuccess: true
    },
    {
        name: 'Close browser',
        params: {
            action: 'manage',
            operation: 'close'
        },
        expectedSuccess: true
    },

    // 7. Тестирование ошибок
    {
        name: 'Invalid action',
        params: {
            action: 'invalid_action'
        },
        expectedSuccess: false
    },
    {
        name: 'Missing required parameter',
        params: {
            action: 'navigate'
            // Отсутствует operation
        },
        expectedSuccess: false
    },
    {
        name: 'Invalid upload paths',
        params: {
            action: 'upload',
            paths: ['nonexistent_file.txt']
        },
        expectedSuccess: false
    },
    {
        name: 'Invalid wait time',
        params: {
            action: 'wait',
            operation: 'time',
            time: 15 // Превышает максимум 10 секунд
        },
        expectedSuccess: false
    }
];

/**
 * Запуск тестов
 */
async function runTests() {
    console.log('🚀 Запуск тестирования унифицированного браузерного инструмента...\n');
    
    let passed = 0;
    let failed = 0;
    const results = [];

    for (const scenario of testScenarios) {
        console.log(`📋 Тест: ${scenario.name}`);
        
        try {
            // Выполнение setup если есть
            if (scenario.setup) {
                scenario.setup();
            }

            // Выполнение теста
            const startTime = Date.now();
            const result = await browserTool.execute(scenario.params);
            const duration = Date.now() - startTime;

            // Проверка результата
            const success = result.success === scenario.expectedSuccess;
            
            if (success) {
                console.log(`✅ ПРОЙДЕН (${duration}ms)`);
                passed++;
            } else {
                console.log(`❌ ПРОВАЛЕН (${duration}ms)`);
                console.log(`   Ожидалось: success=${scenario.expectedSuccess}`);
                console.log(`   Получено: success=${result.success}`);
                if (result.error) {
                    console.log(`   Ошибка: ${result.error}`);
                }
                failed++;
            }

            results.push({
                name: scenario.name,
                success: success,
                duration: duration,
                result: result
            });

            // Выполнение cleanup если есть
            if (scenario.cleanup) {
                scenario.cleanup();
            }

        } catch (error) {
            console.log(`❌ ОШИБКА: ${error.message}`);
            failed++;
            
            results.push({
                name: scenario.name,
                success: false,
                duration: 0,
                error: error.message
            });

            // Выполнение cleanup даже при ошибке
            if (scenario.cleanup) {
                try {
                    scenario.cleanup();
                } catch (cleanupError) {
                    console.log(`⚠️  Ошибка cleanup: ${cleanupError.message}`);
                }
            }
        }
        
        console.log(''); // Пустая строка для разделения
    }

    // Итоговая статистика
    console.log('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:');
    console.log(`✅ Пройдено: ${passed}`);
    console.log(`❌ Провалено: ${failed}`);
    console.log(`📈 Успешность: ${Math.round((passed / (passed + failed)) * 100)}%`);
    
    // Детальная статистика по группам действий
    const actionStats = {};
    results.forEach(result => {
        const action = result.name.includes('Navigate') ? 'navigate' :
                      result.name.includes('Click') || result.name.includes('Type') || result.name.includes('Hover') || 
                      result.name.includes('Drag') || result.name.includes('Select') || result.name.includes('Press') ? 'interact' :
                      result.name.includes('screenshot') || result.name.includes('snapshot') || result.name.includes('PDF') || 
                      result.name.includes('console') || result.name.includes('network') ? 'capture' :
                      result.name.includes('Upload') ? 'upload' :
                      result.name.includes('Wait') ? 'wait' :
                      result.name.includes('Resize') || result.name.includes('dialog') || result.name.includes('tab') || 
                      result.name.includes('Install') || result.name.includes('Close') ? 'manage' : 'error';
        
        if (!actionStats[action]) {
            actionStats[action] = { passed: 0, total: 0 };
        }
        actionStats[action].total++;
        if (result.success) {
            actionStats[action].passed++;
        }
    });

    console.log('\n📋 СТАТИСТИКА ПО ГРУППАМ ДЕЙСТВИЙ:');
    Object.entries(actionStats).forEach(([action, stats]) => {
        const percentage = Math.round((stats.passed / stats.total) * 100);
        console.log(`${action}: ${stats.passed}/${stats.total} (${percentage}%)`);
    });

    // Тестирование схемы OpenAI Function Calling
    console.log('\n🔧 ТЕСТИРОВАНИЕ СХЕМЫ OPENAI FUNCTION CALLING:');
    try {
        const schema = browserTool.getSchema();
        console.log('✅ Схема успешно сгенерирована');
        console.log(`📋 Название функции: ${schema.function.name}`);
        console.log(`📝 Описание: ${schema.function.description}`);
        console.log(`🎯 Доступные действия: ${schema.function.parameters.properties.action.enum.join(', ')}`);
    } catch (error) {
        console.log(`❌ Ошибка генерации схемы: ${error.message}`);
    }

    return {
        passed,
        failed,
        total: passed + failed,
        successRate: Math.round((passed / (passed + failed)) * 100),
        actionStats,
        results
    };
}

/**
 * Тестирование производительности
 */
async function performanceTest() {
    console.log('\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ:');
    
    const iterations = 100;
    const testAction = {
        action: 'navigate',
        operation: 'navigate',
        url: 'https://example.com'
    };

    const startTime = Date.now();
    
    for (let i = 0; i < iterations; i++) {
        await browserTool.execute(testAction);
    }
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    const avgTime = totalTime / iterations;

    console.log(`📊 ${iterations} операций выполнено за ${totalTime}ms`);
    console.log(`⚡ Среднее время на операцию: ${avgTime.toFixed(2)}ms`);
    console.log(`🚀 Операций в секунду: ${Math.round(1000 / avgTime)}`);
}

/**
 * Тестирование кэширования
 */
async function cacheTest() {
    console.log('\n💾 ТЕСТИРОВАНИЕ КЭШИРОВАНИЯ:');
    
    const testAction = {
        action: 'navigate',
        operation: 'navigate',
        url: 'https://example.com'
    };

    // Первый вызов (без кэша)
    const start1 = Date.now();
    await browserTool.execute(testAction);
    const time1 = Date.now() - start1;

    // Второй вызов (с кэшем)
    const start2 = Date.now();
    await browserTool.execute(testAction);
    const time2 = Date.now() - start2;

    console.log(`📊 Первый вызов (без кэша): ${time1}ms`);
    console.log(`📊 Второй вызов (с кэшем): ${time2}ms`);
    
    if (time2 < time1) {
        console.log(`✅ Кэширование работает! Ускорение: ${Math.round((time1 - time2) / time1 * 100)}%`);
    } else {
        console.log(`⚠️  Кэширование не дало ускорения`);
    }

    // Очистка кэша
    browserTool.clearCache();
    console.log('🧹 Кэш очищен');
}

// Запуск всех тестов
async function main() {
    try {
        const testResults = await runTests();
        await performanceTest();
        await cacheTest();
        
        console.log('\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!');
        
        // Возврат результатов для использования в других скриптах
        return testResults;
        
    } catch (error) {
        console.error('💥 Критическая ошибка при тестировании:', error);
        process.exit(1);
    }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    main();
}

module.exports = {
    runTests,
    performanceTest,
    cacheTest,
    testScenarios
};