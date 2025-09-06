"""
Мастер создания команд CrewAI - пошаговый интерфейс для настройки агентов и флоу
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QWidget, QListWidget, QListWidgetItem,
    QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from gopiai.ui.utils.icon_helpers import create_icon_button

logger = logging.getLogger(__name__)

class AgentConfigWidget(QWidget):
    """Виджет конфигурации отдельного агента"""
    
    def __init__(self, agent_template=None, parent=None):
        super().__init__(parent)
        self.agent_data = agent_template or {}
        self._setup_ui()
        self._load_template_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QVBoxLayout(info_group)
        
        # Имя агента
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя агента...")
        name_layout.addWidget(self.name_edit)
        info_layout.addLayout(name_layout)
        
        # Роль
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Роль:"))
        self.role_edit = QLineEdit()
        self.role_edit.setPlaceholderText("Специализация агента...")
        role_layout.addWidget(self.role_edit)
        info_layout.addLayout(role_layout)
        
        # Цель
        goal_layout = QVBoxLayout()
        goal_layout.addWidget(QLabel("Цель:"))
        self.goal_edit = QTextEdit()
        self.goal_edit.setPlaceholderText("Главная цель агента...")
        self.goal_edit.setMaximumHeight(60)
        goal_layout.addWidget(self.goal_edit)
        info_layout.addLayout(goal_layout)
        
        layout.addWidget(info_group)
        
        # Backstory
        story_group = QGroupBox("Предыстория")
        story_layout = QVBoxLayout(story_group)
        self.backstory_edit = QTextEdit()
        self.backstory_edit.setPlaceholderText("Опишите опыт и навыки агента...")
        self.backstory_edit.setMaximumHeight(80)
        story_layout.addWidget(self.backstory_edit)
        layout.addWidget(story_group)
        
        # Инструменты и настройки
        tools_group = QGroupBox("Инструменты и настройки")
        tools_layout = QVBoxLayout(tools_group)
        
        # Чекбоксы для инструментов
        self.tools_checks = {}
        tools = ["search_tool", "file_read_tool", "directory_tool", "web_search_tool", "code_execution"]
        for tool in tools:
            check = QCheckBox(tool.replace("_", " ").title())
            self.tools_checks[tool] = check
            tools_layout.addWidget(check)
        
        # Verbose режим
        self.verbose_check = QCheckBox("Verbose (детальные логи)")
        tools_layout.addWidget(self.verbose_check)
        
        # Делегирование
        self.delegation_check = QCheckBox("Разрешить делегирование задач")
        tools_layout.addWidget(self.delegation_check)
        
        layout.addWidget(tools_group)
    
    def _load_template_data(self):
        """Загружает данные из шаблона"""
        if not self.agent_data:
            return
        
        self.name_edit.setText(self.agent_data.get('name', ''))
        self.role_edit.setText(self.agent_data.get('role', ''))
        self.goal_edit.setPlainText(self.agent_data.get('goal', ''))
        self.backstory_edit.setPlainText(self.agent_data.get('backstory', ''))
        
        # Инструменты
        tools = self.agent_data.get('tools', [])
        for tool_name, check in self.tools_checks.items():
            check.setChecked(tool_name in tools)
        
        self.verbose_check.setChecked(self.agent_data.get('verbose', True))
        self.delegation_check.setChecked(self.agent_data.get('allow_delegation', False))
    
    def get_agent_config(self):
        """Возвращает конфигурацию агента"""
        selected_tools = [tool for tool, check in self.tools_checks.items() if check.isChecked()]
        
        return {
            "name": self.name_edit.text(),
            "role": self.role_edit.text(),
            "goal": self.goal_edit.toPlainText(),
            "backstory": self.backstory_edit.toPlainText(),
            "tools": selected_tools,
            "verbose": self.verbose_check.isChecked(),
            "allow_delegation": self.delegation_check.isChecked()
        }

class CrewWizardDialog(QDialog):
    """Мастер создания команды CrewAI"""
    
    crew_created = Signal(dict)  # Сигнал при создании команды
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Мастер создания команды CrewAI")
        self.setModal(True)
        self.resize(900, 700)
        
        from gopiai.ui.utils.network import get_crewai_server_base_url
        self.api_base = get_crewai_server_base_url()
        
        self.agent_templates = self._load_agent_templates()
        self.crew_config = {
            "name": "",
            "description": "",
            "agents": [],
            "workflow_type": "sequential",
            "manager_agent": None
        }
        
        self._setup_ui()
        self._load_templates()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Создание новой команды CrewAI")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Основной контент
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - шаблоны
        templates_widget = self._create_templates_panel()
        content_splitter.addWidget(templates_widget)
        
        # Правая панель - конфигурация
        config_widget = self._create_config_panel()
        content_splitter.addWidget(config_widget)
        
        content_splitter.setSizes([300, 600])
        layout.addWidget(content_splitter)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        self.create_btn = QPushButton("Создать команду")
        self.create_btn.clicked.connect(self._create_crew)
        self.create_btn.setEnabled(False)
        buttons_layout.addWidget(self.create_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_templates_panel(self):
        """Создает панель шаблонов агентов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        templates_label = QLabel("Шаблоны агентов")
        templates_font = QFont()
        templates_font.setBold(True)
        templates_label.setFont(templates_font)
        layout.addWidget(templates_label)
        
        # Список шаблонов
        self.templates_list = QListWidget()
        self.templates_list.itemDoubleClicked.connect(self._add_template_agent)
        layout.addWidget(self.templates_list)
        
        # Кнопка добавления
        add_template_btn = create_icon_button("plus", "Добавить выбранный шаблон")
        add_template_btn.clicked.connect(self._add_selected_template)
        layout.addWidget(add_template_btn)
        
        # Кастомный агент
        layout.addWidget(QLabel(""))  # Разделитель
        custom_label = QLabel("Создать кастомного агента")
        custom_font = QFont()
        custom_font.setBold(True)
        custom_label.setFont(custom_font)
        layout.addWidget(custom_label)
        
        add_custom_btn = create_icon_button("user-plus", "Создать кастомного агента")
        add_custom_btn.clicked.connect(self._add_custom_agent)
        layout.addWidget(add_custom_btn)
        
        return widget
    
    def _create_config_panel(self):
        """Создает панель конфигурации команды"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Информация о команде
        crew_info_group = QGroupBox("Информация о команде")
        crew_info_layout = QVBoxLayout(crew_info_group)
        
        # Название команды
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.crew_name_edit = QLineEdit()
        self.crew_name_edit.setPlaceholderText("Введите название команды...")
        self.crew_name_edit.textChanged.connect(self._validate_form)
        name_layout.addWidget(self.crew_name_edit)
        crew_info_layout.addLayout(name_layout)
        
        # Описание
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Описание:"))
        self.crew_desc_edit = QTextEdit()
        self.crew_desc_edit.setPlaceholderText("Опишите назначение команды...")
        self.crew_desc_edit.setMaximumHeight(60)
        desc_layout.addWidget(self.crew_desc_edit)
        crew_info_layout.addLayout(desc_layout)
        
        # Тип рабочего процесса
        workflow_layout = QHBoxLayout()
        workflow_layout.addWidget(QLabel("Рабочий процесс:"))
        self.workflow_combo = QComboBox()
        self.workflow_combo.addItems(["sequential", "hierarchical"])
        workflow_layout.addWidget(self.workflow_combo)
        crew_info_layout.addLayout(workflow_layout)
        
        layout.addWidget(crew_info_group)
        
        # Агенты команды
        agents_group = QGroupBox("Агенты команды")
        agents_layout = QVBoxLayout(agents_group)
        
        # Список агентов
        self.agents_list = QListWidget()
        agents_layout.addWidget(self.agents_list)
        
        # Кнопки управления агентами
        agents_buttons = QHBoxLayout()
        
        remove_agent_btn = create_icon_button("minus", "Удалить агента")
        remove_agent_btn.clicked.connect(self._remove_agent)
        agents_buttons.addWidget(remove_agent_btn)
        
        agents_buttons.addStretch()
        
        edit_agent_btn = create_icon_button("edit-2", "Редактировать агента")
        edit_agent_btn.clicked.connect(self._edit_agent)
        agents_buttons.addWidget(edit_agent_btn)
        
        agents_layout.addLayout(agents_buttons)
        layout.addWidget(agents_group)
        
        return widget
    
    def _load_agent_templates(self):
        """Загружает шаблоны агентов"""
        templates = {
            "data_analyst": {
                "name": "Аналитик данных",
                "role": "Аналитик данных",
                "goal": "Анализировать данные и создавать информативные отчеты",
                "backstory": "Опытный аналитик данных с глубокими знаниями в области статистики и визуализации.",
                "tools": ["file_read_tool", "directory_tool"],
                "verbose": True,
                "allow_delegation": False
            },
            "researcher": {
                "name": "Исследователь",
                "role": "Исследователь",
                "goal": "Находить достоверную и актуальную информацию по любой теме",
                "backstory": "Профессиональный исследователь с навыками критического мышления.",
                "tools": ["search_tool", "web_search_tool"],
                "verbose": True,
                "allow_delegation": False
            },
            "code_reviewer": {
                "name": "Ревьюер кода",
                "role": "Ревьюер кода",
                "goal": "Анализировать код на предмет качества, безопасности и производительности",
                "backstory": "Старший разработчик с многолетним опытом code review.",
                "tools": ["file_read_tool", "directory_tool", "code_execution"],
                "verbose": True,
                "allow_delegation": False
            },
            "content_writer": {
                "name": "Контент-райтер",
                "role": "Контент-райтер",
                "goal": "Создавать качественный и увлекательный контент",
                "backstory": "Опытный писатель с пониманием различных стилей письма.",
                "tools": ["search_tool", "web_search_tool"],
                "verbose": True,
                "allow_delegation": False
            },
            "project_manager": {
                "name": "Проект-менеджер",
                "role": "Проект-менеджер",
                "goal": "Эффективно управлять проектами и координировать работу команды",
                "backstory": "Опытный проект-менеджер с сертификацией PMP.",
                "tools": ["file_read_tool", "search_tool"],
                "verbose": True,
                "allow_delegation": True
            }
        }
        return templates
    
    def _load_templates(self):
        """Загружает шаблоны в список"""
        for template_id, template_data in self.agent_templates.items():
            item = QListWidgetItem(f"🤖 {template_data['name']}")
            item.setData(Qt.ItemDataRole.UserRole, template_id)
            item.setToolTip(template_data['backstory'])
            self.templates_list.addItem(item)
    
    def _add_selected_template(self):
        """Добавляет выбранный шаблон"""
        current_item = self.templates_list.currentItem()
        if current_item:
            self._add_template_agent(current_item)
    
    def _add_template_agent(self, item):
        """Добавляет агента из шаблона"""
        template_id = item.data(Qt.ItemDataRole.UserRole)
        template_data = self.agent_templates[template_id]
        
        # Создаем копию шаблона с уникальным именем
        agent_config = template_data.copy()
        agent_config['id'] = f"{template_id}_{len(self.crew_config['agents'])}"
        
        self.crew_config['agents'].append(agent_config)
        self._update_agents_list()
        self._validate_form()
    
    def _add_custom_agent(self):
        """Добавляет кастомного агента"""
        dialog = AgentConfigDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            agent_config = dialog.get_agent_config()
            agent_config['id'] = f"custom_{len(self.crew_config['agents'])}"
            
            self.crew_config['agents'].append(agent_config)
            self._update_agents_list()
            self._validate_form()
    
    def _remove_agent(self):
        """Удаляет выбранного агента"""
        current_row = self.agents_list.currentRow()
        if current_row >= 0:
            del self.crew_config['agents'][current_row]
            self._update_agents_list()
            self._validate_form()
    
    def _edit_agent(self):
        """Редактирует выбранного агента"""
        current_row = self.agents_list.currentRow()
        if current_row >= 0:
            agent_config = self.crew_config['agents'][current_row]
            dialog = AgentConfigDialog(agent_config, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_config = dialog.get_agent_config()
                updated_config['id'] = agent_config['id']  # Сохраняем ID
                self.crew_config['agents'][current_row] = updated_config
                self._update_agents_list()
    
    def _update_agents_list(self):
        """Обновляет список агентов"""
        self.agents_list.clear()
        for agent in self.crew_config['agents']:
            item_text = f"👤 {agent.get('name', 'Безымянный агент')} ({agent.get('role', 'Без роли')})"
            item = QListWidgetItem(item_text)
            item.setToolTip(agent.get('goal', ''))
            self.agents_list.addItem(item)
    
    def _validate_form(self):
        """Проверяет валидность формы"""
        has_name = bool(self.crew_name_edit.text().strip())
        has_agents = len(self.crew_config['agents']) > 0
        
        self.create_btn.setEnabled(has_name and has_agents)
    
    def _create_crew(self):
        """Создает команду"""
        try:
            # Собираем финальную конфигурацию
            final_config = {
                "name": self.crew_name_edit.text().strip(),
                "description": self.crew_desc_edit.toPlainText().strip(),
                "agents": self.crew_config['agents'],
                "workflow_type": self.workflow_combo.currentText(),
                "created_by": "crew_wizard"
            }
            
            # Отправляем на сервер (если нужно)
            # response = requests.post(f"{self.api_base}/api/crews", json=final_config)
            
            # Эмитим сигнал
            self.crew_created.emit(final_config)
            
            QMessageBox.information(
                self, 
                "Успех", 
                f"Команда '{final_config['name']}' создана успешно!"
            )
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Ошибка создания команды: {e}")
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Не удалось создать команду: {str(e)}"
            )

class AgentConfigDialog(QDialog):
    """Диалог конфигурации агента"""
    
    def __init__(self, agent_config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Конфигурация агента")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Виджет конфигурации
        self.config_widget = AgentConfigWidget(agent_config)
        layout.addWidget(self.config_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def get_agent_config(self):
        """Возвращает конфигурацию агента"""
        return self.config_widget.get_agent_config()