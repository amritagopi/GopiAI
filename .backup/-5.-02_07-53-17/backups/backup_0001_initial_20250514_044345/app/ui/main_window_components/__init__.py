"""
Components for MainWindow class.

This package contains mixins and utilities that extend the MainWindow class
functionality while keeping the main class file smaller and more manageable.
"""

# Import all mixins here for easier access
from .file_actions import FileActionsMixin
from .edit_actions import EditActionsMixin
from .tab_management import TabManagementMixin
from .view_management import ViewManagementMixin
from .agent_integration import AgentIntegrationMixin
from .window_events import WindowEventsMixin

# These will be added later when implemented
# from .browser_integration import BrowserIntegrationMixin
# from .settings_dialogs import SettingsDialogsMixin
# from .help_dialogs import HelpDialogsMixin
# from .ui_diagnostics import UIDiagnosticsMixin

def apply_mixins(main_window_class):
    """
    Применяет все миксины к классу MainWindow.

    Args:
        main_window_class: Класс MainWindow, к которому нужно применить миксины

    Returns:
        Модифицированный класс MainWindow с примененными миксинами
    """
    mixins = [
        FileActionsMixin,
        EditActionsMixin,
        TabManagementMixin,
        ViewManagementMixin,
        AgentIntegrationMixin,
        WindowEventsMixin
    ]

    # Создаем новый класс, наследующийся от QMainWindow и всех миксинов
    return type(
        'MainWindow',
        tuple([main_window_class] + mixins),
        {}
    )
