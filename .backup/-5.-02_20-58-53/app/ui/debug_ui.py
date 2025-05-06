import os
import logging
import sys
from PySide6.QtCore import QObject, Signal, QMetaObject
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QMainWindow, QMenu
from PySide6.QtGui import QFont
from app.ui.i18n.translator import tr

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ui_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('UI_Diagnostics')

class UIDiagnostics:
    """Класс для диагностики проблем пользовательского интерфейса."""

    @staticmethod
    def check_signal_connections(signal_instance):
        """Проверяет количество подключений к сигналу."""
        try:
            # В некоторых версиях PySide6 метод receivers() может быть недоступен
            # Поэтому используем более безопасный подход
            if hasattr(signal_instance, 'callbacks'):
                conn_count = len(signal_instance.callbacks)
                logger.info(f"Сигнал {signal_instance} имеет {conn_count} подключений")
                return conn_count
            else:
                # Альтернативный способ - просто проверяем, что сигнал существует
                logger.info(f"Объект {signal_instance} определен как сигнал")
                return "неизвестно - метод receivers() недоступен"
        except Exception as e:
            logger.error(f"Ошибка при проверке подключений сигнала: {e}")
            return -1

    @staticmethod
    def diagnose_translator():
        """Диагностирует состояние менеджера переводов."""
        try:
            from app.ui.i18n.translator import JsonTranslationManager
            translator = JsonTranslationManager.instance()

            # Получаем информацию о текущем языке и доступных переводах
            current_lang = translator.get_current_language()
            available_langs = translator.get_available_languages()

            # Проверяем количество подключений к сигналу смены языка
            connections = UIDiagnostics.check_signal_connections(translator.languageChanged)

            # Проверяем наличие файлов переводов
            i18n_dir = os.path.dirname(os.path.abspath(JsonTranslationManager.__module__))
            translation_files = []

            if os.path.exists(os.path.join(i18n_dir, "en.json")):
                translation_files.append("en.json")
            if os.path.exists(os.path.join(i18n_dir, "ru.json")):
                translation_files.append("ru.json")

            themes_dir = os.path.join(os.path.dirname(i18n_dir), "themes")
            if os.path.exists(os.path.join(themes_dir, "EN-translations.json")):
                translation_files.append("themes/EN-translations.json")
            if os.path.exists(os.path.join(themes_dir, "RU-translations.json")):
                translation_files.append("themes/RU-translations.json")

            # Тестируем работу перевода на нескольких ключах
            test_keys = ["menu.file", "menu.edit", "menu.view", "menu.help", "dock.terminal", "dock.chat"]
            translations = {}
            for key in test_keys:
                translations[key] = translator.get_translation(key, f"[MISSING: {key}]")

            return {
                "current_language": current_lang,
                "available_languages": available_langs,
                "signal_connections": connections,
                "translation_files": translation_files,
                "test_translations": translations
            }
        except Exception as e:
            logger.error(f"Ошибка при диагностике переводчика: {e}")
            return {"error": str(e)}

    @staticmethod
    def diagnose_menu_manager(main_window):
        """Диагностирует состояние менеджера меню."""
        try:
            if not hasattr(main_window, 'menu_manager'):
                return {"error": "Менеджер меню не инициализирован"}

            menu_manager = main_window.menu_manager

            # Проверяем подключения сигналов
            theme_connections = UIDiagnostics.check_signal_connections(menu_manager.theme_changed)
            lang_connections = UIDiagnostics.check_signal_connections(menu_manager.language_changed)

            # Проверяем наличие меню и действий
            menus = {
                "file_menu": hasattr(menu_manager, 'file_menu'),
                "edit_menu": hasattr(menu_manager, 'edit_menu'),
                "view_menu": hasattr(menu_manager, 'view_menu'),
                "tools_menu": hasattr(menu_manager, 'tools_menu'),
                "help_menu": hasattr(menu_manager, 'help_menu'),
                "theme_menu": hasattr(menu_manager, 'theme_menu'),
                "language_menu": hasattr(menu_manager, 'language_menu')
            }

            # Проверяем актуальность переводов
            from app.ui.i18n.translator import tr
            menu_texts = {
                "file_menu": menu_manager.file_menu.title() if hasattr(menu_manager, 'file_menu') else None,
                "expected_file_menu": tr("menu.file", "File"),
                "view_menu": menu_manager.view_menu.title() if hasattr(menu_manager, 'view_menu') else None,
                "expected_view_menu": tr("menu.view", "View"),
                "language_menu": menu_manager.language_menu.title() if hasattr(menu_manager, 'language_menu') else None,
                "expected_language_menu": tr("menu.language", "Language")
            }

            return {
                "theme_signal_connections": theme_connections,
                "language_signal_connections": lang_connections,
                "menus_exist": menus,
                "menu_texts": menu_texts
            }
        except Exception as e:
            logger.error(f"Ошибка при диагностике менеджера меню: {e}")
            return {"error": str(e)}

    @staticmethod
    def fix_language_connections(main_window):
        """Исправляет подключения сигналов смены языка."""
        try:
            # Переподключаем сигнал смены языка
            from app.ui.i18n.translator import JsonTranslationManager

            translator = JsonTranslationManager.instance()

            # Отключаем все текущие соединения для чистоты эксперимента
            try:
                translator.languageChanged.disconnect()
                logger.info("Отключены все подключения к сигналу languageChanged")
            except Exception:
                logger.info("Нет активных подключений к сигналу languageChanged")

            # Подключаем сигнал к обработчику в главном окне
            translator.languageChanged.connect(main_window._on_language_changed_event)
            logger.info("Переподключен сигнал languageChanged к _on_language_changed_event")

            # Если у нас есть менеджер меню, соединяем с ним тоже
            if hasattr(main_window, 'menu_manager'):
                translator.languageChanged.connect(main_window.menu_manager.update_translations)
                logger.info("Переподключен сигнал languageChanged к menu_manager.update_translations")

            # Проверяем количество подключений после исправлений
            connections = UIDiagnostics.check_signal_connections(translator.languageChanged)

            return {
                "status": "success",
                "connections_after_fix": connections
            }
        except Exception as e:
            logger.error(f"Ошибка при исправлении подключений: {e}")
            return {"error": str(e)}

class UI_DiagnosticsDialog(QDialog):
    """Диалог для отображения результатов диагностики."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("debug.ui_diagnostics", "UI Diagnostics"))
        self.setMinimumSize(600, 400)

        # Сохраняем ссылку на главное окно
        self.main_window = parent
        if not self.main_window:
            # Если родитель не указан, пытаемся найти главное окно среди существующих виджетов
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    self.main_window = widget
                    break

        layout = QVBoxLayout(self)

        # Добавляем метку для результатов
        results_label = QLabel(tr("debug.results_label", "UI Diagnostics Results:"))
        layout.addWidget(results_label)

        # Текстовое поле для вывода результатов
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Кнопка для исправления соединений сигналов
        button_layout = QHBoxLayout()
        self.run_diagnostics_button = QPushButton(tr("debug.run_diagnostics", "Run Diagnostics"))
        self.run_diagnostics_button.clicked.connect(self.run_diagnostics)

        self.fix_connections_button = QPushButton(tr("debug.fix_connections", "Fix Signal Connections"))
        self.fix_connections_button.clicked.connect(self.fix_connections)

        close_button = QPushButton(tr("dialogs.close", "Close"))
        close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.run_diagnostics_button)
        button_layout.addWidget(self.fix_connections_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Запускаем диагностику при создании диалога
        QApplication.processEvents()
        self.run_diagnostics()

    def run_diagnostics(self):
        """Запускает диагностику UI и отображает результаты."""
        diagnostics_output = tr("debug.header", "==== GOPI-AI UI DIAGNOSTICS ====\n")

        # Проверяем переводчик
        diagnostics_output += f"\n{tr('debug.translator_section', '=== TRANSLATOR ===')}:\n"
        try:
            from app.ui.i18n.translator import check_translator
            translator_check = check_translator()
            diagnostics_output += translator_check
        except Exception as e:
            diagnostics_output += f"Ошибка при проверке переводчика: {str(e)}\n"

        # Проверяем соединения сигналов меню
        diagnostics_output += f"\n{tr('debug.menu_manager_section', '=== MENU MANAGER ===')}:\n"
        try:
            # Используем сохраненную ссылку на главное окно
            if self.main_window:
                menu_connections = 0
                for menu in self.main_window.menuBar().findChildren(QMenu):
                    for action in menu.actions():
                        if action.isEnabled() and action.text() and action.isCheckable() == False:
                            if hasattr(action, 'triggered'):
                                connections = UIDiagnostics.check_signal_connections(action.triggered)
                                if connections > 0:
                                    menu_connections += 1
                                    diagnostics_output += f"✓ Меню '{action.text()}' имеет {connections} подключение(й).\n"
                                else:
                                    diagnostics_output += f"⚠️ Меню '{action.text()}' не имеет подключений.\n"

                diagnostics_output += f"\nВсего найдено активных подключений меню: {menu_connections}\n"
            else:
                diagnostics_output += tr("debug.main_window_error", "Error: Could not access the main window.")
        except Exception as e:
            diagnostics_output += f"Ошибка при проверке менеджера меню: {str(e)}\n"

        diagnostics_output += tr("debug.footer", "\n==== END OF DIAGNOSTICS ====")

        # Отображаем результаты
        self.results_text.setText(diagnostics_output)

        # Логируем результаты
        logger.debug(diagnostics_output)

    def fix_connections(self):
        """Пытается исправить соединения сигналов меню."""
        fix_output = tr("debug.fix_connections_header", "\n==== FIXING SIGNALS ====")

        try:
            # Используем сохраненную ссылку на главное окно
            if self.main_window:
                # Пытаемся переподключить сигналы для действий меню языка
                from app.ui.i18n.translator import connect_language_actions
                connect_result = connect_language_actions(self.main_window)
                fix_output += f"\n{connect_result}"

                # Предлагаем пользователю проверить работу через переключение языка
                fix_output += tr("debug.try_switch_language", "\nTry switching the language through the menu to test.")
            else:
                fix_output += tr("debug.main_window_error", "Error: Could not access the main window.")
        except Exception as e:
            fix_output += f"\nОшибка при исправлении сигналов: {str(e)}"

        fix_output += f"\n{tr('debug.fix_footer', '==== END OF FIXES ====')}."

        # Добавляем результаты исправления к существующим результатам
        current_text = self.results_text.toPlainText()
        self.results_text.setText(current_text + "\n" + fix_output)

        # Логируем результаты
        logger.debug(fix_output)

def run_ui_diagnostics(main_window):
    """Запускает диалог диагностики UI."""
    dialog = UI_DiagnosticsDialog(main_window)
    dialog.exec()

if __name__ == "__main__":
    # Запуск диагностики как отдельного инструмента
    app = QApplication(sys.argv)
    run_ui_diagnostics(None)
    sys.exit(app.exec())
