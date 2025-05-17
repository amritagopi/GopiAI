"""
Plan View Widget для Reasoning Agent

Компонент для структурированного отображения плана действий с подсветкой
рисков, форматированием и интерактивными элементами.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from app.logger import logger
from app.ui.i18n.translator import tr
from app.ui.icon_adapter import get_icon


class RiskLevelIndicator(QWidget):
    """
    Индикатор уровня риска для шага плана.

    Цветовая индикация уровня риска:
    - Зеленый: Низкий риск
    - Желтый: Средний риск
    - Красный: Высокий риск
    """

    def __init__(self, level: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.level = level.lower()

        # Определяем цвет в зависимости от уровня риска
        self.colors = {
            "low": QColor(0, 170, 0),  # Зеленый
            "medium": QColor(240, 180, 0),  # Желтый
            "high": QColor(220, 0, 0),  # Красный
        }

        self.setToolTip(
            tr(f"plan_view.risk.{level}", f"{level.capitalize()} risk level")
        )

    def paintEvent(self, event):
        """Отрисовывает индикатор риска."""
        from PySide6.QtGui import QBrush, QPainter, QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.colors.get(self.level, QColor(128, 128, 128))  # Серый по умолчанию

        painter.setPen(QPen(color.darker(120), 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()


class PlanStepWidget(QWidget):
    """
    Виджет для отображения одного шага плана.

    Включает:
    - Заголовок шага
    - Описание шага
    - Индикатор риска
    - Список инструментов
    """

    # Сигнал для запроса подробностей о шаге
    details_requested = Signal(int)  # ID шага

    def __init__(
        self,
        step_id: int,
        title: str,
        description: str,
        risk_level: str = "low",
        tools: List[str] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.step_id = step_id
        self.title = title
        self.description = description
        self.risk_level = risk_level
        self.tools = tools or []

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс виджета шага."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Верхняя панель с заголовком и индикатором риска
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Номер и заголовок
        title_label = QLabel(f"<b>Шаг {self.step_id+1}:</b> {self.title}")
        title_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(title_label, 1)

        # Индикатор риска
        risk_indicator = RiskLevelIndicator(self.risk_level)
        risk_text = QLabel(
            tr(
                f"plan_view.risk.{self.risk_level}",
                f"{self.risk_level.capitalize()} risk",
            )
        )
        risk_text.setStyleSheet(
            f"color: {risk_indicator.colors[self.risk_level].name()};"
        )

        header_layout.addWidget(risk_text)
        header_layout.addWidget(risk_indicator)

        # Кнопка для получения дополнительной информации
        details_button = QToolButton()
        details_button.setIcon(get_icon("info"))
        details_button.setToolTip(tr("plan_view.details", "View step details"))
        details_button.clicked.connect(
            lambda: self.details_requested.emit(self.step_id)
        )
        header_layout.addWidget(details_button)

        layout.addLayout(header_layout)

        # Линия-разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Описание шага
        description_text = QTextEdit()
        description_text.setReadOnly(True)
        description_text.setMaximumHeight(100)
        description_text.setText(self.description)
        description_text.setStyleSheet(
            "background-color: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.1);"
        )
        layout.addWidget(description_text)

        # Используемые инструменты
        if self.tools:
            tools_layout = QHBoxLayout()
            tools_layout.setContentsMargins(0, 0, 0, 0)
            tools_label = QLabel(tr("plan_view.tools", "Tools:"))
            tools_label.setStyleSheet("font-weight: bold;")
            tools_layout.addWidget(tools_label)

            for tool in self.tools:
                tool_label = QLabel(tool)
                tool_label.setStyleSheet(
                    "background-color: rgba(0,0,0,0.08); padding: 2px 4px; border-radius: 3px;"
                )
                tools_layout.addWidget(tool_label)

            tools_layout.addStretch(1)
            layout.addLayout(tools_layout)

        self.setStyleSheet(
            """
            PlanStepWidget {
                background-color: white;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 5px;
            }
        """
        )


class PlanRisksWidget(QWidget):
    """
    Виджет для отображения рисков и мер их смягчения.
    """

    def __init__(self, risks: Dict[str, str], parent=None):
        super().__init__(parent)

        self.risks = risks
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс для отображения рисков."""
        layout = QVBoxLayout(self)

        # Заголовок
        header = QLabel(tr("plan_view.risks.header", "Risks and Mitigation"))
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Линия-разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Отображаем риски
        for risk, mitigation in self.risks.items():
            risk_layout = QHBoxLayout()

            # Индикатор риска (определяем уровень на основе текста)
            risk_level = "medium"  # По умолчанию средний
            if (
                "высок" in risk.lower()
                or "критич" in risk.lower()
                or "high" in risk.lower()
            ):
                risk_level = "high"
            elif (
                "низк" in risk.lower()
                or "незначит" in risk.lower()
                or "low" in risk.lower()
            ):
                risk_level = "low"

            risk_indicator = RiskLevelIndicator(risk_level)
            risk_layout.addWidget(risk_indicator)

            # Риск и смягчение
            risk_text = QLabel(f"<b>{risk}</b>: {mitigation}")
            risk_text.setWordWrap(True)
            risk_layout.addWidget(risk_text, 1)

            layout.addLayout(risk_layout)

        layout.addStretch(1)

        self.setStyleSheet(
            """
            PlanRisksWidget {
                background-color: rgba(240, 240, 240, 0.5);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 5px;
                padding: 5px;
            }
        """
        )


class PlanApprovalWidget(QWidget):
    """
    Виджет для одобрения или отклонения плана.
    """

    # Сигналы
    plan_approved = Signal()
    plan_rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает интерфейс для подтверждения/отклонения плана."""
        layout = QVBoxLayout(self)

        # Заголовок
        header = QLabel(tr("plan_view.approval.header", "Plan Approval"))
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Линия-разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Подтверждение ознакомления с рисками
        risk_checkbox = QCheckBox(
            tr(
                "plan_view.approval.risks_acknowledged",
                "I acknowledge the risks and safety measures",
            )
        )
        layout.addWidget(risk_checkbox)

        # Кнопки одобрения и отклонения
        buttons_layout = QHBoxLayout()

        approve_button = QPushButton(tr("plan_view.approval.approve", "Approve Plan"))
        approve_button.setIcon(get_icon("plan_approve"))
        approve_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 8px 16px;"
        )
        approve_button.setEnabled(
            False
        )  # Изначально отключена, пока не отметят чекбокс

        reject_button = QPushButton(tr("plan_view.approval.reject", "Reject Plan"))
        reject_button.setIcon(get_icon("plan_reject"))
        reject_button.setStyleSheet(
            "background-color: #F44336; color: white; padding: 8px 16px;"
        )

        buttons_layout.addWidget(reject_button)
        buttons_layout.addWidget(approve_button)

        layout.addLayout(buttons_layout)

        # Подключаем сигналы
        risk_checkbox.toggled.connect(approve_button.setEnabled)
        approve_button.clicked.connect(self.plan_approved)
        reject_button.clicked.connect(self.plan_rejected)

        self.setStyleSheet(
            """
            PlanApprovalWidget {
                background-color: rgba(240, 240, 240, 0.5);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 5px;
                padding: 5px;
            }
        """
        )


class PlanViewWidget(QWidget):
    """
    Основной виджет для отображения плана действий.

    Включает:
    - Заголовок и описание задачи
    - Список шагов плана
    - Раздел рисков и мер их смягчения
    - Панель одобрения/отклонения плана
    """

    # Сигналы
    plan_approved = Signal()
    plan_rejected = Signal()
    step_details_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.plan_data = None

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        layout = QVBoxLayout(self)

        # Область прокрутки для содержимого плана
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Контейнер для прокручиваемого содержимого
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area, 1)

        # Панель одобрения/отклонения
        self.approval_widget = PlanApprovalWidget()
        self.approval_widget.plan_approved.connect(self.plan_approved)
        self.approval_widget.plan_rejected.connect(self.plan_rejected)
        layout.addWidget(self.approval_widget)

        # Изначально скрываем, пока нет плана
        self.setVisible(False)

    def set_plan(self, plan_data: Dict[str, Any]):
        """
        Устанавливает и отображает данные плана.

        Args:
            plan_data: Словарь с данными плана (задача, шаги, риски)
        """
        self.plan_data = plan_data

        # Очищаем предыдущее содержимое
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Заголовок и описание задачи
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)

        title = QLabel(tr("plan_view.task.title", "Task"))
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        task_layout.addWidget(title)

        task_description = QTextEdit()
        task_description.setReadOnly(True)
        task_description.setText(plan_data.get("task", ""))
        task_description.setMaximumHeight(80)
        task_layout.addWidget(task_description)

        self.content_layout.addWidget(task_widget)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.content_layout.addWidget(line)

        # Шаги плана
        steps_title = QLabel(tr("plan_view.steps.title", "Plan Steps"))
        steps_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.content_layout.addWidget(steps_title)

        steps = plan_data.get("steps", [])
        for i, step in enumerate(steps):
            step_widget = PlanStepWidget(
                i,
                step.get("title", f"Step {i+1}"),
                step.get("description", ""),
                step.get("risk_level", "low"),
                step.get("tools", []),
            )
            step_widget.details_requested.connect(self.step_details_requested)
            self.content_layout.addWidget(step_widget)

        # Разделитель
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        self.content_layout.addWidget(line2)

        # Риски и меры смягчения
        risks = plan_data.get("risks", {})
        risks_widget = PlanRisksWidget(risks)
        self.content_layout.addWidget(risks_widget)

        # Отступ внизу для красоты
        self.content_layout.addStretch(1)

        # Показываем виджет
        self.setVisible(True)

    def clear(self):
        """Очищает данные плана и скрывает виджет."""
        self.plan_data = None
        self.setVisible(False)
