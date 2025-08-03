/**
 * Слой обратной совместимости для унифицированных инструментов
 * 
 * Обеспечивает бесшовную миграцию с существующих инструментов на новые унифицированные.
 * Перенаправляет вызовы старых инструментов на соответствующие действия в новых.
 * 
 * Поддерживаемые инструменты:
 * - 8 инструментов управления задачами → task_manage
 * - 13 инструментов файловой системы → file_system  
 * - 22 браузерных инструмента → browser_control
 * 
 * Автор: GopiAI System
 * Версия: 1.0.0
 */

const { UnifiedTaskTool } = require('./tools/unified_task_tool.js');
const { UnifiedFileSystemTool } = require('./tools/unified_filesystem_tools.js');
const { UnifiedBrowserTool } = require('./tools/unified_browser_tools.js');

/**
 * Основной класс слоя обратной совместимости
 */
class CompatibilityLayer {
    constructor() {
        // Инициализируем унифицированные инструменты
        this.taskTool = new UnifiedTaskTool();
        this.fileSystemTool = new UnifiedFileSystemTool();
        this.browserTool = new UnifiedBrowserTool();
        
        // Статистика использования для мониторинга миграции
        this.usageStats = new Map();
        
        // Настройки совместимости
        this.config = {
            enableLogging: true,
            enableDeprecationWarnings: true,
            enableUsageStats: true
        };
    }

    // ==================== УПРАВЛЕНИЕ ЗАДАЧАМИ ====================

    /**
     * mcp_acf_tool_addTask → task_manage(action: "add")
     */
    async addTask(args) {
        this.logUsage('addTask', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'add',
            data: {
                title: args.title,
                description: args.description,
                priority: args.priority,
                dependsOn: args.dependsOn,
                relatedFiles: args.relatedFiles,
                tests: args.tests
            }
        });
    }

    /**
     * mcp_acf_tool_addSubtask → task_manage(action: "add_subtask")
     */
    async addSubtask(args) {
        this.logUsage('addSubtask', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'add_subtask',
            data: {
                parentId: args.parentId,
                title: args.title,
                relatedFiles: args.relatedFiles,
                tests: args.tests
            }
        });
    }

    /**
     * mcp_acf_tool_listTasks → task_manage(action: "list")
     */
    async listTasks(args) {
        this.logUsage('listTasks', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'list',
            data: {
                status: args.status,
                format: args.format || 'json'
            }
        });
    }

    /**
     * mcp_acf_tool_updateStatus → task_manage(action: "update_status")
     */
    async updateStatus(args) {
        this.logUsage('updateStatus', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'update_status',
            data: {
                id: args.id,
                newStatus: args.newStatus,
                message: args.message
            }
        });
    }

    /**
     * mcp_acf_tool_updateTask → task_manage(action: "update")
     */
    async updateTask(args) {
        this.logUsage('updateTask', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'update',
            data: {
                id: args.id,
                title: args.title,
                description: args.description,
                priority: args.priority,
                dependsOn: args.dependsOn,
                relatedFiles: args.relatedFiles,
                tests: args.tests
            }
        });
    }

    /**
     * mcp_acf_tool_removeTask → task_manage(action: "remove")
     */
    async removeTask(args) {
        this.logUsage('removeTask', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'remove',
            data: {
                id: args.id
            }
        });
    }

    /**
     * mcp_acf_tool_getContext → task_manage(action: "context")
     */
    async getContext(args) {
        this.logUsage('getContext', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'context',
            data: {
                id: args.id
            }
        });
    }

    /**
     * mcp_acf_tool_getNextTask → task_manage(action: "next")
     */
    async getNextTask(args) {
        this.logUsage('getNextTask', 'task_manage');
        
        return await this.taskTool.execute({
            action: 'next',
            data: {}
        });
    }

    // ==================== ФАЙЛОВАЯ СИСТЕМА ====================

    /**
     * mcp_acf_tool_read_file → file_system(action: "read")
     */
    async readFile(args) {
        this.logUsage('readFile', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'read',
            data: {
                path: args.path,
                isUrl: args.isUrl,
                timeout: args.timeout
            }
        });
    }

    /**
     * mcp_acf_tool_read_multiple_files → file_system(action: "read")
     */
    async readMultipleFiles(args) {
        this.logUsage('readMultipleFiles', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'read',
            data: {
                paths: args.paths
            }
        });
    }

    /**
     * mcp_acf_tool_write_file → file_system(action: "write")
     */
    async writeFile(args) {
        this.logUsage('writeFile', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'write',
            data: {
                path: args.path,
                content: args.content
            }
        });
    }

    /**
     * mcp_acf_tool_copy_file → file_system(action: "copy")
     */
    async copyFile(args) {
        this.logUsage('copyFile', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'copy',
            data: {
                source: args.source,
                destination: args.destination
            }
        });
    }

    /**
     * mcp_acf_tool_move_file → file_system(action: "move")
     */
    async moveFile(args) {
        this.logUsage('moveFile', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'move',
            data: {
                source: args.source,
                destination: args.destination
            }
        });
    }

    /**
     * mcp_acf_tool_delete_file → file_system(action: "delete")
     */
    async deleteFile(args) {
        this.logUsage('deleteFile', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'delete',
            data: {
                path: args.path,
                recursive: args.recursive
            }
        });
    }

    /**
     * mcp_acf_tool_list_directory → file_system(action: "list")
     */
    async listDirectory(args) {
        this.logUsage('listDirectory', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'list',
            data: {
                path: args.path,
                detailed: true
            }
        });
    }

    /**
     * mcp_acf_tool_create_directory → file_system(action: "create")
     */
    async createDirectory(args) {
        this.logUsage('createDirectory', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'create',
            data: {
                path: args.path
            }
        });
    }

    /**
     * mcp_acf_tool_tree → file_system(action: "tree")
     */
    async tree(args) {
        this.logUsage('tree', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'tree',
            data: {
                path: args.path,
                depth: args.depth,
                follow_symlinks: args.follow_symlinks
            }
        });
    }

    /**
     * mcp_acf_tool_search_files → file_system(action: "search")
     */
    async searchFiles(args) {
        this.logUsage('searchFiles', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'search',
            data: {
                path: args.path,
                pattern: args.pattern,
                maxResults: args.maxResults
            }
        });
    }

    /**
     * mcp_acf_tool_get_file_info → file_system(action: "info")
     */
    async getFileInfo(args) {
        this.logUsage('getFileInfo', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'info',
            data: {
                path: args.path
            }
        });
    }

    /**
     * mcp_acf_tool_get_filesystem_status → file_system(action: "status")
     */
    async getFilesystemStatus(args) {
        this.logUsage('getFilesystemStatus', 'file_system');
        
        return await this.fileSystemTool.execute({
            action: 'status',
            data: {}
        });
    }

    // ==================== БРАУЗЕРНАЯ АВТОМАТИЗАЦИЯ ====================

    /**
     * mcp_acf_tool_browser_navigate → browser_control(action: "navigate", operation: "navigate")
     */
    async browserNavigate(args) {
        this.logUsage('browserNavigate', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'navigate',
            operation: 'navigate',
            url: args.url
        });
    }

    /**
     * mcp_acf_tool_browser_navigate_back → browser_control(action: "navigate", operation: "back")
     */
    async browserNavigateBack(args) {
        this.logUsage('browserNavigateBack', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'navigate',
            operation: 'back'
        });
    }

    /**
     * mcp_acf_tool_browser_navigate_forward → browser_control(action: "navigate", operation: "forward")
     */
    async browserNavigateForward(args) {
        this.logUsage('browserNavigateForward', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'navigate',
            operation: 'forward'
        });
    }

    /**
     * mcp_acf_tool_browser_click → browser_control(action: "interact", operation: "click")
     */
    async browserClick(args) {
        this.logUsage('browserClick', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'click',
            element: args.element,
            ref: args.ref
        });
    }

    /**
     * mcp_acf_tool_browser_type → browser_control(action: "interact", operation: "type")
     */
    async browserType(args) {
        this.logUsage('browserType', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'type',
            element: args.element,
            ref: args.ref,
            text: args.text,
            options: {
                slowly: args.slowly,
                submit: args.submit
            }
        });
    }

    /**
     * mcp_acf_tool_browser_hover → browser_control(action: "interact", operation: "hover")
     */
    async browserHover(args) {
        this.logUsage('browserHover', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'hover',
            element: args.element,
            ref: args.ref
        });
    }

    /**
     * mcp_acf_tool_browser_drag → browser_control(action: "interact", operation: "drag")
     */
    async browserDrag(args) {
        this.logUsage('browserDrag', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'drag',
            startElement: args.startElement,
            startRef: args.startRef,
            endElement: args.endElement,
            endRef: args.endRef
        });
    }

    /**
     * mcp_acf_tool_browser_select_option → browser_control(action: "interact", operation: "select")
     */
    async browserSelectOption(args) {
        this.logUsage('browserSelectOption', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'select',
            element: args.element,
            ref: args.ref,
            values: args.values
        });
    }

    /**
     * mcp_acf_tool_browser_press_key → browser_control(action: "interact", operation: "key")
     */
    async browserPressKey(args) {
        this.logUsage('browserPressKey', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'interact',
            operation: 'key',
            key: args.key
        });
    }

    /**
     * mcp_acf_tool_browser_take_screenshot → browser_control(action: "capture", operation: "screenshot")
     */
    async browserTakeScreenshot(args) {
        this.logUsage('browserTakeScreenshot', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'capture',
            operation: 'screenshot',
            filename: args.filename,
            element: args.element,
            ref: args.ref,
            raw: args.raw
        });
    }

    /**
     * mcp_acf_tool_browser_snapshot → browser_control(action: "capture", operation: "snapshot")
     */
    async browserSnapshot(args) {
        this.logUsage('browserSnapshot', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'capture',
            operation: 'snapshot'
        });
    }

    /**
     * mcp_acf_tool_browser_pdf_save → browser_control(action: "capture", operation: "pdf")
     */
    async browserPdfSave(args) {
        this.logUsage('browserPdfSave', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'capture',
            operation: 'pdf',
            filename: args.filename
        });
    }

    /**
     * mcp_acf_tool_browser_console_messages → browser_control(action: "capture", operation: "console")
     */
    async browserConsoleMessages(args) {
        this.logUsage('browserConsoleMessages', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'capture',
            operation: 'console'
        });
    }

    /**
     * mcp_acf_tool_browser_file_upload → browser_control(action: "upload")
     */
    async browserFileUpload(args) {
        this.logUsage('browserFileUpload', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'upload',
            paths: args.paths
        });
    }

    /**
     * mcp_acf_tool_browser_wait → browser_control(action: "wait", operation: "time")
     */
    async browserWait(args) {
        this.logUsage('browserWait', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'wait',
            operation: 'time',
            time: args.time
        });
    }

    /**
     * mcp_acf_tool_browser_wait_for → browser_control(action: "wait")
     */
    async browserWaitFor(args) {
        this.logUsage('browserWaitFor', 'browser_control');
        
        let operation, params = {};
        
        if (args.text) {
            operation = 'text';
            params.text = args.text;
        } else if (args.textGone) {
            operation = 'text_gone';
            params.textGone = args.textGone;
        } else if (args.time) {
            operation = 'time';
            params.time = args.time;
        } else {
            operation = 'element';
            params.options = { selector: args.selector || '.default' };
        }
        
        return await this.browserTool.execute({
            action: 'wait',
            operation: operation,
            ...params
        });
    }

    /**
     * mcp_acf_tool_browser_resize → browser_control(action: "manage", operation: "resize")
     */
    async browserResize(args) {
        this.logUsage('browserResize', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'resize',
            width: args.width,
            height: args.height
        });
    }

    /**
     * mcp_acf_tool_browser_handle_dialog → browser_control(action: "manage", operation: "dialog")
     */
    async browserHandleDialog(args) {
        this.logUsage('browserHandleDialog', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'dialog',
            accept: args.accept,
            promptText: args.promptText
        });
    }

    /**
     * mcp_acf_tool_browser_close → browser_control(action: "manage", operation: "close")
     */
    async browserClose(args) {
        this.logUsage('browserClose', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'close'
        });
    }

    /**
     * mcp_acf_tool_browser_install → browser_control(action: "manage", operation: "install")
     */
    async browserInstall(args) {
        this.logUsage('browserInstall', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'install'
        });
    }

    /**
     * mcp_acf_tool_browser_tab_list → browser_control(action: "manage", operation: "tab_list")
     */
    async browserTabList(args) {
        this.logUsage('browserTabList', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'tab_list'
        });
    }

    /**
     * mcp_acf_tool_browser_tab_new → browser_control(action: "manage", operation: "tab_new")
     */
    async browserTabNew(args) {
        this.logUsage('browserTabNew', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'tab_new',
            url: args.url
        });
    }

    /**
     * mcp_acf_tool_browser_tab_select → browser_control(action: "manage", operation: "tab_select")
     */
    async browserTabSelect(args) {
        this.logUsage('browserTabSelect', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'tab_select',
            index: args.index
        });
    }

    /**
     * mcp_acf_tool_browser_tab_close → browser_control(action: "manage", operation: "tab_close")
     */
    async browserTabClose(args) {
        this.logUsage('browserTabClose', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'manage',
            operation: 'tab_close',
            index: args.index
        });
    }

    /**
     * mcp_acf_tool_browser_network_requests → browser_control(action: "capture", operation: "network")
     */
    async browserNetworkRequests(args) {
        this.logUsage('browserNetworkRequests', 'browser_control');
        
        return await this.browserTool.execute({
            action: 'capture',
            operation: 'network'
        });
    }

    // ==================== УТИЛИТЫ И МОНИТОРИНГ ====================

    /**
     * Логирование использования для мониторинга миграции
     */
    logUsage(oldTool, newTool) {
        if (!this.config.enableUsageStats) return;
        
        const key = `${oldTool} → ${newTool}`;
        const current = this.usageStats.get(key) || { count: 0, firstUsed: new Date(), lastUsed: new Date() };
        
        current.count++;
        current.lastUsed = new Date();
        
        this.usageStats.set(key, current);
        
        if (this.config.enableLogging) {
            console.log(`[CompatibilityLayer] ${oldTool} → ${newTool} (usage: ${current.count})`);
        }
        
        if (this.config.enableDeprecationWarnings && current.count === 1) {
            console.warn(`[DEPRECATION] ${oldTool} is deprecated. Please migrate to ${newTool}.`);
        }
    }

    /**
     * Получение статистики использования
     */
    getUsageStats() {
        const stats = {};
        
        for (const [mapping, data] of this.usageStats.entries()) {
            stats[mapping] = {
                count: data.count,
                firstUsed: data.firstUsed.toISOString(),
                lastUsed: data.lastUsed.toISOString(),
                daysSinceFirst: Math.floor((new Date() - data.firstUsed) / (1000 * 60 * 60 * 24))
            };
        }
        
        return {
            totalMappings: this.usageStats.size,
            totalUsages: Array.from(this.usageStats.values()).reduce((sum, data) => sum + data.count, 0),
            mappings: stats,
            generatedAt: new Date().toISOString()
        };
    }

    /**
     * Очистка статистики
     */
    clearUsageStats() {
        this.usageStats.clear();
    }

    /**
     * Настройка конфигурации
     */
    configure(options) {
        this.config = { ...this.config, ...options };
    }

    /**
     * Получение списка всех поддерживаемых старых инструментов
     */
    getSupportedLegacyTools() {
        return {
            taskManagement: [
                'addTask', 'addSubtask', 'listTasks', 'updateStatus', 
                'updateTask', 'removeTask', 'getContext', 'getNextTask'
            ],
            fileSystem: [
                'readFile', 'readMultipleFiles', 'writeFile', 'copyFile', 'moveFile', 
                'deleteFile', 'listDirectory', 'createDirectory', 'tree', 'searchFiles', 
                'getFileInfo', 'getFilesystemStatus'
            ],
            browserAutomation: [
                'browserNavigate', 'browserNavigateBack', 'browserNavigateForward',
                'browserClick', 'browserType', 'browserHover', 'browserDrag', 
                'browserSelectOption', 'browserPressKey', 'browserTakeScreenshot',
                'browserSnapshot', 'browserPdfSave', 'browserConsoleMessages',
                'browserFileUpload', 'browserWait', 'browserWaitFor', 'browserResize',
                'browserHandleDialog', 'browserClose', 'browserInstall', 'browserTabList',
                'browserTabNew', 'browserTabSelect', 'browserTabClose', 'browserNetworkRequests'
            ]
        };
    }
}

// Создание глобального экземпляра
const compatibilityLayer = new CompatibilityLayer();

// Экспорт
module.exports = {
    CompatibilityLayer,
    compatibilityLayer
};