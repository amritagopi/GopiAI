import os
import pytest
from app.ui.icon_manager import IconManager, get_icon, list_icons

@pytest.fixture(scope="module")
def icon_manager():
    return IconManager.instance()

def test_manifest_loaded(icon_manager):
    """Проверяет, что манифест иконок загружен и не пуст."""
    assert icon_manager.manifest, "Манифест иконок пуст!"
    assert isinstance(icon_manager.manifest, dict)

def test_all_icons_exist(icon_manager):
    """Проверяет, что все иконки из манифеста реально существуют как файлы."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    icons_dir = os.path.join(project_root, "assets", "icons")
    for icon_name, icon_file in icon_manager.manifest.items():
        file_path = os.path.join(icons_dir, icon_file)
        assert os.path.exists(file_path), f"Файл иконки не найден: {file_path}"

def test_get_icon_returns_qicon(icon_manager):
    """Проверяет, что get_icon возвращает QIcon для всех иконок из манифеста."""
    for icon_name in icon_manager.manifest.keys():
        icon = get_icon(icon_name)
        assert hasattr(icon, 'isNull'), f"get_icon не вернул QIcon для {icon_name}"
        assert not icon.isNull(), f"QIcon для {icon_name} пустой!"

def test_list_icons(icon_manager):
    """Проверяет, что list_icons возвращает все имена из манифеста."""
    icons = set(list_icons())
    manifest_icons = set(icon_manager.manifest.keys())
    assert icons == manifest_icons
