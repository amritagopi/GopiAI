try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    print('QWebEngineView доступен!')
except ImportError as e:
    print(f'Ошибка: {e}')

print('Проверяем другие модули Qt:')

try:
    from PySide6.QtWidgets import QWidget
    print('QWidget доступен!')
except ImportError as e:
    print(f'Ошибка: {e}')

try:
    from PySide6.QtWebEngineCore import QWebEnginePage
    print('QWebEnginePage доступен!')
except ImportError as e:
    print(f'Ошибка: {e}')
