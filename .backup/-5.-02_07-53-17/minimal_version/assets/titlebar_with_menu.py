from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPoint
from .titlebar import Titlebar
from .menubar import MenuBar

class TitlebarWithMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.menubar = MenuBar(self)
        layout.addWidget(self.menubar)
        self.titlebar = Titlebar(self)
        layout.addWidget(self.titlebar, 1)
        self._main_window = None
        self._drag_active = False
        self._drag_pos = QPoint()
    def set_window(self, main_window):
        self._main_window = main_window
        self.titlebar.minimizeClicked.connect(main_window.showMinimized)
        self.titlebar.maximizeClicked.connect(main_window.showMaximized)
        self.titlebar.restoreClicked.connect(main_window.showNormal)
        self.titlebar.closeClicked.connect(main_window.close)
    def update_title(self, text):
        self.titlebar.set_title(text)
    def maximize_window(self):
        self.titlebar.show_restore(True)
    def restore_window(self):
        self.titlebar.show_restore(False)
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
