import pytest
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.ui.i18n.translator import JsonTranslationManager
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.mark.parametrize("lang_code, expected_title", [
    ("en_US", "GopiAI"),
    ("ru_RU", "GopiAI")
])
def test_mainwindow_retranslate(app, lang_code, expected_title):
    window = MainWindow()
    JsonTranslationManager.instance().switch_language(lang_code)
    window.retranslateUi()
    assert window.windowTitle() == expected_title
