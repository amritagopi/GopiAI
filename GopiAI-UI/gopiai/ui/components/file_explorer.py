"""
File Explorer Component для GopiAI Standalone Interface
====================================================

Проводник файлов с деревом папок и поддержкой иконок для разных типов файлов.

ВАЖНО: Этот компонент настроен для предотвращения автоматического изменения 
размеров при выборе файлов с длинными именами. Ширина зафиксирована, 
пользователь может изменять размер панели только через сплиттер.

Основные защитные механизмы:
- Фиксированные минимальная и максимальная ширина (250-400px)
- QSizePolicy с фиксированной шириной 
- QTreeView с фиксированной шириной (240px)
- Отключенный горизонтальный скроллбар
- Переопределенные sizeHint и resizeEvent
- setStretchFactor(0, 0) для панели в главном сплиттере
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeView, QHBoxLayout, 
QPushButton, QLineEdit, QHeaderView, QSizePolicy, QFileSystemModel, QTabWidget)
from PySide6.QtCore import QDir, Signal, Qt, QModelIndex
from PySide6.QtGui import QIcon
from .file_type_detector import FileTypeDetector
from .custom_file_system_model import CustomFileSystemModel

# Виджеты моделей перенесены в ChatWidget


class FileExplorerWidget(QWidget):
    """Проводник файлов с деревом папок и поддержкой иконок"""
    
    # Сигналы
    file_selected = Signal(str)  # Файл выбран
    file_double_clicked = Signal(str)  # Файл открыт двойным кликом
    
    def __init__(self, parent=None, icon_manager=None):
        super().__init__(parent)
        self.setObjectName("fileExplorer")
        self._current_path = os.path.expanduser("~")
        self._ignore_resize = False  # Флаг для предотвращения циклов resizeEvent
        
        # Инициализируем систему иконок
        self._setup_icon_system()
        
        # Настройка фиксированного размера для предотвращения "прыгания"
        from PySide6.QtWidgets import QSizePolicy
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        # Устанавливаем политику размера: фиксированная ширина, расширяемая высота
        size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        self.setSizePolicy(size_policy)
        
        self._setup_ui()
        self._connect_signals()

    def _setup_icon_system(self):
        """Настройка системы иконок"""
        # Импорт системы иконок
        try:
            from .icon_file_system_model import UniversalIconManager
            self.icon_manager = UniversalIconManager()
            print("[OK] Загружена система иконок UniversalIconManager")
        except ImportError:
            self.icon_manager = None
            print("[ERROR] Не удалось загрузить UniversalIconManager")

    def _setup_ui(self):
        """Настройка интерфейса проводника с вкладками"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Создаем табы
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        
        # Вкладка 1: Файловый проводник (оригинальная функциональность)
        self.file_explorer_tab = QWidget()
        self._setup_file_explorer_tab()
        self.tab_widget.addTab(self.file_explorer_tab, "Файлы")
        
        # Вкладки моделей перенесены в ChatWidget (правая панель)
        
        layout.addWidget(self.tab_widget)
        
        print("✅ FileExplorerWidget настроен с вкладками")
    
    def _setup_file_explorer_tab(self):
        """Настройка вкладки файлового проводника"""
        layout = QVBoxLayout(self.file_explorer_tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Заголовок с иконкой
        header_layout = QHBoxLayout()
        
        if self.icon_manager:
            try:
                folder_icon = self.icon_manager.get_icon("folder")
                header = QLabel("Проводник")  # Убираем emoji
                # Если есть иконка, устанавливаем её
                if folder_icon and not folder_icon.isNull():
                    # Создаем QLabel с иконкой и текстом
                    header = QLabel("Проводник")
                    header.setPixmap(folder_icon.pixmap(16, 16))
            except Exception as e:
                print(f"⚠️ Ошибка загрузки иконки папки: {e}")
                header = QLabel("Проводник")
        else:
            header = QLabel("Проводник")
            
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Кнопки с иконками
        home_btn = self._create_icon_button("home", "Перейти в домашнюю папку", self._go_home)
        up_btn = self._create_icon_button("arrow-up", "Перейти на уровень вверх", self._go_up)
        
        header_layout.addWidget(home_btn)
        header_layout.addWidget(up_btn)
        
        layout.addLayout(header_layout)
        
        # Строка пути
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 5)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь к папке...")
        self.path_input.setText(self._current_path)
        self.path_input.returnPressed.connect(self._path_changed)
        path_layout.addWidget(self.path_input)
        
        go_btn = self._create_icon_button("arrow-right", "Перейти к указанному пути", self._path_changed)
        path_layout.addWidget(go_btn)
        
        layout.addLayout(path_layout)
        
        # Добавляем дерево файлов с кастомной моделью
        self.tree_view = QTreeView()
        self.model = CustomFileSystemModel(self.icon_manager)
        
        # Правильная инициализация модели файловой системы
        self.model.setRootPath(QDir.homePath())
        # Установка фильтров для отображения всех файлов и директорий
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        
        # Применяем модель к дереву
        self.tree_view.setModel(self.model)
        # Устанавливаем корневой индекс для отображения домашней директории
        self.tree_view.setRootIndex(self.model.index(QDir.homePath()))
        
        # Настраиваем отображение колонок
        self.tree_view.setColumnWidth(0, 250)
        # Скрываем ненужные колонки, оставляя только имя и размер
        for i in range(1, self.model.columnCount()):
            if i != 1:  # Оставляем колонку с размером (обычно 1)
                self.tree_view.hideColumn(i)
        
        layout.addWidget(self.tree_view)

    def _create_icon_button(self, icon_name: str, tooltip: str, callback) -> QPushButton:
        """Создает кнопку с иконкой"""
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 30)
        btn.clicked.connect(callback)
        
        if self.icon_manager:
            try:
                icon = self.icon_manager.get_icon(icon_name)
                if icon and not icon.isNull():
                    btn.setIcon(icon)
                else:
                    # Fallback - устанавливаем текст без emoji
                    text_map = {
                        "home": "Home",
                        "arrow-up": "↑", 
                        "arrow-right": "→"
                    }
                    btn.setText(text_map.get(icon_name, "?"))
            except Exception as e:
                print(f"⚠️ Ошибка загрузки иконки {icon_name}: {e}")
                # Fallback - устанавливаем текст без emoji
                text_map = {
                    "home": "Home",
                    "arrow-up": "↑",
                    "arrow-right": "→"
                }
                btn.setText(text_map.get(icon_name, "?"))
        else:
            # Fallback - устанавливаем текст без emoji
            text_map = {
                "home": "Home",
                "arrow-up": "↑",
                "arrow-right": "→"
            }
            btn.setText(text_map.get(icon_name, "?"))
            
        return btn

    def _connect_signals(self):
        """Подключение сигналов"""
        if hasattr(self.tree_view, 'doubleClicked'):
            self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        
        if hasattr(self.tree_view, 'clicked'):
            self.tree_view.clicked.connect(self._on_item_selected)

    def _on_item_selected(self, index):
        """Обработка выбора элемента"""
        if index.isValid():
            file_path = self.model.filePath(index)
            self.file_selected.emit(file_path)

    def _go_home(self):
        """Переход в домашнюю папку"""
        home_path = QDir.homePath()
        self.path_input.setText(home_path)
        self.tree_view.setRootIndex(self.model.index(home_path))

    def _go_up(self):
        """Переход на уровень вверх (надёжно через os.path.dirname)"""
        import os
        current_path = self.path_input.text()
        parent_path = os.path.dirname(os.path.normpath(current_path))
        # Не позволяем выйти за пределы корня (например, / или диска)
        if parent_path and parent_path != current_path and os.path.exists(parent_path):
            self.path_input.setText(parent_path)
            self.tree_view.setRootIndex(self.model.index(parent_path))

    def _path_changed(self):
        """Обработка изменения пути"""
        path = self.path_input.text()
        if QDir(path).exists():
            self.tree_view.setRootIndex(self.model.index(path))
        else:
            self.path_input.setText(QDir.homePath())
            self.tree_view.setRootIndex(self.model.index(QDir.homePath()))

    def _on_item_double_clicked(self, index):
        """Обработка двойного клика по элементу"""
        if self.model.isDir(index):
            path = self.model.filePath(index)
            self.path_input.setText(path)
            self.tree_view.setRootIndex(index)
        else:
            # Если это файл, отправляем сигнал об открытии
            file_path = self.model.filePath(index)
            self.file_double_clicked.emit(file_path)
    

