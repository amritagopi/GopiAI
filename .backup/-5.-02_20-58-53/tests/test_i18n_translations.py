import os
import pytest
import json
from app.ui.i18n import translator

TRANSLATIONS_DIR = os.path.dirname(os.path.abspath(translator.__file__))

@pytest.fixture(scope="module")
def all_translations():
    """Загружает все переводы из JSON-файлов."""
    translations = {}
    for lang in ["en.json", "ru.json"]:
        path = os.path.join(TRANSLATIONS_DIR, lang)
        with open(path, encoding="utf-8") as f:
            translations[lang[:-5]] = json.load(f)
    return translations

@pytest.mark.parametrize("lang_code", ["en_US", "ru_RU"])
def test_switch_language(lang_code):
    """Проверяет, что смена языка работает корректно и сигнал испускается."""
    manager = translator.JsonTranslationManager()
    called = []
    def on_changed(code):
        called.append(code)
    manager.languageChanged.connect(on_changed)
    assert manager.switch_language(lang_code)
    assert manager.get_current_language() == lang_code
    assert called and called[0] == lang_code

@pytest.mark.parametrize("lang_code, key, default, expected", [
    ("en_US", "settings.llm.model", "LLM Model", "LLM Model:"),
    ("ru_RU", "settings.llm.model", "LLM модель", "LLM модель:")
])
def test_get_translation(lang_code, key, default, expected):
    manager = translator.JsonTranslationManager()
    manager.switch_language(lang_code)
    assert manager.get_translation(key, default) == expected

def test_all_keys_present(all_translations):
    """Проверяет, что во всех языках присутствуют одинаковые ключи."""
    def flatten(d, prefix=""):
        items = []
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key))
            else:
                items.append(new_key)
        return items
    keys_en = set(flatten(all_translations["en"]))
    keys_ru = set(flatten(all_translations["ru"]))
    assert keys_en == keys_ru, f"Ключи не совпадают!\nEN only: {keys_en - keys_ru}\nRU only: {keys_ru - keys_en}"
