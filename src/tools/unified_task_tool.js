/**
 * Унифицированный инструмент управления задачами
 * 
 * Объединяет 8 отдельных инструментов в один с параметром action:
 * - add: добавление задач/подзадач
 * - list: список задач
 * - update: обновление задач/статуса
 * - remove: удаление задач
 * - context: получение контекста
 * - next: следующая задача
 * 
 * Автор: GopiAI System
 * Версия: 1.0.0
 */

const fs = require('fs').promises;
const path = require('path');

class UnifiedTaskTool {
    constructor() {
        this.tasksFile = '.acf/tasks.json';
        this.cache = new Map();
        this.cacheTimeout = 5000; // 5 секунд
    }

    /**
     * Основная точка входа для всех операций с задачами
     * @param {Object} params - Параметры операции
     * @param {string} params.action - Действие (add, list, update, remove, context, next)
     * @param {Object} params.data - Данные для операции
     * @returns {Promise<Object>} Результат операции
     */
    async execute(params) {
        const { action, data = {} } = params;

        try {
            switch (action) {
                case 'add':
                    return await this.addTask(data);
                case 'add_subtask':
                    return await this.addSubtask(data);
                case 'list':
                    return await this.listTasks(data);
                case 'update':
                    return await this.updateTask(data);
                case 'update_status':
                    return await this.updateStatus(data);
                case 'remove':
                    return await this.removeTask(data);
                case 'context':
                    return await this.getContext(data);
                case 'next':
                    return await this.getNextTask(data);
                default:
                    throw new Error(`Неизвестное действие: ${action}`);
            }
        } catch (error) {
            return {
                success: false,
                error: error.message,
                action: action
            };
        }
    }

    /**
     * Добавление новой задачи
     */
    async addTask(data) {
        const { title, description, priority = 'medium', dependsOn = [], relatedFiles = [], tests = [] } = data;

        if (!title) {
            throw new Error('Название задачи обязательно');
        }

        const tasks = await this.loadTasks();
        const newId = this.generateId(tasks);
        
        const newTask = {
            id: newId,
            title,
            description: description || '',
            status: 'todo',
            priority: this.normalizePriority(priority),
            dependsOn: Array.isArray(dependsOn) ? dependsOn : [],
            relatedFiles: Array.isArray(relatedFiles) ? relatedFiles : [],
            tests: Array.isArray(tests) ? tests : [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            subtasks: [],
            lastSubtaskIndex: 0,
            activityLog: [{
                timestamp: new Date().toISOString(),
                type: 'log',
                message: `Задача создана: "${title}"`
            }]
        };

        tasks.push(newTask);
        await this.saveTasks(tasks);

        return {
            success: true,
            message: `Задача "${title}" создана с ID ${newId}`,
            taskId: newId,
            task: newTask
        };
    }

    /**
     * Добавление подзадачи
     */
    async addSubtask(data) {
        const { parentId, title, relatedFiles = [], tests = [] } = data;

        if (!parentId || !title) {
            throw new Error('ID родительской задачи и название подзадачи обязательны');
        }

        const tasks = await this.loadTasks();
        const parentTask = tasks.find(t => t.id === parseInt(parentId));

        if (!parentTask) {
            throw new Error(`Задача с ID ${parentId} не найдена`);
        }

        const subtaskId = `${parentId}.${parentTask.lastSubtaskIndex + 1}`;
        
        const newSubtask = {
            id: subtaskId,
            title,
            status: 'todo',
            relatedFiles: Array.isArray(relatedFiles) ? relatedFiles : [],
            tests: Array.isArray(tests) ? tests : [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            activityLog: [{
                timestamp: new Date().toISOString(),
                type: 'log',
                message: `Подзадача создана: "${title}"`
            }]
        };

        parentTask.subtasks.push(newSubtask);
        parentTask.lastSubtaskIndex++;
        parentTask.updatedAt = new Date().toISOString();

        await this.saveTasks(tasks);

        return {
            success: true,
            message: `Подзадача "${title}" создана с ID ${subtaskId}`,
            subtaskId: subtaskId,
            subtask: newSubtask
        };
    }

    /**
     * Получение списка задач
     */
    async listTasks(data) {
        const { status, format = 'json' } = data;
        const tasks = await this.loadTasks();

        let filteredTasks = tasks;
        if (status) {
            filteredTasks = tasks.filter(task => task.status === status);
        }

        if (format === 'human') {
            return {
                success: true,
                format: 'human',
                tasks: this.formatTasksForHuman(filteredTasks)
            };
        }

        return {
            success: true,
            tasks: filteredTasks,
            total: filteredTasks.length
        };
    }

    /**
     * Обновление задачи
     */
    async updateTask(data) {
        const { id, title, description, priority, dependsOn, relatedFiles, tests } = data;

        if (!id) {
            throw new Error('ID задачи обязателен');
        }

        const tasks = await this.loadTasks();
        const task = tasks.find(t => t.id === parseInt(id));

        if (!task) {
            throw new Error(`Задача с ID ${id} не найдена`);
        }

        // Обновляем поля
        if (title !== undefined) task.title = title;
        if (description !== undefined) task.description = description;
        if (priority !== undefined) task.priority = this.normalizePriority(priority);
        if (dependsOn !== undefined) task.dependsOn = Array.isArray(dependsOn) ? dependsOn : [];
        if (relatedFiles !== undefined) task.relatedFiles = Array.isArray(relatedFiles) ? relatedFiles : [];
        if (tests !== undefined) task.tests = Array.isArray(tests) ? tests : [];

        task.updatedAt = new Date().toISOString();
        task.activityLog.push({
            timestamp: new Date().toISOString(),
            type: 'log',
            message: 'Задача обновлена'
        });

        await this.saveTasks(tasks);

        return {
            success: true,
            message: `Задача ${id} обновлена`,
            task: task
        };
    }

    /**
     * Обновление статуса задачи
     */
    async updateStatus(data) {
        const { id, newStatus, message } = data;

        if (!id || !newStatus) {
            throw new Error('ID задачи и новый статус обязательны');
        }

        const validStatuses = ['todo', 'inprogress', 'testing', 'done', 'blocked', 'error'];
        if (!validStatuses.includes(newStatus)) {
            throw new Error(`Недопустимый статус: ${newStatus}`);
        }

        const tasks = await this.loadTasks();
        
        // Поиск задачи или подзадачи
        let targetTask = null;
        let isSubtask = false;

        if (id.includes('.')) {
            // Это подзадача
            const [parentId, subtaskIndex] = id.split('.');
            const parentTask = tasks.find(t => t.id === parseInt(parentId));
            if (parentTask) {
                targetTask = parentTask.subtasks.find(st => st.id === id);
                isSubtask = true;
            }
        } else {
            // Это основная задача
            targetTask = tasks.find(t => t.id === parseInt(id));
        }

        if (!targetTask) {
            throw new Error(`Задача с ID ${id} не найдена`);
        }

        const oldStatus = targetTask.status;
        targetTask.status = newStatus;
        targetTask.updatedAt = new Date().toISOString();

        const logMessage = message || `Статус изменён с "${oldStatus}" на "${newStatus}"`;
        targetTask.activityLog.push({
            timestamp: new Date().toISOString(),
            type: 'log',
            message: logMessage
        });

        await this.saveTasks(tasks);

        return {
            success: true,
            message: `Статус задачи ${id} изменён на "${newStatus}"`,
            oldStatus: oldStatus,
            newStatus: newStatus,
            task: targetTask
        };
    }

    /**
     * Удаление задачи
     */
    async removeTask(data) {
        const { id } = data;

        if (!id) {
            throw new Error('ID задачи обязателен');
        }

        const tasks = await this.loadTasks();

        if (id.includes('.')) {
            // Удаление подзадачи
            const [parentId, subtaskIndex] = id.split('.');
            const parentTask = tasks.find(t => t.id === parseInt(parentId));
            
            if (!parentTask) {
                throw new Error(`Родительская задача с ID ${parentId} не найдена`);
            }

            const subtaskIndex_num = parentTask.subtasks.findIndex(st => st.id === id);
            if (subtaskIndex_num === -1) {
                throw new Error(`Подзадача с ID ${id} не найдена`);
            }

            const removedSubtask = parentTask.subtasks.splice(subtaskIndex_num, 1)[0];
            parentTask.updatedAt = new Date().toISOString();

            await this.saveTasks(tasks);

            return {
                success: true,
                message: `Подзадача ${id} удалена`,
                removedSubtask: removedSubtask
            };
        } else {
            // Удаление основной задачи
            const taskIndex = tasks.findIndex(t => t.id === parseInt(id));
            
            if (taskIndex === -1) {
                throw new Error(`Задача с ID ${id} не найдена`);
            }

            const removedTask = tasks.splice(taskIndex, 1)[0];
            await this.saveTasks(tasks);

            return {
                success: true,
                message: `Задача ${id} удалена`,
                removedTask: removedTask
            };
        }
    }

    /**
     * Получение контекста задачи
     */
    async getContext(data) {
        const { id } = data;

        if (!id) {
            throw new Error('ID задачи обязателен');
        }

        const tasks = await this.loadTasks();
        let targetTask = null;

        if (id.includes('.')) {
            // Подзадача
            const [parentId, subtaskIndex] = id.split('.');
            const parentTask = tasks.find(t => t.id === parseInt(parentId));
            if (parentTask) {
                targetTask = parentTask.subtasks.find(st => st.id === id);
            }
        } else {
            // Основная задача
            targetTask = tasks.find(t => t.id === parseInt(id));
        }

        if (!targetTask) {
            throw new Error(`Задача с ID ${id} не найдена`);
        }

        return {
            success: true,
            task: targetTask,
            context: {
                id: targetTask.id,
                title: targetTask.title,
                description: targetTask.description,
                status: targetTask.status,
                relatedFiles: targetTask.relatedFiles || [],
                tests: targetTask.tests || [],
                activityLog: targetTask.activityLog || []
            }
        };
    }

    /**
     * Получение следующей задачи для выполнения
     */
    async getNextTask(data) {
        const tasks = await this.loadTasks();
        
        // Фильтруем задачи по статусу и зависимостям
        const availableTasks = tasks.filter(task => {
            if (task.status !== 'todo') return false;
            
            // Проверяем зависимости
            if (task.dependsOn && task.dependsOn.length > 0) {
                const dependenciesMet = task.dependsOn.every(depId => {
                    const depTask = tasks.find(t => t.id === depId);
                    return depTask && depTask.status === 'done';
                });
                if (!dependenciesMet) return false;
            }
            
            return true;
        });

        if (availableTasks.length === 0) {
            return {
                success: true,
                message: 'Нет доступных задач для выполнения',
                task: null
            };
        }

        // Сортируем по приоритету
        availableTasks.sort((a, b) => {
            const priorityA = typeof a.priority === 'number' ? a.priority : this.normalizePriority(a.priority);
            const priorityB = typeof b.priority === 'number' ? b.priority : this.normalizePriority(b.priority);
            return priorityB - priorityA;
        });

        const nextTask = availableTasks[0];

        return {
            success: true,
            message: `Следующая задача (ID: ${nextTask.id}): "${nextTask.title}"`,
            task: nextTask
        };
    }

    /**
     * Загрузка задач из файла с кэшированием
     */
    async loadTasks() {
        const cacheKey = 'tasks';
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const data = await fs.readFile(this.tasksFile, 'utf8');
            const tasks = JSON.parse(data);
            
            this.cache.set(cacheKey, {
                data: tasks,
                timestamp: Date.now()
            });
            
            return tasks;
        } catch (error) {
            if (error.code === 'ENOENT') {
                return [];
            }
            throw error;
        }
    }

    /**
     * Сохранение задач в файл
     */
    async saveTasks(tasks) {
        // Создаём директорию если не существует
        const dir = path.dirname(this.tasksFile);
        try {
            await fs.mkdir(dir, { recursive: true });
        } catch (error) {
            // Игнорируем ошибку если директория уже существует
        }

        await fs.writeFile(this.tasksFile, JSON.stringify(tasks, null, 2), 'utf8');
        
        // Обновляем кэш
        this.cache.set('tasks', {
            data: tasks,
            timestamp: Date.now()
        });
    }

    /**
     * Генерация нового ID для задачи
     */
    generateId(tasks) {
        if (tasks.length === 0) return 1;
        return Math.max(...tasks.map(t => t.id)) + 1;
    }

    /**
     * Нормализация приоритета
     */
    normalizePriority(priority) {
        if (typeof priority === 'number') return priority;
        
        const priorityMap = {
            'low': 300,
            'medium': 500,
            'high': 700,
            'critical': 900
        };
        
        return priorityMap[priority] || 500;
    }

    /**
     * Форматирование задач для человекочитаемого вывода
     */
    formatTasksForHuman(tasks) {
        let output = '';
        
        for (const task of tasks) {
            const statusIcon = this.getStatusIcon(task.status);
            const priorityLabel = this.getPriorityLabel(task.priority);
            
            output += `${statusIcon} #${task.id} [${priorityLabel}] ${task.title}\n`;
            
            if (task.description) {
                output += `   ${task.description}\n`;
            }
            
            if (task.subtasks && task.subtasks.length > 0) {
                for (const subtask of task.subtasks) {
                    const subStatusIcon = this.getStatusIcon(subtask.status);
                    output += `   ${subStatusIcon} #${subtask.id} ${subtask.title}\n`;
                }
            }
            
            output += '\n';
        }
        
        return output;
    }

    /**
     * Получение иконки статуса
     */
    getStatusIcon(status) {
        const icons = {
            'todo': '⬜',
            'inprogress': '🔄',
            'testing': '🧪',
            'done': '✅',
            'blocked': '🚫',
            'error': '❌'
        };
        return icons[status] || '❓';
    }

    /**
     * Получение метки приоритета
     */
    getPriorityLabel(priority) {
        if (typeof priority === 'number') {
            if (priority >= 900) return 'CRITICAL';
            if (priority >= 700) return 'HIGH';
            if (priority >= 500) return 'MEDIUM';
            return 'LOW';
        }
        return priority.toUpperCase();
    }
}

// Экспорт для использования в MCP сервере
module.exports = {
    UnifiedTaskTool,
    
    // Схема инструмента для OpenAI Function Calling
    getToolSchema() {
        return {
            type: "function",
            function: {
                name: "task_manage",
                description: "Унифицированный инструмент управления задачами с поддержкой всех операций",
                parameters: {
                    type: "object",
                    properties: {
                        action: {
                            type: "string",
                            description: "Действие для выполнения",
                            enum: [
                                "add",
                                "add_subtask", 
                                "list",
                                "update",
                                "update_status",
                                "remove",
                                "context",
                                "next"
                            ]
                        },
                        data: {
                            type: "object",
                            description: "Данные для операции (зависят от действия)",
                            properties: {
                                // Для add
                                title: { type: "string", description: "Название задачи" },
                                description: { type: "string", description: "Описание задачи" },
                                priority: { 
                                    oneOf: [
                                        { type: "string", enum: ["low", "medium", "high", "critical"] },
                                        { type: "number", minimum: 1, maximum: 1000 }
                                    ],
                                    description: "Приоритет задачи"
                                },
                                dependsOn: { 
                                    type: "array", 
                                    items: { type: "number" },
                                    description: "ID задач, от которых зависит эта задача"
                                },
                                relatedFiles: {
                                    type: "array",
                                    items: { type: "string" },
                                    description: "Связанные файлы"
                                },
                                tests: {
                                    type: "array", 
                                    items: { type: "string" },
                                    description: "Тесты для проверки выполнения"
                                },
                                
                                // Для add_subtask
                                parentId: { type: "string", description: "ID родительской задачи" },
                                
                                // Для list
                                status: { 
                                    type: "string", 
                                    enum: ["todo", "inprogress", "testing", "done", "blocked", "error"],
                                    description: "Фильтр по статусу"
                                },
                                format: {
                                    type: "string",
                                    enum: ["json", "human"],
                                    description: "Формат вывода"
                                },
                                
                                // Для update, update_status, remove, context
                                id: { type: "string", description: "ID задачи или подзадачи" },
                                newStatus: {
                                    type: "string",
                                    enum: ["todo", "inprogress", "testing", "done", "blocked", "error"],
                                    description: "Новый статус"
                                },
                                message: { type: "string", description: "Сообщение для лога" }
                            }
                        }
                    },
                    required: ["action"]
                }
            }
        };
    },

    // Примеры использования
    getUsageExamples() {
        return [
            {
                description: "Добавить новую задачу",
                arguments: {
                    action: "add",
                    data: {
                        title: "Реализовать новую функцию",
                        description: "Добавить поддержку экспорта данных",
                        priority: "high",
                        relatedFiles: ["src/export.js", "tests/export.test.js"]
                    }
                }
            },
            {
                description: "Получить список задач",
                arguments: {
                    action: "list",
                    data: {
                        status: "todo",
                        format: "human"
                    }
                }
            },
            {
                description: "Обновить статус задачи",
                arguments: {
                    action: "update_status",
                    data: {
                        id: "1",
                        newStatus: "inprogress",
                        message: "Начал работу над задачей"
                    }
                }
            },
            {
                description: "Получить следующую задачу",
                arguments: {
                    action: "next"
                }
            }
        ];
    }
};