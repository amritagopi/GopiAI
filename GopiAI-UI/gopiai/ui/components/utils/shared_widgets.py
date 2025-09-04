from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QFont

def create_attached_frame(title_text: str) -> QFrame:
    """Создает рамку для отображения прикрепленных элементов."""
    frame = QFrame()
    frame.setFrameStyle(QFrame.Shape.Box)
    layout = QVBoxLayout(frame)
    
    title = QLabel(title_text)
    title_font = QFont()
    title_font.setBold(True)
    title.setFont(title_font)
    layout.addWidget(title)
    
    return frame