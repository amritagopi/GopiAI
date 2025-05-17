from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QToolBar
from PySide6.QtCore import Qt # Added Qt import
from .widgets import CodeEditor # Assuming CodeEditor is now in widgets.py
from app.ui.i18n.translator import tr # Corrected import path for tr
from .window_control_widget import WindowControlWidget

def setup_central_widget(main_window, parent_widget=None):
    """
    Настраивает центральный виджет.

    Args:
        main_window: Главное окно приложения
        parent_widget: Родительский виджет, в который добавятся центральные вкладки.
                      Если None, то используется setCentralWidget
    """
    # Создаем центральные вкладки
    main_window.central_tabs = QTabWidget()
    main_window.central_tabs.setTabsClosable(True)
    # Возвращаем возможность перемещения вкладок
    main_window.central_tabs.setMovable(True)
    main_window.central_tabs.setContextMenuPolicy(Qt.CustomContextMenu)
    # Оставляем вкладки в верхней части с выравниванием по левому краю с помощью стиля
    main_window.central_tabs.setStyleSheet("QTabWidget::tab-bar { alignment: left; } QTabBar::tab { text-align: left; }")

    # Assuming _show_tab_context_menu and _close_tab are methods in main_window
    # or will be handled by event_handlers.py
    if hasattr(main_window, "_show_tab_context_menu"):
        main_window.central_tabs.customContextMenuRequested.connect(main_window._show_tab_context_menu)
    if hasattr(main_window, "_close_tab"):
        main_window.central_tabs.tabCloseRequested.connect(main_window._close_tab)

    # Создаем контейнер с содержимым редактора
    main_window.code_editor = CodeEditor(main_window) # CodeEditor is now imported from .widgets
    main_window.central_tabs.addTab(main_window.code_editor, tr("code.new_file", "new_file.py"))

    # Если указан родительский виджет, добавляем в него
    if parent_widget:
        # Если у виджета есть макет, используем его
        if hasattr(parent_widget, 'layout') and parent_widget.layout():
            parent_widget.layout().addWidget(main_window.central_tabs)
        # Иначе создаем новый макет
        else:
            layout = QVBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(main_window.central_tabs)
            parent_widget.setLayout(layout)
    else:
        # Стандартное поведение, если не указан родительский виджет
        main_window.setCentralWidget(main_window.central_tabs)
