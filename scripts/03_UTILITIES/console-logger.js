/**
 * JavaScript Console Logging System for WebView Debugging
 * ========================================================
 * 
 * Этот код перехватывает все консольные вызовы (log, warn, error, etc.)
 * и передает их в Python через QWebChannel bridge для отладки WebView.
 */

// Глобальная переменная для хранения logging bridge
window.consoleLogger = null;

// Функция для установки console logging bridge
function setupConsoleLogging(bridge) {
    if (!bridge) {
        console.warn('⚠️ Bridge not available for console logging setup');
        return;
    }
    
    window.consoleLogger = bridge;
    console.log('🔧 Console logging bridge established');
    
    // Сохраняем оригинальные методы консоли
    const originalConsole = {
        log: console.log,
        info: console.info,
        warn: console.warn,
        error: console.error,
        debug: console.debug
    };
    
    // Функция для безопасной передачи сообщений в Python
    function safeLogToPython(level, message, source = '') {
        try {
            if (window.consoleLogger && typeof window.consoleLogger[`log_js_${level}`] === 'function') {
                window.consoleLogger[`log_js_${level}`](String(message));
            }
        } catch (e) {
            // Используем оригинальный console.error для сообщения об ошибке логирования
            originalConsole.error('Console logging error:', e);
        }
    }
    
    // Переопределяем console.log
    console.log = function(...args) {
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        originalConsole.log(...args); // Сохраняем оригинальное поведение
        safeLogToPython('log', message);
    };
    
    // Переопределяем console.info
    console.info = function(...args) {
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        originalConsole.info(...args);
        safeLogToPython('info', message);
    };
    
    // Переопределяем console.warn
    console.warn = function(...args) {
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        originalConsole.warn(...args);
        safeLogToPython('warn', message);
    };
    
    // Переопределяем console.error
    console.error = function(...args) {
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        originalConsole.error(...args);
        safeLogToPython('error', message);
    };
    
    // Переопределяем console.debug
    console.debug = function(...args) {
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');
        
        originalConsole.debug(...args);
        safeLogToPython('debug', message);
    };
    
    // Перехват необработанных ошибок JavaScript
    window.addEventListener('error', function(event) {
        const errorMessage = `${event.message} at ${event.filename}:${event.lineno}:${event.colno}`;
        const stackTrace = event.error ? event.error.stack : '';
        
        if (window.consoleLogger && typeof window.consoleLogger.log_js_exception === 'function') {
            try {
                window.consoleLogger.log_js_exception(errorMessage, stackTrace);
            } catch (e) {
                originalConsole.error('Exception logging error:', e);
            }
        }
    });
    
    // Перехват необработанных Promise ошибок
    window.addEventListener('unhandledrejection', function(event) {
        const errorMessage = `Unhandled Promise rejection: ${event.reason}`;
        const stackTrace = event.reason && event.reason.stack ? event.reason.stack : '';
        
        if (window.consoleLogger && typeof window.consoleLogger.log_js_exception === 'function') {
            try {
                window.consoleLogger.log_js_exception(errorMessage, stackTrace);
            } catch (e) {
                originalConsole.error('Promise rejection logging error:', e);
            }
        }
    });
    
    // Специальный логгер для чата
    
    window.logChatEvent = function(eventData) {
        if (window.consoleLogger && typeof window.consoleLogger.log_chat_event === 'function') {
            try {
                const message = typeof eventData === 'object' ? JSON.stringify(eventData) : String(eventData);
                window.consoleLogger.log_chat_event(message);
            } catch (e) {
                originalConsole.error('Chat event logging error:', e);
            }
        }
    };
    
    console.log('✅ Console logging system activated');
    console.info('ℹ️ All console messages will now be forwarded to Python');
}

// Автоматическая активация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 DOM loaded, waiting for WebChannel bridge...');
    
    // Пытаемся установить логирование каждые 100ms до успеха
    let attempts = 0;
    const maxAttempts = 50; // 5 секунд максимум
    
    const setupInterval = setInterval(function() {
        attempts++;
        
        // Проверяем доступность bridge в разных местах
        let bridge = null;
        
        if (window.chat && window.chat.bridge) {
            bridge = window.chat.bridge;
        } else if (window.gopiaiChat && window.gopiaiChat.bridge) {
            bridge = window.gopiaiChat.bridge;
        } else if (window.bridge) {
            bridge = window.bridge;
        }
        
        if (bridge) {
            setupConsoleLogging(bridge);
            clearInterval(setupInterval);
            console.log(`✅ Console logging established after ${attempts} attempts`);
        } else if (attempts >= maxAttempts) {
            clearInterval(setupInterval);
            console.warn('⚠️ Failed to establish console logging - bridge not found');
        }
    }, 100);
});