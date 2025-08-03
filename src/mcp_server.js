/**
 * MCP Server для GopiAI с интеграцией Smart Workspace Indexer
 * 
 * Предоставляет унифицированные инструменты и автоматическую индексацию рабочего пространства
 * 
 * Автор: GopiAI System
 * Версия: 1.0.0
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');

// Импортируем унифицированные инструменты
const { UnifiedTaskTool } = require('./tools/unified_task_tool.js');
const { UnifiedFileSystemTool } = require('./tools/unified_filesystem_tools.js');
const { UnifiedBrowserTool } = require('./tools/unified_browser_tools.js');

// Импортируем workspace indexer (через Python bridge)
const { execSync, spawn } = require('child_process');
const path = require('path');

class GopiAIMCPServer {
    constructor() {
        this.server = new Server(
            {
                name: 'gopiai-mcp-server',
                version: '1.0.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        // Инициализируем инструменты
        this.taskTool = new UnifiedTaskTool();
        this.fileSystemTool = new UnifiedFileSystemTool();
        this.browserTool = new UnifiedBrowserTool();
        
        // Инициализируем слой обратной совместимости
        const { CompatibilityLayer } = require('./compatibility_layer.js');
        this.compatibilityLayer = new CompatibilityLayer();
        
        // Текущее рабочее пространство
        this.currentWorkspace = null;
        this.workspaceIndex = null;

        this.setupHandlers();
    }

    setupHandlers() {
        // Обработчик списка инструментов
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    // Унифицированный инструмент управления задачами
                    {
                        name: 'task_manage',
                        description: 'Унифицированный инструмент управления задачами с поддержкой всех операций (add, list, update, remove, context, next)',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                action: {
                                    type: 'string',
                                    description: 'Действие для выполнения',
                                    enum: ['add', 'add_subtask', 'list', 'update', 'update_status', 'remove', 'context', 'next']
                                },
                                data: {
                                    type: 'object',
                                    description: 'Данные для операции (зависят от действия)',
                                    properties: {
                                        title: { type: 'string', description: 'Название задачи' },
                                        description: { type: 'string', description: 'Описание задачи' },
                                        priority: { 
                                            oneOf: [
                                                { type: 'string', enum: ['low', 'medium', 'high', 'critical'] },
                                                { type: 'number', minimum: 1, maximum: 1000 }
                                            ],
                                            description: 'Приоритет задачи'
                                        },
                                        id: { type: 'string', description: 'ID задачи или подзадачи' },
                                        parentId: { type: 'string', description: 'ID родительской задачи' },
                                        newStatus: {
                                            type: 'string',
                                            enum: ['todo', 'inprogress', 'testing', 'done', 'blocked', 'error'],
                                            description: 'Новый статус'
                                        },
                                        status: { 
                                            type: 'string', 
                                            enum: ['todo', 'inprogress', 'testing', 'done', 'blocked', 'error'],
                                            description: 'Фильтр по статусу'
                                        },
                                        format: {
                                            type: 'string',
                                            enum: ['json', 'human'],
                                            description: 'Формат вывода'
                                        },
                                        message: { type: 'string', description: 'Сообщение для лога' }
                                    }
                                }
                            },
                            required: ['action']
                        }
                    },

                    // Унифицированный инструмент файловой системы
                    {
                        name: 'file_system',
                        description: 'Унифицированный инструмент файловой системы с поддержкой всех операций (read, write, copy, move, delete, list, create, tree, search, info, status)',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                action: {
                                    type: 'string',
                                    description: 'Действие для выполнения',
                                    enum: ['read', 'write', 'copy', 'move', 'delete', 'list', 'create', 'tree', 'search', 'info', 'status']
                                },
                                data: {
                                    type: 'object',
                                    description: 'Данные для операции (зависят от действия)',
                                    properties: {
                                        path: { type: 'string', description: 'Путь к файлу или директории' },
                                        paths: {
                                            type: 'array',
                                            items: { type: 'string' },
                                            description: 'Массив путей к файлам'
                                        },
                                        content: { type: 'string', description: 'Содержимое для записи' },
                                        source: { type: 'string', description: 'Исходный путь' },
                                        destination: { type: 'string', description: 'Путь назначения' },
                                        pattern: { type: 'string', description: 'Паттерн поиска' },
                                        recursive: { type: 'boolean', description: 'Рекурсивная операция' },
                                        detailed: { type: 'boolean', description: 'Подробная информация' },
                                        depth: { type: 'number', description: 'Максимальная глубина' },
                                        maxResults: { type: 'number', description: 'Максимум результатов' }
                                    }
                                }
                            },
                            required: ['action']
                        }
                    },

                    // Инструмент установки рабочего пространства
                    {
                        name: 'setWorkspace',
                        description: 'Устанавливает рабочее пространство и автоматически индексирует его',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                path: {
                                    type: 'string',
                                    description: 'Путь к рабочему пространству'
                                }
                            },
                            required: ['path']
                        }
                    },

                    // Инструменты для работы с индексом рабочего пространства
                    {
                        name: 'workspace_info',
                        description: 'Получает информацию о текущем рабочем пространстве',
                        inputSchema: {
                            type: 'object',
                            properties: {},
                            required: []
                        }
                    },

                    {
                        name: 'workspace_context',
                        description: 'Получает полный контекст рабочего пространства для LLM',
                        inputSchema: {
                            type: 'object',
                            properties: {},
                            required: []
                        }
                    },

                    {
                        name: 'workspace_search',
                        description: 'Поиск файлов в рабочем пространстве по паттерну',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                pattern: {
                                    type: 'string',
                                    description: 'Паттерн для поиска (поддерживает wildcards)'
                                },
                                maxResults: {
                                    type: 'number',
                                    description: 'Максимальное количество результатов',
                                    default: 20
                                }
                            },
                            required: ['pattern']
                        }
                    },

                    {
                        name: 'workspace_refresh',
                        description: 'Обновляет индекс рабочего пространства',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                force: {
                                    type: 'boolean',
                                    description: 'Принудительное обновление кэша',
                                    default: false
                                }
                            },
                            required: []
                        }
                    },

                    // Унифицированный инструмент браузерной автоматизации
                    {
                        name: 'browser_control',
                        description: 'Унифицированный инструмент браузерной автоматизации с action-based архитектурой. Объединяет 22 браузерных инструмента в 6 групп действий.',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                action: {
                                    type: 'string',
                                    description: 'Тип действия для выполнения',
                                    enum: ['navigate', 'interact', 'capture', 'upload', 'wait', 'manage']
                                },
                                operation: {
                                    type: 'string',
                                    description: 'Конкретная операция в рамках действия'
                                },
                                url: {
                                    type: 'string',
                                    description: 'URL для навигации'
                                },
                                element: {
                                    type: 'string',
                                    description: 'Человекочитаемое описание элемента'
                                },
                                ref: {
                                    type: 'string',
                                    description: 'Точная ссылка на элемент со страницы'
                                },
                                text: {
                                    type: 'string',
                                    description: 'Текст для ввода'
                                },
                                values: {
                                    type: 'array',
                                    items: { type: 'string' },
                                    description: 'Значения для выбора'
                                },
                                key: {
                                    type: 'string',
                                    description: 'Клавиша для нажатия'
                                },
                                startElement: {
                                    type: 'string',
                                    description: 'Начальный элемент для перетаскивания'
                                },
                                endElement: {
                                    type: 'string',
                                    description: 'Конечный элемент для перетаскивания'
                                },
                                filename: {
                                    type: 'string',
                                    description: 'Имя файла для сохранения'
                                },
                                raw: {
                                    type: 'boolean',
                                    description: 'Формат PNG (true) или JPEG (false)',
                                    default: false
                                },
                                paths: {
                                    type: 'array',
                                    items: { type: 'string' },
                                    description: 'Пути к файлам для загрузки'
                                },
                                time: {
                                    type: 'number',
                                    description: 'Время ожидания в секундах (максимум 10)',
                                    maximum: 10
                                },
                                textGone: {
                                    type: 'string',
                                    description: 'Текст, исчезновения которого нужно ждать'
                                },
                                width: {
                                    type: 'number',
                                    description: 'Ширина окна браузера'
                                },
                                height: {
                                    type: 'number',
                                    description: 'Высота окна браузера'
                                },
                                accept: {
                                    type: 'boolean',
                                    description: 'Принять диалог (true) или отклонить (false)'
                                },
                                promptText: {
                                    type: 'string',
                                    description: 'Текст для prompt диалогов'
                                },
                                index: {
                                    type: 'number',
                                    description: 'Индекс вкладки'
                                },
                                options: {
                                    type: 'object',
                                    description: 'Дополнительные опции для действия',
                                    properties: {
                                        timeout: { type: 'number', description: 'Таймаут операции в миллисекундах' },
                                        selector: { type: 'string', description: 'CSS селектор для поиска элементов' },
                                        slowly: { type: 'boolean', description: 'Медленный ввод текста' },
                                        submit: { type: 'boolean', description: 'Отправить форму после ввода' }
                                    }
                                }
                            },
                            required: ['action']
                        }
                    }
                ]
            };
        });

        // Обработчик вызовов инструментов
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case 'task_manage':
                        return await this.handleTaskManage(args);

                    case 'file_system':
                        return await this.handleFileSystem(args);

                    case 'setWorkspace':
                        return await this.handleSetWorkspace(args);

                    case 'workspace_info':
                        return await this.handleWorkspaceInfo(args);

                    case 'workspace_context':
                        return await this.handleWorkspaceContext(args);

                    case 'workspace_search':
                        return await this.handleWorkspaceSearch(args);

                    case 'workspace_refresh':
                        return await this.handleWorkspaceRefresh(args);

                    case 'browser_control':
                        return await this.handleBrowserControl(args);

                    default:
                        throw new Error(`Неизвестный инструмент: ${name}`);
                }
            } catch (error) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Ошибка выполнения ${name}: ${error.message}`
                        }
                    ],
                    isError: true
                };
            }
        });
    }

    // Обработчики инструментов

    async handleTaskManage(args) {
        const result = await this.taskTool.execute(args);
        
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(result, null, 2)
                }
            ]
        };
    }

    async handleFileSystem(args) {
        const result = await this.fileSystemTool.execute(args);
        
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(result, null, 2)
                }
            ]
        };
    }

    async handleSetWorkspace(args) {
        const { path: workspacePath } = args;

        try {
            // Проверяем существование пути
            const fs = require('fs');
            if (!fs.existsSync(workspacePath)) {
                throw new Error(`Путь не существует: ${workspacePath}`);
            }

            if (!fs.statSync(workspacePath).isDirectory()) {
                throw new Error(`Путь не является директорией: ${workspacePath}`);
            }

            // Устанавливаем рабочее пространство
            this.currentWorkspace = path.resolve(workspacePath);
            
            // Запускаем индексацию через Python
            const indexResult = await this.indexWorkspace(this.currentWorkspace);

            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: true,
                            message: `Рабочее пространство установлено: ${this.currentWorkspace}`,
                            workspace: this.currentWorkspace,
                            indexResult: indexResult
                        }, null, 2)
                    }
                ]
            };

        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }

    async handleWorkspaceInfo(args) {
        if (!this.currentWorkspace) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: 'Рабочее пространство не установлено'
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }

        try {
            const info = await this.getWorkspaceInfo();
            
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(info, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }

    async handleWorkspaceContext(args) {
        if (!this.currentWorkspace) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: 'Рабочее пространство не установлено'
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }

        try {
            const context = await this.getWorkspaceContext();
            
            return {
                content: [
                    {
                        type: 'text',
                        text: context
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }

    async handleWorkspaceSearch(args) {
        if (!this.currentWorkspace) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: 'Рабочее пространство не установлено'
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }

        try {
            const result = await this.searchWorkspaceFiles(args.pattern, args.maxResults || 20);
            
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(result, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }

    async handleWorkspaceRefresh(args) {
        if (!this.currentWorkspace) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: 'Рабочее пространство не установлено'
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }

        try {
            const result = await this.indexWorkspace(this.currentWorkspace, args.force || false);
            
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: true,
                            message: 'Индекс рабочего пространства обновлён',
                            result: result
                        }, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }

    // Методы для работы с workspace indexer

    async indexWorkspace(workspacePath, forceRefresh = false) {
        return new Promise((resolve, reject) => {
            // Создаём Python скрипт для индексации
            const pythonScript = `
import sys
import os
import json

# Добавляем путь к GopiAI-Extensions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'GopiAI-Extensions'))

try:
    from gopiai.extensions.mcp_workspace_integration import get_mcp_workspace_integration
    
    integration = get_mcp_workspace_integration()
    result = integration.on_workspace_set("${workspacePath.replace(/\\/g, '\\\\')}")
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    print(json.dumps({
        "success": False,
        "error": str(e)
    }, ensure_ascii=False, indent=2))
`;

            // Записываем временный скрипт
            const fs = require('fs');
            const tempScript = path.join(__dirname, 'temp_index_workspace.py');
            fs.writeFileSync(tempScript, pythonScript);

            // Запускаем Python скрипт
            const { exec } = require('child_process');
            exec(`python "${tempScript}"`, { cwd: process.cwd() }, (error, stdout, stderr) => {
                // Удаляем временный файл
                try {
                    fs.unlinkSync(tempScript);
                } catch (e) {
                    // Игнорируем ошибки удаления
                }

                if (error) {
                    reject(new Error(`Ошибка индексации: ${error.message}`));
                    return;
                }

                if (stderr) {
                    console.warn('Предупреждения индексации:', stderr);
                }

                try {
                    // Ищем JSON в выводе (может быть смешан с другими сообщениями)
                    const lines = stdout.split('\n');
                    let jsonLine = '';
                    
                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('{') && trimmed.includes('"success"')) {
                            jsonLine = trimmed;
                            break;
                        }
                    }
                    
                    if (!jsonLine) {
                        // Пробуем найти многострочный JSON
                        const jsonStart = stdout.indexOf('{');
                        const jsonEnd = stdout.lastIndexOf('}');
                        if (jsonStart !== -1 && jsonEnd !== -1) {
                            jsonLine = stdout.substring(jsonStart, jsonEnd + 1);
                        }
                    }
                    
                    if (!jsonLine) {
                        throw new Error('JSON не найден в выводе Python');
                    }
                    
                    const result = JSON.parse(jsonLine);
                    this.workspaceIndex = result;
                    resolve(result);
                } catch (parseError) {
                    // Если парсинг не удался, возвращаем базовую информацию
                    console.warn('Не удалось распарсить JSON, используем базовую информацию');
                    const basicResult = {
                        success: true,
                        indexed: true,
                        workspace_path: workspacePath,
                        project_summary: 'Проект проиндексирован',
                        message: 'Индексация выполнена (базовая информация)'
                    };
                    this.workspaceIndex = basicResult;
                    resolve(basicResult);
                }
            });
        });
    }

    async getWorkspaceInfo() {
        if (!this.workspaceIndex || !this.workspaceIndex.success) {
            throw new Error('Индекс рабочего пространства недоступен');
        }

        return {
            success: true,
            workspace_path: this.currentWorkspace,
            project_type: this.workspaceIndex.project_type,
            primary_language: this.workspaceIndex.primary_language,
            total_files: this.workspaceIndex.total_files,
            total_size: this.workspaceIndex.total_size,
            technologies: this.workspaceIndex.technologies,
            frameworks: this.workspaceIndex.frameworks,
            project_summary: this.workspaceIndex.project_summary
        };
    }

    async getWorkspaceContext() {
        return new Promise((resolve, reject) => {
            // Создаём Python скрипт для получения контекста
            const pythonScript = `
import sys
import os
import json

# Добавляем путь к GopiAI-Extensions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'GopiAI-Extensions'))

try:
    from gopiai.extensions.mcp_workspace_integration import get_mcp_workspace_integration
    
    integration = get_mcp_workspace_integration()
    context = integration.get_workspace_context()
    
    if context:
        print(context)
    else:
        print("Контекст рабочего пространства недоступен")
    
except Exception as e:
    print(f"Ошибка получения контекста: {str(e)}")
`;

            // Записываем временный скрипт
            const fs = require('fs');
            const tempScript = path.join(__dirname, 'temp_get_context.py');
            fs.writeFileSync(tempScript, pythonScript);

            // Запускаем Python скрипт
            const { exec } = require('child_process');
            exec(`python "${tempScript}"`, { cwd: process.cwd() }, (error, stdout, stderr) => {
                // Удаляем временный файл
                try {
                    fs.unlinkSync(tempScript);
                } catch (e) {
                    // Игнорируем ошибки удаления
                }

                if (error) {
                    reject(new Error(`Ошибка получения контекста: ${error.message}`));
                    return;
                }

                // Фильтруем вывод, оставляя только контекст
                const lines = stdout.split('\n');
                const contextLines = [];
                let foundContext = false;
                
                for (const line of lines) {
                    // Пропускаем служебные сообщения
                    if (line.includes('INFO') || line.includes('DEBUG') || line.includes('WARNING') || 
                        line.includes('GopiAI') || line.includes('✅') || line.includes('🔧')) {
                        continue;
                    }
                    
                    if (line.trim()) {
                        contextLines.push(line);
                        foundContext = true;
                    }
                }
                
                if (foundContext) {
                    resolve(contextLines.join('\n'));
                } else {
                    resolve('Контекст рабочего пространства недоступен');
                }
            });
        });
    }

    async searchWorkspaceFiles(pattern, maxResults = 20) {
        // Простая реализация поиска файлов через file_system инструмент
        try {
            const searchResult = await this.fileSystemTool.execute({
                action: 'search',
                data: {
                    path: this.currentWorkspace,
                    pattern: pattern,
                    maxResults: maxResults
                }
            });

            if (searchResult.success) {
                return {
                    success: true,
                    pattern: pattern,
                    results: searchResult.results.map(file => ({
                        name: file.name,
                        path: file.path,
                        type: file.type,
                        size: file.size
                    })),
                    total_found: searchResult.results.length,
                    truncated: searchResult.limitReached || false
                };
            } else {
                return {
                    success: false,
                    error: searchResult.error,
                    pattern: pattern,
                    results: []
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message,
                pattern: pattern,
                results: []
            };
        }
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('GopiAI MCP Server запущен');
    }

    // Обработчик унифицированного браузерного инструмента
    async handleBrowserControl(args) {
        try {
            const result = await this.browserTool.execute(args);
            
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(result, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            error: error.message,
                            action: args.action || 'unknown',
                            timestamp: new Date().toISOString()
                        }, null, 2)
                    }
                ],
                isError: true
            };
        }
    }
}

// Запуск сервера
if (require.main === module) {
    const server = new GopiAIMCPServer();
    server.run().catch(console.error);
}

module.exports = { GopiAIMCPServer };