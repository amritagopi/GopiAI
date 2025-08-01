/**
 * Тестовый скрипт для проверки MCP сервера
 */

const { GopiAIMCPServer } = require('./mcp_server.js');
const path = require('path');

async function testMCPServer() {
    console.log('🚀 Тестирование GopiAI MCP Server');
    console.log('=' * 50);

    try {
        // Создаём экземпляр сервера
        const server = new GopiAIMCPServer();
        console.log('✅ MCP сервер создан');

        // Тестируем установку рабочего пространства
        console.log('\n📁 Тестирование setWorkspace...');
        const workspacePath = process.cwd();
        
        const workspaceResult = await server.handleSetWorkspace({ path: workspacePath });
        console.log('Результат setWorkspace:', JSON.stringify(workspaceResult, null, 2));

        // Тестируем получение информации о рабочем пространстве
        console.log('\n📊 Тестирование workspace_info...');
        const infoResult = await server.handleWorkspaceInfo({});
        console.log('Результат workspace_info:', JSON.stringify(infoResult, null, 2));

        // Тестируем поиск файлов
        console.log('\n🔍 Тестирование workspace_search...');
        const searchResult = await server.handleWorkspaceSearch({ pattern: '*.js', maxResults: 5 });
        console.log('Результат workspace_search:', JSON.stringify(searchResult, null, 2));

        // Тестируем унифицированный инструмент задач
        console.log('\n📋 Тестирование task_manage...');
        const taskResult = await server.handleTaskManage({
            action: 'list',
            data: { format: 'human' }
        });
        console.log('Результат task_manage:', JSON.stringify(taskResult, null, 2));

        // Тестируем унифицированный инструмент файловой системы
        console.log('\n📂 Тестирование file_system...');
        const fileResult = await server.handleFileSystem({
            action: 'list',
            data: { path: '.', detailed: false }
        });
        console.log('Результат file_system:', JSON.stringify(fileResult, null, 2));

        console.log('\n🎉 Все тесты завершены!');

    } catch (error) {
        console.error('❌ Ошибка тестирования:', error.message);
        console.error(error.stack);
    }
}

// Запуск тестов
if (require.main === module) {
    testMCPServer();
}

module.exports = { testMCPServer };