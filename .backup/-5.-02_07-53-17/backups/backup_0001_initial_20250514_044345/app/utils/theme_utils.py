import base64
import logging
import os

logger = logging.getLogger(__name__)


def get_additional_qss_template() -> str:
    # Импортируем здесь, чтобы избежать циклического импорта
    from app.utils.theme_manager import ThemeManager

    theme_manager = ThemeManager.instance()
    # Получаем цвета из темы
    tooltip_fg = theme_manager.get_color("tooltip_foreground", "#ffffff")
    tooltip_bg = theme_manager.get_color("tooltip_background", "#333333")
    border_color = theme_manager.get_color("border", "#555555")

    logger.debug(
        f"tooltip_fg: {tooltip_fg}, tooltip_bg: {tooltip_bg}, border_color: {border_color}"
    )

    """
    Generates a QSS template string for tab close buttons, tab bars, and dock widgets.
    This template uses placeholders (e.g., @placeholder_color) that should be
    replaced by actual color values by the ThemeManager.
    """
    qss_parts = []

    # Пример использования полученных цветов в QSS
    example_tooltip_qss = f"""
    QToolTip {{
        color: {tooltip_fg};
        background-color: {tooltip_bg};
        border: 1px solid {border_color};
        padding: 2px;
    }}
    """
    qss_parts.append(example_tooltip_qss)
    logger.debug("Added tooltip QSS template")

    # 1. Tab Close Button Icon and Style
    try:
        # Пути к иконкам относительно корня проекта
        # Пытаемся найти иконку закрытия в нескольких возможных местах
        possible_icon_paths = [
            os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "assets",
                "icons",
                "close.svg",
            ),
            os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "assets",
                "icons",
                "x.svg",
            ),
            os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "assets",
                "close.svg",
            ),
        ]

        close_icon_path = None
        for path in possible_icon_paths:
            if os.path.exists(path):
                close_icon_path = path
                break

        if close_icon_path:
            logger.info(f"Найдена иконка закрытия вкладки: {close_icon_path}")
            with open(close_icon_path, "r", encoding="utf-8") as icon_file:
                svg_content = icon_file.read()
                svg_bytes = svg_content.encode("utf-8")
                svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
                tab_close_style_template = f"""
                QTabBar::close-button {{
                    image: url(data:image/svg+xml;base64,{svg_base64});
                    subcontrol-position: right;
                    width: 16px;
                    height: 16px;
                    padding: 2px;
                    border-radius: @tab_close_button_border_radius;
                }}
                QTabBar::close-button:hover {{
                    background-color: @tab_close_button_hover_bg_color;
                }}
                """
                qss_parts.append(tab_close_style_template)
        else:
            logger.warning(
                "Иконка закрытия вкладки не найдена ни в одном из ожидаемых мест"
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке иконки закрытия вкладки: {e}")

    # 2. Generic Tab and Dock Styles Template
    # These placeholders should be defined in the theme JSON files
    generic_styles_template = """
    QTabWidget::tab-bar {
        alignment: @tab_bar_alignment;
    }
    QTabBar::tab {
        background-color: @tab_background_color;
        border: 1px solid @tab_border_color;
        border-bottom-color: @tab_border_bottom_color;
        border-top-left-radius: @tab_border_top_left_radius;
        border-top-right-radius: @tab_border_top_right_radius;
        min-width: @tab_min_width;
        padding: @tab_padding;
        margin-right: @tab_margin_right;
        color: @tab_text_color;
    }
    QTabBar::tab:selected {
        background-color: @tab_selected_background_color;
        border-bottom-color: @tab_selected_border_bottom_color;
        font-weight: @tab_selected_font_weight;
        color: @tab_selected_text_color;
    }
    QTabBar::tab:hover:!selected {
        background-color: @tab_hover_background_color;
    }

    /* TerminalDock specific tab styles */
    #TerminalDock QTabBar::tab {
        background-color: @terminal_tab_background_color;
        border: 1px solid @terminal_tab_border_color;
        color: @terminal_tab_text_color;
    }
    #TerminalDock QTabBar::tab:selected {
        background-color: @terminal_tab_selected_background_color;
        border-bottom-color: @terminal_tab_selected_border_bottom_color;
        color: @terminal_tab_selected_text_color;
    }
    #TerminalDock QTabBar::tab:hover:!selected {
        background-color: @terminal_tab_hover_background_color;
    }

    /* BrowserDock specific tab styles */
    #BrowserDock QTabBar::tab {
        background-color: @browser_tab_background_color;
        border: 1px solid @browser_tab_border_color;
        color: @browser_tab_text_color;
    }
    #BrowserDock QTabBar::tab:selected {
        background-color: @browser_tab_selected_background_color;
        border-bottom-color: @browser_tab_selected_border_bottom_color;
        color: @browser_tab_selected_text_color;
    }
    #BrowserDock QTabBar::tab:hover:!selected {
        background-color: @browser_tab_hover_background_color;
    }

    /* DockWidget Styles */
    QDockWidget {
    }
    QDockWidget::title {
        text-align: @dock_title_text_align;
        background: @dock_title_background_color;
        padding-left: @dock_title_padding_left;
        height: @dock_title_height;
        color: @dock_title_text_color;
    }
    QDockWidget::close-button, QDockWidget::float-button {
        border: @dock_title_button_border;
        border-radius: @dock_title_button_border_radius;
        background: @dock_title_button_background_color;
    }
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {
        background: @dock_title_button_hover_background_color;
    }
    QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
        background: @dock_title_button_pressed_background_color;
    }

    /* Custom DockTitleBar (if used) */
    DockTitleBar {
        background-color: @custom_dock_title_bar_background_color;
        border-bottom: 1px solid @custom_dock_title_bar_border_bottom_color;
    }
    DockTitleBar QLabel {
        font-weight: @custom_dock_title_bar_label_font_weight;
        color: @custom_dock_title_bar_label_text_color;
    }
    DockTitleBar QPushButton {
        background-color: @custom_dock_title_bar_button_background_color;
        border: @custom_dock_title_bar_button_border;
        border-radius: @custom_dock_title_bar_button_border_radius;
        font-size: @custom_dock_title_bar_button_font_size;
        color: @custom_dock_title_bar_button_text_color;
    }
    DockTitleBar QPushButton:hover {
        background-color: @custom_dock_title_bar_button_hover_background_color;
    }
    DockTitleBar QPushButton[text=\"❌\"]:hover {
        background-color: @custom_dock_title_bar_close_button_hover_background_color;
    }
    """
    qss_parts.append(generic_styles_template)

    final_generated_qss = "\n".join(qss_parts)
    logger.debug("Сгенерирован дополнительный QSS шаблон для UI")
    return final_generated_qss


def on_theme_changed_event(main_window, theme_name: str):
    """
    Handles the theme change event.
    The actual application of styles is now done by ThemeManager.
    This function is responsible for any UI updates needed in MainWindow
    after a theme change, like updating menus.
    """
    logger.debug(f"Обработка события смены темы: '{theme_name}'")
    try:
        # Импортируем ThemeManager при необходимости
        from app.utils.theme_manager import ThemeManager

        # Убедимся, что тема действительно применена
        theme_manager = ThemeManager.instance()
        if theme_manager:
            logger.debug(f"Убеждаемся, что тема '{theme_name}' применена")
            # Это не вызовет повторную отправку сигнала, если тема уже активна
            theme_manager.switch_visual_theme(theme_name)

        # Update parts of MainWindow UI that might need explicit refresh or state change
        if hasattr(main_window, "_update_themes_menu") and callable(
            main_window._update_themes_menu
        ):
            logger.debug("Вызов main_window._update_themes_menu()")
            main_window._update_themes_menu()
        else:
            logger.warning(
                "Метод _update_themes_menu не найден в main_window или не вызываемый"
            )

        # Force a repaint/update of the main window
        main_window.update()

        logger.info(f"Успешно обработано обновление UI для темы '{theme_name}'")
    except Exception as e:
        logger.error(f"Ошибка обработки события смены темы: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


# Old load_styles function is removed as its responsibilities are now split:
# 1. Template generation: get_additional_qss_template()
# 2. Style application: ThemeManager._apply_visual_theme()
# 3. MainWindow UI updates: on_theme_changed_event()
