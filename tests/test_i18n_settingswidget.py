import pytest
from PySide6.QtWidgets import QApplication
from app.ui.settings_widget import SettingsWidget
from app.ui.i18n.translator import JsonTranslationManager
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.mark.parametrize("lang_code, expected_label", [
    ("en_US", "LLM Model:"),
    ("ru_RU", "LLM модель:")
])
def test_settingswidget_retranslate(app, lang_code, expected_label):
    widget = SettingsWidget()
    JsonTranslationManager.instance().switch_language(lang_code)
    widget.retranslateUi()
    label = widget.form.labelForField(widget.llm_model_edit).text()
    assert label == expected_label
