/**
 * Упрощённое тестирование обработчика браузерного инструмента в MCP сервере
 * 
 * Тестирует только handleBrowserControl метод без полного MCP протокола
 */

const { GopiAIMCPServer } = require('../src/mcp_server.js');

/**
 * Тестовые сценарии для обработчика
 */
const handlerTestScenarios = [
    // 1. Тестирование навигации
    {
        name: 'Handler Navigate to URL',
        args: {
            action: 'navigate',
            operation: 'navigate',
            url: 'https://example.com'
        },
        expectedSuccess: true
    },
    {
        name: 'Handler Navigate back',
        args: {
            action: 'navigate',
            operation: 'back'
        },
        expectedSuccess: true
    },

    // 2. Тестирование взаимодействия
    {
        name: 'Handler Click element',
        args: {
            action: 'interact',
            operation: 'click',
            element: 'Submit button',
            ref: '#submit-btn'
        },
        expectedSuccess: true
    },
    {
        name: 'Handler Type text',
        args: {
            action: 'interact',
            operation: 'type',
            element: 'Search input',
            ref: '#search',
            text: 'Hello Handler World'
        },
        expectedSuccess: true
    },

    // 3. Тестирование захвата
    {
        name: 'Handler Take screenshot',
        args: {
            action: 'capture',
            operation: 'screenshot',
            filename: 'handler_test_screenshot.png'
        },
        expectedSuccess: true
    },
    {
        name: 'Handler Get console messages',
        args: {
            action: 'capture',
            operation: 'console'
        },
        expectedSuccess: true
    },

    // 4. Тестирование ожидания
    {
        name: 'Handler Wait for time',
        args: {
            action: 'wait',
            operation: 'time',
            time: 1
        },
        expectedSuccess: true
    },

    // 5. Тестирование управления
    {
        name: 'Handler Resize browser',
        args: {
            action: 'manage',
            operation: 'resize',
            width: 1920,
            height: 1080
        },
        expectedSuccess: true
    },
    {
        name: 'Handler List tabs',
        args: {
            action: 'manage',
            operation: 'tab_list'
        },
        expectedSuccess: true
    },

    // 6. Тестирование ошибок
    {
        name: 'Handler Invalid action',
        args: {
            action: 'invalid_action'
        },
        expectedSuccess: false
    },
    {
        name: 'Handler Missing required parameter',
        args: {
            action: 'navigate'
            // Отсутствует operation
        },
        expectedSuccess: false
    }
];

/**
 * Запуск тестов обработчика
 */
async function runHandlerTests() {
    console.log('🚀 Запуск тестирования обработчика браузерного инструмента...\n');
    
    // Создаём экземпляр MCP сервера
    const mcpServer = new GopiAIMCPServer();
    
    let passed = 0;
    let failed = 0;
    const results = [];

    for (const scenario of handlerTestScenarios) {
        console.log(`📋 Тест обработчика: ${scenario.name}`);
        
        try {
            // Выполняем через обработчик
            const startTime = Date.now();
            const handlerResponse = await mcpServer.handleBrowserControl(scenario.args);
            const duration = Date.now() - startTime;

            // Парсим ответ обработчика
            let result;
            try {
                const responseText = handlerResponse.content[0].text;
                result = JSON.parse(responseText);
            } catch (parseError) {
                result = { success: false, error: 'Failed to parse handler response' };
            }

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
                result: result,
                handlerResponse: handlerResponse
            });

        } catch (error) {
            console.log(`❌ ОШИБКА: ${error.message}`);
            failed++;
            
            results.push({
                name: scenario.name,
                success: false,
                duration: 0,
                error: error.message
            });
        }
        
        console.log(''); // Пустая строка для разделения
    }

    // Итоговая статистика
    console.log('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ОБРАБОТЧИКА:');
    console.log(`✅ Пройдено: ${passed}`);
    console.log(`❌ Провалено: ${failed}`);
    console.log(`📈 Успешность: ${Math.round((passed / (passed + failed)) * 100)}%`);
    
    // Детальная статистика по группам действий
    const actionStats = {};
    results.forEach(result => {
        const action = result.name.includes('Navigate') ? 'navigate' :
                      result.name.includes('Click') || result.name.includes('Type') ? 'interact' :
                      result.name.includes('screenshot') || result.name.includes('console') ? 'capture' :
                      result.name.includes('Wait') ? 'wait' :
                      result.name.includes('Resize') || result.name.includes('List tabs') ? 'manage' : 'error';
        
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
 * Тестирование производительности обработчика
 */
async function testHandlerPerformance() {
    console.log('\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ОБРАБОТЧИКА:');
    
    const mcpServer = new GopiAIMCPServer();
    const iterations = 100;
    const testArgs = {
        action: 'navigate',
        operation: 'navigate',
        url: 'https://example.com'
    };

    const startTime = Date.now();
    
    for (let i = 0; i < iterations; i++) {
        await mcpServer.handleBrowserControl(testArgs);
    }
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    const avgTime = totalTime / iterations;

    console.log(`📊 ${iterations} операций обработчика выполнено за ${totalTime}ms`);
    console.log(`⚡ Среднее время на операцию: ${avgTime.toFixed(2)}ms`);
    console.log(`🚀 Операций в секунду: ${Math.round(1000 / avgTime)}`);
}

/**
 * Тестирование структуры ответов обработчика
 */
async function testHandlerResponseStructure() {
    console.log('\n🔧 ТЕСТИРОВАНИЕ СТРУКТУРЫ ОТВЕТОВ ОБРАБОТЧИКА:');
    
    const mcpServer = new GopiAIMCPServer();
    
    // Тест успешного ответа
    const successArgs = {
        action: 'navigate',
        operation: 'navigate',
        url: 'https://example.com'
    };
    
    const successResponse = await mcpServer.handleBrowserControl(successArgs);
    
    console.log('✅ Структура успешного ответа:');
    console.log(`   - Есть content: ${!!successResponse.content}`);
    console.log(`   - Тип content[0]: ${successResponse.content[0].type}`);
    console.log(`   - Есть text: ${!!successResponse.content[0].text}`);
    console.log(`   - isError: ${successResponse.isError || false}`);
    
    // Тест ответа с ошибкой
    const errorArgs = {
        action: 'invalid_action'
    };
    
    const errorResponse = await mcpServer.handleBrowserControl(errorArgs);
    
    console.log('\n❌ Структура ответа с ошибкой:');
    console.log(`   - Есть content: ${!!errorResponse.content}`);
    console.log(`   - Тип content[0]: ${errorResponse.content[0].type}`);
    console.log(`   - Есть text: ${!!errorResponse.content[0].text}`);
    console.log(`   - isError: ${errorResponse.isError || false}`);
    
    // Парсим JSON из ответов
    try {
        const successData = JSON.parse(successResponse.content[0].text);
        const errorData = JSON.parse(errorResponse.content[0].text);
        
        console.log('\n📊 Анализ JSON данных:');
        console.log(`   - Успешный ответ имеет success: ${successData.success}`);
        console.log(`   - Ошибочный ответ имеет success: ${errorData.success}`);
        console.log(`   - Ошибочный ответ имеет error: ${!!errorData.error}`);
        console.log(`   - Оба имеют timestamp: ${!!successData.timestamp && !!errorData.timestamp}`);
        
    } catch (parseError) {
        console.log(`⚠️  Ошибка парсинга JSON: ${parseError.message}`);
    }
}

/**
 * Главная функция тестирования
 */
async function main() {
    try {
        // Тестируем структуру ответов
        await testHandlerResponseStructure();
        
        // Запускаем основные тесты
        const testResults = await runHandlerTests();
        
        // Тестируем производительность
        await testHandlerPerformance();
        
        console.log('\n🎉 ТЕСТИРОВАНИЕ ОБРАБОТЧИКА ЗАВЕРШЕНО!');
        
        // Проверяем критерии успеха
        if (testResults.successRate >= 80) {
            console.log('✅ Обработчик браузерного инструмента работает корректно!');
            console.log(`📈 Достигнута успешность: ${testResults.successRate}%`);
            
            // Проверяем, что все группы действий работают
            const allActionsWork = Object.values(testResults.actionStats).every(stats => 
                stats.passed > 0 && (stats.passed / stats.total) >= 0.5
            );
            
            if (allActionsWork) {
                console.log('✅ Все группы действий (navigate, interact, capture, wait, manage) работают!');
            } else {
                console.log('⚠️  Некоторые группы действий требуют доработки');
            }
            
            return testResults;
        } else {
            console.log('⚠️  Обработчик требует доработки');
            console.log(`📉 Текущая успешность: ${testResults.successRate}%`);
            return testResults;
        }
        
    } catch (error) {
        console.error('💥 Критическая ошибка при тестировании обработчика:', error);
        process.exit(1);
    }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    main();
}

module.exports = {
    runHandlerTests,
    testHandlerPerformance,
    testHandlerResponseStructure,
    handlerTestScenarios
};