import pytest
from app.ui.icon_manager import get_icon, list_icons
from app.ui.main_window import MainWindow
from app.ui.tools_widget import ToolsWidget
from app.ui.settings_widget import SettingsWidget

@pytest.mark.parametrize("icon_name", [
    "app_icon", "save", "agent", "tools", "browser", "play", "stop"
])
def test_get_icon_returns_qicon(icon_name):
    icon = get_icon(icon_name)
    assert icon is not None
    assert hasattr(icon, 'isNull')
    assert not icon.isNull(), f"Иконка {icon_name} не найдена или пуста!"

def test_mainwindow_icons():
    window = MainWindow()
    # Проверяем, что иконка приложения установлена через get_icon
    assert window.windowIcon() is not None
    assert hasattr(window.windowIcon(), 'isNull')
    assert not window.windowIcon().isNull(), "Иконка приложения не установлена!"

def test_toolswidget_icons():
    widget = ToolsWidget()
    # Проверяем, что иконки вкладок не пустые
    for i in range(widget.tabs.count()):
        icon = widget.tabs.tabIcon(i)
        assert icon is not None
        assert hasattr(icon, 'isNull')
        assert not icon.isNull(), f"Иконка вкладки {i} пуста!"

def test_settingswidget_save_icon():
    widget = SettingsWidget()
    icon = widget.save_btn.icon()
    assert icon is not None
    assert hasattr(icon, 'isNull')
    assert not icon.isNull(), "Иконка кнопки сохранения пуста!"
