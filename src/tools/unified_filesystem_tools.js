/**
 * Унифицированный инструмент файловой системы
 * 
 * Объединяет 13 отдельных инструментов в один с параметром action:
 * - read: чтение файлов (одного/нескольких)
 * - write: запись файлов
 * - copy: копирование
 * - move: перемещение
 * - delete: удаление
 * - list: список директорий
 * - create: создание директорий
 * - tree: дерево файлов
 * - search: поиск файлов
 * - info: информация о файлах
 * - status: статус системы
 * 
 * Автор: GopiAI System
 * Версия: 1.0.0
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

class UnifiedFileSystemTool {
    constructor() {
        this.allowedDirectories = ['.', './'];
        this.cache = new Map();
        this.cacheTimeout = 3000; // 3 секунды для файловых операций
    }

    /**
     * Основная точка входа для всех файловых операций
     * @param {Object} params - Параметры операции
     * @param {string} params.action - Действие (read, write, copy, move, delete, list, create, tree, search, info, status)
     * @param {Object} params.data - Данные для операции
     * @returns {Promise<Object>} Результат операции
     */
    async execute(params) {
        const { action, data = {} } = params;

        try {
            switch (action) {
                case 'read':
                    return await this.readFiles(data);
                case 'write':
                    return await this.writeFile(data);
                case 'copy':
                    return await this.copyFile(data);
                case 'move':
                    return await this.moveFile(data);
                case 'delete':
                    return await this.deleteFile(data);
                case 'list':
                    return await this.listDirectory(data);
                case 'create':
                    return await this.createDirectory(data);
                case 'tree':
                    return await this.getDirectoryTree(data);
                case 'search':
                    return await this.searchFiles(data);
                case 'info':
                    return await this.getFileInfo(data);
                case 'status':
                    return await this.getFileSystemStatus(data);
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
     * Чтение файлов (одного или нескольких)
     */
    async readFiles(data) {
        const { paths, path: singlePath, encoding = 'utf8' } = data;

        const filePaths = paths || (singlePath ? [singlePath] : []);

        if (filePaths.length === 0) {
            throw new Error('Не указаны пути к файлам');
        }

        const results = [];

        for (const filePath of filePaths) {
            try {
                const content = await fs.readFile(filePath, encoding);
                results.push({
                    path: filePath,
                    success: true,
                    content: content,
                    size: Buffer.byteLength(content, encoding)
                });
            } catch (error) {
                results.push({
                    path: filePath,
                    success: false,
                    error: error.message
                });
            }
        }

        return {
            success: true,
            action: 'read',
            files: results,
            totalFiles: results.length,
            successfulReads: results.filter(r => r.success).length
        };
    }

    /**
     * Запись файла
     */
    async writeFile(data) {
        const { path: filePath, content, encoding = 'utf8', createDirectories = true } = data;

        if (!filePath || content === undefined) {
            throw new Error('Путь к файлу и содержимое обязательны');
        }

        if (createDirectories) {
            const dir = path.dirname(filePath);
            await fs.mkdir(dir, { recursive: true });
        }

        await fs.writeFile(filePath, content, encoding);

        const stats = await fs.stat(filePath);

        return {
            success: true,
            action: 'write',
            path: filePath,
            size: stats.size,
            message: `Файл "${filePath}" успешно записан (${stats.size} байт)`
        };
    }

    /**
     * Копирование файла или директории
     */
    async copyFile(data) {
        const { source, destination, recursive = false } = data;

        if (!source || !destination) {
            throw new Error('Исходный путь и путь назначения обязательны');
        }

        const sourceStats = await fs.stat(source);

        if (sourceStats.isDirectory()) {
            if (!recursive) {
                throw new Error('Для копирования директории установите recursive: true');
            }
            await this.copyDirectory(source, destination);
        } else {
            // Создаём директорию назначения если не существует
            const destDir = path.dirname(destination);
            await fs.mkdir(destDir, { recursive: true });

            await fs.copyFile(source, destination);
        }

        return {
            success: true,
            action: 'copy',
            source: source,
            destination: destination,
            type: sourceStats.isDirectory() ? 'directory' : 'file',
            message: `${sourceStats.isDirectory() ? 'Директория' : 'Файл'} "${source}" скопирован в "${destination}"`
        };
    }

    /**
     * Перемещение/переименование файла или директории
     */
    async moveFile(data) {
        const { source, destination } = data;

        if (!source || !destination) {
            throw new Error('Исходный путь и путь назначения обязательны');
        }

        const sourceStats = await fs.stat(source);

        // Создаём директорию назначения если не существует
        const destDir = path.dirname(destination);
        await fs.mkdir(destDir, { recursive: true });

        await fs.rename(source, destination);

        return {
            success: true,
            action: 'move',
            source: source,
            destination: destination,
            type: sourceStats.isDirectory() ? 'directory' : 'file',
            message: `${sourceStats.isDirectory() ? 'Директория' : 'Файл'} "${source}" перемещён в "${destination}"`
        };
    }

    /**
     * Удаление файла или директории
     */
    async deleteFile(data) {
        const { path: targetPath, recursive = false } = data;

        if (!targetPath) {
            throw new Error('Путь для удаления обязателен');
        }

        const stats = await fs.stat(targetPath);

        if (stats.isDirectory()) {
            if (!recursive) {
                throw new Error('Для удаления директории установите recursive: true');
            }
            await fs.rmdir(targetPath, { recursive: true });
        } else {
            await fs.unlink(targetPath);
        }

        return {
            success: true,
            action: 'delete',
            path: targetPath,
            type: stats.isDirectory() ? 'directory' : 'file',
            message: `${stats.isDirectory() ? 'Директория' : 'Файл'} "${targetPath}" удалён`
        };
    }

    /**
     * Получение списка файлов в директории
     */
    async listDirectory(data) {
        const { path: dirPath = '.', detailed = true, recursive = false } = data;

        const items = [];

        if (recursive) {
            await this.listDirectoryRecursive(dirPath, items, detailed);
        } else {
            const entries = await fs.readdir(dirPath);

            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry);

                if (detailed) {
                    try {
                        const stats = await fs.stat(fullPath);
                        items.push({
                            name: entry,
                            path: fullPath,
                            type: stats.isDirectory() ? 'directory' : 'file',
                            size: stats.size,
                            modified: stats.mtime.toISOString(),
                            permissions: stats.mode.toString(8)
                        });
                    } catch (error) {
                        items.push({
                            name: entry,
                            path: fullPath,
                            type: 'unknown',
                            error: error.message
                        });
                    }
                } else {
                    items.push({
                        name: entry,
                        path: fullPath
                    });
                }
            }
        }

        return {
            success: true,
            action: 'list',
            directory: dirPath,
            items: items,
            totalItems: items.length,
            directories: items.filter(i => i.type === 'directory').length,
            files: items.filter(i => i.type === 'file').length
        };
    }

    /**
     * Создание директории
     */
    async createDirectory(data) {
        const { path: dirPath, recursive = true } = data;

        if (!dirPath) {
            throw new Error('Путь к директории обязателен');
        }

        await fs.mkdir(dirPath, { recursive });

        return {
            success: true,
            action: 'create',
            path: dirPath,
            message: `Директория "${dirPath}" создана`
        };
    }

    /**
     * Получение дерева директорий
     */
    async getDirectoryTree(data) {
        const { path: rootPath = '.', depth = 3, followSymlinks = false } = data;

        const tree = await this.buildDirectoryTree(rootPath, depth, followSymlinks);

        return {
            success: true,
            action: 'tree',
            rootPath: rootPath,
            tree: tree,
            maxDepth: depth
        };
    }

    /**
     * Поиск файлов по паттерну
     */
    async searchFiles(data) {
        const { path: searchPath = '.', pattern, caseSensitive = false, maxResults = 100 } = data;

        if (!pattern) {
            throw new Error('Паттерн поиска обязателен');
        }

        const results = [];
        // Преобразуем glob-паттерн в регулярное выражение
        const regexPattern = pattern
            .replace(/\./g, '\\.')  // Экранируем точки
            .replace(/\*/g, '.*')   // Заменяем * на .*
            .replace(/\?/g, '.');   // Заменяем ? на .
        const regex = new RegExp(`^${regexPattern}$`, caseSensitive ? '' : 'i');

        await this.searchFilesRecursive(searchPath, regex, results, maxResults);

        return {
            success: true,
            action: 'search',
            searchPath: searchPath,
            pattern: pattern,
            results: results,
            totalFound: results.length,
            limitReached: results.length >= maxResults
        };
    }

    /**
     * Получение информации о файле
     */
    async getFileInfo(data) {
        const { path: filePath } = data;

        if (!filePath) {
            throw new Error('Путь к файлу обязателен');
        }

        const stats = await fs.stat(filePath);
        const absolutePath = path.resolve(filePath);

        return {
            success: true,
            action: 'info',
            path: filePath,
            absolutePath: absolutePath,
            type: stats.isDirectory() ? 'directory' : 'file',
            size: stats.size,
            created: stats.birthtime.toISOString(),
            modified: stats.mtime.toISOString(),
            accessed: stats.atime.toISOString(),
            permissions: stats.mode.toString(8),
            isReadable: !!(stats.mode & parseInt('444', 8)),
            isWritable: !!(stats.mode & parseInt('222', 8)),
            isExecutable: !!(stats.mode & parseInt('111', 8))
        };
    }

    /**
     * Получение статуса файловой системы
     */
    async getFileSystemStatus(data) {
        const currentDir = process.cwd();

        try {
            // Получаем информацию о диске (только для Unix-систем)
            let diskInfo = null;
            try {
                const df = execSync('df -h .', { encoding: 'utf8' });
                const lines = df.split('\n');
                if (lines.length > 1) {
                    const parts = lines[1].split(/\s+/);
                    diskInfo = {
                        filesystem: parts[0],
                        size: parts[1],
                        used: parts[2],
                        available: parts[3],
                        usePercent: parts[4]
                    };
                }
            } catch (error) {
                // Игнорируем ошибки получения информации о диске
            }

            return {
                success: true,
                action: 'status',
                currentDirectory: currentDir,
                allowedDirectories: this.allowedDirectories,
                diskInfo: diskInfo,
                platform: process.platform,
                nodeVersion: process.version
            };
        } catch (error) {
            throw new Error(`Ошибка получения статуса: ${error.message}`);
        }
    }

    // Вспомогательные методы

    /**
     * Рекурсивное копирование директории
     */
    async copyDirectory(source, destination) {
        await fs.mkdir(destination, { recursive: true });

        const entries = await fs.readdir(source);

        for (const entry of entries) {
            const sourcePath = path.join(source, entry);
            const destPath = path.join(destination, entry);

            const stats = await fs.stat(sourcePath);

            if (stats.isDirectory()) {
                await this.copyDirectory(sourcePath, destPath);
            } else {
                await fs.copyFile(sourcePath, destPath);
            }
        }
    }

    /**
     * Рекурсивный список директорий
     */
    async listDirectoryRecursive(dirPath, items, detailed, currentDepth = 0, maxDepth = 10) {
        if (currentDepth >= maxDepth) return;

        const entries = await fs.readdir(dirPath);

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry);

            if (detailed) {
                try {
                    const stats = await fs.stat(fullPath);
                    items.push({
                        name: entry,
                        path: fullPath,
                        type: stats.isDirectory() ? 'directory' : 'file',
                        size: stats.size,
                        modified: stats.mtime.toISOString(),
                        depth: currentDepth
                    });

                    if (stats.isDirectory()) {
                        await this.listDirectoryRecursive(fullPath, items, detailed, currentDepth + 1, maxDepth);
                    }
                } catch (error) {
                    items.push({
                        name: entry,
                        path: fullPath,
                        type: 'unknown',
                        error: error.message,
                        depth: currentDepth
                    });
                }
            } else {
                items.push({
                    name: entry,
                    path: fullPath,
                    depth: currentDepth
                });
            }
        }
    }

    /**
     * Построение дерева директорий
     */
    async buildDirectoryTree(rootPath, maxDepth, followSymlinks, currentDepth = 0) {
        if (currentDepth >= maxDepth) return null;

        const stats = await fs.stat(rootPath);

        const node = {
            name: path.basename(rootPath),
            path: rootPath,
            type: stats.isDirectory() ? 'directory' : 'file',
            size: stats.size,
            modified: stats.mtime.toISOString()
        };

        if (stats.isDirectory()) {
            node.children = [];

            try {
                const entries = await fs.readdir(rootPath);

                for (const entry of entries) {
                    const childPath = path.join(rootPath, entry);
                    const childNode = await this.buildDirectoryTree(childPath, maxDepth, followSymlinks, currentDepth + 1);

                    if (childNode) {
                        node.children.push(childNode);
                    }
                }
            } catch (error) {
                node.error = error.message;
            }
        }

        return node;
    }

    /**
     * Рекурсивный поиск файлов
     */
    async searchFilesRecursive(searchPath, regex, results, maxResults, currentDepth = 0, maxDepth = 10) {
        if (results.length >= maxResults || currentDepth >= maxDepth) return;

        try {
            const entries = await fs.readdir(searchPath);

            for (const entry of entries) {
                if (results.length >= maxResults) break;

                const fullPath = path.join(searchPath, entry);

                if (regex.test(entry)) {
                    const stats = await fs.stat(fullPath);
                    results.push({
                        name: entry,
                        path: fullPath,
                        type: stats.isDirectory() ? 'directory' : 'file',
                        size: stats.size,
                        modified: stats.mtime.toISOString()
                    });
                }

                // Рекурсивный поиск в поддиректориях
                try {
                    const stats = await fs.stat(fullPath);
                    if (stats.isDirectory()) {
                        await this.searchFilesRecursive(fullPath, regex, results, maxResults, currentDepth + 1, maxDepth);
                    }
                } catch (error) {
                    // Игнорируем ошибки доступа к поддиректориям
                }
            }
        } catch (error) {
            // Игнорируем ошибки доступа к директории
        }
    }
}

// Экспорт для использования в MCP сервере
module.exports = {
    UnifiedFileSystemTool,

    // Схема инструмента для OpenAI Function Calling
    getToolSchema() {
        return {
            type: "function",
            function: {
                name: "file_system",
                description: "Унифицированный инструмент файловой системы с поддержкой всех операций",
                parameters: {
                    type: "object",
                    properties: {
                        action: {
                            type: "string",
                            description: "Действие для выполнения",
                            enum: [
                                "read",
                                "write",
                                "copy",
                                "move",
                                "delete",
                                "list",
                                "create",
                                "tree",
                                "search",
                                "info",
                                "status"
                            ]
                        },
                        data: {
                            type: "object",
                            description: "Данные для операции (зависят от действия)",
                            properties: {
                                // Для read
                                paths: {
                                    type: "array",
                                    items: { type: "string" },
                                    description: "Массив путей к файлам для чтения"
                                },
                                path: { type: "string", description: "Путь к файлу или директории" },
                                encoding: { type: "string", description: "Кодировка файла", default: "utf8" },

                                // Для write
                                content: { type: "string", description: "Содержимое для записи" },
                                createDirectories: { type: "boolean", description: "Создавать директории", default: true },

                                // Для copy, move
                                source: { type: "string", description: "Исходный путь" },
                                destination: { type: "string", description: "Путь назначения" },
                                recursive: { type: "boolean", description: "Рекурсивная операция", default: false },

                                // Для list
                                detailed: { type: "boolean", description: "Подробная информация", default: true },

                                // Для tree
                                depth: { type: "number", description: "Максимальная глубина", default: 3 },
                                followSymlinks: { type: "boolean", description: "Следовать символическим ссылкам", default: false },

                                // Для search
                                pattern: { type: "string", description: "Паттерн поиска" },
                                caseSensitive: { type: "boolean", description: "Учитывать регистр", default: false },
                                maxResults: { type: "number", description: "Максимум результатов", default: 100 }
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
                description: "Прочитать файл",
                arguments: {
                    action: "read",
                    data: {
                        path: "package.json"
                    }
                }
            },
            {
                description: "Записать файл",
                arguments: {
                    action: "write",
                    data: {
                        path: "output.txt",
                        content: "Hello, World!"
                    }
                }
            },
            {
                description: "Получить список файлов",
                arguments: {
                    action: "list",
                    data: {
                        path: "./src",
                        detailed: true
                    }
                }
            },
            {
                description: "Поиск файлов по паттерну",
                arguments: {
                    action: "search",
                    data: {
                        path: ".",
                        pattern: "*.js",
                        maxResults: 50
                    }
                }
            },
            {
                description: "Получить дерево директорий",
                arguments: {
                    action: "tree",
                    data: {
                        path: "./src",
                        depth: 2
                    }
                }
            }
        ];
    }
};
// Экспорт для использования в MCP сервере
module.exports = {
    UnifiedFileSystemTool,

    // Схема инструмента для OpenAI Function Calling
    getToolSchema() {
        return {
            type: "function",
            function: {
                name: "file_system",
                description: "Унифицированный инструмент файловой системы с поддержкой всех операций",
                parameters: {
                    type: "object",
                    properties: {
                        action: {
                            type: "string",
                            description: "Действие для выполнения",
                            enum: [
                                "read",
                                "write",
                                "copy",
                                "move",
                                "delete",
                                "list",
                                "create",
                                "tree",
                                "search",
                                "info",
                                "status"
                            ]
                        },
                        data: {
                            type: "object",
                            description: "Данные для операции (зависят от действия)",
                            properties: {
                                // Для read
                                paths: {
                                    type: "array",
                                    items: { type: "string" },
                                    description: "Массив путей к файлам для чтения"
                                },
                                path: { type: "string", description: "Путь к файлу или директории" },
                                encoding: { type: "string", description: "Кодировка файла", default: "utf8" },

                                // Для write
                                content: { type: "string", description: "Содержимое для записи" },
                                createDirectories: { type: "boolean", description: "Создавать директории", default: true },

                                // Для copy, move
                                source: { type: "string", description: "Исходный путь" },
                                destination: { type: "string", description: "Путь назначения" },
                                recursive: { type: "boolean", description: "Рекурсивная операция", default: false },

                                // Для list
                                detailed: { type: "boolean", description: "Подробная информация", default: true },

                                // Для tree
                                depth: { type: "number", description: "Максимальная глубина", default: 3 },
                                followSymlinks: { type: "boolean", description: "Следовать символическим ссылкам", default: false },

                                // Для search
                                pattern: { type: "string", description: "Паттерн поиска" },
                                caseSensitive: { type: "boolean", description: "Учитывать регистр", default: false },
                                maxResults: { type: "number", description: "Максимум результатов", default: 100 }
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
                description: "Прочитать файл",
                arguments: {
                    action: "read",
                    data: {
                        path: "package.json"
                    }
                }
            },
            {
                description: "Записать файл",
                arguments: {
                    action: "write",
                    data: {
                        path: "output.txt",
                        content: "Hello, World!"
                    }
                }
            },
            {
                description: "Получить список файлов",
                arguments: {
                    action: "list",
                    data: {
                        path: "./src",
                        detailed: true
                    }
                }
            },
            {
                description: "Поиск файлов по паттерну",
                arguments: {
                    action: "search",
                    data: {
                        path: ".",
                        pattern: "*.js",
                        maxResults: 50
                    }
                }
            },
            {
                description: "Получить дерево директорий",
                arguments: {
                    action: "tree",
                    data: {
                        path: "./src",
                        depth: 2
                    }
                }
            }
        ];
    }
};