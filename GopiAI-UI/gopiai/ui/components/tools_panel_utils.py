"""
Утилиты для работы с панелью инструментов.
Загружает информацию об инструментах из JSON и предоставляет функции для работы с ними.
"""

import json
import os
import logging
from typing import List, Optional, Tuple
from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QCursor

logger = logging.getLogger(__name__)

# Путь к файлу с инструментами в GopiAI-CrewAI
TOOLS_INFO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))), 'GopiAI-CrewAI', 'config', 'tools_info.json')

# Альтернативный путь (если основной недоступен)
ALT_TOOLS_INFO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), 'config', 'tools_info.json')

class ToolsManager(QObject):
    """Менеджер инструментов для панели инструментов."""
    
    # Сигнал, отправляемый при выборе инструмента
    tool_selected = Signal(str, dict)
    
    def __init__(self):
        """Инициализация менеджера инструментов."""
        super().__init__()
        self.logger = logging.getLogger(__name__ + ".ToolsManager")
        self._tools_info = {}
        self._load_tools_info()
    
    def _load_tools_info(self) -> None:
        """
        Загружает информацию об инструментах из JSON-файла.
        Сначала пытается загрузить из основного пути, затем из альтернативного.
        """
        paths = [TOOLS_INFO_PATH, ALT_TOOLS_INFO_PATH]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self._tools_info = json.load(f)
                        self.logger.info(f"Загружена информация об инструментах из {path}")
                        return
                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке информации об инструментах из {path}: {e}")
        
        self.logger.warning("Не удалось загрузить информацию об инструментах из файлов конфигурации.")
        self._tools_info = {}
    
    def get_tools_categories(self) -> List[str]:
        """
        Возвращает список категорий инструментов.
        
        Returns:
            Список названий категорий
        """
        return list(self._tools_info.keys())
    
    def get_tools_in_category(self, category: str) -> List[Tuple[str, dict]]:
        """
        Возвращает список инструментов в указанной категории.
        
        Args:
            category: Название категории
            
        Returns:
            Список кортежей (id инструмента, информация об инструменте)
        """
        if category not in self._tools_info:
            return []
        
        return [(tool_id, tool_info) for tool_id, tool_info in self._tools_info[category].items()]
    
    def get_all_tools(self) -> List[Tuple[str, str, dict]]:
        """
        Возвращает список всех инструментов.
        
        Returns:
            Список кортежей (категория, id инструмента, информация об инструменте)
        """
        result = []
        
        for category, tools in self._tools_info.items():
            for tool_id, tool_info in tools.items():
                result.append((category, tool_id, tool_info))
        
        return result
    
    def get_tool_info(self, category: str, tool_id: str) -> Optional[dict]:
        """
        Возвращает информацию об указанном инструменте.
        
        Args:
            category: Название категории
            tool_id: Идентификатор инструмента
            
        Returns:
            Информация об инструменте или None, если инструмент не найден
        """
        if category not in self._tools_info or tool_id not in self._tools_info[category]:
            return None
        
        return self._tools_info[category][tool_id]

    def create_tool_card(self, tool_id: str, tool_info: dict) -> QFrame:
        """
        Создает виджет карточки инструмента для отображения в панели.
        
        Args:
            tool_id: Идентификатор инструмента
            tool_info: Информация об инструменте
            
        Returns:
            Виджет карточки инструмента
        """
        card = QFrame()
        card.setObjectName("toolCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # Название инструмента (кнопка)
        name = tool_info.get("name", tool_id)
        name_button = QPushButton(name)
        # PySide6: use QCursor with Qt.CursorShape
        try:
            name_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # type: ignore[attr-defined]
        except Exception:
            # Conservative fallback to ArrowCursor
            name_button.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        layout.addWidget(name_button)
        
        # Описание инструмента
        if "description" in tool_info:
            desc_label = QLabel(tool_info["description"])
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Использование (свернуто по умолчанию)
        if "usage" in tool_info:
            usage_button = QPushButton("Показать примеры использования")
            try:
                usage_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # type: ignore[attr-defined]
            except Exception:
                usage_button.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            usage_label = QLabel(tool_info["usage"])
            usage_label.setWordWrap(True)
            usage_label.hide()
            
            layout.addWidget(usage_button)
            layout.addWidget(usage_label)
            
            usage_button.clicked.connect(lambda: self._toggle_visibility(usage_label, usage_button))
        
        # Сигнал для выбора инструмента
        tool_data = {
            "tool_id": tool_id,
            "name": tool_info.get("name", tool_id),
            "description": tool_info.get("description", ""),
            "usage": tool_info.get("usage", "")
        }
        name_button.clicked.connect(lambda: self.tool_selected.emit(tool_id, tool_data))
        
        return card
    
    def _toggle_visibility(self, widget, button):
        """
        Переключает видимость виджета и текст кнопки.
        
        Args:
            widget: Виджет, видимость которого нужно переключить
            button: Кнопка, текст которой нужно изменить
        """
        if widget.isVisible():
            widget.hide()
            button.setText("Показать примеры использования")
        else:
            widget.show()
            button.setText("Скрыть примеры использования")


# Создаем экземпляр ToolsManager для использования в других модулях
tools_manager = ToolsManager()

def get_tools_manager() -> ToolsManager:
    """
    Возвращает экземпляр ToolsManager.
    
    Returns:
        Экземпляр ToolsManager
    """
    return tools_manager
