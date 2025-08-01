/**
 * Тесты для унифицированного инструмента управления задачами
 * 
 * Проверяет все действия: add, list, update, remove, context, next
 */

const { UnifiedTaskTool } = require('../src/tools/unified_task_tool');
const fs = require('fs').promises;
const path = require('path');

class TaskToolTester {
    constructor() {
        this.tool = new UnifiedTaskTool();
        this.testDir = 'test_temp';
        this.originalTasksFile = this.tool.tasksFile;
    }

    async setup() {
        // Создаём временную директорию для тестов
        await fs.mkdir(this.testDir, { recursive: true });
        this.tool.tasksFile = path.join(this.testDir, 'tasks.json');
        console.log('🔧 Тестовая среда настроена');
    }

    async cleanup() {
        // Очищаем временную директорию
        try {
            await fs.rm(this.testDir, { recursive: true, force: true });
            console.log('🧹 Тестовая среда очищена');
        } catch (error) {
            console.warn('⚠️ Не удалось очистить тестовую среду:', error.message);
        }
        this.tool.tasksFile = this.originalTasksFile;
    }

    async runAllTests() {
        console.log('🚀 Запуск тестов унифицированного инструмента управления задачами');
        console.log('=' * 60);

        try {
            await this.setup();

            await this.testAddTask();
            await this.testAddSubtask();
            await this.testListTasks();
            await this.testUpdateTask();
            await this.testUpdateStatus();
            await this.testGetContext();
            await this.testGetNextTask();
            await this.testRemoveTask();

            console.log('\n✅ Все тесты пройдены успешно!');
            return true;

        } catch (error) {
            console.error('\n❌ Тесты не прошли:', error.message);
            console.error(error.stack);
            return false;

        } finally {
            await this.cleanup();
        }
    }

    async testAddTask() {
        console.log('\n📝 Тест: Добавление задачи');

        const result = await this.tool.execute({
            action: 'add',
            data: {
                title: 'Тестовая задача',
                description: 'Описание тестовой задачи',
                priority: 'high',
                relatedFiles: ['test.js'],
                tests: ['npm test']
            }
        });

        this.assert(result.success, 'Задача должна быть создана успешно');
        this.assert(result.taskId === 1, 'ID задачи должен быть 1');
        this.assert(result.task.title === 'Тестовая задача', 'Название задачи должно совпадать');
        this.assert(result.task.status === 'todo', 'Статус должен быть todo');

        console.log('✅ Задача успешно добавлена');
    }

    async testAddSubtask() {
        console.log('\n📝 Тест: Добавление подзадачи');

        const result = await this.tool.execute({
            action: 'add_subtask',
            data: {
                parentId: '1',
                title: 'Тестовая подзадача',
                relatedFiles: ['subtest.js']
            }
        });

        this.assert(result.success, 'Подзадача должна быть создана успешно');
        this.assert(result.subtaskId === '1.1', 'ID подзадачи должен быть 1.1');
        this.assert(result.subtask.title === 'Тестовая подзадача', 'Название подзадачи должно совпадать');

        console.log('✅ Подзадача успешно добавлена');
    }

    async testListTasks() {
        console.log('\n📝 Тест: Получение списка задач');

        // Тест JSON формата
        const jsonResult = await this.tool.execute({
            action: 'list',
            data: { format: 'json' }
        });

        this.assert(jsonResult.success, 'Список должен быть получен успешно');
        this.assert(jsonResult.tasks.length === 1, 'Должна быть одна задача');
        this.assert(jsonResult.tasks[0].subtasks.length === 1, 'У задачи должна быть одна подзадача');

        // Тест человекочитаемого формата
        const humanResult = await this.tool.execute({
            action: 'list',
            data: { format: 'human' }
        });

        this.assert(humanResult.success, 'Человекочитаемый список должен быть получен');
        this.assert(typeof humanResult.tasks === 'string', 'Результат должен быть строкой');

        console.log('✅ Список задач успешно получен');
    }

    async testUpdateTask() {
        console.log('\n📝 Тест: Обновление задачи');

        const result = await this.tool.execute({
            action: 'update',
            data: {
                id: '1',
                title: 'Обновлённая задача',
                description: 'Новое описание',
                priority: 'critical'
            }
        });

        this.assert(result.success, 'Задача должна быть обновлена успешно');
        this.assert(result.task.title === 'Обновлённая задача', 'Название должно быть обновлено');
        this.assert(result.task.priority === 900, 'Приоритет должен быть critical (900)');

        console.log('✅ Задача успешно обновлена');
    }

    async testUpdateStatus() {
        console.log('\n📝 Тест: Обновление статуса');

        // Обновляем статус основной задачи
        const taskResult = await this.tool.execute({
            action: 'update_status',
            data: {
                id: '1',
                newStatus: 'inprogress',
                message: 'Начал работу над задачей'
            }
        });

        this.assert(taskResult.success, 'Статус задачи должен быть обновлён');
        this.assert(taskResult.newStatus === 'inprogress', 'Новый статус должен быть inprogress');

        // Обновляем статус подзадачи
        const subtaskResult = await this.tool.execute({
            action: 'update_status',
            data: {
                id: '1.1',
                newStatus: 'done',
                message: 'Подзадача выполнена'
            }
        });

        this.assert(subtaskResult.success, 'Статус подзадачи должен быть обновлён');
        this.assert(subtaskResult.newStatus === 'done', 'Новый статус подзадачи должен быть done');

        console.log('✅ Статусы успешно обновлены');
    }

    async testGetContext() {
        console.log('\n📝 Тест: Получение контекста');

        // Контекст основной задачи
        const taskContext = await this.tool.execute({
            action: 'context',
            data: { id: '1' }
        });

        this.assert(taskContext.success, 'Контекст задачи должен быть получен');
        this.assert(taskContext.task.id === 1, 'ID задачи должен совпадать');
        this.assert(taskContext.context.title === 'Обновлённая задача', 'Название в контексте должно совпадать');

        // Контекст подзадачи
        const subtaskContext = await this.tool.execute({
            action: 'context',
            data: { id: '1.1' }
        });

        this.assert(subtaskContext.success, 'Контекст подзадачи должен быть получен');
        this.assert(subtaskContext.task.id === '1.1', 'ID подзадачи должен совпадать');

        console.log('✅ Контекст успешно получен');
    }

    async testGetNextTask() {
        console.log('\n📝 Тест: Получение следующей задачи');

        // Добавляем ещё одну задачу для теста
        await this.tool.execute({
            action: 'add',
            data: {
                title: 'Вторая задача',
                priority: 'low'
            }
        });

        const result = await this.tool.execute({
            action: 'next'
        });

        this.assert(result.success, 'Следующая задача должна быть найдена');
        this.assert(result.task !== null, 'Задача должна существовать');
        this.assert(result.task.id === 2, 'Должна быть возвращена задача с ID 2 (todo статус)');

        console.log('✅ Следующая задача успешно найдена');
    }

    async testRemoveTask() {
        console.log('\n📝 Тест: Удаление задач');

        // Удаляем подзадачу
        const subtaskResult = await this.tool.execute({
            action: 'remove',
            data: { id: '1.1' }
        });

        this.assert(subtaskResult.success, 'Подзадача должна быть удалена');
        this.assert(subtaskResult.removedSubtask.id === '1.1', 'ID удалённой подзадачи должен совпадать');

        // Удаляем основную задачу
        const taskResult = await this.tool.execute({
            action: 'remove',
            data: { id: '1' }
        });

        this.assert(taskResult.success, 'Задача должна быть удалена');
        this.assert(taskResult.removedTask.id === 1, 'ID удалённой задачи должен совпадать');

        // Проверяем, что осталась только одна задача
        const listResult = await this.tool.execute({
            action: 'list'
        });

        this.assert(listResult.tasks.length === 1, 'Должна остаться только одна задача');

        console.log('✅ Задачи успешно удалены');
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}`);
        }
    }
}

// Запуск тестов
async function runTests() {
    const tester = new TaskToolTester();
    const success = await tester.runAllTests();
    process.exit(success ? 0 : 1);
}

// Запускаем тесты если файл выполняется напрямую
if (require.main === module) {
    runTests().catch(console.error);
}

module.exports = { TaskToolTester };