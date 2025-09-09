"""
Вкладка управления агентами и флоу GopiAI
Позволяет выбирать и прикреплять агентов/флоу к сообщениям для принудительного использования
"""

import logging
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox,
    QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import requests
from gopiai.ui.utils.icon_helpers import create_icon_button
from gopiai.ui.components.utils.shared_widgets import create_attached_frame

logger = logging.getLogger(__name__)

class AgentItemWidget(QWidget):
    """Виджет для отображения одного агента или флоу"""
    
    agent_attached = Signal(str, str, str)  # agent_id, agent_name, agent_type
    
    def __init__(self, agent_data: Dict, parent=None):
        super().__init__(parent)
        self.agent_data = agent_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Информация об агенте
        info_layout = QVBoxLayout()
        
        # Название агента
        name_label = QLabel(self.agent_data.get('name', ''))
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)
        
        # Описание
        desc_label = QLabel(self.agent_data.get('description', ''))
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout, 1)
        
        # Тип агента/флоу
        type_label = QLabel(self.agent_data.get('type', '').upper())
        type_label.setFixedWidth(60)
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Убираем хардкод цветов — полагаемся на тему/палитру
        
        layout.addWidget(type_label)
        
        # Кнопка прикрепления (иконка)
        attach_btn = create_icon_button("paperclip", "Прикрепить к сообщению")
        attach_btn.clicked.connect(self._on_attach_clicked)
        layout.addWidget(attach_btn)
    
    def _on_attach_clicked(self):
        agent_id = self.agent_data.get('id', '')
        agent_name = self.agent_data.get('name', '')
        agent_type = self.agent_data.get('type', '')
        self.agent_attached.emit(agent_id, agent_name, agent_type)

class AgentsTab(QWidget):
    """Вкладка управления агентами и флоу"""
    
    agents_attached = Signal(list)  # Список прикрепленных агентов
    flow_attached = Signal(dict)    # Прикрепленный флоу (может быть только один)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from gopiai.ui.utils.network import get_crewai_server_base_url
        self.api_base = get_crewai_server_base_url()
        self.agents_data = []
        self.attached_agents = []
        self.attached_flow = None
        self._setup_ui()
        self._load_agents()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        title_label = QLabel("Агенты и флоу")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Статус загрузки
        self.status_label = QLabel("Загрузка агентов...")
        layout.addWidget(self.status_label)
        
        # Прикрепленные элементы
        attached_frame = create_attached_frame("Прикрепленные к сообщению:")
        attached_layout = attached_frame.layout()
        
        # Прикрепленные агенты
        agents_layout = QHBoxLayout()
        agents_layout.addWidget(QLabel("Агенты:"))
        self.attached_agents_label = QLabel("нет")
        self.attached_agents_label.setWordWrap(True)
        agents_layout.addWidget(self.attached_agents_label, 1)
        attached_layout.addLayout(agents_layout)
        
        # Прикрепленный флоу
        flow_layout = QHBoxLayout()
        flow_layout.addWidget(QLabel("Флоу:"))
        self.attached_flow_label = QLabel("нет")
        self.attached_flow_label.setWordWrap(True)
        flow_layout.addWidget(self.attached_flow_label, 1)
        attached_layout.addLayout(flow_layout)
        
        # Кнопки очистки (иконки)
        clear_layout = QHBoxLayout()
        clear_agents_btn = create_icon_button("eraser", "Очистить прикрепленных агентов")
        clear_agents_btn.clicked.connect(self._clear_agents)
        clear_layout.addWidget(clear_agents_btn)
        
        clear_flow_btn = create_icon_button("minus-circle", "Очистить прикрепленный флоу")
        clear_flow_btn.clicked.connect(self._clear_flow)
        clear_layout.addWidget(clear_flow_btn)
        
        clear_all_btn = create_icon_button("trash-2", "Очистить всё")
        clear_all_btn.clicked.connect(self._clear_all)
        clear_layout.addWidget(clear_all_btn)
        
        attached_layout.addLayout(clear_layout)
        layout.addWidget(attached_frame)
        
        # Область прокрутки для агентов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.agents_container = QWidget()
        self.agents_layout = QVBoxLayout(self.agents_container)
        self.agents_layout.setContentsMargins(0, 0, 0, 0)
        self.agents_layout.setSpacing(4)
        
        scroll_area.setWidget(self.agents_container)
        layout.addWidget(scroll_area, 1)
        
        # Кнопки управления
        control_buttons = QHBoxLayout()
        
        # Кнопка обновления
        refresh_btn = create_icon_button("refresh-cw", "Обновить список агентов")
        refresh_btn.clicked.connect(self._load_agents)
        control_buttons.addWidget(refresh_btn)
        
        control_buttons.addStretch()
        
        layout.addLayout(control_buttons)
    
    def _load_agents(self):
        """Загружает список агентов с сервера"""
        self.status_label.setText("Загрузка агентов...")
        
        try:
            response = requests.get(f"{self.api_base}/api/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.agents_data = data.get('agents', [])
                self._render_agents()
                self.status_label.setText(f"Загружено {len(self.agents_data)} агентов/флоу")
            else:
                error_msg = f"Ошибка загрузки: {response.status_code}"
                self.status_label.setText(error_msg)
                logger.error(error_msg)
        except requests.RequestException as e:
            error_msg = f"Ошибка подключения: {str(e)}"
            self.status_label.setText(error_msg)
            logger.error(error_msg)
    
    def _render_agents(self):
        """Отображает агентов и флоу"""
        # Очищаем предыдущие виджеты
        while self.agents_layout.count():
            child = self.agents_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Группируем по типам и категориям
        agents = [a for a in self.agents_data if a.get('type') == 'agent']
        flows = [a for a in self.agents_data if a.get('type') == 'flow']
        
        # Группы агентов по категориям
        if agents:
            # Группируем агентов по категориям
            categories = {}
            for agent in agents:
                category = agent.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(agent)
            
            # Словарь для красивых названий категорий
            category_names = {
                'research': '🔬 Исследование и анализ',
                'analytics': '📊 Аналитика данных',
                'content': '✍️ Создание контента',
                'documentation': '📚 Документация',
                'development': '💻 Разработка',
                'security': '🔒 Безопасность',
                'management': '📋 Управление проектами',
                'strategy': '🎯 Стратегия и консалтинг',
                'other': '🔧 Другие'
            }
            
            # Создаем группы для каждой категории
            for category, category_agents in categories.items():
                category_name = category_names.get(category, f'📁 {category.title()}')
                agents_group = QGroupBox(category_name)
                agents_group_layout = QVBoxLayout(agents_group)
                agents_group_layout.setContentsMargins(8, 8, 8, 8)
                agents_group_layout.setSpacing(2)
                
                for agent in category_agents:
                    agent_widget = AgentItemWidget(agent)
                    agent_widget.agent_attached.connect(self._on_agent_attached)
                    agents_group_layout.addWidget(agent_widget)
                
                self.agents_layout.addWidget(agents_group)
        
        # Группа флоу
        if flows:
            flows_group = QGroupBox("Флоу")
            flows_group_layout = QVBoxLayout(flows_group)
            flows_group_layout.setContentsMargins(8, 8, 8, 8)
            flows_group_layout.setSpacing(2)
            
            for flow in flows:
                flow_widget = AgentItemWidget(flow)
                flow_widget.agent_attached.connect(self._on_agent_attached)
                flows_group_layout.addWidget(flow_widget)
            
            self.agents_layout.addWidget(flows_group)
        
        # Добавляем растягивающийся элемент в конец
        self.agents_layout.addStretch()
    
    def _on_agent_attached(self, agent_id: str, agent_name: str, agent_type: str):
        """Обрабатывает прикрепление агента или флоу"""
        if agent_type == 'flow':
            # Для флоу может быть только один активный
            self.attached_flow = {
                'id': agent_id,
                'name': agent_name,
                'type': agent_type
            }
            self.flow_attached.emit(self.attached_flow)
            self.status_label.setText(f"Флоу {agent_name} прикреплен к сообщению")
        else:
            # Для агентов можно прикреплять несколько
            agent_info = {
                'id': agent_id,
                'name': agent_name,
                'type': agent_type
            }
            
            # Проверяем, что агент еще не прикреплен
            if not any(a['id'] == agent_id for a in self.attached_agents):
                self.attached_agents.append(agent_info)
                self.agents_attached.emit(self.attached_agents)
                self.status_label.setText(f"Агент {agent_name} прикреплен к сообщению")
        
        self._update_attached_display()
    
    def _clear_agents(self):
        """Очищает прикрепленных агентов"""
        self.attached_agents.clear()
        self.agents_attached.emit(self.attached_agents)
        self._update_attached_display()
        self.status_label.setText("Прикрепленные агенты очищены")
    
    def _clear_flow(self):
        """Очищает прикрепленный флоу"""
        self.attached_flow = None
        self.flow_attached.emit({})
        self._update_attached_display()
        self.status_label.setText("Прикрепленный флоу очищен")
    
    def _clear_all(self):
        """Очищает все прикрепления"""
        self.attached_agents.clear()
        self.attached_flow = None
        self.agents_attached.emit(self.attached_agents)
        self.flow_attached.emit({})
        self._update_attached_display()
        self.status_label.setText("Все прикрепления очищены")
    
    def _update_attached_display(self):
        """Обновляет отображение прикрепленных элементов"""
        # Агенты
        if self.attached_agents:
            agents_names = [a['name'] for a in self.attached_agents]
            self.attached_agents_label.setText(", ".join(agents_names))
        else:
            self.attached_agents_label.setText("нет")
        
        # Флоу
        if self.attached_flow:
            self.attached_flow_label.setText(self.attached_flow['name'])
        else:
            self.attached_flow_label.setText("нет")
    
    def get_attached_agents(self) -> List[Dict]:
        """Возвращает список прикрепленных агентов"""
        return self.attached_agents.copy()
    
    def get_attached_flow(self) -> Optional[Dict]:
        """Возвращает прикрепленный флоу"""
        return self.attached_flow.copy() if self.attached_flow else None
