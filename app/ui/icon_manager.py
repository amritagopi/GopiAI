import os
import re
import logging
from typing import Optional, Dict, Any, Tuple, Union, Set, List, Callable

from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter, QImage
from PySide6.QtCore import QSize, QRect, QPoint, QByteArray, Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QLineEdit, QComboBox, QDialog, QApplication
from PySide6.QtSvg import QSvgRenderer

# Импортируем библиотеки для работы с иконками
try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

try:
    from tablerqicon import TablerQIcon
    HAS_TABLERQICON = True
except ImportError:
    HAS_TABLERQICON = False

try:
    from pytablericons import TablerIcons, OutlineIcon, FilledIcon
    HAS_PYTABLERICONS = True
except ImportError:
    HAS_PYTABLERICONS = False

try:
    from iconipy import IconFactory
    HAS_ICONIPY = True
except ImportError:
    HAS_ICONIPY = False

from app.utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)

SVG_ICON_DATA = {
    "close": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                  <path fill="currentColor" d="M8 1.33A6.67 6.67 0 1 1 1.33 8 6.67 6.67 0 0 1 8 1.33zM8 0a8 8 0 1 0 8 8 8 8 0 0 0-8-8zm3.7 11.36a.62.62 0 0 1-.01.88a.63.63 0 0 1-.88 0L8 9.44l-2.81 2.8a.63.63 0 0 1-.88-.01.62.62 0 0 1 0-.88L7.11 8.5 4.3 5.7a.63.63 0 0 1 .01-.89.62.62 0 0 1 .88 0L8 7.61l2.81-2.8a.63.63 0 0 1 .88.01.62.62 0 0 1 0 .88L8.88 8.5z"/>
                </svg>""",
    "open": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                 <path fill="currentColor" d="M14.36 4.74h-4.8V3.51a1.33 1.33 0 0 0-1.33-1.33H3.97a1.33 1.33 0 0 0-1.33 1.33v8.9h11.72a1.33 0 0 0 1.33-1.33V6.08a1.33 0 0 0-1.33-1.34z"/>
               </svg>""",
    "save": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" />
  <path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7" />
  <path d="M7 3v4a1 1 0 0 0 1 1h7" />
</svg>""",
    "file": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
  <path d="M14 2v4a2 2 0 0 0 2 2h4" />
</svg>""",
    # "file" (placeholder) был удален, так как хорошее определение выше.
    "folder": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                   <path fill="currentColor" d="M7 2H2a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1H8z"/>
                 </svg>""",
    "python_file": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M7.8 1.5c-4 0-3.7 1.7-3.7 1.7l.1 1.8h3.8v.5H2.8S1 5.5 1 9.2c0 3.7 1.6 3.5 1.6 3.5h1v-1.7s0-2 2-2h3.4s1.9 0 1.9-1.8V4.3s.3-2.8-3-2.8zm-2.1 1.6c.4 0 .7.3.7.7 0 .4-.3.7-.7.7-.4 0-.7-.3-.7-.7 0-.4.3-.7.7-.7z"/><path fill="currentColor" d="M8.2 14.5c4 0 3.7-1.7 3.7-1.7l-.1-1.8H8.1v-.5h5.2s1.8 0 1.8-3.8c0-3.7-1.6-3.5-1.6-3.5h-1v1.7s0 2-2 2H7.1s-1.9 0-1.9 1.8v2.9s-.3 2.8 3 2.8zm2.1-1.6c-.4 0-.7-.3-.7-.7 0-.4.3-.7.7-.7.4 0 .7.3.7.7 0 .4-.3-.7-.7-.7z"/></svg>""",
    # "python_file" (placeholder) был удален.
    "settings": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
  <circle cx="12" cy="12" r="3" />
</svg>""",
    "terminal": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                     <path fill="currentColor" d="M1.5 2A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13zm5.41 7.59L4.5 12l1.41 1.41 4.5-4.5-4.5-4.5L4.5 5.82 7.09 8.5z"/>
                   </svg>""",
    "text": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M3 2.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5z"/></svg>""",
    "html": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 0h13l-1.2 13.5L8 16l-5.3-2.5L1.5 0zM12 4H4l.2 2h7.6l-.2 2H4.4l.2 2h3.2l.2 2.2-1.8.5-1.8-.5L4 10H2l.4 4.5 5.6 1.5 5.6-1.5L14 4z"/></svg>""",
    "javascript": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M4.53 1.81a.5.5 0 0 0-.4.2L1.81 5.47a.5.5 0 0 0 .2.8l2.32 1.34a.5.5 0 0 0 .6-.2L7.26 4.15a.5.5 0 0 0-.2-.8L4.53 1.81zm6.94 0l-2.53 1.54a.5.5 0 0 0-.2.8l2.32 3.26a.5.5 0 0 0 .6.2l2.32-1.34a.5.5 0 0 0 .2-.8L11.87 2a.5.5 0 0 0-.4-.19zm-6.6 7.42L1.81 10.6a.5.5 0 0 0-.2.8l2.32 3.26a.5.5 0 0 0 .6.2l2.53-1.54a.5.5 0 0 0 .2-.8L4.87 9.23a.5.5 0 0 0-.6-.2zm6.6 0l-2.53 3.26a.5.5 0 0 0 .2.8l2.53 1.54a.5.5 0 0 0 .6-.2l2.32-3.26a.5.5 0 0 0-.2-.8l-2.53-1.54a.5.5 0 0 0-.6.2z"/></svg>""",
    "css": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M3.5 1.5A.5.5 0 0 0 3 2v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V2a.5.5 0 0 0-.5-.5h-9zM4 2h8v12H4V2zm1.5 2a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5z"/></svg>""",
    "json": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8 1.5a6.5 6.5 0 1 0 0 13a6.5 6.5 0 0 0 0-13zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8z"/><path fill="currentColor" d="M6.5 5.5a1 1 0 1 0 0-2a1 1 0 0 0 0 2zm3 0a1 1 0 1 0 0-2a1 1 0 0 0 0 2zm-1.5 5a2.5 2.5 0 0 0 2.5-2.5H5A2.5 2.5 0 0 0 7.5 10.5z"/></svg>""",
    "image_png": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M14 2H2a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1zM3 12V4h2.5l1.5 2 1.5-2H11v3l-1.5 1.5L11 12H8.5l-1-1-1 1H3zm3-3.5a.5.5 0 1 1-1 0a.5.5 0 0 1 1 0zm4 0a.5.5 0 1 1-1 0a.5.5 0 0 1 1 0z"/></svg>""",
    "browser": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 0A1.5 1.5 0 0 0 0 1.5v13A1.5 1.5 0 0 0 1.5 16h13a1.5 1.5 0 0 0 1.5-1.5v-13A1.5 1.5 0 0 0 14.5 0h-13zm0 1h13a.5.5 0 0 1 .5.5V4H1V1.5A.5.5 0 0 1 1.5 1zM1 5h14v9.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V5z"/><path fill="currentColor" d="M3 2.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0zm2 0a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0zm2 0a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0z"/></svg>""",
    "run": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>""",
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5V14a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354l-6-6zM13 14h-3v-2.5a1.5 1.5 0 0 0-1.5-1.5h-1A1.5 1.5 0 0 0 6 11.5V14H3V7.707L8 2.707l5 5V14z"/></svg>""",
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.064.293.006.399.287.47l.45.082.082.38-2.29.287V12h-.002L7.11 9.93l-.24-1.107-.44-.081a.652.652 0 0 1-.49-.67a.678.678 0 0 1 .226-.490c.16-.155.359-.2.533-.2.266 0 .494.09.673.285l.777.865c.09.103.159.199.288.199.12 0 .223-.096.288-.199l1.897-2.137c.11-.124.09-.29-.053-.375zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg>""",
    "documentation": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1 2.5A1.5 1.5 0 0 1 2.5 1h11A1.5 1.5 0 0 1 15 2.5v11a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 1 13.5v-11zM2.5 2a.5.5 0 0 0-.5.5v11a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-11a.5.5 0 0 0-.5-.5h-11z"/><path fill="currentColor" d="M4.5 5.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7zm0 3a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7zm0 3a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z"/></svg>""",
    "preferences": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M9.796 1.375a.75.75 0 0 1 .75-.75h.008c.69 0 1.313.28 1.768.732l.001.001c.42.42.691.99.691 1.625V4.5h1.25a.75.75 0 0 1 0 1.5h-1.25V7.5h1.25a.75.75 0 0 1 0 1.5h-1.25v1.375c0 .635-.271 1.205-.691 1.625l-.001-.001c-.455.452-1.079.732-1.768.732h-.008a.75.75 0 0 1-.75-.75v-1.25H6.204v1.25a.75.75 0 0 1-.75.75h-.008c-.69 0-1.313-.28-1.768-.732l-.001-.001c-.42-.42-.691-.99-.691-1.625V9H2.5a.75.75 0 0 1 0-1.5H3.75V6H2.5a.75.75 0 0 1 0-1.5H3.75V3.125c0-.635.271-1.205.691-1.625l.001-.001c.455-.452 1.079-.732 1.768-.732h.008a.75.75 0 0 1 .75.75v1.25h3.588v-1.25zM6.954 3.125V4.5H5.458c-.262 0-.506.105-.685.283L4.77 4.787c-.178.178-.283.423-.283.685V6H3a.5.5 0 0 0 0 1h1.492v2H3a.5.5 0 0 0 0 1h1.492v1.375c0 .262.105.506.283.685l.003.003c.179.178.423.283.685.283h.008a.5.5 0 0 0 .5-.5v-1.25h3.588v1.25a.5.5 0 0 0 .5.5h.008c.262 0 .506-.105.685-.283l.003-.003c.178-.178.283-.423.283-.685V9H13a.5.5 0 0 0 0-1h-1.492V6H13a.5.5 0 0 0 0-1h-1.492V3.125c0-.262-.105-.506-.283-.685l-.003-.003A.967.967 0 0 0 10.542 2h-.008a.5.5 0 0 0-.5.5v1.25H6.954V3.125a.5.5 0 0 0-.5-.5h-.008a.967.967 0 0 0-.685.283L5.758 2.91a.967.967 0 0 0-.283.685l-.003.003v.001z"/></svg>""",
    "emoji": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 16zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path fill="currentColor" d="M4.285 9.567a.5.5 0 0 1 .683.183A3.498 3.498 0 0 0 8 11.5a3.498 3.498 0 0 0 3.032-1.75a.5.5 0 1 1 .866.5A4.498 4.498 0 0 1 8 12.5a4.498 4.498 0 0 1-3.898-2.25a.5.5 0 0 1 .183-.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z"/></svg>""",
    "link": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M6.354 5.526a.5.5 0 0 0-.708.708L7.293 8l-1.647 1.646a.5.5 0 1 0 .708.708L8 8.707l1.646 1.647a.5.5 0 0 0 .708-.708L8.707 8l1.647-1.646a.5.5 0 0 0-.708-.708L8 7.293 6.354 5.526z"/><path fill="currentColor" d="M2.5 0A2.5 2.5 0 0 0 0 2.5v11A2.5 2.5 0 0 0 2.5 16h11a2.5 2.5 0 0 0 2.5-2.5v-11A2.5 2.5 0 0 0 13.5 0h-11zM1.5 2.5A1.5 1.5 0 0 1 3 1h10a1.5 1.5 0 0 1 1.5 1.5v11a1.5 1.5 0 0 1-1.5 1.5H3A1.5 1.5 0 0 1 1.5 13.5v-11z"/></svg>""",
    "shell": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M3.479 2.404a.5.5 0 0 0-.479.438L2.5 4.5v7l.5 1.658a.5.5 0 0 0 .479.438L5.5 14h5l2.021-.5a.5.5 0 0 0 .479-.438L13.5 11.5v-7l-.5-1.658a.5.5 0 0 0-.479-.438L10.5 2h-5zM4 5h1.5v1H4V5zm2.5 0h5v1h-5V5z"/></svg>""",
    "text_file": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M4 0h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2zm0 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H4zM5 4h6v1H5V4zm0 2h6v1H5V6zm0 2h4v1H5V8z"/></svg>""",
    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8 2.5A5.5 5.5 0 0 0 2.5 8H4a4 4 0 0 1 7.54-.996l.306 1.223A.5.5 0 0 0 12.5 9H10V7.5a.5.5 0 0 0-1 0V9h-.5A5.5 5.5 0 0 0 8 2.5zM8 13.5a5.5 5.5 0 0 0 5.5-5.5H12a4 4 0 0 1-7.54.996l-.306-1.223A.5.5 0 0 0 3.5 7H6v1.5a.5.5 0 0 0 1 0V7h.5A5.5 5.5 0 0 0 8 13.5z"/></svg>""",
    "home_folder": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M6.5 14.5v-3.505c0-.245.25-.495.5-.495h2c.25 0 .5.25.5.505V14.5H11V7.097L8.354 4.854a.5.5 0 0 0-.708 0L5 7.097V14.5h1.5z"/><path fill="currentColor" d="M5.354 4.146L8 1.897l6.354 4.354a.5.5 0 0 0 .353.146H15.5a.5.5 0 0 0 .5-.5V4.5a.5.5 0 0 0-.5-.5h-1.646a.5.5 0 0 0-.354.146L8 8.103 2.5 4.146a.5.5 0 0 0-.854.353V6.5a.5.5 0 0 0 .5.5H4a.5.5 0 0 0 .354-.146L5.354 4.146zM14 5.707V14.5a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V11c0-.75-.25-1-1-1h-2c-.75 0-1 .25-1 1v3.5a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V5.707l3-2.15 3 2.15z"/></svg>""",
    "drive": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H2zm0 1h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm3 2v1h6V5H5zm0 2v1h6V7H5zm0 2v1h4V9H5z"/></svg>""",
    "close_black": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>""",
    "float_black": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 1A1.5 1.5 0 0 0 0 2.5v11A1.5 1.5 0 0 0 1.5 15h13A1.5 1.5 0 0 0 16 13.5v-11A1.5 1.5 0 0 0 14.5 1h-13zm0 1h13a.5.5 0 0 1 .5.5V4H1V2.5a.5.5 0 0 1 .5-.5z"/></svg>""", # Placeholder, needs better icon
    "maximize_black": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 1A1.5 1.5 0 0 0 0 2.5v11A1.5 1.5 0 0 0 1.5 15h13A1.5 1.5 0 0 0 16 13.5v-11A1.5 1.5 0 0 0 14.5 1h-13zm0 1h13a.5.5 0 0 1 .5.5v11a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5z"/></svg>""",
    "close_white": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>""",
    "float_white": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 1A1.5 1.5 0 0 0 0 2.5v11A1.5 1.5 0 0 0 1.5 15h13A1.5 1.5 0 0 0 16 13.5v-11A1.5 1.5 0 0 0 14.5 1h-13zm0 1h13a.5.5 0 0 1 .5.5V4H1V2.5a.5.5 0 0 1 .5-.5z"/></svg>""",
    "maximize_white": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 1A1.5 1.5 0 0 0 0 2.5v11A1.5 1.5 0 0 0 1.5 15h13A1.5 1.5 0 0 0 16 13.5v-11A1.5 1.5 0 0 0 14.5 1h-13zm0 1h13a.5.5 0 0 1 .5.5v11a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5z"/></svg>""",
    "app_icon": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M0 1.5A1.5 1.5 0 0 1 1.5 0h13A1.5 1.5 0 0 1 16 1.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13zM8 4a4 4 0 1 0 0 8a4 4 0 0 0 0-8z"/></svg>""", # Simple circle, can be GopiAI logo later
    "code": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M5.854 4.146a.5.5 0 0 1 0 .708L3.207 7.5l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0zm4.292 0a.5.5 0 0 0 0 .708L12.793 7.5l-2.647 2.646a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708 0z"/></svg>""",
    "folder_open": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" />
</svg>""",
    "play": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>""", # This was already good, but was overwritten by a placeholder
    "chat": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586L1.707 12.88A.5.5 0 0 1 1 12.5V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v10.5a1.5 1.5 0 0 0 2.25 1.31L3.56 12.5H4a1 1 0 0 1 .707.293L6.586 14H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/><path fill="currentColor" d="M5 6h6v1H5V6zm0 2h6v1H5V8z"/></svg>""",
    "debug": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M11.5 1a.5.5 0 0 1 .5.5V3h1.25a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75H12v1.5h1.25a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75H12v1.5a.5.5 0 0 1-1 0V11H5v1.5a.5.5 0 0 1-1 0V11H2.75a.75.75 0 0 1-.75-.75v-1.5A.75.75 0 0 1 2.75 8H4V6.5H2.75A.75.75 0 0 1 2 5.75v-1.5A.75.75 0 0 1 2.75 3H4V1.5a.5.5 0 0 1 .5-.5zM5 4v2.5h6V4H5zm0 3.5v2.5h6V7.5H5z"/></svg>""",
    # "file" (placeholder) был удален.
    "cut": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <circle cx="6" cy="6" r="3" />
  <path d="M8.12 8.12 12 12" />
  <path d="M20 4 8.12 15.88" />
  <circle cx="6" cy="18" r="3" />
  <path d="M14.8 14.8 20 20" />
</svg>""",
    "copy": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
</svg>""",
    "paste": """<svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <path d="M11 14h10" />
  <path d="M16 4h2a2 2 0 0 1 2 2v1.344" />
  <path d="m17 18 4-4-4-4" />
  <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 1.793-1.113" />
  <rect x="8" y="2" width="8" height="4" rx="1" />
</svg>""",
    "arrow_left": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v1a.5.5 0 0 0 .5.5h12a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.146-.354l-6-6zM2.5 8V7.707L8 2.707l5.5 5V8h-11z"/></svg>""",
    "arrow_right": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M7.646 14.854a.5.5 0 0 0 .708 0l6-6a.5.5 0 0 0 .146-.354v-1a.5.5 0 0 0-.5-.5H1.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .146.354l6 6zM13.5 8v.293L8 13.293 2.5 8V8h11z"/></svg>""",
    "arrow": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M8 16a.5.5 0 0 1-.354-.146l-6-6A.5.5 0 0 1 1.5 9.5v-1a.5.5 0 0 1 .5-.5h12a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.146.354l-6 6A.5.5 0 0 1 8 16zM2.5 9v-.293L8 3.707 13.5 9V9h-11z"/></svg>""", # Generic arrow down
    # "python_file" (placeholder) был удален.
    "markdown": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1 2.5A1.5 1.5 0 0 1 2.5 1h11A1.5 1.5 0 0 1 15 2.5v11a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 1 13.5v-11zM2.5 2a.5.5 0 0 0-.5.5v11a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5v-11a.5.5 0 0 0-.5-.5h-11zM4.5 6.5H6V10H4.5V6.5zm2.5-1h1.5L10 8l1.5-2.5h1.5L11.25 8l1.75 2.5h-1.5L10 8l-1.5 2.5H7l1.75-2.5L7 5.5z"/></svg>""",
    "flow": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M12.5 2.5a.5.5 0 0 1 0-1h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0V2.5h-1zM10 5a.5.5 0 0 1 .5-.5h1.5a.5.5 0 0 1 .5.5v1.5a.5.5 0 0 1-.5.5H10a.5.5 0 0 1-.5-.5V5zm2.5 2a.5.5 0 0 0-1 0v1.5H10a.5.5 0 0 0 0 1h1.5V11a.5.5 0 0 0 1 0V9.5H14a.5.5 0 0 0 0-1h-1.5V7a.5.5 0 0 0-.5-.5zM6 2.5a.5.5 0 0 1 0-1h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0V2.5H6zM3.5 5a.5.5 0 0 1 .5-.5H5a.5.5 0 0 1 .5.5v1.5a.5.5 0 0 1-.5.5H3.5a.5.5 0 0 1-.5-.5V5zm2.5 2a.5.5 0 0 0-1 0v1.5H3.5a.5.5 0 0 0 0 1H5V11a.5.5 0 0 0 1 0V9.5H7.5a.5.5 0 0 0 0-1H6V7a.5.5 0 0 0-.5-.5zM8.5 11.5a.5.5 0 0 1 0-1h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0v-.5h-1z"/><path fill="currentColor" d="M1.5 0A1.5 1.5 0 0 0 0 1.5v13A1.5 1.5 0 0 0 1.5 16h13a1.5 1.5 0 0 0 1.5-1.5v-13A1.5 1.5 0 0 0 14.5 0h-13zM1 1.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 .5.5v13a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-13z"/></svg>""",
    "archive": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="currentColor" d="M1.5 0A1.5 1.5 0 0 0 0 1.5V3h16V1.5A1.5 1.5 0 0 0 14.5 0h-13zM0 4.5v9A1.5 1.5 0 0 0 1.5 15h13a1.5 1.5 0 0 0 1.5-1.5v-9H0zm2 2h12v1H2v-1zm0 3h12v1H2v-1z"/></svg>""",
    # Добавляем логотип GopiAI в виде SVG
    "gopi_logo": """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
        <path fill="#81D4FA" d="M256 96c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm45 215c0 25-20 45-45 45s-45-20-45-45c0-22 16-40 37-44-9-11-16-24-21-38-32 12-55 42-55 77 0 46 37 83 83 83s83-37 83-83c0-18-6-35-16-48-2 3-5 6-8 8 11 12 17 27 17 43zm-45-170c-53 0-97 39-103 90 5 25 18 48 36 64 3-35 32-62 67-62 37 0 67 30 67 67 0 19-8 36-21 48 34-15 58-49 58-89 0-65-47-118-104-118zm69 265c-9 7-18 13-28 18l-14 29c-7 15-22 24-38 24h-14c-17 0-32-9-39-24l-24-49c-11-4-22-10-32-17l-15 3c-17 4-34-2-44-15l-7-12c-10-14-10-32-1-47l13-20c-2-8-3-16-3-24s1-16 3-24l-13-20c-9-15-9-33 1-47l7-12c10-13 27-19 44-15l24 5c9-7 18-13 28-18l14-29c7-15 22-24 38-24h14c17 0 32 9 39 24l24 49c11 4 22 10 32 17l15-3c17-4 34 2 44 15l7 12c10 14 10 32 1 47l-13 20c2 8 3 16 3 24s-1 16-3 24l13 20c9 15 9 33-1 47l-7 12c-10 13-27 19-44 15l-24-5z"/>
    </svg>"""
} # Closing brace for SVG_ICON_DATA


class IconManager:
    """Управляет иконками приложения, генерируя их из SVG строк."""

    _cache = {}
    _svg_cache = {}  # Кеш для SVG данных

    # Основной цвет иконок, который будет заменяться
    ICON_BASE_COLOR = "#2ca9bc" # Базовый цвет, который используется в SVG как fill="currentColor" или специфичный цвет

    def __init__(self):
        """Инициализирует менеджер иконок."""
        self.manifest = {} # Будет загружен из SVG_ICON_DATA или внешнего manifest.json если решим его оставить
        self._load_svg_icon_data() # Загружаем SVG строки

        # Инициализируем дополнительные библиотеки иконок
        self._init_additional_icon_libraries()

        try:
            theme_manager = ThemeManager.instance()
            theme_manager.themeChanged.connect(self.clear_cache)
            theme_manager.visualThemeChanged.connect(self.clear_cache)
        except Exception as e:
            logger.warning(f"Не удалось подключиться к сигналам менеджера тем: {e}")

    def _init_additional_icon_libraries(self):
        """Инициализирует дополнительные библиотеки иконок."""
        # Инициализируем IconFactory из iconipy для создания иконок Lucide
        if HAS_ICONIPY:
            try:
                self.icon_factory = IconFactory(
                    icon_set='lucide',
                    icon_size=24,
                    font_size=18,
                    font_color=(51, 51, 51, 255),
                    background_color=None,  # Прозрачный фон
                )
                logger.info("Библиотека iconipy успешно инициализирована для иконок Lucide")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать IconFactory: {e}")
                self.icon_factory = None
        else:
            self.icon_factory = None

    def _load_svg_icon_data(self):
        """Загружает SVG данные из словаря SVG_ICON_DATA в self.manifest."""
        # Ключи в self.manifest будут именами иконок, значения - SVG строками
        self.manifest = SVG_ICON_DATA.copy()
        logger.info(f"Загружены SVG данные для {len(self.manifest)} иконок из встроенного словаря.")

    def clear_cache(self):
        """Очищает кеш иконок при изменении темы."""
        logger.info("Очистка кеша иконок из-за изменения темы")
        self._cache = {}
        self._svg_cache = {} # Также очищаем кеш SVG данных, если он используется для файлов

    def get_icon(self, icon_name: str, color_override: Optional[str] = None, size: QSize = QSize(16,16)):
        """
        Возвращает иконку по имени, генерируя её из SVG строки.
        Цвет 'currentColor' в SVG будет заменен на color_override или цвет темы.
        """
        cache_key = f"{icon_name}_{color_override}_{size.width()}x{size.height()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if icon_name not in self.manifest:
            logger.warning(f"Иконка '{icon_name}' не найдена в манифесте SVG_ICON_DATA.")
            # Возвращаем пустую иконку или стандартную системную
            default_icon = self.get_system_icon("application-octet-stream") # Пример системной иконки
            if default_icon.isNull():
                logger.warning(f"Системная иконка по умолчанию для '{icon_name}' не найдена.")
                return QIcon()
            return default_icon

        svg_data_template = self.manifest[icon_name]
        logger.debug(f"Запрос иконки: '{icon_name}', color_override: {color_override}, size: {size.width()}x{size.height()}")
        logger.debug(f"Оригинальный SVG для '{icon_name}': {svg_data_template[:150]}...") # Логируем начало SVG

        final_color = color_override
        if final_color is None:
            try:
                theme_manager = ThemeManager.instance()
                icon_theme_color = theme_manager.get_color('icon_color')
                text_theme_color = theme_manager.get_color('text_color')
                final_color = icon_theme_color or text_theme_color or "#000000"
                logger.debug(f"Цвет из темы для '{icon_name}': icon_color='{icon_theme_color}', text_color='{text_theme_color}', выбран: '{final_color}'")
            except Exception as e:
                final_color = "#000000" # Черный по умолчанию, если тема не доступна
                logger.warning(f"Ошибка получения цвета из ThemeManager для '{icon_name}': {e}. Используется цвет по умолчанию: {final_color}")
        else:
            logger.debug(f"Используется color_override для '{icon_name}': {final_color}")


        # Для иконки python используем ее собственные цвета, если не передан color_override
        if icon_name == "python" and color_override is None:
            svg_data = svg_data_template
            logger.debug(f"Для иконки 'python' без color_override цвета не заменяются.")
        else:
            # Заменяем currentColor или ICON_BASE_COLOR на final_color
            svg_data = svg_data_template
            was_replaced = False

            # Паттерн для поиска атрибутов (fill, stroke) со значением currentColor
            # Ищет: fill="currentColor", stroke='currentColor' и т.д.
            # \bcurrentColor\b гарантирует, что мы заменяем целое слово "currentColor"
            pattern_currentColor = re.compile(r'(fill|stroke)=(["\'])\bcurrentColor\b\2')

            # Функция для замены
            def replace_with_final_color(match):
                nonlocal was_replaced
                was_replaced = True
                attribute = match.group(1)
                quote = match.group(2)
                logger.debug(f"Найдено '{attribute}=\"{quote}currentColor{quote}\"' для замены на '{final_color}' в иконке '{icon_name}'.")
                return f'{attribute}={quote}{final_color}{quote}'

            svg_data = pattern_currentColor.sub(replace_with_final_color, svg_data)

            if was_replaced:
                logger.debug(f"Произведена замена 'currentColor' на '{final_color}' для '{icon_name}' с использованием regex.")

            # Если currentColor не был найден и заменен, пробуем заменить ICON_BASE_COLOR
            if not was_replaced:
                # Проверяем наличие ICON_BASE_COLOR в атрибутах fill или stroke
                pattern_base_color = re.compile(r'(fill|stroke)=(["\'])\b' + re.escape(self.ICON_BASE_COLOR) + r'\b\2')

                def replace_base_color(match):
                    nonlocal was_replaced
                    was_replaced = True
                    attribute = match.group(1)
                    quote = match.group(2)
                    logger.debug(f"Найдено '{attribute}=\"{quote}{self.ICON_BASE_COLOR}{quote}\"' для замены на '{final_color}' в иконке '{icon_name}'.")
                    return f'{attribute}={quote}{final_color}{quote}'

                svg_data = pattern_base_color.sub(replace_base_color, svg_data)
                if was_replaced:
                    logger.debug(f"Произведена замена базового цвета '{self.ICON_BASE_COLOR}' на '{final_color}' для '{icon_name}' с использованием regex.")

            if not was_replaced:
                 logger.debug(f"Для '{icon_name}' не найдены 'currentColor' или '{self.ICON_BASE_COLOR}' в атрибутах fill/stroke для замены. Используется оригинальный SVG (или SVG после других модификаций, если они были).")

        logger.debug(f"Обработанный SVG для '{icon_name}' (перед рендерингом): {svg_data[:150]}...")

        try:
            svg_bytes = QByteArray(svg_data.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)

            if not renderer.isValid():
                logger.error(f"Невалидный SVG для иконки '{icon_name}'. Данные SVG: {svg_data[:100]}...")
                return self.get_system_icon("image-missing") # Возвращаем иконку "файл не найден"

            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent) # Прозрачный фон
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            if pixmap.isNull():
                logger.error(f"Не удалось создать QPixmap для иконки '{icon_name}'.")
                return self.get_system_icon("image-missing")

            icon = QIcon(pixmap)
            self._cache[cache_key] = icon
            return icon
        except Exception as e:
            logger.error(f"Ошибка при рендеринге SVG для иконки '{icon_name}': {e}. Данные SVG: {svg_data[:100]}...")
            return self.get_system_icon("image-missing")


    def get_system_icon(self, name):
        """
        Получает системную иконку, если она доступна.
        """
        system_icon_map = {
            "document": ["text-x-generic", "document", "accessories-text-editor"],
            # ... (можно добавить другие системные иконки при необходимости)
            "image-missing": ["image-missing", "gtk-missing-image"],
            "application-octet-stream": ["application-octet-stream", "unknown"]
        }
        if name in system_icon_map:
            for icon_name_candidate in system_icon_map[name]:
                icon = QIcon.fromTheme(icon_name_candidate)
                if not icon.isNull():
                    return icon
        else:
            # Если имя не в нашей карте, пробуем напрямую
            icon = QIcon.fromTheme(name)
            if not icon.isNull():
                return icon
        return QIcon() # Возвращаем пустую иконку, если ничего не найдено

    def list_available_icons(self):
        """Returns a list of available icon names."""
        return list(self.manifest.keys())

    def get_modern_icon(self, name: str, color: Optional[str] = None, size: int = 24) -> QIcon:
        """
        Получает современную иконку из установленных библиотек иконок.

        Args:
            name: Имя иконки.
            color: Цвет иконки (в формате hex строки или названия цвета).
            size: Размер иконки в пикселях.

        Returns:
            QIcon: Объект иконки.
        """
        # Ключ для кеша, учитывающий имя, цвет и размер
        cache_key = f"modern_{name}_{color}_{size}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        icon = QIcon()  # Пустая иконка по умолчанию

        # Пробуем получить иконку через tabler-qicon
        if HAS_TABLERQICON:
            try:
                # Создаем кастомизированную иконку TablerQIcon
                tabler_icon = TablerQIcon(color=color) if color else TablerQIcon()
                # Пытаемся получить иконку по имени как атрибут
                if hasattr(tabler_icon, name):
                    icon = getattr(tabler_icon, name)
                    logger.debug(f"Иконка '{name}' получена через TablerQIcon")
                    self._cache[cache_key] = icon
                    return icon
            except Exception as e:
                logger.debug(f"Не удалось получить иконку '{name}' через TablerQIcon: {e}")

        # Пробуем получить иконку через pytablericons
        if HAS_PYTABLERICONS and not icon.isNull():
            try:
                # Сначала пробуем как OutlineIcon
                if hasattr(OutlineIcon, name.upper()):
                    pil_icon = TablerIcons.load(
                        getattr(OutlineIcon, name.upper()),
                        color=color if color else "#000000",
                        size=size
                    )
                    # Преобразуем PIL Image в QIcon
                    pixmap = QPixmap.fromImage(QImage(
                        pil_icon.tobytes(),
                        pil_icon.width,
                        pil_icon.height,
                        QImage.Format_RGBA8888
                    ))
                    icon = QIcon(pixmap)
                    logger.debug(f"Иконка '{name}' получена через pytablericons (OutlineIcon)")
                    self._cache[cache_key] = icon
                    return icon
                # Если не нашли, пробуем как FilledIcon
                elif hasattr(FilledIcon, name.upper()):
                    pil_icon = TablerIcons.load(
                        getattr(FilledIcon, name.upper()),
                        color=color if color else "#000000",
                        size=size
                    )
                    # Преобразуем PIL Image в QIcon
                    pixmap = QPixmap.fromImage(QImage(
                        pil_icon.tobytes(),
                        pil_icon.width,
                        pil_icon.height,
                        QImage.Format_RGBA8888
                    ))
                    icon = QIcon(pixmap)
                    logger.debug(f"Иконка '{name}' получена через pytablericons (FilledIcon)")
                    self._cache[cache_key] = icon
                    return icon
            except Exception as e:
                logger.debug(f"Не удалось получить иконку '{name}' через pytablericons: {e}")

        # Пробуем получить иконку через qtawesome
        if HAS_QTAWESOME and not icon.isNull():
            try:
                # Пробуем различные префиксы иконок
                prefixes = ['fa6s', 'fa6', 'fa6b', 'mdi6', 'ph', 'ri', 'msc']
                for prefix in prefixes:
                    try:
                        icon = qta.icon(f"{prefix}.{name}", color=color)
                        if not icon.isNull():
                            logger.debug(f"Иконка '{name}' получена через qtawesome с префиксом '{prefix}'")
                            self._cache[cache_key] = icon
                            return icon
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Не удалось получить иконку '{name}' через qtawesome: {e}")

        # Пробуем создать иконку через iconipy (Lucide)
        if HAS_ICONIPY and self.icon_factory and not icon.isNull():
            try:
                # Получаем иконку как QPixmap
                pixmap = self.icon_factory.asQPixmap(name)
                if pixmap:
                    icon = QIcon(pixmap)
                    logger.debug(f"Иконка '{name}' получена через iconipy (Lucide)")
                    self._cache[cache_key] = icon
                    return icon
            except Exception as e:
                logger.debug(f"Не удалось получить иконку '{name}' через iconipy: {e}")

        # Если все способы не удались, пробуем получить встроенную иконку
        if not icon.isNull():
            try:
                icon = self.get_icon(name, color=color, size=QSize(size, size))
                if not icon.isNull():
                    logger.debug(f"Иконка '{name}' получена через встроенные SVG данные")
                    self._cache[cache_key] = icon
                    return icon
            except Exception as e:
                logger.debug(f"Не удалось получить иконку '{name}' через встроенные SVG данные: {e}")

        # Если ничего не нашли, возвращаем системную иконку или пустую
        if not icon.isNull():
            icon = self.get_system_icon(name)
            if not icon.isNull():
                logger.debug(f"Иконка '{name}' получена через системные иконки")
                self._cache[cache_key] = icon
                return icon

        logger.warning(f"Не удалось найти иконку '{name}' ни в одном из доступных источников")
        return icon

    def get_available_icon_sets(self) -> Dict[str, Set[str]]:
        """
        Получает список доступных наборов иконок и их элементов.

        Returns:
            Dict[str, Set[str]]: Словарь, где ключи - названия наборов, значения - множества имен иконок.
        """
        result = {
            'svg_builtin': set(self.manifest.keys())
        }

        # Добавляем иконки из TablerQIcon
        if HAS_TABLERQICON:
            try:
                result['tabler_qicon'] = set(TablerQIcon.get_icon_names())
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из TablerQIcon: {e}")

        # Добавляем иконки из pytablericons
        if HAS_PYTABLERICONS:
            try:
                # Получаем названия иконок из OutlineIcon и FilledIcon
                outline_icons = {name.lower() for name in dir(OutlineIcon) if not name.startswith('_')}
                filled_icons = {name.lower() for name in dir(FilledIcon) if not name.startswith('_')}
                result['pytabler_outline'] = outline_icons
                result['pytabler_filled'] = filled_icons
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из pytablericons: {e}")

        # Добавляем иконки из qtawesome
        if HAS_QTAWESOME:
            try:
                prefixes = ['fa6s', 'fa6', 'fa6b', 'mdi6', 'ph', 'ri', 'msc']
                for prefix in prefixes:
                    result[f'qtawesome_{prefix}'] = set()
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из qtawesome: {e}")

        # Добавляем иконки из iconipy
        if HAS_ICONIPY and self.icon_factory:
            try:
                result['lucide'] = set(self.icon_factory.icon_names)
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из iconipy: {e}")

        return result

    def list_all_available_icons(self) -> List[str]:
        """
        Возвращает список всех доступных иконок из всех источников.

        Returns:
            List[str]: Список названий всех доступных иконок.
        """
        all_icons = set()

        # Добавляем встроенные иконки
        all_icons.update(self.manifest.keys())

        # Добавляем иконки из TablerQIcon
        if HAS_TABLERQICON:
            try:
                all_icons.update(TablerQIcon.get_icon_names())
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из TablerQIcon: {e}")

        # Добавляем иконки из pytablericons
        if HAS_PYTABLERICONS:
            try:
                # Получаем названия иконок из OutlineIcon и FilledIcon
                for name in dir(OutlineIcon):
                    if not name.startswith('_'):
                        all_icons.add(name.lower())
                for name in dir(FilledIcon):
                    if not name.startswith('_'):
                        all_icons.add(name.lower())
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из pytablericons: {e}")

        # Добавляем иконки из iconipy
        if HAS_ICONIPY and self.icon_factory:
            try:
                all_icons.update(self.icon_factory.icon_names)
            except Exception as e:
                logger.warning(f"Не удалось получить список иконок из iconipy: {e}")

        return sorted(list(all_icons))

# Глобальные функции больше не нужны, так как IconManager не Singleton

class IconBrowser(QWidget):
    """Виджет для просмотра и выбора иконок."""

    iconSelected = Signal(str)  # Сигнал, отправляемый при выборе иконки

    def __init__(self, icon_manager: IconManager, parent=None):
        """
        Инициализирует браузер иконок.

        Args:
            icon_manager: Менеджер иконок.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.icon_manager = icon_manager
        self.icon_size = 32
        self.icon_color = None
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        main_layout = QVBoxLayout(self)

        # Верхняя панель поиска и фильтрации
        top_panel = QHBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск иконок...")
        self.search_input.textChanged.connect(self._filter_icons)
        top_panel.addWidget(self.search_input)

        # Выбор набора иконок
        self.icon_set_combo = QComboBox()
        self._fill_icon_sets()
        self.icon_set_combo.currentIndexChanged.connect(self._filter_icons)
        top_panel.addWidget(self.icon_set_combo)

        main_layout.addLayout(top_panel)

        # Область прокрутки для иконок
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Контейнер для сетки иконок
        self.icons_container = QWidget()
        self.icons_grid = QGridLayout(self.icons_container)
        self.icons_grid.setSpacing(10)

        scroll_area.setWidget(self.icons_container)
        main_layout.addWidget(scroll_area)

        # Статусная строка
        self.status_label = QLabel("Готов")
        main_layout.addWidget(self.status_label)

        # Заполняем иконками
        self._populate_icons()

        self.setWindowTitle("Браузер иконок")
        self.resize(800, 600)

    def _fill_icon_sets(self):
        """Заполняет выпадающий список наборов иконок."""
        self.icon_set_combo.addItem("Все наборы", "all")

        icon_sets = self.icon_manager.get_available_icon_sets()
        for set_name, icons in icon_sets.items():
            if icons:  # Только если набор не пустой
                display_name = set_name.replace('_', ' ').title()
                self.icon_set_combo.addItem(f"{display_name} ({len(icons)})", set_name)

    def _populate_icons(self):
        """Заполняет сетку иконками."""
        # Очищаем существующие иконки
        while self.icons_grid.count():
            item = self.icons_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Получаем список иконок для отображения
        icons = self._get_filtered_icons()

        # Заполняем сетку
        row, col = 0, 0
        max_cols = 8  # Максимальное количество столбцов

        for icon_name in icons:
            icon_button = QPushButton()
            icon_button.setFixedSize(80, 80)

            # Получаем иконку
            icon = self.icon_manager.get_modern_icon(icon_name, color=self.icon_color, size=self.icon_size)
            icon_button.setIcon(icon)
            icon_button.setIconSize(QSize(self.icon_size, self.icon_size))

            # Добавляем название иконки
            icon_button.setText(icon_name)
            icon_button.setToolTip(icon_name)

            # Настраиваем стиль кнопки
            icon_button.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding-top: 40px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

            # Подключаем сигнал клика
            icon_button.clicked.connect(lambda checked=False, name=icon_name: self._on_icon_selected(name))

            # Добавляем кнопку в сетку
            self.icons_grid.addWidget(icon_button, row, col)

            # Переходим к следующей позиции
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.status_label.setText(f"Найдено {len(icons)} иконок")

    def _get_filtered_icons(self) -> List[str]:
        """
        Получает отфильтрованный список иконок.

        Returns:
            List[str]: Отфильтрованный список иконок.
        """
        search_text = self.search_input.text().lower()
        selected_set = self.icon_set_combo.currentData()

        if selected_set == "all":
            # Все иконки
            all_icons = self.icon_manager.list_all_available_icons()
            if search_text:
                return [name for name in all_icons if search_text in name.lower()]
            return all_icons[:200]  # Ограничиваем количество, чтобы не перегружать UI
        else:
            # Иконки из конкретного набора
            icon_sets = self.icon_manager.get_available_icon_sets()
            if selected_set in icon_sets:
                icons = list(icon_sets[selected_set])
                if search_text:
                    return [name for name in icons if search_text in name.lower()]
                return icons[:200]  # Ограничиваем количество
            return []

    def _filter_icons(self):
        """Фильтрует иконки по поисковому запросу и выбранному набору."""
        self._populate_icons()

    def _on_icon_selected(self, icon_name: str):
        """
        Обрабатывает выбор иконки.

        Args:
            icon_name: Имя выбранной иконки.
        """
        self.iconSelected.emit(icon_name)
        self.status_label.setText(f"Выбрана иконка: {icon_name}")

    def set_icon_size(self, size: int):
        """
        Устанавливает размер иконок.

        Args:
            size: Размер иконок в пикселях.
        """
        self.icon_size = size
        self._populate_icons()

    def set_icon_color(self, color: Optional[str]):
        """
        Устанавливает цвет иконок.

        Args:
            color: Цвет иконок (hex-строка или имя цвета).
        """
        self.icon_color = color
        self._populate_icons()

def show_icon_browser(icon_manager: IconManager, callback: Optional[Callable[[str], None]] = None) -> QDialog:
    """
    Показывает диалог выбора иконки.

    Args:
        icon_manager: Менеджер иконок.
        callback: Функция обратного вызова, вызываемая при выборе иконки.

    Returns:
        QDialog: Объект диалога.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Выбор иконки")
    dialog.resize(800, 600)

    layout = QVBoxLayout(dialog)

    browser = IconBrowser(icon_manager)
    if callback:
        browser.iconSelected.connect(callback)
    browser.iconSelected.connect(dialog.accept)

    layout.addWidget(browser)

    # Добавляем кнопки управления
    controls_layout = QHBoxLayout()

    # Выбор размера иконок
    size_combo = QComboBox()
    size_combo.addItem("16x16", 16)
    size_combo.addItem("24x24", 24)
    size_combo.addItem("32x32", 32)
    size_combo.addItem("48x48", 48)
    size_combo.setCurrentIndex(2)  # 32x32 по умолчанию
    size_combo.currentIndexChanged.connect(lambda: browser.set_icon_size(size_combo.currentData()))

    controls_layout.addWidget(QLabel("Размер:"))
    controls_layout.addWidget(size_combo)

    # Выбор цвета иконок
    color_combo = QComboBox()
    color_combo.addItem("По умолчанию", None)
    color_combo.addItem("Черный", "#000000")
    color_combo.addItem("Белый", "#ffffff")
    color_combo.addItem("Красный", "#ff0000")
    color_combo.addItem("Зеленый", "#00ff00")
    color_combo.addItem("Синий", "#0000ff")
    color_combo.addItem("Серый", "#808080")

    color_combo.currentIndexChanged.connect(lambda: browser.set_icon_color(color_combo.currentData()))

    controls_layout.addWidget(QLabel("Цвет:"))
    controls_layout.addWidget(color_combo)

    controls_layout.addStretch()

    # Кнопка отмены
    cancel_button = QPushButton("Отмена")
    cancel_button.clicked.connect(dialog.reject)
    controls_layout.addWidget(cancel_button)

    layout.addLayout(controls_layout)

    dialog.setLayout(layout)
    dialog.setModal(True)
    dialog.show()

    return dialog
