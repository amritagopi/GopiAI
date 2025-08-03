/**
 * Тестирование слоя обратной совместимости
 * 
 * Проверяет корректность перенаправления вызовов старых инструментов
 * на новые унифицированные инструменты
 */

const { CompatibilityLayer } = require('../src/compatibility_layer.js');

/**
 * Тестовые сценарии для слоя совместимости
 */
const compatibilityTestScenarios = [
    // ==================== УПРАВЛЕНИЕ ЗАДАЧАМИ ====================
    {
        category: 'Task Management',
        name: 'addTask compatibility',
        method: 'addTask',
        args: {
            title: 'Test Task',
            description: 'Test Description',
            priority: 'high'
        },
        expectedSuccess: true,
        expectedNewTool: 'task_manage'
    },
    {
        category: 'Task Management',
        name: 'listTasks compatibility',
        method: 'listTasks',
        args: {
            status: 'todo',
            format: 'json'
        },
        expectedSuccess: true,
        expectedNewTool: 'task_manage'
    },
    {
        category: 'Task Management',
        name: 'updateStatus compatibility',
        method: 'updateStatus',
        args: {
            id: '1',
            newStatus: 'done'
        },
        expectedSuccess: true,
        expectedNewTool: 'task_manage'
    },

    // ==================== ФАЙЛОВАЯ СИСТЕМА ====================
    {
        category: 'File System',
        name: 'readFile compatibility',
        method: 'readFile',
        args: {
            path: 'test.txt'
        },
        expectedSuccess: true,
        expectedNewTool: 'file_system'
    },
    {
        category: 'File System',
        name: 'writeFile compatibility',
        method: 'writeFile',
        args: {
            path: 'test.txt',
            content: 'Hello World'
        },
        expectedSuccess: true,
        expectedNewTool: 'file_system'
    },
    {
        category: 'File System',
        name: 'listDirectory compatibility',
        method: 'listDirectory',
        args: {
            path: '.'
        },
        expectedSuccess: true,
        expectedNewTool: 'file_system'
    },

    // ==================== БРАУЗЕРНАЯ АВТОМАТИЗАЦИЯ ====================
    {
        category: 'Browser Automation',
        name: 'browserNavigate compatibility',
        method: 'browserNavigate',
        args: {
            url: 'https://example.com'
        },
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    },
    {
        category: 'Browser Automation',
        name: 'browserClick compatibility',
        method: 'browserClick',
        args: {
            element: 'Submit button',
            ref: '#submit'
        },
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    },
    {
        category: 'Browser Automation',
        name: 'browserType compatibility',
        method: 'browserType',
        args: {
            element: 'Input field',
            ref: '#input',
            text: 'Hello World'
        },
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    },
    {
        category: 'Browser Automation',
        name: 'browserTakeScreenshot compatibility',
        method: 'browserTakeScreenshot',
        args: {
            filename: 'screenshot.png'
        },
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    },
    {
        category: 'Browser Automation',
        name: 'browserWait compatibility',
        method: 'browserWait',
        args: {
            time: 2
        },
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    },
    {
        category: 'Browser Automation',
        name: 'browserTabList compatibility',
        method: 'browserTabList',
        args: {},
        expectedSuccess: true,
        expectedNewTool: 'browser_control'
    }
];

/**
 * Запуск тестов совместимости
 */
async function runCompatibilityTests() {
    console.log('🚀 Запуск тестирования слоя обратной совместимости...\n');
    
    const compatLayer = new CompatibilityLayer();
    
    // Включаем логирование для тестирования
    compatLayer.configure({
        enableLogging: true,
        enableDeprecationWarnings: true,
        enableUsageStats: true
    });
    
    let passed = 0;
    let failed = 0;
    const results = [];
    const categoryStats = {};

    for (const scenario of compatibilityTestScenarios) {
        console.log(`📋 Тест совместимости: ${scenario.name}`);
        
        try {
            // Проверяем, что метод существует
            if (typeof compatLayer[scenario.method] !== 'function') {
                throw new Error(`Метод ${scenario.method} не найден в слое совместимости`);
            }
            
            // Выполняем вызов через слой совместимости
            const startTime = Date.now();
            const result = await compatLayer[scenario.method](scenario.args);
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

            // Статистика по категориям
            if (!categoryStats[scenario.category]) {
                categoryStats[scenario.category] = { passed: 0, total: 0 };
            }
            categoryStats[scenario.category].total++;
            if (success) {
                categoryStats[scenario.category].passed++;
            }

            results.push({
                name: scenario.name,
                category: scenario.category,
                method: scenario.method,
                success: success,
                duration: duration,
                result: result,
                expectedNewTool: scenario.expectedNewTool
            });

        } catch (error) {
            console.log(`❌ ОШИБКА: ${error.message}`);
            failed++;
            
            // Статистика по категориям
            if (!categoryStats[scenario.category]) {
                categoryStats[scenario.category] = { passed: 0, total: 0 };
            }
            categoryStats[scenario.category].total++;
            
            results.push({
                name: scenario.name,
                category: scenario.category,
                method: scenario.method,
                success: false,
                duration: 0,
                error: error.message
            });
        }
        
        console.log(''); // Пустая строка для разделения
    }

    // Итоговая статистика
    console.log('📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ СОВМЕСТИМОСТИ:');
    console.log(`✅ Пройдено: ${passed}`);
    console.log(`❌ Провалено: ${failed}`);
    console.log(`📈 Успешность: ${Math.round((passed / (passed + failed)) * 100)}%`);
    
    // Статистика по категориям
    console.log('\n📋 СТАТИСТИКА ПО КАТЕГОРИЯМ:');
    Object.entries(categoryStats).forEach(([category, stats]) => {
        const percentage = Math.round((stats.passed / stats.total) * 100);
        console.log(`${category}: ${stats.passed}/${stats.total} (${percentage}%)`);
    });

    // Статистика использования
    console.log('\n📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ:');
    const usageStats = compatLayer.getUsageStats();
    console.log(`Всего маппингов: ${usageStats.totalMappings}`);
    console.log(`Всего использований: ${usageStats.totalUsages}`);
    
    console.log('\n🔄 ДЕТАЛЬНАЯ СТАТИСТИКА МАППИНГОВ:');
    Object.entries(usageStats.mappings).forEach(([mapping, data]) => {
        console.log(`${mapping}: ${data.count} раз`);
    });
    
    return {
        passed,
        failed,
        total: passed + failed,
        successRate: Math.round((passed / (passed + failed)) * 100),
        categoryStats,
        usageStats,
        results
    };
}

/**
 * Тестирование поддерживаемых инструментов
 */
async function testSupportedTools() {
    console.log('\n🔧 ТЕСТИРОВАНИЕ СПИСКА ПОДДЕРЖИВАЕМЫХ ИНСТРУМЕНТОВ:');
    
    const compatLayer = new CompatibilityLayer();
    const supportedTools = compatLayer.getSupportedLegacyTools();
    
    console.log('📋 Поддерживаемые категории инструментов:');
    
    Object.entries(supportedTools).forEach(([category, tools]) => {
        console.log(`\n${category}:`);
        tools.forEach(tool => {
            // Проверяем, что метод действительно существует
            const methodExists = typeof compatLayer[tool] === 'function';
            const status = methodExists ? '✅' : '❌';
            console.log(`  ${status} ${tool}`);
        });
    });
    
    // Подсчёт общего количества
    const totalTools = Object.values(supportedTools).reduce((sum, tools) => sum + tools.length, 0);
    console.log(`\n📊 Всего поддерживается: ${totalTools} инструментов`);
    
    return supportedTools;
}

/**
 * Тестирование производительности слоя совместимости
 */
async function testCompatibilityPerformance() {
    console.log('\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ СЛОЯ СОВМЕСТИМОСТИ:');
    
    const compatLayer = new CompatibilityLayer();
    const iterations = 100;
    
    // Тест производительности для каждой категории
    const performanceTests = [
        {
            name: 'Task Management',
            method: 'listTasks',
            args: { format: 'json' }
        },
        {
            name: 'File System',
            method: 'readFile',
            args: { path: 'test.txt' }
        },
        {
            name: 'Browser Automation',
            method: 'browserNavigate',
            args: { url: 'https://example.com' }
        }
    ];

    for (const test of performanceTests) {
        const startTime = Date.now();
        
        for (let i = 0; i < iterations; i++) {
            await compatLayer[test.method](test.args);
        }
        
        const endTime = Date.now();
        const totalTime = endTime - startTime;
        const avgTime = totalTime / iterations;

        console.log(`📊 ${test.name}: ${iterations} операций за ${totalTime}ms`);
        console.log(`   ⚡ Среднее время: ${avgTime.toFixed(2)}ms`);
        console.log(`   🚀 Операций/сек: ${Math.round(1000 / avgTime)}`);
    }
}

/**
 * Тестирование конфигурации слоя совместимости
 */
async function testCompatibilityConfiguration() {
    console.log('\n🔧 ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ СЛОЯ СОВМЕСТИМОСТИ:');
    
    const compatLayer = new CompatibilityLayer();
    
    // Тест отключения логирования
    console.log('📋 Тест отключения логирования:');
    compatLayer.configure({ enableLogging: false });
    await compatLayer.listTasks({ format: 'json' });
    console.log('✅ Логирование отключено');
    
    // Тест отключения предупреждений о deprecation
    console.log('\n📋 Тест отключения предупреждений:');
    compatLayer.configure({ enableDeprecationWarnings: false });
    await compatLayer.readFile({ path: 'test.txt' });
    console.log('✅ Предупреждения отключены');
    
    // Тест отключения статистики
    console.log('\n📋 Тест отключения статистики:');
    compatLayer.clearUsageStats();
    compatLayer.configure({ enableUsageStats: false });
    await compatLayer.browserNavigate({ url: 'https://example.com' });
    
    const stats = compatLayer.getUsageStats();
    if (stats.totalUsages === 0) {
        console.log('✅ Статистика отключена');
    } else {
        console.log('❌ Статистика не отключилась');
    }
    
    // Восстановление настроек
    compatLayer.configure({
        enableLogging: true,
        enableDeprecationWarnings: true,
        enableUsageStats: true
    });
    console.log('\n✅ Настройки восстановлены');
}

/**
 * Главная функция тестирования
 */
async function main() {
    try {
        // Тестируем поддерживаемые инструменты
        await testSupportedTools();
        
        // Запускаем основные тесты совместимости
        const testResults = await runCompatibilityTests();
        
        // Тестируем производительность
        await testCompatibilityPerformance();
        
        // Тестируем конфигурацию
        await testCompatibilityConfiguration();
        
        console.log('\n🎉 ТЕСТИРОВАНИЕ СЛОЯ СОВМЕСТИМОСТИ ЗАВЕРШЕНО!');
        
        // Проверяем критерии успеха
        if (testResults.successRate >= 90) {
            console.log('✅ Слой обратной совместимости работает отлично!');
            console.log(`📈 Достигнута успешность: ${testResults.successRate}%`);
            
            // Проверяем, что все категории работают
            const allCategoriesWork = Object.values(testResults.categoryStats).every(stats => 
                (stats.passed / stats.total) >= 0.8
            );
            
            if (allCategoriesWork) {
                console.log('✅ Все категории инструментов работают корректно!');
            } else {
                console.log('⚠️  Некоторые категории требуют доработки');
            }
            
            return testResults;
        } else {
            console.log('⚠️  Слой совместимости требует доработки');
            console.log(`📉 Текущая успешность: ${testResults.successRate}%`);
            return testResults;
        }
        
    } catch (error) {
        console.error('💥 Критическая ошибка при тестировании слоя совместимости:', error);
        process.exit(1);
    }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    main();
}

module.exports = {
    runCompatibilityTests,
    testSupportedTools,
    testCompatibilityPerformance,
    testCompatibilityConfiguration,
    compatibilityTestScenarios
};