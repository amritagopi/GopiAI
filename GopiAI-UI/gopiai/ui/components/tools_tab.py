"""
Вкладка управления инструментами GopiAI
Позволяет включать/выключать инструменты, устанавливать API ключи и прикреплять к сообщениям
"""

import logging
from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox,
    QLabel, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import requests
from gopiai.ui.utils.icon_helpers import create_icon_button, get_icon
from gopiai.ui.components.utils.shared_widgets import create_attached_frame

logger = logging.getLogger(__name__)

class ToolItemWidget(QWidget):
    """Виджет для отображения одного инструмента"""
    
    tool_toggled = Signal(str, bool)  # tool_name, enabled
    tool_attached = Signal(str)  # tool_name
    key_set = Signal(str, str)  # tool_name, api_key
    
    def __init__(self, tool_name: str, tool_data: Dict, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.tool_data = tool_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Информация об инструменте
        info_layout = QVBoxLayout()
        
        # Название инструмента
        name_label = QLabel(self.tool_name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)
        
        # Описание
        desc_label = QLabel(self.tool_data.get('description', ''))
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout, 1)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)
        
        # Переключатель включен/выключен (иконка)
        self.toggle_btn = create_icon_button(
            "power-off" if self.tool_data.get('enabled', True) else "power",
            "Выключить инструмент" if self.tool_data.get('enabled', True) else "Включить инструмент",
        )
        self._update_toggle_button()
        self.toggle_btn.clicked.connect(self._on_toggle_clicked)
        controls_layout.addWidget(self.toggle_btn)
        
        # Кнопка установки ключа (иконка)
        self.key_btn = create_icon_button("key", "Добавить ключ")
        self._update_key_button()
        self.key_btn.clicked.connect(self._on_key_clicked)
        controls_layout.addWidget(self.key_btn)
        
        # Кнопка прикрепления (иконка)
        attach_btn = create_icon_button("paperclip", "Прикрепить к сообщению")
        attach_btn.clicked.connect(lambda: self.tool_attached.emit(self.tool_name))
        controls_layout.addWidget(attach_btn)
        
        layout.addLayout(controls_layout)
    
    def _update_toggle_button(self):
        enabled = self.tool_data.get('enabled', True)
        if enabled:
            icon = get_icon("power-off")
            if icon:
                self.toggle_btn.setIcon(icon)
            self.toggle_btn.setToolTip("Выключить инструмент")
        else:
            icon = get_icon("power")
            if icon:
                self.toggle_btn.setIcon(icon)
            self.toggle_btn.setToolTip("Включить инструмент")
    
    def _update_key_button(self):
        has_key = self.tool_data.get('has_custom_key', False)
        self.key_btn.setToolTip("Изменить API ключ" if has_key else "Добавить API ключ")
    
    def _on_toggle_clicked(self):
        current_enabled = self.tool_data.get('enabled', True)
        new_enabled = not current_enabled
        self.tool_data['enabled'] = new_enabled
        self._update_toggle_button()
        self.tool_toggled.emit(self.tool_name, new_enabled)
    
    def _on_key_clicked(self):
        current_key = ""  # Мы не показываем текущий ключ по соображениям безопасности
        key, ok = QInputDialog.getText(
            self, 
            f"API ключ для {self.tool_name}",
            "Введите API ключ (оставьте пустым для удаления):",
            text=current_key
        )
        
        if ok:
            self.tool_data['has_custom_key'] = bool(key.strip())
            self._update_key_button()
            self.key_set.emit(self.tool_name, key)

class ToolsTab(QWidget):
    """Вкладка управления инструментами"""
    
    tools_attached = Signal(list)  # Список прикрепленных инструментов
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from gopiai.ui.utils.network import get_crewai_server_base_url
        self.api_base = get_crewai_server_base_url()
        self.tools_data = {}
        self.attached_tools = []
        self._setup_ui()
        self._load_tools()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        title_label = QLabel("Управление инструментами")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Статус загрузки
        self.status_label = QLabel("Загрузка инструментов...")
        layout.addWidget(self.status_label)
        
        # Прикрепленные инструменты
        attached_frame = create_attached_frame("Прикрепленные к сообщению:")
        attached_layout = attached_frame.layout()
        
        self.attached_label = QLabel("нет")
        self.attached_label.setWordWrap(True)
        attached_layout.addWidget(self.attached_label)
        
        clear_btn = create_icon_button("trash-2", "Очистить прикрепления")
        clear_btn.clicked.connect(self._clear_attached)
        attached_layout.addWidget(clear_btn)
        
        layout.addWidget(attached_frame)
        
        # Область прокрутки для инструментов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.tools_container = QWidget()
        self.tools_layout = QVBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(4)
        
        scroll_area.setWidget(self.tools_container)
        layout.addWidget(scroll_area, 1)
        
        # Кнопка обновления
        refresh_btn = create_icon_button("refresh-cw", "Обновить список инструментов")
        refresh_btn.clicked.connect(self._load_tools)
        layout.addWidget(refresh_btn)
    
    def _load_tools(self):
        """Загружает список инструментов с сервера"""
        self.status_label.setText("Загрузка инструментов...")
        
        try:
            response = requests.get(f"{self.api_base}/api/tools", timeout=5)
            if response.status_code == 200:
                self.tools_data = response.json()
                self._render_tools()
                self.status_label.setText(f"Загружено {self._count_tools()} инструментов")
            else:
                error_msg = f"Ошибка загрузки: {response.status_code}"
                self.status_label.setText(error_msg)
                logger.error(error_msg)
        except requests.RequestException as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            self.status_label.setText(error_msg)
            logger.error(error_msg)
    
    def _count_tools(self) -> int:
        """Подсчитывает общее количество инструментов"""
        # Проверяем формат ответа от API
        if isinstance(self.tools_data, dict):
            if 'count' in self.tools_data:
                # Новый формат API: {"tools": [...], "count": N}
                return self.tools_data['count']
            else:
                # Старый формат API: {category: [tools]}
                count = 0
                for category_tools in self.tools_data.values():
                    if isinstance(category_tools, (list, tuple)):
                        count += len(category_tools)
                    elif isinstance(category_tools, int):
                        count += category_tools
                return count
        return 0
    
    def _render_tools(self):
        """Отображает инструменты по категориям"""
        # Очищаем предыдущие виджеты
        while self.tools_layout.count():
            child = self.tools_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Обрабатываем данные в зависимости от формата API
        if 'tools' in self.tools_data:
            # Новый формат API: {"tools": [...], "count": N}
            tools_list = self.tools_data.get('tools', [])
            
            # Группируем инструменты по категориям
            categories = {}
            for tool in tools_list:
                category = tool.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(tool)
            
            # Создаем группы по категориям
            for category, tools in categories.items():
                self._create_category_group(category, tools)
        else:
            # Старый формат API: {category: [tools]}
            for category, tools in self.tools_data.items():
                if not isinstance(tools, list):
                    continue
                self._create_category_group(category, tools)
    
    def _create_category_group(self, category, tools):
        """Создает группу инструментов для категории"""
        if not tools:
            return
                
        # Группа для категории
        group_box = QGroupBox(category.replace('_', ' ').title())
        group_layout = QVBoxLayout(group_box)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(2)
        
        # Добавляем инструменты в группу
        for tool in tools:
            if isinstance(tool, dict) and 'name' in tool:
                tool_widget = ToolItemWidget(tool['name'], tool)
                tool_widget.tool_toggled.connect(self._on_tool_toggled)
                tool_widget.tool_attached.connect(self._on_tool_attached)
                tool_widget.key_set.connect(self._on_key_set)
                group_layout.addWidget(tool_widget)
        
        self.tools_layout.addWidget(group_box)
        
        # Добавляем растягивающийся элемент в конец
        self.tools_layout.addStretch()
    
    def _on_tool_toggled(self, tool_name: str, enabled: bool):
        """Обрабатывает переключение инструмента"""
        try:
            response = requests.post(
                f"{self.api_base}/api/tools/toggle",
                json={"tool_name": tool_name, "enabled": enabled},
                timeout=5
            )
            
            if response.status_code == 200:
                status = "включен" if enabled else "выключен"
                self.status_label.setText(f"Инструмент {tool_name} {status}")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', 'Неизвестная ошибка')
                self.status_label.setText(f"Ошибка: {error_msg}")
                logger.error(f"Toggle error: {error_msg}")
        except requests.RequestException as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            self.status_label.setText(error_msg)
            logger.error(error_msg)
    
    def _on_key_set(self, tool_name: str, api_key: str):
        """Обрабатывает установку API ключа"""
        try:
            response = requests.post(
                f"{self.api_base}/api/tools/set_key",
                json={"tool_name": tool_name, "api_key": api_key},
                timeout=5
            )
            
            if response.status_code == 200:
                action = "установлен" if api_key.strip() else "удален"
                self.status_label.setText(f"API ключ для {tool_name} {action}")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', 'Неизвестная ошибка')
                self.status_label.setText(f"Ошибка: {error_msg}")
                logger.error(f"Key set error: {error_msg}")
        except requests.RequestException as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            self.status_label.setText(error_msg)
            logger.error(error_msg)
    
    def _on_tool_attached(self, tool_name: str):
        """Обрабатывает прикрепление инструмента к сообщению"""
        if tool_name not in self.attached_tools:
            self.attached_tools.append(tool_name)
            self._update_attached_display()
            self.tools_attached.emit(self.attached_tools)
            self.status_label.setText(f"Инструмент {tool_name} прикреплен к сообщению")
    
    def _clear_attached(self):
        """Очищает все прикрепленные инструменты"""
        self.attached_tools.clear()
        self._update_attached_display()
        self.tools_attached.emit(self.attached_tools)
        self.status_label.setText("Все прикрепления очищены")
    
    def _update_attached_display(self):
        """Обновляет отображение прикрепленных инструментов"""
        if self.attached_tools:
            self.attached_label.setText(", ".join(self.attached_tools))
        else:
            self.attached_label.setText("нет")
    
    def get_attached_tools(self) -> List[str]:
        """Возвращает список прикрепленных инструментов"""
        return self.attached_tools.copy()
