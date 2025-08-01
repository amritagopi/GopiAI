/**
 * Унифицированный инструмент браузерной автоматизации
 * 
 * Объединяет 22 отдельных браузерных инструмента в 6 action-based инструментов:
 * - navigate: навигация и управление страницами
 * - interact: взаимодействие с элементами
 * - capture: захват контента (скриншоты, PDF, консоль)
 * - upload: загрузка файлов
 * - wait: ожидание и синхронизация
 * - manage: управление браузером и вкладками
 */

const fs = require('fs');
const path = require('path');

// Кэш для оптимизации производительности
const browserCache = new Map();
const CACHE_TTL = 30000; // 30 секунд

/**
 * Основной класс унифицированного браузерного инструмента
 */
class UnifiedBrowserTool {
    constructor() {
        this.name = 'browser_control';
        this.description = 'Унифицированный инструмент браузерной автоматизации с action-based архитектурой';
        this.cache = browserCache;
    }

    /**
     * Выполнение действия браузерной автоматизации
     */
    async execute(params) {
        const { action, ...actionParams } = params;
        
        try {
            // Валидация параметров
            this.validateParams(action, actionParams);
            
            // Выполнение действия
            switch (action) {
                case 'navigate':
                    return await this.handleNavigate(actionParams);
                case 'interact':
                    return await this.handleInteract(actionParams);
                case 'capture':
                    return await this.handleCapture(actionParams);
                case 'upload':
                    return await this.handleUpload(actionParams);
                case 'wait':
                    return await this.handleWait(actionParams);
                case 'manage':
                    return await this.handleManage(actionParams);
                default:
                    throw new Error(`Неизвестное действие: ${action}`);
            }
        } catch (error) {
            return {
                success: false,
                error: error.message,
                action: action,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Валидация параметров
     */
    validateParams(action, params) {
        const requiredParams = {
            navigate: ['operation'],
            interact: ['operation'],
            capture: ['operation'],
            upload: ['paths'],
            wait: ['operation'],
            manage: ['operation']
        };

        if (!requiredParams[action]) {
            throw new Error(`Неподдерживаемое действие: ${action}`);
        }

        for (const param of requiredParams[action]) {
            if (!(param in params)) {
                throw new Error(`Отсутствует обязательный параметр: ${param}`);
            }
        }
    }

    /**
     * Обработка навигационных действий
     * Объединяет: navigate, navigate_back, navigate_forward
     */
    async handleNavigate(params) {
        const { operation, url, options = {} } = params;
        
        const cacheKey = `navigate_${operation}_${url || 'current'}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        let result;
        
        switch (operation) {
            case 'navigate':
                if (!url) throw new Error('URL обязателен для навигации');
                result = await this.navigateToUrl(url, options);
                break;
                
            case 'back':
                result = await this.navigateBack(options);
                break;
                
            case 'forward':
                result = await this.navigateForward(options);
                break;
                
            case 'refresh':
                result = await this.refreshPage(options);
                break;
                
            default:
                throw new Error(`Неизвестная навигационная операция: ${operation}`);
        }

        this.setCache(cacheKey, result);
        return result;
    }

    /**
     * Обработка интерактивных действий
     * Объединяет: click, type, hover, drag, select_option, press_key
     */
    async handleInteract(params) {
        const { operation, element, ref, text, values, key, startElement, endElement, options = {} } = params;
        
        let result;
        
        switch (operation) {
            case 'click':
                if (!element || !ref) throw new Error('element и ref обязательны для клика');
                result = await this.clickElement(element, ref, options);
                break;
                
            case 'type':
                if (!element || !ref || !text) throw new Error('element, ref и text обязательны для ввода');
                result = await this.typeText(element, ref, text, options);
                break;
                
            case 'hover':
                if (!element || !ref) throw new Error('element и ref обязательны для наведения');
                result = await this.hoverElement(element, ref, options);
                break;
                
            case 'drag':
                if (!startElement || !endElement) throw new Error('startElement и endElement обязательны для перетаскивания');
                result = await this.dragElement(startElement, endElement, options);
                break;
                
            case 'select':
                if (!element || !ref || !values) throw new Error('element, ref и values обязательны для выбора');
                result = await this.selectOption(element, ref, values, options);
                break;
                
            case 'key':
                if (!key) throw new Error('key обязателен для нажатия клавиши');
                result = await this.pressKey(key, options);
                break;
                
            default:
                throw new Error(`Неизвестная интерактивная операция: ${operation}`);
        }

        return result;
    }

    /**
     * Обработка захвата контента
     * Объединяет: take_screenshot, snapshot, pdf_save, console_messages
     */
    async handleCapture(params) {
        const { operation, filename, element, ref, raw = false, options = {} } = params;
        
        const cacheKey = `capture_${operation}_${filename || 'default'}`;
        
        let result;
        
        switch (operation) {
            case 'screenshot':
                result = await this.takeScreenshot(filename, element, ref, raw, options);
                break;
                
            case 'snapshot':
                result = await this.takeSnapshot(options);
                break;
                
            case 'pdf':
                result = await this.savePdf(filename, options);
                break;
                
            case 'console':
                result = await this.getConsoleMessages(options);
                break;
                
            case 'network':
                result = await this.getNetworkRequests(options);
                break;
                
            default:
                throw new Error(`Неизвестная операция захвата: ${operation}`);
        }

        return result;
    }

    /**
     * Обработка загрузки файлов
     */
    async handleUpload(params) {
        const { paths, options = {} } = params;
        
        if (!Array.isArray(paths) || paths.length === 0) {
            throw new Error('paths должен быть непустым массивом');
        }

        // Проверка существования файлов
        for (const filePath of paths) {
            if (!fs.existsSync(filePath)) {
                throw new Error(`Файл не найден: ${filePath}`);
            }
        }

        return await this.uploadFiles(paths, options);
    }

    /**
     * Обработка ожидания
     * Объединяет: wait, wait_for
     */
    async handleWait(params) {
        const { operation, time, text, textGone, options = {} } = params;
        
        let result;
        
        switch (operation) {
            case 'time':
                if (!time || time > 10) throw new Error('time должно быть от 1 до 10 секунд');
                result = await this.waitTime(time);
                break;
                
            case 'text':
                if (!text) throw new Error('text обязателен для ожидания текста');
                result = await this.waitForText(text, options);
                break;
                
            case 'text_gone':
                if (!textGone) throw new Error('textGone обязателен для ожидания исчезновения текста');
                result = await this.waitForTextGone(textGone, options);
                break;
                
            case 'element':
                if (!options.selector) throw new Error('selector обязателен для ожидания элемента');
                result = await this.waitForElement(options.selector, options);
                break;
                
            default:
                throw new Error(`Неизвестная операция ожидания: ${operation}`);
        }

        return result;
    }

    /**
     * Обработка управления браузером
     * Объединяет: resize, handle_dialog, close, install, tab_*, network_requests
     */
    async handleManage(params) {
        const { operation, width, height, accept, promptText, index, url, options = {} } = params;
        
        let result;
        
        switch (operation) {
            case 'resize':
                if (!width || !height) throw new Error('width и height обязательны для изменения размера');
                result = await this.resizeBrowser(width, height, options);
                break;
                
            case 'dialog':
                if (accept === undefined) throw new Error('accept обязателен для обработки диалога');
                result = await this.handleDialog(accept, promptText, options);
                break;
                
            case 'close':
                result = await this.closeBrowser(options);
                break;
                
            case 'install':
                result = await this.installBrowser(options);
                break;
                
            case 'tab_list':
                result = await this.listTabs(options);
                break;
                
            case 'tab_new':
                result = await this.newTab(url, options);
                break;
                
            case 'tab_select':
                if (index === undefined) throw new Error('index обязателен для выбора вкладки');
                result = await this.selectTab(index, options);
                break;
                
            case 'tab_close':
                result = await this.closeTab(index, options);
                break;
                
            default:
                throw new Error(`Неизвестная операция управления: ${operation}`);
        }

        return result;
    }

    // ==================== РЕАЛИЗАЦИЯ МЕТОДОВ ====================

    /**
     * Навигация к URL
     */
    async navigateToUrl(url, options) {
        // Заглушка для демонстрации - в реальной реализации здесь будет вызов браузерного API
        return {
            success: true,
            action: 'navigate',
            url: url,
            title: `Navigated to ${url}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Навигация назад
     */
    async navigateBack(options) {
        return {
            success: true,
            action: 'navigate_back',
            message: 'Navigated back',
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Навигация вперёд
     */
    async navigateForward(options) {
        return {
            success: true,
            action: 'navigate_forward',
            message: 'Navigated forward',
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Обновление страницы
     */
    async refreshPage(options) {
        return {
            success: true,
            action: 'refresh',
            message: 'Page refreshed',
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Клик по элементу
     */
    async clickElement(element, ref, options) {
        return {
            success: true,
            action: 'click',
            element: element,
            ref: ref,
            message: `Clicked on ${element}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Ввод текста
     */
    async typeText(element, ref, text, options) {
        return {
            success: true,
            action: 'type',
            element: element,
            ref: ref,
            text: text,
            message: `Typed "${text}" into ${element}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Наведение на элемент
     */
    async hoverElement(element, ref, options) {
        return {
            success: true,
            action: 'hover',
            element: element,
            ref: ref,
            message: `Hovered over ${element}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Перетаскивание элемента
     */
    async dragElement(startElement, endElement, options) {
        return {
            success: true,
            action: 'drag',
            startElement: startElement,
            endElement: endElement,
            message: `Dragged from ${startElement} to ${endElement}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Выбор опции
     */
    async selectOption(element, ref, values, options) {
        return {
            success: true,
            action: 'select',
            element: element,
            ref: ref,
            values: values,
            message: `Selected ${values.join(', ')} in ${element}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Нажатие клавиши
     */
    async pressKey(key, options) {
        return {
            success: true,
            action: 'press_key',
            key: key,
            message: `Pressed key: ${key}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Создание скриншота
     */
    async takeScreenshot(filename, element, ref, raw, options) {
        const screenshotPath = filename || `screenshot_${Date.now()}.${raw ? 'png' : 'jpg'}`;
        
        return {
            success: true,
            action: 'screenshot',
            filename: screenshotPath,
            element: element,
            ref: ref,
            raw: raw,
            message: `Screenshot saved as ${screenshotPath}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Создание снимка доступности
     */
    async takeSnapshot(options) {
        return {
            success: true,
            action: 'snapshot',
            message: 'Accessibility snapshot captured',
            snapshot: {
                // Заглушка для структуры снимка доступности
                elements: [],
                tree: {},
                timestamp: new Date().toISOString()
            },
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Сохранение PDF
     */
    async savePdf(filename, options) {
        const pdfPath = filename || `page_${Date.now()}.pdf`;
        
        return {
            success: true,
            action: 'pdf_save',
            filename: pdfPath,
            message: `PDF saved as ${pdfPath}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Получение сообщений консоли
     */
    async getConsoleMessages(options) {
        return {
            success: true,
            action: 'console_messages',
            messages: [
                // Заглушка для сообщений консоли
                { level: 'info', text: 'Page loaded', timestamp: new Date().toISOString() },
                { level: 'warning', text: 'Deprecated API used', timestamp: new Date().toISOString() }
            ],
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Получение сетевых запросов
     */
    async getNetworkRequests(options) {
        return {
            success: true,
            action: 'network_requests',
            requests: [
                // Заглушка для сетевых запросов
                { url: 'https://example.com/api/data', method: 'GET', status: 200, timestamp: new Date().toISOString() }
            ],
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Загрузка файлов
     */
    async uploadFiles(paths, options) {
        return {
            success: true,
            action: 'file_upload',
            paths: paths,
            message: `Uploaded ${paths.length} file(s)`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Ожидание времени
     */
    async waitTime(seconds) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    success: true,
                    action: 'wait_time',
                    seconds: seconds,
                    message: `Waited for ${seconds} seconds`,
                    timestamp: new Date().toISOString()
                });
            }, seconds * 1000);
        });
    }

    /**
     * Ожидание появления текста
     */
    async waitForText(text, options) {
        return {
            success: true,
            action: 'wait_for_text',
            text: text,
            message: `Waited for text: "${text}"`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Ожидание исчезновения текста
     */
    async waitForTextGone(text, options) {
        return {
            success: true,
            action: 'wait_for_text_gone',
            text: text,
            message: `Waited for text to disappear: "${text}"`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Ожидание элемента
     */
    async waitForElement(selector, options) {
        return {
            success: true,
            action: 'wait_for_element',
            selector: selector,
            message: `Waited for element: ${selector}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Изменение размера браузера
     */
    async resizeBrowser(width, height, options) {
        return {
            success: true,
            action: 'resize',
            width: width,
            height: height,
            message: `Browser resized to ${width}x${height}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Обработка диалога
     */
    async handleDialog(accept, promptText, options) {
        return {
            success: true,
            action: 'handle_dialog',
            accept: accept,
            promptText: promptText,
            message: `Dialog ${accept ? 'accepted' : 'dismissed'}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Закрытие браузера
     */
    async closeBrowser(options) {
        return {
            success: true,
            action: 'close',
            message: 'Browser closed',
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Установка браузера
     */
    async installBrowser(options) {
        return {
            success: true,
            action: 'install',
            message: 'Browser installed',
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Список вкладок
     */
    async listTabs(options) {
        return {
            success: true,
            action: 'tab_list',
            tabs: [
                { index: 0, title: 'Tab 1', url: 'https://example.com', active: true },
                { index: 1, title: 'Tab 2', url: 'https://google.com', active: false }
            ],
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Новая вкладка
     */
    async newTab(url, options) {
        return {
            success: true,
            action: 'tab_new',
            url: url,
            message: `New tab created${url ? ` with URL: ${url}` : ''}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Выбор вкладки
     */
    async selectTab(index, options) {
        return {
            success: true,
            action: 'tab_select',
            index: index,
            message: `Selected tab ${index}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    /**
     * Закрытие вкладки
     */
    async closeTab(index, options) {
        return {
            success: true,
            action: 'tab_close',
            index: index,
            message: `Closed tab ${index || 'current'}`,
            timestamp: new Date().toISOString(),
            options: options
        };
    }

    // ==================== КЭШИРОВАНИЕ ====================

    /**
     * Получение из кэша
     */
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
            return cached.data;
        }
        return null;
    }

    /**
     * Сохранение в кэш
     */
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    /**
     * Очистка кэша
     */
    clearCache() {
        this.cache.clear();
    }

    // ==================== СХЕМА OPENAI FUNCTION CALLING ====================

    /**
     * Получение схемы для OpenAI Function Calling
     */
    getSchema() {
        return {
            type: "function",
            function: {
                name: "browser_control",
                description: "Унифицированный инструмент браузерной автоматизации с action-based архитектурой. Объединяет 22 браузерных инструмента в 6 групп действий.",
                parameters: {
                    type: "object",
                    properties: {
                        action: {
                            type: "string",
                            description: "Тип действия для выполнения",
                            enum: ["navigate", "interact", "capture", "upload", "wait", "manage"]
                        },
                        // Параметры для navigate
                        operation: {
                            type: "string",
                            description: "Конкретная операция в рамках действия"
                        },
                        url: {
                            type: "string",
                            description: "URL для навигации"
                        },
                        // Параметры для interact
                        element: {
                            type: "string",
                            description: "Человекочитаемое описание элемента"
                        },
                        ref: {
                            type: "string",
                            description: "Точная ссылка на элемент со страницы"
                        },
                        text: {
                            type: "string",
                            description: "Текст для ввода"
                        },
                        values: {
                            type: "array",
                            items: { type: "string" },
                            description: "Значения для выбора"
                        },
                        key: {
                            type: "string",
                            description: "Клавиша для нажатия"
                        },
                        startElement: {
                            type: "string",
                            description: "Начальный элемент для перетаскивания"
                        },
                        endElement: {
                            type: "string",
                            description: "Конечный элемент для перетаскивания"
                        },
                        // Параметры для capture
                        filename: {
                            type: "string",
                            description: "Имя файла для сохранения"
                        },
                        raw: {
                            type: "boolean",
                            description: "Формат PNG (true) или JPEG (false)",
                            default: false
                        },
                        // Параметры для upload
                        paths: {
                            type: "array",
                            items: { type: "string" },
                            description: "Пути к файлам для загрузки"
                        },
                        // Параметры для wait
                        time: {
                            type: "number",
                            description: "Время ожидания в секундах (максимум 10)",
                            maximum: 10
                        },
                        textGone: {
                            type: "string",
                            description: "Текст, исчезновения которого нужно ждать"
                        },
                        // Параметры для manage
                        width: {
                            type: "number",
                            description: "Ширина окна браузера"
                        },
                        height: {
                            type: "number",
                            description: "Высота окна браузера"
                        },
                        accept: {
                            type: "boolean",
                            description: "Принять диалог (true) или отклонить (false)"
                        },
                        promptText: {
                            type: "string",
                            description: "Текст для prompt диалогов"
                        },
                        index: {
                            type: "number",
                            description: "Индекс вкладки"
                        },
                        // Общие параметры
                        options: {
                            type: "object",
                            description: "Дополнительные опции для действия",
                            properties: {
                                timeout: { type: "number", description: "Таймаут операции в миллисекундах" },
                                selector: { type: "string", description: "CSS селектор для поиска элементов" },
                                slowly: { type: "boolean", description: "Медленный ввод текста" },
                                submit: { type: "boolean", description: "Отправить форму после ввода" }
                            }
                        }
                    },
                    required: ["action"]
                }
            }
        };
    }
}

// Создание экземпляра для использования
const unifiedBrowserTool = new UnifiedBrowserTool();

// Экспорт
module.exports = {
    UnifiedBrowserTool,
    unifiedBrowserTool,
    browserCache
};