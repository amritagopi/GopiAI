"""
Пакет модулей с JavaScript-скриптами для браузерных инструментов.

Этот пакет содержит различные JavaScript-скрипты, разделенные по тематическим модулям:
- page_info: скрипты для получения информации о странице
- content: скрипты для работы с текстовым и структурным содержимым
- elements: скрипты для работы с DOM-элементами
- forms: скрипты для заполнения и отправки форм
- monitoring: скрипты для мониторинга изменений страницы
"""

from .page_info import GET_PAGE_INFO
from .content import (
    GET_PAGE_TEXT_CONTENT,
    GET_NAVIGATION_MENU,
    GET_TABLE_DATA,
    GET_STRUCTURED_DATA
)
from .elements import (
    GET_ELEMENTS_BY_SELECTOR,
    CLICK_ELEMENT
)
from .forms import FILL_FORM
from .monitoring import (
    MONITOR_PAGE_CHANGES,
    GET_PAGE_PERFORMANCE
)

__all__ = [
    # Информация о странице
    'GET_PAGE_INFO',

    # Содержимое страницы
    'GET_PAGE_TEXT_CONTENT',
    'GET_NAVIGATION_MENU',
    'GET_TABLE_DATA',
    'GET_STRUCTURED_DATA',

    # Работа с элементами
    'GET_ELEMENTS_BY_SELECTOR',
    'CLICK_ELEMENT',

    # Работа с формами
    'FILL_FORM',

    # Мониторинг страницы
    'MONITOR_PAGE_CHANGES',
    'GET_PAGE_PERFORMANCE'
]
