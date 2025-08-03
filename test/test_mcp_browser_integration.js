/**
 * Тестирование интеграции унифицированного браузерного инструмента с MCP сервером
 * 
 * Проверяет корректность работы browser_control инструмента через MCP протокол
 */

const { GopiAIMCPServer } = require('../src/mcp_server.js');

/**
 * Тестовые сценарии для MCP интеграции
 */
const mcpTestScenarios = [
    // 1. Тестирование навигации через MCP
    {
        name: 'MCP Navigate to URL',
        toolName: 'browser_control',
        args: {
            action: 'navigate',
            operation: 'navigate',
            url: 'https://example.com'
        },
        expectedSuccess: true
    },
    {
        name: 'MCP Navigate back',
        toolName: 'browser_control',
        args: {
            action: 'navigate',
            operation: 'back'
        },
        expectedSuccess: true
    },

    // 2. Тестирование взаимодействия через MCP
    {
        name: 'MCP Click element',
        toolName: 'browser_control',
        args: {
            action: 'interact',
            operation: 'click',
            element: 'Submit button',
            ref: '#submit-btn'
        },
        expectedSuccess: true
    },
    {
        name: 'MCP Type text',
        toolName: 'browser_control',
        args: {
            action: 'interact',
            operation: 'type',
            element: 'Search input',
            ref: '#search',
            text: 'Hello MCP World'
        },
        expectedSuccess: true
    },

    // 3. Тестирование захвата через MCP
    {
        name: 'MCP Take screenshot',
        toolName: 'browser_control',
        args: {
            action: 'capture',
            operation: 'screenshot',
            filename: 'mcp_test_screenshot.png'
        },
        expectedSuccess: true
    },
    {
        name: 'MCP Get console messages',
        toolName: 'browser_control',
        args: {
            action: 'capture',
            operation: 'console'
        },
        expectedSuccess: true
    },

    // 4. Тестирование ожидания через MCP
    {
        name: 'MCP Wait for time',
        toolName: 'browser_control',
        args: {
            action: 'wait',
            operation: 'time',
            time: 1
        },
        expectedSuccess: true
    },

    // 5. Тестирование управления через MCP
    {
        name: 'MCP Resize browser',
        toolName: 'browser_control',
        args: {
            action: 'manage',
            operation: 'resize',
            width: 1920,
            height: 1080
        },
        expectedSuccess: true
    },
    {
        name: 'MCP List tabs',
        toolName: 'browser_control',
        args: {
            action: 'manage',
            operation: 'tab_list'
        },
        expectedSuccess: true
    },

    // 6. Тестирование ошибок через MCP
    {
        name: 'MCP Invalid action',
        toolName: 'browser_control',
        args: {
            action: 'invalid_action'
        },
        expectedSuccess: false
    },
    {
        name: 'MCP Missing required parameter',
        toolName: 'browser_control',
        args: {
            action: 'navigate'
            // Отсутствует operation
        },
        expectedSuccess: false
    }
];

/**
 * Создание мок MCP запроса
 */
function createMCPRequest(toolName, args) {
    return {
        params: {
            name: toolName,
            arguments: args
        }
    };
}

/**
 * Запуск тестов MCP интеграции
 */
async function runMCPTests() {
    console.log('🚀 Запуск тестирования MCP интеграции браузерного инструмента...\n');
    
    // Создаём экземпляр MCP сервера
    const mcpServer = new GopiAIMCPServer();
    
    let passed = 0;
    let failed = 0;
    const results = [];

    for (const scenario of mcpTestScenarios) {
        console.log(`📋 MCP Тест: ${scenario.name}`);
        
        try {
            // Создаём MCP запрос
            const request = createMCPRequest(scenario.toolName, scenario.args);
            
            // Выполняем через MCP обработчик
            const startTime = Date.now();
            const mcpResponse = await mcpServer.handleBrowserControl(scenario.args);
            const duration = Date.now() - startTime;

            // Парсим ответ MCP
            let result;
            try {
                const responseText = mcpResponse.content[0].text;
                result = JSON.parse(responseText);
            } catch (parseError) {
                result = { success: false, error: 'Failed to parse MCP response' };
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
                mcpResponse: mcpResponse
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
    console.log('📊 РЕЗУЛЬТАТЫ MCP ТЕСТИРОВАНИЯ:');
    console.log(`✅ Пройдено: ${passed}`);
    console.log(`❌ Провалено: ${failed}`);
    console.log(`📈 Успешность: ${Math.round((passed / (passed + failed)) * 100)}%`);
    
    return {
        passed,
        failed,
        total: passed + failed,
        successRate: Math.round((passed / (passed + failed)) * 100),
        results
    };
}

/**
 * Тестирование списка инструментов MCP
 */
async function testMCPToolsList() {
    console.log('\n🔧 ТЕСТИРОВАНИЕ СПИСКА ИНСТРУМЕНТОВ MCP:');
    
    try {
        const mcpServer = new GopiAIMCPServer();
        
        // Получаем список инструментов (имитируем ListToolsRequest)
        const toolsResponse = await mcpServer.server.request({
            method: 'tools/list',
            params: {}
        });

        // Проверяем наличие browser_control в списке
        const tools = toolsResponse.tools || [];
        const browserTool = tools.find(tool => tool.name === 'browser_control');
        
        if (browserTool) {
            console.log('✅ browser_control найден в списке инструментов');
            console.log(`📝 Описание: ${browserTool.description}`);
            console.log(`🎯 Доступные действия: ${browserTool.inputSchema.properties.action.enum.join(', ')}`);
            
            // Проверяем схему
            const schema = browserTool.inputSchema;
            const requiredFields = schema.required || [];
            const properties = Object.keys(schema.properties || {});
            
            console.log(`📋 Обязательные поля: ${requiredFields.join(', ')}`);
            console.log(`🔧 Всего параметров: ${properties.length}`);
            
            return true;
        } else {
            console.log('❌ browser_control НЕ найден в списке инструментов');
            console.log(`📋 Доступные инструменты: ${tools.map(t => t.name).join(', ')}`);
            return false;
        }
        
    } catch (error) {
        console.log(`❌ Ошибка получения списка инструментов: ${error.message}`);
        return false;
    }
}

/**
 * Тестирование производительности MCP
 */
async function testMCPPerformance() {
    console.log('\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ MCP:');
    
    const mcpServer = new GopiAIMCPServer();
    const iterations = 50;
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

    console.log(`📊 ${iterations} MCP операций выполнено за ${totalTime}ms`);
    console.log(`⚡ Среднее время на MCP операцию: ${avgTime.toFixed(2)}ms`);
    console.log(`🚀 MCP операций в секунду: ${Math.round(1000 / avgTime)}`);
}

/**
 * Главная функция тестирования
 */
async function main() {
    try {
        // Тестируем список инструментов
        const toolsListOk = await testMCPToolsList();
        
        if (!toolsListOk) {
            console.log('❌ Критическая ошибка: browser_control не найден в MCP сервере');
            process.exit(1);
        }
        
        // Запускаем основные тесты
        const testResults = await runMCPTests();
        
        // Тестируем производительность
        await testMCPPerformance();
        
        console.log('\n🎉 MCP ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!');
        
        // Проверяем критерии успеха
        if (testResults.successRate >= 80) {
            console.log('✅ MCP интеграция работает корректно!');
            return testResults;
        } else {
            console.log('⚠️  MCP интеграция требует доработки');
            return testResults;
        }
        
    } catch (error) {
        console.error('💥 Критическая ошибка при MCP тестировании:', error);
        process.exit(1);
    }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    main();
}

module.exports = {
    runMCPTests,
    testMCPToolsList,
    testMCPPerformance,
    mcpTestScenarios
};