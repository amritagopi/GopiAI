from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint

class Titlebar(QWidget):
    minimizeClicked = Signal()
    maximizeClicked = Signal()
    restoreClicked = Signal()
    closeClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebarWidget")
        self.setFixedHeight(40)
        self._drag_active = False
        self._drag_pos = QPoint()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        self.window_title = QLabel("GopiAI - Минимальная версия", self)
        self.window_title.setObjectName("windowTitle")
        self.window_title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.window_title, 1)
        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.clicked.connect(self.minimizeClicked.emit)
        layout.addWidget(self.minimize_button)
        self.restore_button = QPushButton("❐", self)
        self.restore_button.setObjectName("restoreButton")
        self.restore_button.setFixedSize(40, 40)
        self.restore_button.setVisible(False)
        self.restore_button.clicked.connect(self.restoreClicked.emit)
        layout.addWidget(self.restore_button)
        self.maximize_button = QPushButton("□", self)
        self.maximize_button.setObjectName("maximizeButton")
        self.maximize_button.setFixedSize(40, 40)
        self.maximize_button.clicked.connect(self.maximizeClicked.emit)
        layout.addWidget(self.maximize_button)
        self.close_button = QPushButton("×", self)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(40, 40)
        self.close_button.clicked.connect(self.closeClicked.emit)
        layout.addWidget(self.close_button)
    def set_title(self, text):
        self.window_title.setText(text)
    def show_restore(self, show):
        self.restore_button.setVisible(show)
        self.maximize_button.setVisible(not show)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)
