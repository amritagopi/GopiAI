"""
JavaScript-скрипты для получения основной информации о веб-странице.
"""

# Скрипт для получения основной информации о странице
GET_PAGE_INFO = """
(function() {
    const info = {
        title: document.title,
        url: window.location.href,
        description: "",
        h1: [],
        h2: [],
        metaKeywords: "",
        metaDescription: "",
        links: [],
        images: [],
        forms: []
    };

    // Добавляем мета-описание и ключевые слова
    const descriptionMeta = document.querySelector('meta[name="description"]');
    if (descriptionMeta) {
        info.metaDescription = descriptionMeta.getAttribute('content');
        info.description = info.metaDescription;
    }

    const keywordsMeta = document.querySelector('meta[name="keywords"]');
    if (keywordsMeta) {
        info.metaKeywords = keywordsMeta.getAttribute('content');
    }

    // Добавляем заголовки
    document.querySelectorAll('h1').forEach(h1 => {
        info.h1.push(h1.innerText.trim());
    });

    document.querySelectorAll('h2').forEach(h2 => {
        info.h2.push(h2.innerText.trim());
    });

    // Если нет мета-описания, используем первый параграф
    if (!info.description) {
        const firstParagraph = document.querySelector('p');
        if (firstParagraph) {
            info.description = firstParagraph.innerText.trim();
        }
    }

    // Добавляем ссылки (ограничиваем количество)
    const links = document.querySelectorAll('a[href]');
    for (let i = 0; i < Math.min(links.length, 20); i++) {
        const link = links[i];
        info.links.push({
            text: link.innerText.trim(),
            url: link.href,
            isExternal: link.href.startsWith('http') && !link.href.includes(window.location.hostname)
        });
    }

    // Добавляем изображения (ограничиваем количество)
    const images = document.querySelectorAll('img[src]');
    for (let i = 0; i < Math.min(images.length, 10); i++) {
        const img = images[i];
        info.images.push({
            alt: img.alt || "",
            src: img.src,
            width: img.width,
            height: img.height
        });
    }

    // Добавляем формы
    document.querySelectorAll('form').forEach(form => {
        const formInfo = {
            action: form.action || "",
            method: form.method || "get",
            id: form.id || "",
            fields: []
        };

        form.querySelectorAll('input, select, textarea').forEach(field => {
            formInfo.fields.push({
                type: field.tagName.toLowerCase() === 'input' ? field.type : field.tagName.toLowerCase(),
                name: field.name || "",
                id: field.id || "",
                placeholder: field.placeholder || "",
                value: field.value || "",
                isRequired: field.required || false
            });
        });

        info.forms.push(formInfo);
    });

    return info;
})();
"""
