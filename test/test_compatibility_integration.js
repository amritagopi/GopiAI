/**
 * Интеграционное тестирование слоя обратной совместимости
 * 
 * Тестирует слой совместимости с правильной инициализацией
 * и интеграцией с реальными унифицированными инструментами
 */

const { CompatibilityLayer } = require('../src/compatibility_layer.js');
const fs = require('fs');
const path = require('path');

/**
 * Создание тестовой среды
 */
async function setupTestEnvironment() {
    // Создаём тестовый файл tasks.json если его нет
    const tasksFile = path.join(process.cwd(), 'tasks.json');
    if (!fs.existsSync(tasksFile)) {
        const initialTasks = {
            tasks: [],
            nextId: 1,
            lastUpdated: new Date().toISOString()
        };
        fs.writeFileSync(tasksFile, JSON.stringify(initialTasks, null, 2));
        console.log('✅ Создан тестовый файл tasks.json');
    }
    
    // Создаём тестовую директорию
    const testDir = path.join(process.cwd(), 'test_files');
    if (!fs.existsSync(testDir)) {
        fs.mkdirSync(testDir, { recursive: true });
        console.log('✅ Создана тестовая директория test_files');
    }
    
    // Создаём тестовый файл
    const testFile = path.join(testDir, 'test.txt');
    fs.writeFileSync(testFile, 'Hello World from compatibility test');
    console.log('✅ Создан тестовый файл test.txt');
}

/**
 * Очистка тестовой среды
 */
async function cleanupTestEnvironment() {
    try {
        // Удаляем тестовую директорию
        const testDir = path.join(process.cwd(), 'test_files');
        if (fs.existsSync(testDir)) {
            fs.rmSync(testDir, { recursive: true, force: true });
            console.log('✅ Удалена тестовая директория');
        }
    } catch (error) {
        console.warn('⚠️  Ошибка при очистке:', error.message);
    }
}

/**
 * Интеграционные тестовые сценарии
 */
const integrationTestScenarios = [
    // ==================== УПРАВЛЕНИЕ ЗАДАЧАМИ ====================
    {
        category: 'Task Management',
        name: 'Full task workflow compatibility',
        steps: [
            {
                method: 'addTask',
                args: {
                    title: 'Compatibility Test Task',
                    description: 'Testing backward compatibility',
                    priority: 'high'
                },
                expectedSuccess: true
            },
            {
                method: 'listTasks',
                args: { format: 'json' },
                expectedSuccess: true,
                validate: (result) => result.tasks && Array.isArray(result.tasks)
            },
            {
                method: 'updateStatus',
                args: {
                    id: '1',
                    newStatus: 'inprogress'
                },
                expectedSuccess: true
            }
        ]
    },

    // ==================== ФАЙЛОВАЯ СИСТЕМА ====================
    {
        category: 'File System',
        name: 'Full file operations compatibility',
        steps: [
            {
                method: 'writeFile',
                args: {
                    path: 'test_files/compat_test.txt',
                    content: 'Compatibility test content'
                },
                expectedSuccess: true
            },
            {
                method: 'readFile',
                args: {
                    path: 'test_files/compat_test.txt'
                },
                expectedSuccess: true,
                validate: (result) => result.content && result.content.includes('Compatibility test')
            },
            {
                method: 'listDirectory',
                args: {
                    path: 'test_files'
                },
                expectedSuccess: true,
                validate: (result) => result.files && Array.isArray(result.files)
            }
        ]
    },

    // ==================== БРАУЗЕРНАЯ АВТОМАТИЗАЦИЯ ====================
    {
        category: 'Browser Automation',
        name: 'Full browser workflow compatibility',
        steps: [
            {
                method: 'browserNavigate',
                args: {
                    url: 'https://example.com'
                },
                expectedSuccess: true
            },
            {
                method: 'browserTakeScreenshot',
                args: {
                    filename: 'compat_test_screenshot.png'
                },
                expectedSuccess: true
            },
            {
                method: 'browserTabList',
                args: {},
                expectedSuccess: true,
                validate: (result) => result.tabs && Array.isArray(result.tabs)
            }
        ]
    }
];

/**
 * Запуск интеграционных тестов
 */
async function runIntegrationTests() {
    console.log('🚀 Запуск интеграционного тестирования слоя совместимости...\n');
    
    // Настройка тестовой среды
    await setupTestEnvironment();
    
    const compatLayer = new CompatibilityLayer();
    
    // Настройка слоя совместимости
    compatLayer.configure({
        enableLogging: true,
        enableDeprecationWarnings: false, // Отключаем для чистоты вывода
        enableUsageStats: true
    });
    
    let totalPassed = 0;
    let totalFailed = 0;
    const results = [];

    for (const scenario of integrationTestScenarios) {
        console.log(`📋 Интеграционный тест: ${scenario.name}`);
        
        let scenarioPassed = 0;
        let scenarioFailed = 0;
        const scenarioResults = [];
        
        for (let i = 0; i < scenario.steps.length; i++) {
            const step = scenario.steps[i];
            console.log(`  📝 Шаг ${i + 1}: ${step.method}`);
            
            try {
                // Проверяем, что метод существует
                if (typeof compatLayer[step.method] !== 'function') {
                    throw new Error(`Метод ${step.method} не найден`);
                }
                
                // Выполняем шаг
                const startTime = Date.now();
                const result = await compatLayer[step.method](step.args);
                const duration = Date.now() - startTime;

                // Базовая проверка успешности
                let success = result.success === step.expectedSuccess;
                
                // Дополнительная валидация если есть
                if (success && step.validate) {
                    try {
                        success = step.validate(result);
                    } catch (validateError) {
                        success = false;
                        console.log(`    ⚠️  Ошибка валидации: ${validateError.message}`);
                    }
                }
                
                if (success) {
                    console.log(`    ✅ Успешно (${duration}ms)`);
                    scenarioPassed++;
                    totalPassed++;
                } else {
                    console.log(`    ❌ Провалено (${duration}ms)`);
                    console.log(`       Ожидалось: success=${step.expectedSuccess}`);
                    console.log(`       Получено: success=${result.success}`);
                    if (result.error) {
                        console.log(`       Ошибка: ${result.error}`);
                    }
                    scenarioFailed++;
                    totalFailed++;
                }

                scenarioResults.push({
                    step: i + 1,
                    method: step.method,
                    success: success,
                    duration: duration,
                    result: result
                });

            } catch (error) {
                console.log(`    ❌ ОШИБКА: ${error.message}`);
                scenarioFailed++;
                totalFailed++;
                
                scenarioResults.push({
                    step: i + 1,
                    method: step.method,
                    success: false,
                    duration: 0,
                    error: error.message
                });
            }
        }
        
        const scenarioSuccess = scenarioFailed === 0;
        const scenarioRate = Math.round((scenarioPassed / (scenarioPassed + scenarioFailed)) * 100);
        
        console.log(`  📊 Сценарий: ${scenarioPassed}/${scenarioPassed + scenarioFailed} (${scenarioRate}%) ${scenarioSuccess ? '✅' : '❌'}`);
        console.log(''); // Пустая строка
        
        results.push({
            name: scenario.name,
            category: scenario.category,
            success: scenarioSuccess,
            passed: scenarioPassed,
            failed: scenarioFailed,
            rate: scenarioRate,
            steps: scenarioResults
        });
    }

    // Итоговая статистика
    console.log('📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ:');
    console.log(`✅ Пройдено шагов: ${totalPassed}`);
    console.log(`❌ Провалено шагов: ${totalFailed}`);
    console.log(`📈 Общая успешность: ${Math.round((totalPassed / (totalPassed + totalFailed)) * 100)}%`);
    
    // Статистика по сценариям
    console.log('\n📋 СТАТИСТИКА ПО СЦЕНАРИЯМ:');
    results.forEach(result => {
        const status = result.success ? '✅' : '❌';
        console.log(`${status} ${result.name}: ${result.rate}%`);
    });

    // Статистика использования
    console.log('\n📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ СЛОЯ СОВМЕСТИМОСТИ:');
    const usageStats = compatLayer.getUsageStats();
    console.log(`Всего маппингов использовано: ${usageStats.totalMappings}`);
    console.log(`Всего вызовов через слой: ${usageStats.totalUsages}`);
    
    // Очистка тестовой среды
    await cleanupTestEnvironment();
    
    return {
        totalPassed,
        totalFailed,
        totalSteps: totalPassed + totalFailed,
        successRate: Math.round((totalPassed / (totalPassed + totalFailed)) * 100),
        scenarios: results,
        usageStats
    };
}

/**
 * Тестирование производительности интеграции
 */
async function testIntegrationPerformance() {
    console.log('\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ИНТЕГРАЦИИ:');
    
    await setupTestEnvironment();
    
    const compatLayer = new CompatibilityLayer();
    compatLayer.configure({ enableLogging: false, enableDeprecationWarnings: false });
    
    const performanceTests = [
        {
            name: 'Task Management Chain',
            operations: [
                () => compatLayer.addTask({ title: 'Perf Test', priority: 'medium' }),
                () => compatLayer.listTasks({ format: 'json' }),
                () => compatLayer.updateStatus({ id: '1', newStatus: 'done' })
            ]
        },
        {
            name: 'File System Chain',
            operations: [
                () => compatLayer.writeFile({ path: 'test_files/perf.txt', content: 'Performance test' }),
                () => compatLayer.readFile({ path: 'test_files/perf.txt' }),
                () => compatLayer.listDirectory({ path: 'test_files' })
            ]
        },
        {
            name: 'Browser Automation Chain',
            operations: [
                () => compatLayer.browserNavigate({ url: 'https://example.com' }),
                () => compatLayer.browserTakeScreenshot({ filename: 'perf.png' }),
                () => compatLayer.browserTabList({})
            ]
        }
    ];

    for (const test of performanceTests) {
        const iterations = 10;
        const startTime = Date.now();
        
        for (let i = 0; i < iterations; i++) {
            for (const operation of test.operations) {
                await operation();
            }
        }
        
        const endTime = Date.now();
        const totalTime = endTime - startTime;
        const avgTime = totalTime / (iterations * test.operations.length);

        console.log(`📊 ${test.name}:`);
        console.log(`   ${iterations * test.operations.length} операций за ${totalTime}ms`);
        console.log(`   ⚡ Среднее время: ${avgTime.toFixed(2)}ms`);
        console.log(`   🚀 Операций/сек: ${Math.round(1000 / avgTime)}`);
    }
    
    await cleanupTestEnvironment();
}

/**
 * Главная функция
 */
async function main() {
    try {
        console.log('🔧 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ СЛОЯ ОБРАТНОЙ СОВМЕСТИМОСТИ\n');
        
        // Запускаем интеграционные тесты
        const testResults = await runIntegrationTests();
        
        // Тестируем производительность
        await testIntegrationPerformance();
        
        console.log('\n🎉 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!');
        
        // Проверяем критерии успеха
        if (testResults.successRate >= 80) {
            console.log('✅ Слой обратной совместимости работает корректно!');
            console.log(`📈 Достигнута успешность: ${testResults.successRate}%`);
            
            // Проверяем успешность сценариев
            const successfulScenarios = testResults.scenarios.filter(s => s.success).length;
            const totalScenarios = testResults.scenarios.length;
            
            console.log(`📋 Успешных сценариев: ${successfulScenarios}/${totalScenarios}`);
            
            if (successfulScenarios === totalScenarios) {
                console.log('✅ Все интеграционные сценарии работают!');
            } else {
                console.log('⚠️  Некоторые сценарии требуют доработки');
            }
            
            return testResults;
        } else {
            console.log('⚠️  Слой совместимости требует доработки');
            console.log(`📉 Текущая успешность: ${testResults.successRate}%`);
            return testResults;
        }
        
    } catch (error) {
        console.error('💥 Критическая ошибка при интеграционном тестировании:', error);
        process.exit(1);
    }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    main();
}

module.exports = {
    runIntegrationTests,
    testIntegrationPerformance,
    setupTestEnvironment,
    cleanupTestEnvironment,
    integrationTestScenarios
};