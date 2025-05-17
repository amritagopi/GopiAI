import json
import os
import threading  # Добавляем этот импорт

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from app.logger import logger


class ThemeManager(QObject):
    """Централизованный менеджер тем для GopiAI."""

    # Сигнал для изменения только визуальной темы
    visualThemeChanged = Signal(str)

    # Сигнал при изменении темы
    themeChanged = Signal(str)

    # Фолбэк для темной темы (если JSON не найден)
    FALLBACK_DARK_THEME_DATA = {
        "name": "dark",
        "type": "dark",
        "display_name": "Темная тема (Фолбэк)",
        "description": "Базовая темная тема, если файл dark.json не найден.",
        "colors": {
            "background": "#2D2D2D",
            "foreground": "#FFFFFF",
            "accent": "#3498DB",
            "secondary_background": "#3C3C3C",
            "secondary_foreground": "#B0B0B0",  # Добавлены для соответствия
            "border": "#444444",
            "button_normal": "#555555",
            "button_hover": "#6A6A6A",
            "button_pressed": "#3498DB",
            "button_text": "#EAEAEA",  # Обновлены
            "input_background": "#3D3D3D",
            "input_text": "#EAEAEA",
            "input_border": "#555555",
            "input_placeholder": "#888888",  # Добавлен placeholder
            "text_color": "#EAEAEA",
            "text_secondary": "#B0B0B0",  # Добавлены
            "link_color": "#3498DB",
            "link_hover_color": "#5DADE2",  # Добавлены
            "error": "#E74C3C",
            "success": "#2ECC71",
            "warning": "#F39C12",
            "info": "#3498DB",  # Добавлен info
            "icon_color": "#EAEAEA",
            "icon_hover_color": "#FFFFFF",
            "icon_disabled_color": "#777777",  # Добавлены hover и disabled
            "tab_active_background": "#3498DB",
            "tab_active_foreground": "#FFFFFF",  # Обновлены ключи
            "tab_inactive_background": "#3C3C3C",
            "tab_inactive_foreground": "#B0B0B0",  # Обновлены ключи
            "tab_hover_background": "#6A6A6A",
            "tab_hover_foreground": "#FFFFFF",  # Обновлены ключи
            "tab_selected_background": "#3498DB",
            "tab_selected_foreground": "#FFFFFF",  # Обновлены ключи
            "tab_border_color": "#2D2D2D",  # Обновлен ключ
            "dock_title_background": "#3C3C3C",
            "dock_title_foreground": "#EAEAEA",  # Обновлены ключи
            "dock_border_color": "#444444",  # Обновлен ключ
            "pane_border_color": "#444444",  # Обновлен ключ
            "menu_background": "#3C3C3C",
            "menu_foreground": "#EAEAEA",  # Обновлены ключи
            "menu_selection_background": "#3498DB",
            "menu_selection_foreground": "#FFFFFF",  # Обновлены ключи
            "menu_separator": "#555555",  # Обновлен ключ
            "tooltip_background": "#555555",
            "tooltip_foreground": "#EAEAEA",  # Обновлены ключи
            "scrollbar_background": "#3C3C3C",
            "scrollbar_handle": "#555555",
            "scrollbar_handle_hover": "#6A6A6A",  # Обновлены ключи
            "window_background_color": "#2D2D2D",
            "window_text_color": "#EAEAEA",  # Обновлены ключи
            "dialog_background_color": "#3C3C3C",
            "dialog_text_color": "#EAEAEA",  # Обновлены ключи
            "code_background": "#272822",
            "code_text": "#F8F8F2",
            "code_comment": "#75715E",  # Добавлены code цвета
            "code_keyword": "#F92672",
            "code_string": "#E6DB74",
            "code_number": "#AE81FF",
            "code_operator": "#F92672",
            "code_builtin": "#66D9EF",
            "selection_background": "#3498DB",
            "selection_foreground": "#FFFFFF",  # Добавлены
            "disabled_foreground": "#777777",
            "disabled_background": "#404040",  # Добавлены
        },
    }

    # Фолбэк для светлой темы (если JSON не найден)
    FALLBACK_LIGHT_THEME_DATA = {
        "name": "light",
        "type": "light",
        "display_name": "Светлая тема (Фолбэк)",
        "description": "Базовая светлая тема, если файл light.json не найден.",
        "colors": {  # Аналогично обновим ключи для светлой темы для консистентности
            "background": "#F5F5F5",
            "foreground": "#333333",
            "accent": "#2980B9",
            "secondary_background": "#E0E0E0",
            "secondary_foreground": "#555555",
            "border": "#CCCCCC",
            "button_normal": "#DDDDDD",
            "button_hover": "#C0C0C0",
            "button_pressed": "#2980B9",
            "button_text": "#333333",
            "input_background": "#FFFFFF",
            "input_text": "#333333",
            "input_border": "#CCCCCC",
            "input_placeholder": "#AAAAAA",
            "text_color": "#333333",
            "text_secondary": "#555555",
            "link_color": "#2980B9",
            "link_hover_color": "#3498DB",
            "error": "#C0392B",
            "success": "#27AE60",
            "warning": "#E67E22",
            "info": "#2980B9",
            "icon_color": "#333333",
            "icon_hover_color": "#000000",
            "icon_disabled_color": "#999999",
            "tab_active_background": "#2980B9",
            "tab_active_foreground": "#FFFFFF",
            "tab_inactive_background": "#E0E0E0",
            "tab_inactive_foreground": "#555555",
            "tab_hover_background": "#C0C0C0",
            "tab_hover_foreground": "#333333",
            "tab_selected_background": "#2980B9",
            "tab_selected_foreground": "#FFFFFF",
            "tab_border_color": "#F5F5F5",
            "dock_title_background": "#E0E0E0",
            "dock_title_foreground": "#333333",
            "dock_border_color": "#CCCCCC",
            "pane_border_color": "#CCCCCC",
            "menu_background": "#E0E0E0",
            "menu_foreground": "#333333",
            "menu_selection_background": "#2980B9",
            "menu_selection_foreground": "#FFFFFF",
            "menu_separator": "#CCCCCC",
            "tooltip_background": "#DDDDDD",
            "tooltip_foreground": "#333333",
            "scrollbar_background": "#E0E0E0",
            "scrollbar_handle": "#CCCCCC",
            "scrollbar_handle_hover": "#B0B0B0",
            "window_background_color": "#F5F5F5",
            "window_text_color": "#333333",
            "dialog_background_color": "#E0E0E0",
            "dialog_text_color": "#333333",
            "code_background": "#FDFDFD",
            "code_text": "#333333",
            "code_comment": "#999988",
            "code_keyword": "#A71D5D",
            "code_string": "#183691",
            "code_number": "#008080",
            "code_operator": "#A71D5D",
            "code_builtin": "#0086B3",
            "selection_background": "#2980B9",
            "selection_foreground": "#FFFFFF",
            "disabled_foreground": "#999999",
            "disabled_background": "#D0D0D0",
        },
    }

    _instance = None
    _lock = threading.Lock()  # Добавим блокировку для потокобезопасности

    @classmethod
    def instance(cls, app=None):
        """Получение единственного экземпляра менеджера тем (паттерн Singleton)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()  # app больше не нужен
        return cls._instance

    def __init__(self):  # Убираем app из параметров
        super().__init__()
        # self.app больше не хранится как атрибут экземпляра постоянно.
        # Он будет получаться через QApplication.instance() по мере необходимости.

        logger.info("ThemeManager.__init__ called.")
        # Логирование типа QApplication.instance() можно сделать здесь для информации,
        # но без сохранения self.app
        current_qapp_instance = QApplication.instance()
        if current_qapp_instance:
            logger.info(
                f"QApplication.instance() type at ThemeManager init: {type(current_qapp_instance)}"
            )
        else:
            logger.warning(
                "QApplication.instance() is None at ThemeManager init. Темы будут загружены, но не применены."
            )

        self.themes = {}  # Инициализируем пустым словарем
        self._load_default_themes()  # Загружаем 'light' и 'dark' из JSON или используем фолбэки

        # Устанавливаем current_visual_theme после загрузки стандартных тем,
        # чтобы убедиться, что тема 'light' (по умолчанию) существует в self.themes.
        self.current_visual_theme = "light"

        # Загружаем пользовательские настройки темы, которые могут перезаписать
        # current_visual_theme или добавить/обновить пользовательские темы.
        self.load_user_theme_settings()

    def _load_default_themes(self):
        """Загружает стандартные темы 'light' и 'dark' из JSON-файлов или использует фолбэки."""
        default_theme_configs = {
            "light": {"fallback_data": self.FALLBACK_LIGHT_THEME_DATA},
            "dark": {"fallback_data": self.FALLBACK_DARK_THEME_DATA},
        }
        # Путь к директории app/ui/themes/
        # os.path.dirname(os.path.abspath(__file__)) -> app/utils/
        # os.path.dirname(...) -> app/
        # os.path.join(..., "ui", "themes") -> app/ui/themes/
        theme_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "themes"
        )

        for name, config in default_theme_configs.items():
            json_path = os.path.join(theme_dir, f"{name}.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                        # Проверяем, что загруженные данные содержат ключ 'colors'
                        if "colors" not in theme_data:
                            logger.error(
                                f"Ключ 'colors' отсутствует в {json_path}. Используется фолбэк для темы '{name}'."
                            )
                            self.themes[name] = config["fallback_data"]
                        else:
                            self.themes[name] = theme_data
                            logger.info(f"Загружена тема '{name}' из {json_path}")
                except Exception as e:
                    logger.error(
                        f"Ошибка загрузки темы '{name}' из {json_path}: {e}. Используется фолбэк."
                    )
                    self.themes[name] = config["fallback_data"]
            else:
                logger.warning(
                    f"Файл темы {json_path} не найден. Используется фолбэк для темы '{name}'."
                )
                self.themes[name] = config["fallback_data"]

    def load_user_theme_settings(self):
        """Загружает пользовательские настройки темы из файла конфигурации."""
        try:
            # Путь к theme_config.json относительно текущего файла (app/utils/theme_config.json)
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "theme_config.json"
            )
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    if (
                        "visual_theme" in config_data
                        and config_data["visual_theme"] in self.themes
                    ):
                        self.current_visual_theme = config_data["visual_theme"]
                    elif "visual_theme" in config_data:
                        logger.warning(
                            f"Сохраненная тема '{config_data['visual_theme']}' не найдена среди доступных. Используется '{self.current_visual_theme}'."
                        )

                    if "custom_themes" in config_data:
                        for theme_name, theme_data in config_data[
                            "custom_themes"
                        ].items():
                            if "colors" not in theme_data:
                                logger.warning(
                                    f"Пользовательская тема '{theme_name}' не содержит ключ 'colors'. Тема не будет загружена."
                                )
                                continue
                            # add_custom_theme позаботится о проверках и сохранении
                            self.add_custom_theme(
                                theme_name, theme_data, save_settings=False
                            )  # Не сохраняем здесь, сохраним один раз в конце
                logger.info(
                    f"Загружены настройки темы. Текущая тема: {self.current_visual_theme}"
                )
        except Exception as e:
            logger.error(
                f"Ошибка при загрузке настроек темы из {config_path if 'config_path' in locals() else 'theme_config.json'}: {str(e)}"
            )

    def save_user_theme_settings(self):
        """Сохраняет пользовательские настройки темы в файл конфигурации."""
        try:
            # Сохраняем только те темы, которые не являются 'light' или 'dark' по умолчанию
            # или если они были изменены (хотя текущая логика не позволяет изменять 'light'/'dark' напрямую,
            # а только через custom_themes с другими именами).
            # Если 'light' или 'dark' были загружены из JSON, они не считаются "пользовательскими" в этом контексте.
            custom_themes_to_save = {}
            for theme_name, theme_data in self.themes.items():
                # Пользовательскими считаются темы, не являющиеся стандартными 'light' или 'dark'
                if theme_name not in ["light", "dark"]:
                    custom_themes_to_save[theme_name] = theme_data
                # Либо, если это 'light' или 'dark', но они отличаются от фолбэков (т.е. загружены из JSON)
                # Это условие можно усложнить, если нужно сохранять измененные стандартные темы.
                # Пока что, если light.json/dark.json изменятся, они просто будут загружены при следующем старте.
                # theme_config.json хранит только *дополнительные* пользовательские темы и выбранную тему.

            config = {
                "visual_theme": self.current_visual_theme,
                "custom_themes": custom_themes_to_save,
            }
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "theme_config.json"
            )
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logger.info(
                f"Сохранены настройки темы в {config_path}. Текущая тема: {self.current_visual_theme}"
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек темы: {str(e)}")

    def get_color(self, key, default=None):
        """Получает цвет из текущей темы с улучшенным фолбэком."""
        active_theme_name = self.current_visual_theme

        # Получаем данные текущей активной темы
        current_theme_data = self.themes.get(active_theme_name)

        if not current_theme_data or "colors" not in current_theme_data:
            logger.warning(
                f"Данные или секция 'colors' для темы '{active_theme_name}' не найдены. Временно используется фолбэк 'light'."
            )
            current_theme_data = (
                self.FALLBACK_LIGHT_THEME_DATA
            )  # Используем полный объект фолбэка
            theme_for_logging = (
                f"{active_theme_name} (не найдена, фолбэк на FALLBACK_LIGHT_THEME_DATA)"
            )
        else:
            theme_for_logging = active_theme_name

        current_theme_colors = current_theme_data.get("colors", {})

        # Пытаемся получить цвет из текущей темы
        if key in current_theme_colors:
            return current_theme_colors[key]
        elif default is not None:
            return default
        else:
            logger.warning(
                f"Цвет '{key}' не найден в секции 'colors' темы '{theme_for_logging}'. Попытка использовать базовый фолбэк."
            )

            # Определяем базовую тему для фолбэка (light или dark)
            # Используем 'type' из данных темы, если есть, иначе по имени
            theme_type = current_theme_data.get(
                "type", "light" if "light" in active_theme_name.lower() else "dark"
            )

            if theme_type == "dark":
                base_fallback_theme_colors = self.FALLBACK_DARK_THEME_DATA.get(
                    "colors", {}
                )
                base_theme_name_for_log = "FALLBACK_DARK_THEME_DATA"
            else:  # light или неизвестный тип
                base_fallback_theme_colors = self.FALLBACK_LIGHT_THEME_DATA.get(
                    "colors", {}
                )
                base_theme_name_for_log = "FALLBACK_LIGHT_THEME_DATA"

            if key in base_fallback_theme_colors:
                return base_fallback_theme_colors[key]
            else:
                logger.error(
                    f"Цвет '{key}' не найден ни в теме '{theme_for_logging}', ни в {base_theme_name_for_log}."
                )
                # Последний уровень фолбэка - общие значения по умолчанию
                general_fallbacks = {
                    "background": "#2D2D2D",
                    "foreground": "#EAEAEA",
                    "accent": "#3498DB",
                    "border": "#444444",
                    "window_background_color": "#2D2D2D",
                    "window_text_color": "#EAEAEA",
                    "menu_background": "#3C3C3C",
                    "menu_foreground": "#EAEAEA",
                    "tab_background_color": "#3C3C3C",
                    "tab_selected_background_color": "#3498DB",
                    "tab_text_color": "#B0B0B0",
                    "tab_selected_text_color": "#FFFFFF",
                    "button_normal": "#555555",
                    "button_text": "#EAEAEA",
                    "tooltip_background": "#555555",
                    "tooltip_foreground": "#EAEAEA",
                }
                return general_fallbacks.get(key, "#FFFFFF")

    def get_qcolor(self, key):
        """Получает QColor из текущей темы."""
        return QColor(self.get_color(key))

    def switch_visual_theme(self, visual_theme, force_apply=False):
        """
        Переключает текущую визуальную тему.

        Args:
            visual_theme (str): Имя темы для переключения.
            force_apply (bool): Применить тему, даже если она уже активна.

        Returns:
            bool: True, если тема переключена успешно, False - если нет.
        """
        # Проверяем, что запрошенная тема существует в списке доступных
        if visual_theme not in self.themes:
            logger.error(f"Тема '{visual_theme}' не найдена в списке доступных.")
            return False

        # Проверяем, нужно ли переключать тему
        if not force_apply and visual_theme == self.current_visual_theme:
            logger.info(f"Тема '{visual_theme}' уже активна.")
            return True

        # Переключаем тему
        self.current_visual_theme = visual_theme
        logger.info(f"Тема переключена на '{visual_theme}'.")

        # Проверяем наличие QApplication перед применением темы
        app = QApplication.instance()
        if not app:
            logger.warning(
                "QApplication.instance() is None при переключении темы. Тема будет применена позже."
            )
            return True  # Возвращаем True, т.к. тема сохранена, но не применена

        # Применяем тему к приложению
        self._apply_visual_theme()

        # Сохраняем настройки
        self.save_user_theme_settings()

        # Отправляем сигнал об изменении темы
        self.visualThemeChanged.emit(visual_theme)
        self.themeChanged.emit(visual_theme)  # Для обратной совместимости

        return True

    def _apply_visual_theme(self, app_instance=None):
        """
        Применяет текущую визуальную тему к экземпляру QApplication.

        Args:
            app_instance (QApplication, optional): Экземпляр QApplication.
                Если None, будет использован QApplication.instance().
        """
        # Получаем экземпляр QApplication, если не предоставлен
        app = app_instance if app_instance else QApplication.instance()
        if not app:
            logger.error(
                "QApplication.instance() is None. Невозможно применить тему. Темы будут загружены, но применены позже."
            )
            return False

        # Генерируем и применяем QSS
        qss = self._generate_stylesheet()
        app.setStyleSheet(qss)
        logger.info(f"Применён QSS стиль для темы '{self.current_visual_theme}'")
        return True

    def _replace_color_placeholders(self, qss_content):
        """
        Заменяет все плейсхолдеры вида @color_name в QSS на реальные значения цветов из текущей темы.

        Args:
            qss_content (str): Исходная QSS строка с плейсхолдерами @color_name.

        Returns:
            str: QSS строка с замененными плейсхолдерами.
        """
        if not qss_content:
            return ""

        # Получаем все цвета текущей темы
        theme_colors = self.themes.get(self.current_visual_theme, {}).get("colors", {})

        # Создаем словарь для замены
        replacements = {}

        # Перебираем все цвета в теме
        for color_name, color_value in theme_colors.items():
            placeholder = f"@{color_name}"
            replacements[placeholder] = color_value

        # Добавляем дополнительные alias-плейсхолдеры для совместимости
        aliases = {
            "@window_background": theme_colors.get("background", "#2D2D2D"),
            "@window_text": theme_colors.get("foreground", "#EAEAEA"),
            "@primary_color": theme_colors.get("accent", "#3498DB"),
            "@secondary_color": theme_colors.get("secondary_background", "#3C3C3C"),
            "@text_primary": theme_colors.get("foreground", "#EAEAEA"),
            "@text_secondary": theme_colors.get("secondary_foreground", "#B0B0B0"),
        }
        replacements.update(aliases)

        # Заменяем все плейсхолдеры
        result = qss_content
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        # Проверяем, остались ли незамененные плейсхолдеры
        import re

        remaining = re.findall(r"@(\w+)", result)
        if remaining:
            logger.warning(f"Незамененные плейсхолдеры в QSS: {set(remaining)}")

            # Логируем, каких ключей не хватает в теме
            for ph in set(remaining):
                logger.debug(f"В теме отсутствует ключ для плейсхолдера: {ph}")
                # Используем фолбэк для незамененных плейсхолдеров
                result = result.replace(
                    f"@{ph}", "#808080"
                )  # Нейтральный серый для неизвестных плейсхолдеров

        return result

    def add_custom_theme(self, theme_name, theme_data, save_settings=True):
        """Добавляет или обновляет пользовательскую тему.
        theme_data должен быть словарем, содержащим как минимум ключ 'colors'.
        """
        if not isinstance(theme_data, dict) or "colors" not in theme_data:
            logger.error(
                f"Некорректные данные для пользовательской темы '{theme_name}'. Отсутствует ключ 'colors' или данные не являются словарем."
            )
            return False

        if theme_name in ["light", "dark"]:
            logger.warning(
                f"Невозможно перезаписать встроенную тему '{theme_name}' через add_custom_theme. Используйте JSON файлы в 'app/ui/themes/'."
            )
            return False

        # Добавляем новую тему в словарь тем
        self.themes[theme_name] = theme_data

        if save_settings:
            self.save_user_theme_settings()

        logger.info(f"Добавлена/обновлена пользовательская тема: {theme_name}")

        # Переключаемся на новую тему вместо просто отправки сигнала
        self.switch_visual_theme(theme_name)

        return True

    def delete_custom_theme(self, theme_name_to_delete):
        """Удаляет пользовательскую тему."""
        if theme_name_to_delete in ["light", "dark"]:
            logger.warning(
                f"Невозможно удалить встроенную тему: {theme_name_to_delete}"
            )
            return False

        if theme_name_to_delete not in self.themes:
            logger.warning(
                f"Пользовательская тема '{theme_name_to_delete}' не найдена."
            )
            return False

        try:
            del self.themes[theme_name_to_delete]
            logger.info(
                f"Пользовательская тема '{theme_name_to_delete}' удалена из словаря self.themes."
            )

            current_theme_was_deleted = False
            if self.current_visual_theme == theme_name_to_delete:
                logger.info(
                    f"Удалена текущая активная тема '{theme_name_to_delete}'. Переключение на 'light'."
                )
                self.current_visual_theme = "light"
                current_theme_was_deleted = True

            self.save_user_theme_settings()

            if current_theme_was_deleted:
                logger.info(
                    f"Принудительное переключение на тему '{self.current_visual_theme}' после удаления активной темы."
                )
                self.switch_visual_theme(self.current_visual_theme)
            else:
                logger.info(
                    f"Удалена неактивная тема '{theme_name_to_delete}'. Текущая тема '{self.current_visual_theme}' остается. Отправка сигнала visualThemeChanged для обновления UI."
                )
                self.visualThemeChanged.emit(self.current_visual_theme)

            logger.info(
                f"Пользовательская тема '{theme_name_to_delete}' успешно удалена."
            )
            return True
        except Exception as e:
            logger.error(
                f"Ошибка при удалении пользовательской темы '{theme_name_to_delete}': {str(e)}"
            )
            return False

    def _generate_stylesheet(self):
        """
        Генерирует полный QSS стиль для текущей темы.

        Returns:
            str: QSS строка с примененными значениями цветов из темы.
        """
        try:
            # Загружаем базовый QSS из файла
            theme_qss_path = self.get_theme_qss_path()
            base_qss = ""

            if os.path.exists(theme_qss_path):
                try:
                    with open(theme_qss_path, "r", encoding="utf-8") as f:
                        base_qss = f.read()
                    logger.info(f"Загружен базовый QSS из файла: {theme_qss_path}")
                except Exception as e:
                    logger.error(
                        f"Ошибка при чтении файла стиля {theme_qss_path}: {str(e)}"
                    )
                    base_qss = self._fallback_stylesheet()
            else:
                logger.warning(
                    f"QSS файл не найден: {theme_qss_path}. Используется резервный стиль."
                )
                base_qss = self._fallback_stylesheet()

            # Добавляем дополнительный QSS из других источников (если нужно)
            # Например, из theme_utils
            try:
                from app.utils.theme_utils import get_additional_qss_template

                additional_qss = get_additional_qss_template()
                base_qss += "\n" + additional_qss
                logger.info("Добавлен QSS из get_additional_qss_template")
            except Exception as e:
                logger.warning(f"Не удалось загрузить дополнительный QSS: {str(e)}")

            # Заменяем плейсхолдеры на значения из текущей темы
            final_qss = self._replace_color_placeholders(base_qss)

            # Проверяем замену всех плейсхолдеров
            if "@" in final_qss:
                logger.warning("В финальном QSS остались незамененные плейсхолдеры")
                # Находим все незамененные плейсхолдеры для логгирования
                import re

                placeholders = re.findall(r"@(\w+)", final_qss)
                logger.debug(f"Незамененные плейсхолдеры: {set(placeholders)}")

            return final_qss

        except Exception as e:
            logger.error(f"Ошибка при генерации стиля: {str(e)}")
            return ""

    def _fallback_stylesheet(self):
        """Возвращает минимальный базовый стиль в случае ошибок с основным QSS."""
        return """
        QWidget {
            background-color: #2D2D2D;
            color: #EAEAEA;
        }
        QPushButton {
            background-color: #555555;
            color: #EAEAEA;
            border: 1px solid #444444;
            border-radius: 3px;
            padding: 4px 8px;
        }
        QPushButton:hover {
            background-color: #6A6A6A;
        }
        QPushButton:pressed {
            background-color: #3498DB;
        }
        """

    def get_theme_qss_path(self):
        """Получает путь к файлу QSS для текущей темы."""
        theme_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "themes"
        )
        return os.path.join(theme_dir, f"{self.current_visual_theme}.qss")

    def get_available_visual_themes(self):
        """Получает список доступных визуальных тем."""
        return list(self.themes.keys())

    def get_current_visual_theme(self):
        """Возвращает текущую визуальную тему."""
        return self.current_visual_theme

    def get_theme_display_name(self, theme_name):
        """Получает отображаемое имя темы, сначала из данных темы, потом из фолбэка."""
        theme_data = self.themes.get(theme_name)

        if isinstance(theme_data, dict) and "display_name" in theme_data:
            return theme_data["display_name"]

        if theme_name == "light":
            return self.FALLBACK_LIGHT_THEME_DATA.get("display_name", "Светлая")
        if theme_name == "dark":
            return self.FALLBACK_DARK_THEME_DATA.get("display_name", "Темная")

        if theme_name.startswith("custom_"):
            friendly_name = theme_name.replace("custom_", "").replace("_", " ").title()
            return f"{friendly_name} (Пользовательская)"

        return theme_name.replace("_", " ").title()
