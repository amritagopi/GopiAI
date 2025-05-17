"""
JavaScript-скрипты для мониторинга страницы: изменения в DOM, производительность, сетевые запросы.
"""

# Скрипт для непрерывного мониторинга изменений страницы
MONITOR_PAGE_CHANGES = """
function startMonitoringPageChanges(callback) {
    // Получение текущего состояния страницы
    function getPageState() {
        return {
            url: window.location.href,
            title: document.title,
            bodyContent: document.body.innerHTML.length,
            elementCount: document.querySelectorAll('*').length,
            scrollPosition: window.scrollY
        };
    }

    // Начальное состояние
    let lastState = getPageState();

    // Обработчик изменений DOM
    const observer = new MutationObserver(mutations => {
        // Получаем текущее состояние
        const currentState = getPageState();

        // Проверяем значимые изменения
        const changes = {
            urlChanged: currentState.url !== lastState.url,
            titleChanged: currentState.title !== lastState.title,
            contentSizeChanged: Math.abs(currentState.bodyContent - lastState.bodyContent) > 100,
            elementCountChanged: Math.abs(currentState.elementCount - lastState.elementCount) > 5,
            scrollPositionChanged: Math.abs(currentState.scrollPosition - lastState.scrollPosition) > 100
        };

        // Если есть значимые изменения, вызываем callback
        if (changes.urlChanged || changes.titleChanged || changes.contentSizeChanged ||
            changes.elementCountChanged || changes.scrollPositionChanged) {

            // Обновляем состояние
            lastState = currentState;

            // Вызываем callback с информацией об изменениях
            callback({
                changes: changes,
                state: currentState,
                timestamp: new Date().toISOString()
            });
        }
    });

    // Запускаем наблюдение за DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true
    });

    // Обработчики для отслеживания навигации и скролла
    window.addEventListener('popstate', () => {
        const currentState = getPageState();
        lastState = currentState;
        callback({
            changes: { urlChanged: true },
            state: currentState,
            timestamp: new Date().toISOString()
        });
    });

    window.addEventListener('scroll', () => {
        // Используем throttle, чтобы не перегружать систему
        clearTimeout(window._scrollTimer);
        window._scrollTimer = setTimeout(() => {
            const currentState = getPageState();
            if (Math.abs(currentState.scrollPosition - lastState.scrollPosition) > 100) {
                lastState.scrollPosition = currentState.scrollPosition;
                callback({
                    changes: { scrollPositionChanged: true },
                    state: { scrollPosition: currentState.scrollPosition },
                    timestamp: new Date().toISOString()
                });
            }
        }, 300);
    });

    // Возвращаем функцию для остановки мониторинга
    return function stopMonitoring() {
        observer.disconnect();
        window.removeEventListener('popstate');
        window.removeEventListener('scroll');
    };
}

// Использование:
// const stopMonitoring = startMonitoringPageChanges(function(changes) {
//     console.log('Страница изменилась:', changes);
// });
//
// // Позже можно остановить мониторинг:
// stopMonitoring();
"""

# Скрипт для получения метрик производительности страницы
GET_PAGE_PERFORMANCE = """
(function() {
    // Проверка поддержки API
    if (!window.performance || !window.performance.timing) {
        return { error: "Performance API не поддерживается" };
    }

    const timing = window.performance.timing;
    const now = Date.now();

    // Базовые метрики загрузки
    const metrics = {
        // Время от начала навигации до полной загрузки страницы
        pageLoadTime: timing.loadEventEnd - timing.navigationStart,

        // Время установки соединения
        connectionTime: timing.connectEnd - timing.connectStart,

        // Время ответа сервера (первый байт)
        serverResponseTime: timing.responseStart - timing.requestStart,

        // Время загрузки документа
        documentLoadTime: timing.domComplete - timing.responseEnd,

        // Время до готовности DOM
        domReadyTime: timing.domContentLoadedEventEnd - timing.navigationStart,

        // Время рендеринга
        renderTime: timing.domComplete - timing.domContentLoadedEventStart,

        // Времена ресурсов
        resources: {
            totalCount: window.performance.getEntriesByType('resource').length,
            totalSize: 0,
            totalTime: 0,
            byType: {
                script: { count: 0, size: 0, time: 0 },
                css: { count: 0, size: 0, time: 0 },
                image: { count: 0, size: 0, time: 0 },
                font: { count: 0, size: 0, time: 0 },
                other: { count: 0, size: 0, time: 0 }
            }
        }
    };

    // Анализ загруженных ресурсов
    window.performance.getEntriesByType('resource').forEach(resource => {
        metrics.resources.totalSize += resource.transferSize || 0;
        metrics.resources.totalTime += resource.duration || 0;

        let type = 'other';
        if (resource.initiatorType === 'script' || resource.name.match(/\\.js(\\?.*)?$/i)) {
            type = 'script';
        } else if (resource.initiatorType === 'css' || resource.name.match(/\\.css(\\?.*)?$/i)) {
            type = 'css';
        } else if (resource.initiatorType === 'img' || resource.name.match(/\\.(png|jpg|jpeg|gif|svg|webp)(\\?.*)?$/i)) {
            type = 'image';
        } else if (resource.name.match(/\\.(woff|woff2|ttf|otf|eot)(\\?.*)?$/i)) {
            type = 'font';
        }

        metrics.resources.byType[type].count++;
        metrics.resources.byType[type].size += resource.transferSize || 0;
        metrics.resources.byType[type].time += resource.duration || 0;
    });

    // Добавляем текущие метрики производительности
    if (window.performance.memory) {
        metrics.memory = {
            usedJSHeapSize: window.performance.memory.usedJSHeapSize,
            totalJSHeapSize: window.performance.memory.totalJSHeapSize,
            jsHeapSizeLimit: window.performance.memory.jsHeapSizeLimit
        };
    }

    return metrics;
})();
"""
