"""
Виджет визуализации дерева мыслей для Reasoning Agent

Предоставляет графическое отображение дерева мыслей с возможностью
навигации, фильтрации и взаимодействия с узлами мыслей.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction, QBrush, QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QToolBar,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.agent.thought_tree import ThoughtNode, ThoughtTree
from app.logger import logger
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon


class ThoughtTreeItem(QTreeWidgetItem):
    """
    Элемент дерева для отображения одного узла в дереве мыслей.
    """

    def __init__(
        self,
        node: ThoughtNode,
        is_current: bool = False,
        is_alternative: bool = False,
        parent=None,
    ):
        """
        Инициализирует элемент дерева.

        Args:
            node: Узел дерева мыслей
            is_current: Является ли этот узел текущим активным узлом
            is_alternative: Является ли этот узел альтернативным путем
            parent: Родительский элемент дерева
        """
        super().__init__(parent)

        self.node = node
        self.node_id = node.node_id
        self.is_current = is_current
        self.is_alternative = is_alternative

        # Отображаемый текст
        content = node.content
        if len(content) > 60:
            content = content[:57] + "..."

        # Удаляем переносы строк
        content = content.replace("\n", " ")

        self.setText(0, content)

        # Устанавливаем тип узла как дополнительную информацию
        self.setText(1, node.node_type)

        # Устанавливаем ID узла как скрытую информацию
        self.setData(0, Qt.UserRole, node.node_id)

        # Форматирование для различных типов узлов
        self._apply_formatting()

    def _apply_formatting(self):
        """Применяет форматирование в зависимости от типа узла."""
        node_type = self.node.node_type.lower()

        # Базовый шрифт
        font = QFont()

        # Цвет текста и фона
        text_color = QColor("#000000")  # Черный по умолчанию
        background = None

        # Форматирование по типу узла
        if node_type == "root":
            font.setBold(True)
            font.setPointSize(10)
        elif node_type == "decision_point":
            font.setBold(True)
            text_color = QColor("#8B4513")  # SaddleBrown
        elif node_type == "decision_option":
            text_color = QColor("#4169E1")  # RoyalBlue
        elif node_type == "decision_result":
            text_color = QColor("#2E8B57")  # SeaGreen
        elif node_type == "step_reasoning":
            text_color = QColor("#9932CC")  # DarkOrchid
        elif node_type == "conclusion":
            font.setBold(True)
            text_color = QColor("#008000")  # Green
        elif node_type == "question":
            text_color = QColor("#FF4500")  # OrangeRed
            font.setItalic(True)

        # Если это текущий узел
        if self.is_current:
            background = QBrush(QColor("#E6F3FF"))  # Светло-голубой
            font.setBold(True)

        # Если это альтернативный путь
        if self.is_alternative:
            text_color = QColor("#808080")  # Серый
            font.setItalic(True)

        # Применяем форматирование
        self.setFont(0, font)
        self.setForeground(0, text_color)

        if background:
            self.setBackground(0, background)


class ThoughtDetailView(QWidget):
    """
    Виджет для отображения детальной информации об узле дерева мыслей.
    """

    def __init__(self, parent=None):
        """Инициализирует виджет детальной информации."""
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        layout = QVBoxLayout(self)

        # Заголовок
        self.title_label = QLabel(tr("thought_tree.detail.title", "Thought Details"))
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Линия-разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Информация об узле
        info_layout = QVBoxLayout()

        # Тип узла
        type_layout = QHBoxLayout()
        type_label = QLabel(tr("thought_tree.detail.type", "Type:"))
        type_label.setStyleSheet("font-weight: bold;")
        self.type_value = QLabel()
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_value, 1)
        info_layout.addLayout(type_layout)

        # Содержимое узла
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet(
            "background-color: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.1);"
        )
        info_layout.addWidget(self.content_text, 1)

        # Метаданные
        metadata_layout = QVBoxLayout()
        metadata_label = QLabel(tr("thought_tree.detail.metadata", "Metadata:"))
        metadata_label.setStyleSheet("font-weight: bold;")
        metadata_layout.addWidget(metadata_label)

        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(100)
        self.metadata_text.setStyleSheet(
            "background-color: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.1);"
        )
        metadata_layout.addWidget(self.metadata_text)

        info_layout.addLayout(metadata_layout)

        layout.addLayout(info_layout)

    def set_node(self, node: Optional[ThoughtNode]):
        """
        Устанавливает данные узла для отображения.

        Args:
            node: Узел для отображения или None для очистки
        """
        if not node:
            self.title_label.setText(tr("thought_tree.detail.title", "Thought Details"))
            self.type_value.setText("")
            self.content_text.setText("")
            self.metadata_text.setText("")
            return

        # Устанавливаем данные
        self.title_label.setText(
            f"{tr('thought_tree.detail.title', 'Thought Details')}: {node.node_type}"
        )
        self.type_value.setText(node.node_type)
        self.content_text.setText(node.content)

        # Форматируем метаданные как JSON
        if node.metadata:
            import json

            metadata_json = json.dumps(node.metadata, indent=2, ensure_ascii=False)
            self.metadata_text.setText(metadata_json)
        else:
            self.metadata_text.setText(
                tr("thought_tree.detail.no_metadata", "No metadata")
            )

    def clear(self):
        """Очищает данные."""
        self.set_node(None)


class ThoughtTreeWidget(QWidget):
    """
    Виджет для визуализации дерева мыслей.

    Предоставляет графическое представление дерева мыслей
    с возможностью навигации и взаимодействия.
    """

    # Сигналы
    node_selected = Signal(str)  # ID выбранного узла
    tree_saved = Signal(str)  # Путь к сохраненному файлу
    tree_loaded = Signal(str)  # Путь к загруженному файлу

    def __init__(self, parent=None):
        """Инициализирует виджет дерева мыслей."""
        super().__init__(parent)

        self.thought_tree = None
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        layout = QVBoxLayout(self)

        # Панель инструментов
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(20, 20))

        # Действия
        self.expand_all_action = QAction(
            get_icon("expand"), tr("thought_tree.expand_all", "Expand All"), self
        )
        self.collapse_all_action = QAction(
            get_icon("collapse"), tr("thought_tree.collapse_all", "Collapse All"), self
        )
        self.refresh_action = QAction(
            get_icon("refresh"), tr("thought_tree.refresh", "Refresh"), self
        )
        self.save_action = QAction(
            get_icon("save"), tr("thought_tree.save", "Save Tree"), self
        )
        self.load_action = QAction(
            get_icon("open"), tr("thought_tree.load", "Load Tree"), self
        )

        # Добавляем действия на панель
        toolbar.addAction(self.expand_all_action)
        toolbar.addAction(self.collapse_all_action)
        toolbar.addAction(self.refresh_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.load_action)

        # Фильтр по типу узла
        toolbar.addSeparator()
        filter_label = QLabel(tr("thought_tree.filter", "Filter:"))
        toolbar.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem(tr("thought_tree.filter.all", "All Types"), "")
        self.filter_combo.addItem(
            tr("thought_tree.filter.thought", "Thoughts"), "thought"
        )
        self.filter_combo.addItem(
            tr("thought_tree.filter.decision", "Decisions"), "decision_point"
        )
        self.filter_combo.addItem(
            tr("thought_tree.filter.question", "Questions"), "question"
        )
        self.filter_combo.addItem(
            tr("thought_tree.filter.conclusion", "Conclusions"), "conclusion"
        )
        toolbar.addWidget(self.filter_combo)

        layout.addWidget(toolbar)

        # Основной виджет с разделителем
        splitter = QSplitter(Qt.Horizontal)

        # Дерево
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(
            [
                tr("thought_tree.column.content", "Content"),
                tr("thought_tree.column.type", "Type"),
            ]
        )
        self.tree_widget.setColumnWidth(0, 400)
        self.tree_widget.setColumnWidth(1, 100)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setAnimated(True)
        splitter.addWidget(self.tree_widget)

        # Панель деталей
        self.detail_view = ThoughtDetailView()
        splitter.addWidget(self.detail_view)

        # Устанавливаем начальное соотношение (60/40)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter, 1)

        # Подключаем сигналы
        self._connect_signals()

    def _connect_signals(self):
        """Подключает сигналы к слотам."""
        self.tree_widget.itemSelectionChanged.connect(self._on_item_selected)

        self.expand_all_action.triggered.connect(self.tree_widget.expandAll)
        self.collapse_all_action.triggered.connect(self.tree_widget.collapseAll)
        self.refresh_action.triggered.connect(self.refresh_tree)
        self.save_action.triggered.connect(self._save_tree)
        self.load_action.triggered.connect(self._load_tree)

        self.filter_combo.currentIndexChanged.connect(self._apply_filter)

    def set_thought_tree(self, thought_tree: ThoughtTree):
        """
        Устанавливает дерево мыслей для отображения.

        Args:
            thought_tree: Дерево мыслей для визуализации
        """
        self.thought_tree = thought_tree
        self.refresh_tree()

    def refresh_tree(self):
        """Обновляет отображение дерева."""
        self.tree_widget.clear()

        if not self.thought_tree or not self.thought_tree.root:
            return

        # Создаем корневой элемент
        root_item = self._create_tree_item(
            self.thought_tree.root,
            is_current=self.thought_tree.current_node_id
            == self.thought_tree.root.node_id,
        )

        self.tree_widget.addTopLevelItem(root_item)

        # Заполняем дерево рекурсивно
        self._populate_children(root_item, self.thought_tree.root.node_id)

        # Разворачиваем корневой элемент и его первый уровень
        root_item.setExpanded(True)

        # Выделяем текущий узел, если есть
        if self.thought_tree.current_node_id:
            self._select_node_by_id(self.thought_tree.current_node_id)

    def _create_tree_item(
        self, node: ThoughtNode, is_current: bool = False, is_alternative: bool = False
    ) -> ThoughtTreeItem:
        """
        Создает элемент дерева для узла.

        Args:
            node: Узел дерева мыслей
            is_current: Является ли узел текущим
            is_alternative: Является ли узел альтернативным

        Returns:
            Созданный элемент дерева
        """
        return ThoughtTreeItem(node, is_current, is_alternative)

    def _populate_children(self, parent_item: QTreeWidgetItem, parent_id: str):
        """
        Рекурсивно добавляет дочерние элементы в дерево.

        Args:
            parent_item: Родительский элемент дерева
            parent_id: ID родительского узла
        """
        if parent_id not in self.thought_tree.nodes:
            return

        parent_node = self.thought_tree.nodes[parent_id]

        # Добавляем дочерние узлы
        for child_id in parent_node.children:
            if child_id in self.thought_tree.nodes:
                child_node = self.thought_tree.nodes[child_id]

                # Проверяем текущий фильтр
                if self._should_show_node(child_node):
                    child_item = self._create_tree_item(
                        child_node,
                        is_current=self.thought_tree.current_node_id == child_id,
                    )

                    parent_item.addChild(child_item)
                    self._populate_children(child_item, child_id)

        # Добавляем альтернативы
        for alt_id in parent_node.alternatives:
            if alt_id in self.thought_tree.nodes:
                alt_node = self.thought_tree.nodes[alt_id]

                # Проверяем текущий фильтр
                if self._should_show_node(alt_node):
                    alt_item = self._create_tree_item(
                        alt_node,
                        is_current=self.thought_tree.current_node_id == alt_id,
                        is_alternative=True,
                    )

                    parent_item.addChild(alt_item)
                    self._populate_children(alt_item, alt_id)

    def _select_node_by_id(self, node_id: str):
        """
        Выбирает элемент дерева по ID узла.

        Args:
            node_id: ID узла для выбора
        """
        if not node_id:
            return

        def find_item(item, target_id):
            # Проверяем текущий элемент
            if item.data(0, Qt.UserRole) == target_id:
                return item

            # Рекурсивно проверяем дочерние элементы
            for i in range(item.childCount()):
                child = item.child(i)
                result = find_item(child, target_id)
                if result:
                    return result

            return None

        # Ищем элемент в корневых элементах
        for i in range(self.tree_widget.topLevelItemCount()):
            root_item = self.tree_widget.topLevelItem(i)
            item = find_item(root_item, node_id)

            if item:
                self.tree_widget.setCurrentItem(item)
                self.tree_widget.scrollToItem(item)
                break

    def _on_item_selected(self):
        """Обработчик выбора элемента в дереве."""
        selected_items = self.tree_widget.selectedItems()

        if not selected_items:
            self.detail_view.clear()
            return

        # Получаем выбранный элемент
        item = selected_items[0]
        node_id = item.data(0, Qt.UserRole)

        if node_id and self.thought_tree and node_id in self.thought_tree.nodes:
            node = self.thought_tree.nodes[node_id]
            self.detail_view.set_node(node)
            self.node_selected.emit(node_id)
        else:
            self.detail_view.clear()

    def _apply_filter(self):
        """Применяет выбранный фильтр и обновляет дерево."""
        self.refresh_tree()

    def _should_show_node(self, node: ThoughtNode) -> bool:
        """
        Проверяет, должен ли узел отображаться с учетом фильтра.

        Args:
            node: Узел для проверки

        Returns:
            True, если узел должен отображаться
        """
        filter_type = self.filter_combo.currentData()

        # Если фильтр не задан, показываем все
        if not filter_type:
            return True

        # Проверяем по типу
        return node.node_type == filter_type

    def _save_tree(self):
        """Сохраняет дерево мыслей в файл."""
        if not self.thought_tree or not self.thought_tree.root:
            QMessageBox.warning(
                self,
                tr("thought_tree.save.error.title", "Save Error"),
                tr("thought_tree.save.error.empty", "No thought tree to save."),
            )
            return

        # Запрашиваем путь для сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("thought_tree.save.dialog.title", "Save Thought Tree"),
            "",
            tr("thought_tree.save.dialog.filter", "JSON Files (*.json)"),
        )

        if not file_path:
            return

        # Добавляем расширение, если не указано
        if not file_path.lower().endswith(".json"):
            file_path += ".json"

        try:
            # Сериализуем дерево в JSON
            json_data = self.thought_tree.to_json()

            # Сохраняем в файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_data)

            # Уведомляем об успешном сохранении
            QMessageBox.information(
                self,
                tr("thought_tree.save.success.title", "Save Successful"),
                tr(
                    "thought_tree.save.success.message",
                    "Thought tree saved successfully.",
                ),
            )

            # Отправляем сигнал
            self.tree_saved.emit(file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                tr("thought_tree.save.error.title", "Save Error"),
                tr(
                    "thought_tree.save.error.message", "Error saving thought tree: {0}"
                ).format(str(e)),
            )

    def _load_tree(self):
        """Загружает дерево мыслей из файла."""
        # Запрашиваем путь для загрузки
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("thought_tree.load.dialog.title", "Load Thought Tree"),
            "",
            tr("thought_tree.load.dialog.filter", "JSON Files (*.json)"),
        )

        if not file_path:
            return

        try:
            # Загружаем JSON из файла
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = f.read()

            # Создаем дерево из JSON
            new_tree = ThoughtTree.from_json(json_data)

            # Устанавливаем загруженное дерево
            self.thought_tree = new_tree
            self.refresh_tree()

            # Уведомляем об успешной загрузке
            QMessageBox.information(
                self,
                tr("thought_tree.load.success.title", "Load Successful"),
                tr(
                    "thought_tree.load.success.message",
                    "Thought tree loaded successfully.",
                ),
            )

            # Отправляем сигнал
            self.tree_loaded.emit(file_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                tr("thought_tree.load.error.title", "Load Error"),
                tr(
                    "thought_tree.load.error.message", "Error loading thought tree: {0}"
                ).format(str(e)),
            )
