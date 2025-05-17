"""
JavaScript-скрипты для работы с формами: заполнение полей, отправка форм, валидация.
"""

# Скрипт для заполнения форм
FILL_FORM = """
function fillFormFields(formFields) {
    try {
        const results = [];

        formFields.forEach(field => {
            const { selector, value, type = 'input' } = field;
            const elements = document.querySelectorAll(selector);

            if (elements.length === 0) {
                results.push({
                    selector: selector,
                    success: false,
                    error: "Элемент не найден"
                });
                return;
            }

            const element = elements[0];

            // Проверяем видимость
            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            const isVisible = style.display !== 'none' &&
                             style.visibility !== 'hidden' &&
                             style.opacity !== '0' &&
                             rect.width > 0 &&
                             rect.height > 0;

            if (!isVisible) {
                results.push({
                    selector: selector,
                    success: false,
                    error: "Элемент не виден"
                });
                return;
            }

            try {
                // Прокручиваем до элемента
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // В зависимости от типа элемента выполняем разные действия
                if (element.tagName === 'SELECT') {
                    // Для выпадающих списков
                    for (let i = 0; i < element.options.length; i++) {
                        if (element.options[i].text === value || element.options[i].value === value) {
                            element.selectedIndex = i;
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            break;
                        }
                    }
                } else if (element.tagName === 'INPUT' && (element.type === 'checkbox' || element.type === 'radio')) {
                    // Для чекбоксов и радиокнопок
                    if ((value === true || value === 'true' || value === 'checked') !== element.checked) {
                        element.click();
                    }
                } else {
                    // Для обычных полей ввода
                    element.focus();
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }

                results.push({
                    selector: selector,
                    success: true,
                    value: value
                });
            } catch (error) {
                results.push({
                    selector: selector,
                    success: false,
                    error: error.toString()
                });
            }
        });

        return results;
    } catch (error) {
        return { success: false, error: error.toString() };
    }
}

// Использование:
// fillFormFields([
//   { selector: '#username', value: 'john.doe' },
//   { selector: '#password', value: 'secret123' },
//   { selector: '#remember-me', value: true }
// ])
"""
