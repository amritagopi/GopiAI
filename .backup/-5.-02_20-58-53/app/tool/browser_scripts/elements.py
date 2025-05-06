"""
JavaScript-скрипты для работы с DOM-элементами: поиск, получение информации и взаимодействие.
"""

# Скрипт для извлечения списка элементов по CSS селектору
GET_ELEMENTS_BY_SELECTOR = """
function getElementsBySelectorWithInfo(selector) {
    const elements = document.querySelectorAll(selector);
    const results = [];

    elements.forEach((element, index) => {
        // Получаем координаты элемента
        const rect = element.getBoundingClientRect();

        // Проверяем, виден ли элемент
        const style = window.getComputedStyle(element);
        const isVisible = style.display !== 'none' &&
                          style.visibility !== 'hidden' &&
                          style.opacity !== '0' &&
                          rect.width > 0 &&
                          rect.height > 0;

        results.push({
            index: index,
            tagName: element.tagName.toLowerCase(),
            id: element.id,
            className: element.className,
            textContent: element.textContent.trim().substring(0, 100), // Ограничиваем длину текста
            attributes: Array.from(element.attributes).map(attr => {
                return { name: attr.name, value: attr.value };
            }),
            position: {
                x: rect.left + window.scrollX,
                y: rect.top + window.scrollY,
                width: rect.width,
                height: rect.height
            },
            isVisible: isVisible,
            hasChildren: element.children.length > 0
        });
    });

    return results;
}

// Использование: getElementsBySelectorWithInfo('div.product-item')
"""

# Скрипт для клика по элементу
CLICK_ELEMENT = """
function clickElement(selector, index = 0) {
    try {
        const elements = document.querySelectorAll(selector);
        if (elements.length === 0) {
            return { success: false, error: "Элементы не найдены" };
        }

        if (index >= elements.length) {
            return { success: false, error: `Индекс ${index} вне диапазона (найдено ${elements.length} элементов)` };
        }

        const element = elements[index];

        // Проверяем, виден ли элемент
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        const isVisible = style.display !== 'none' &&
                         style.visibility !== 'hidden' &&
                         style.opacity !== '0' &&
                         rect.width > 0 &&
                         rect.height > 0;

        if (!isVisible) {
            return { success: false, error: "Элемент не виден" };
        }

        // Прокручиваем страницу до элемента
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Кликаем по элементу
        setTimeout(() => {
            element.click();
        }, 300);

        return {
            success: true,
            elementInfo: {
                tagName: element.tagName.toLowerCase(),
                id: element.id,
                className: element.className,
                text: element.textContent.trim().substring(0, 50)
            }
        };
    } catch (error) {
        return { success: false, error: error.toString() };
    }
}

// Использование: clickElement('.add-to-cart-button', 0)
"""
