"""
GopiAI Icon System - Автоматическая система иконок
================================================

Автоматическая система загрузки и применения иконок для всех UI компонентов.
Поддерживает Lucide SVG иконки с автоматическим маппингом названий.

Автор: Crazy Coder  
Версия: 1.0.0
"""
from typing import Optional
from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMenuBar, QWidget

# Импортируем универсальный менеджер иконок из компонентов
try:
    from ..components.icon_file_system_model import UniversalIconManager, get_icon
    icon_manager = UniversalIconManager.instance()
    print(f"✅ Инициализирован универсальный менеджер иконок")
except ImportError as e:
    print(f"⚠️ Не удалось импортировать UniversalIconManager: {e}")
    icon_manager = None

class AutoIconMapper:
    """Автоматический маппер названий действий в иконки"""
    
    # Автоматический маппинг названий действий в Lucide иконки
    AUTO_ICON_MAP = {
        # Файловые операции
        'new': 'file-plus',
        'new_action': 'file-plus', 
        'create': 'file-plus',
        'open': 'folder-open',
        'open_action': 'folder-open',
        'save': 'save',
        'save_action': 'save',
        'save_as': 'save',
        'save_as_action': 'save',
        'close': 'x',
        'close_action': 'x',
        'exit': 'log-out',
        'exit_action': 'log-out',
        'quit': 'log-out',
        'quit_action': 'log-out',
          # Редактирование
        'edit': 'edit',
        'edit_action': 'edit',
        'undo': 'undo',
        'undo_action': 'undo',
        'redo': 'redo',
        'redo_action': 'redo',
        'cut': 'scissors',
        'cut_action': 'scissors',
        'copy': 'copy',
        'copy_action': 'copy',
        'paste': 'clipboard',
        'paste_action': 'clipboard',
        'delete': 'trash-2',
        'delete_action': 'trash-2',
        'select_all': 'text-select',
        'selectAll': 'text-select',
        'select_all_action': 'text-select',
        'find': 'search',
        'find_action': 'search',
        'replace': 'replace',
        'replace_action': 'replace',
          # Вид
        'view': 'eye',
        'view_action': 'eye',
        'project_explorer_action': 'folder-open',
        'chat_action': 'message-circle',
        'browser_action': 'globe',
        'terminal_action': 'terminal',
        'text_editor_action': 'file-text',
        'zoom_in': 'zoom-in',
        'zoom_in_action': 'zoom-in',
        'zoom_out': 'zoom-out',
        'zoom_out_action': 'zoom-out',
        'fullscreen': 'maximize',
        'fullscreen_action': 'maximize',
        'normal_size': 'minimize',
        'normal_size_action': 'minimize',
        'show': 'eye',
        'show_action': 'eye',
        'hide': 'eye-off',
        'hide_action': 'eye-off',
        
        # Инструменты
        'tools': 'tool',
        'tools_action': 'tool',
        'settings': 'settings',
        'settings_action': 'settings',
        'preferences': 'settings',
        'preferences_action': 'settings',
        'options': 'settings',
        'options_action': 'settings',
        
        # Помощь
        'help': 'help-circle',
        'help_action': 'help-circle',
        'about': 'info',
        'about_action': 'info',
        'documentation': 'book-open',
        'documentation_action': 'book-open',
        
        # Файловый браузер
        'refresh': 'refresh-cw',
        'refresh_action': 'refresh-cw',
        'reload': 'refresh-cw',
        'reload_action': 'refresh-cw',
        'up': 'arrow-up',
        'up_action': 'arrow-up',
        'back': 'arrow-left',
        'back_action': 'arrow-left',
        'forward': 'arrow-right',
        'forward_action': 'arrow-right',
        'home': 'home',
        'home_action': 'home',
        
        # Разное
        'add': 'plus',
        'add_action': 'plus',
        'remove': 'minus',
        'remove_action': 'minus',
        'play': 'play',
        'play_action': 'play',
        'pause': 'pause',
        'pause_action': 'pause',
        'stop': 'square',
        'stop_action': 'square',
        'download': 'download',
        'download_action': 'download',
        'upload': 'upload',
        'upload_action': 'upload',
        'chat': 'message-square',
        'chat_action': 'message-square',
        'console': 'terminal',
        'console_action': 'terminal',
        'terminal': 'terminal',
        'terminal_action': 'terminal',
        'run': 'play',
        'run_action': 'play',
        'debug': 'bug',
        'debug_action': 'bug',
        'clean': 'trash-2',
        'clean_action': 'trash-2',
        'build': 'hammer',
        'build_action': 'hammer',
        'folder': 'folder',
        'folder_action': 'folder',
        'file': 'file',
        'file_action': 'file',
        
        # UI компоненты
        'titlebar': 'layout',
        'statusbar': 'layout',
        'menubar': 'layout',
        'toolbar': 'layout',
        'sidebar': 'layout',
        'dock': 'layout',
        'panel': 'layout',
        'tab': 'layout',
    }
    
    def __init__(self):
        """Инициализация маппера"""
        # Кеш для сопоставления названий
        self.name_cache = {}
        
    def get_icon_name(self, action_name: str) -> str:
        """Получить имя иконки по названию действия"""
        # Проверяем кеш
        if action_name in self.name_cache:
            return self.name_cache[action_name]
        
        # Проверяем наличие соответствия в маппинге
        if action_name in self.AUTO_ICON_MAP:
            icon_name = self.AUTO_ICON_MAP[action_name]
            self.name_cache[action_name] = icon_name
            return icon_name
        
        # Если точного соответствия нет, пытаемся найти по частям имени
        for key, value in self.AUTO_ICON_MAP.items():
            if key in action_name.lower():
                self.name_cache[action_name] = value
                return value
        
        # Если соответствие не найдено, используем само имя действия
        self.name_cache[action_name] = action_name
        return action_name


class AutoIconSystem:
    """Автоматическая система иконок для меню и действий"""
    
    def __init__(self, provided_icon_manager=None):
        """
        Инициализация системы иконок.
        
        Args:
            provided_icon_manager: Опционально, предоставленный icon_manager
        """
        if provided_icon_manager is None:
            # Используем глобальный icon_manager из модуля
            global icon_manager
            if icon_manager is None:
                # Если глобальный тоже не определен, пробуем импортировать UniversalIconManager
                try:
                    from ..components.icon_file_system_model import UniversalIconManager
                    self.icon_manager = UniversalIconManager.instance()
                    print("✅ AutoIconSystem использует UniversalIconManager")
                except ImportError:
                    print("⚠️ Не удалось загрузить UniversalIconManager, иконки не будут работать")
                    self.icon_manager = None
            else:
                self.icon_manager = icon_manager
        else:
            self.icon_manager = provided_icon_manager
            
        self.mapper = AutoIconMapper()
        self.default_size = QSize(24, 24)
        
    def apply_icons_to_menu(self, menu_bar: QMenuBar, icon_size: Optional[QSize] = None) -> int:
        """Автоматически применить иконки ко всем действиям в меню"""
        if icon_size is None:
            icon_size = self.default_size
            
        # Если icon_manager недоступен, ничего не делаем
        if self.icon_manager is None:
            print("⚠️ icon_manager недоступен, пропускаем применение иконок к меню")
            return 0
            
        applied_count = 0
        
        # Проходим по всем действиям в меню
        for action in menu_bar.findChildren(QAction):
            if action.objectName():  # Если у действия есть имя
                try:
                    icon_name = self.mapper.get_icon_name(action.objectName())
                    icon = self.icon_manager.get_icon(icon_name)
                    
                    if not icon.isNull():
                        action.setIcon(icon)
                        action.setIconVisibleInMenu(True)
                        applied_count += 1
                        print(f"✓ Автоиконка: {action.objectName()} -> {icon_name}")
                except Exception as e:
                    print(f"⚠️ Ошибка применения иконки к {action.objectName()}: {e}")
        
        # Принудительное обновление
        menu_bar.update()
        
        # Отложенное обновление
        QTimer.singleShot(100, lambda: menu_bar.repaint())
        print(f"🎨 Автоматически применено {applied_count} иконок к меню")
        return applied_count
        
    def apply_icons_to_widget(self, widget: QWidget, icon_size: Optional[QSize] = None) -> int:
        """Автоматически применить иконки ко всем действиям в виджете"""
        if icon_size is None:
            icon_size = self.default_size
            
        # Если icon_manager недоступен, ничего не делаем
        if self.icon_manager is None:
            print("⚠️ icon_manager недоступен, пропускаем применение иконок к виджету")
            return 0
            
        applied_count = 0
        
        # Находим все действия в виджете
        for action in widget.findChildren(QAction):
            if action.objectName():
                try:
                    icon_name = self.mapper.get_icon_name(action.objectName())
                    icon = self.icon_manager.get_icon(icon_name)
                    
                    if not icon.isNull():
                        action.setIcon(icon)
                        applied_count += 1
                        print(f"✓ Автоиконка виджета: {action.objectName()} -> {icon_name}")
                except Exception as e:
                    print(f"⚠️ Ошибка применения иконки к {action.objectName()}: {e}")
        
        widget.update()
        print(f"🎨 Автоматически применено {applied_count} иконок к виджету")
        return applied_count
        
    def get_icon_for_action_name(self, action_name: str, icon_size: Optional[QSize] = None) -> QIcon:
        """Получить иконку для названия действия"""
        icon_name = self.mapper.get_icon_name(action_name)
        
        if self.icon_manager is None:
            # Возвращаем пустую иконку если icon_manager недоступен
            print(f"⚠️ icon_manager недоступен, возвращаем пустую иконку для {action_name}")
            return QIcon()
        
        return self.icon_manager.get_icon(icon_name)
