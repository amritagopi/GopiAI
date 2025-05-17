"""
JavaScript-скрипты для анализа и извлечения содержимого веб-страницы: текст, таблицы, меню и т.д.
"""

# Скрипт для анализа текстового содержимого страницы
GET_PAGE_TEXT_CONTENT = """
(function() {
    // Функция для рекурсивного извлечения текста из DOM
    function extractText(element, depth = 0, maxDepth = 3) {
        if (depth > maxDepth) return "";

        let text = "";
        for (const node of element.childNodes) {
            // Текстовый узел
            if (node.nodeType === Node.TEXT_NODE) {
                const trimmed = node.textContent.trim();
                if (trimmed) {
                    text += trimmed + " ";
                }
            }
            // Элемент
            else if (node.nodeType === Node.ELEMENT_NODE) {
                // Пропускаем скрипты, стили, и другие технические элементы
                if (['SCRIPT', 'STYLE', 'META', 'LINK', 'NOSCRIPT'].includes(node.tagName)) {
                    continue;
                }

                // Добавляем перенос строки перед заголовками и параграфами
                if (['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'P', 'DIV', 'LI'].includes(node.tagName)) {
                    text += "\\n";
                }

                // Рекурсивно извлекаем текст
                text += extractText(node, depth + 1, maxDepth);

                // Добавляем перенос строки после блочных элементов
                if (['DIV', 'P', 'LI', 'TR', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(node.tagName)) {
                    text += "\\n";
                }
            }
        }
        return text;
    }

    const mainContent = document.body;
    const extractedText = extractText(mainContent).replace(/\\s+/g, ' ').trim();

    // Разбиваем на параграфы
    const paragraphs = extractedText.split('\\n')
        .map(p => p.trim())
        .filter(p => p.length > 0);

    return {
        fullText: extractedText,
        paragraphs: paragraphs,
        wordCount: extractedText.split(/\\s+/).filter(w => w.length > 0).length
    };
})();
"""

# Скрипт для анализа навигационного меню
GET_NAVIGATION_MENU = """
(function() {
    const possibleMenus = [];

    // Ищем элементы, которые могут быть меню
    const navElements = document.querySelectorAll('nav, [role="navigation"], header ul, .menu, .nav, .navigation');

    navElements.forEach(nav => {
        const links = nav.querySelectorAll('a');
        if (links.length > 2) {  // Если есть хотя бы 3 ссылки, считаем это меню
            const menuItems = [];
            links.forEach(link => {
                menuItems.push({
                    text: link.innerText.trim(),
                    url: link.href,
                    isActive: link.classList.contains('active') ||
                              link.getAttribute('aria-current') === 'page' ||
                              link.pathname === window.location.pathname
                });
            });

            possibleMenus.push({
                element: nav.tagName + (nav.id ? '#' + nav.id : '') + (nav.className ? '.' + nav.className.replace(/\\s+/g, '.') : ''),
                items: menuItems
            });
        }
    });

    return possibleMenus;
})();
"""

# Скрипт для поиска и извлечения данных из таблиц
GET_TABLE_DATA = """
(function() {
    const tables = [];

    document.querySelectorAll('table').forEach((table, tableIndex) => {
        const headers = [];
        const rows = [];

        // Получаем заголовки
        table.querySelectorAll('thead th, tr:first-child th').forEach(th => {
            headers.push(th.innerText.trim());
        });

        // Если заголовков нет, пробуем получить их из первой строки
        if (headers.length === 0) {
            table.querySelectorAll('tr:first-child td').forEach(td => {
                headers.push(td.innerText.trim());
            });
        }

        // Получаем данные
        let rowSelector = headers.length > 0 ? 'tbody tr, tr:not(:first-child)' : 'tr';
        table.querySelectorAll(rowSelector).forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach(td => {
                row.push(td.innerText.trim());
            });

            if (row.length > 0) {
                rows.push(row);
            }
        });

        tables.push({
            index: tableIndex,
            headers: headers,
            rows: rows,
            rowCount: rows.length,
            columnCount: headers.length || (rows[0] ? rows[0].length : 0)
        });
    });

    return tables;
})();
"""

# Скрипт для извлечения структурированных данных (schema.org и т.п.)
GET_STRUCTURED_DATA = """
(function() {
    const structuredData = [];

    // Ищем JSON-LD
    document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
        try {
            const data = JSON.parse(script.textContent);
            structuredData.push({
                type: 'JSON-LD',
                data: data
            });
        } catch (e) {
            // Игнорируем ошибки парсинга
        }
    });

    // Ищем микроданные
    function extractMicrodata(element, result = {}) {
        const itemtype = element.getAttribute('itemtype');
        const itemprop = element.getAttribute('itemprop');

        if (itemtype) {
            result.type = itemtype;
            result.properties = {};
        }

        if (itemprop && result.properties) {
            const itemcontent = element.getAttribute('content') || element.textContent.trim();
            result.properties[itemprop] = itemcontent;
        }

        // Рекурсивно обходим дочерние элементы
        element.children.forEach(child => {
            extractMicrodata(child, result);
        });

        return result;
    }

    document.querySelectorAll('[itemscope]').forEach(item => {
        const data = extractMicrodata(item);
        if (Object.keys(data).length > 0) {
            structuredData.push({
                type: 'Microdata',
                data: data
            });
        }
    });

    return structuredData;
})();
"""
