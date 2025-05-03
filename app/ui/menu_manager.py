from PySide6.QtWidgets import QMenu, QMenuBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject, Signal

from .i18n.translator import tr
from .icon_manager import get_icon


class MenuManager(QObject):
    """
    Класс для управления меню приложения.
    Обеспечивает централизованное создание и управление меню и действиями.
    """

    # Сигналы
    menu_action_triggered = Signal(str)  # Сигнал с идентификатором действия

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.menus = {}
        self.actions = {}

    def create_menu(self, parent_menu, menu_id, title, icon=None):
        """
        Создает подменю и добавляет его в родительское меню.
        
        Args:
            parent_menu (QMenu): Родительское меню
            menu_id (str): Идентификатор меню
            title (str): Заголовок меню
            icon (QIcon, optional): Иконка для меню
            
        Returns:
            QMenu: Созданное меню
        """
        menu = QMenu(parent_menu)
        menu.setObjectName(menu_id)
        
        if title.startswith("tr:"):
            # Если title начинается с 'tr:', используем функцию перевода
            tr_key = title[3:]
            menu.setTitle(tr(tr_key, tr_key.split('.')[-1]))
        else:
            menu.setTitle(title)
            
        if icon:
            if isinstance(icon, str):
                icon = get_icon(icon)
            menu.setIcon(icon)
            
        parent_menu.addMenu(menu)
        self.menus[menu_id] = menu
        
        return menu

    def create_action(self, action_id, title, shortcut=None, status_tip=None, 
                      icon=None, checkable=False, checked=False):
        """
        Создает QAction с заданными параметрами.
        
        Args:
            action_id (str): Идентификатор действия
            title (str): Заголовок действия
            shortcut (str, optional): Комбинация клавиш
            status_tip (str, optional): Текст подсказки в статусной строке
            icon (QIcon/str, optional): Иконка или имя иконки
            checkable (bool, optional): Может ли действие быть отмечено
            checked (bool, optional): Начальное состояние отметки
            
        Returns:
            QAction: Созданное действие
        """
        # Если icon передан как строка, получаем иконку
        if isinstance(icon, str):
            icon = get_icon(icon)
            
        # Создаем действие
        action = QAction(icon, title, self.parent)
        action.setObjectName(action_id)
        
        # Настраиваем действие
        if shortcut:
            action.setShortcut(shortcut)
        if status_tip:
            action.setStatusTip(status_tip)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
            
        # Подключаем сигнал
        action.triggered.connect(lambda: self._on_action_triggered(action_id))
        
        # Сохраняем действие
        self.actions[action_id] = action
        
        return action

    def add_action_to_menu(self, menu_id, action_id):
        """
        Добавляет существующее действие в меню.
        
        Args:
            menu_id (str): Идентификатор меню
            action_id (str): Идентификатор действия
            
        Returns:
            bool: True если добавление успешно, иначе False
        """
        if menu_id in self.menus and action_id in self.actions:
            self.menus[menu_id].addAction(self.actions[action_id])
            return True
        return False

    def add_separator_to_menu(self, menu_id):
        """
        Добавляет разделитель в меню.
        
        Args:
            menu_id (str): Идентификатор меню
            
        Returns:
            bool: True если добавление успешно, иначе False
        """
        if menu_id in self.menus:
            self.menus[menu_id].addSeparator()
            return True
        return False

    def get_action(self, action_id):
        """
        Возвращает действие по идентификатору.
        
        Args:
            action_id (str): Идентификатор действия
            
        Returns:
            QAction: Действие или None, если не найдено
        """
        return self.actions.get(action_id)

    def get_menu(self, menu_id):
        """
        Возвращает меню по идентификатору.
        
        Args:
            menu_id (str): Идентификатор меню
            
        Returns:
            QMenu: Меню или None, если не найдено
        """
        return self.menus.get(menu_id)

    def _on_action_triggered(self, action_id):
        """
        Обработчик сигнала triggered для действий.
        
        Args:
            action_id (str): Идентификатор действия
        """
        self.menu_action_triggered.emit(action_id)

    def update_translations(self):
        """
        Обновляет переводы для всех меню и действий.
        Должна вызываться при изменении языка.
        """
        # Обновление меню
        for menu_id, menu in self.menus.items():
            title = menu.title()
            if title.startswith("tr:"):
                tr_key = title[3:]
                menu.setTitle(tr(tr_key, tr_key.split('.')[-1]))
                
        # Обновление действий
        for action_id, action in self.actions.items():
            title = action.text()
            if title.startswith("tr:"):
                tr_key = title[3:]
                action.setText(tr(tr_key, tr_key.split('.')[-1]))
                
            status_tip = action.statusTip()
            if status_tip and status_tip.startswith("tr:"):
                tr_key = status_tip[3:]
                action.setStatusTip(tr(tr_key, tr_key.split('.')[-1]))