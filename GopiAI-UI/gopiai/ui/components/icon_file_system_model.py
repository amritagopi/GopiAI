"""
GopiAI Universal Icon Manager - Универсальный менеджер иконок
==========================================================

Универсальный менеджер иконок, который работает с разными источниками:
1. Lucide SVG иконки из node_modules
2. Локальные SVG иконки из assets
3. Системные иконки

Автор: Crazy Coder  
Версия: 1.0.0
"""
import sys
from pathlib import Path
from typing import Optional, Union
import logging

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtGui import QPainter

# Константы
RenderHints = {
    "Antialiasing": QPainter.RenderHint.Antialiasing,
}
QtConstants = {
    "transparent": Qt.GlobalColor.transparent,
    "AlignCenter": Qt.AlignmentFlag.AlignCenter,
}

# Настройка логгера
logger = logging.getLogger("icon_manager")
handler = logging.StreamHandler(sys.stdout)
# Убираем параметр encoding, так как он не поддерживается в logging.Formatter
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class UniversalIconManager:
    """Универсальный менеджер иконок"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Получение синглтон-экземпляра"""
        if cls._instance is None:
            cls._instance = UniversalIconManager()
        return cls._instance
    
    def __init__(self):
        """Инициализация менеджера иконок"""
        self.icon_cache = {}
        self.lucide_manager = None
        self.fallback_icons = {}
        self._fallback_icons_created = False
        
        # Пытаемся инициализировать Lucide менеджер
        self._init_lucide_manager()
        
        # Логируем статус
        if self.lucide_manager:
            logger.info(f"Инициализирован UniversalIconManager с Lucide иконками")
        else:            
            logger.warning("Инициализирован UniversalIconManager без Lucide иконок")
    
    def _init_lucide_manager(self):
        """Инициализация Lucide менеджера иконок"""
        try:
            # Создаем словарь для хранения Lucide иконок
            self.lucide_icons = {}
            
            # Путь к директории с SVG иконками Lucide
            lucide_icons_dir = Path(__file__).parent.parent / "assets" / "icons" / "lucide"
            
            # Проверяем существование директории
            if lucide_icons_dir.exists() and lucide_icons_dir.is_dir():
                # Сканируем директорию с SVG файлами
                for svg_file in lucide_icons_dir.glob("*.svg"):
                    icon_name = svg_file.stem
                    with open(svg_file, 'r', encoding='utf-8') as f:
                        self.lucide_icons[icon_name] = f.read()
                
                logger.info(f"[OK] Загружено {len(self.lucide_icons)} Lucide иконок")
                self.lucide_manager = self  # Используем себя в качестве менеджера
                return True
            else:
                logger.warning(f"Директория с Lucide иконками не найдена: {lucide_icons_dir}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при инициализации Lucide иконок: {e}")
            return False
    
    def _create_fallback_icons(self):
        """Создает базовые fallback иконки (lazy loading)"""
        if self._fallback_icons_created:
            return
            
        # Базовые иконки для часто используемых действий
        icons = {
            "file-plus": self._create_file_plus_icon,
            "folder-open": self._create_folder_open_icon,
            "save": self._create_save_icon,
            "settings": self._create_settings_icon,
            "x": self._create_close_icon,
            "plus": self._create_plus_icon,
            "minus": self._create_minus_icon,
            "menu": self._create_menu_icon,
            "maximize": self._create_maximize_icon,
            "minimize": self._create_minimize_icon,
        }
        
        # Создаем иконки размером 24x24
        size = QSize(24, 24)
        for name, creator_func in icons.items():
            self.fallback_icons[name] = creator_func(size)
            
        self._fallback_icons_created = True
    
    def get_icon(self, icon_name: str, color: Optional[str] = None, size: Union[QSize, int] = 24) -> QIcon:
        """
        Получает иконку по имени
        
        Args:
            icon_name: Имя иконки
            color: Цвет иконки (опционально)
            size: Размер иконки в пикселях или QSize
            
        Returns:
            QIcon: Иконка
        """
        # Нормализуем размер
        if isinstance(size, int):
            size = QSize(size, size)
        
        # Создаем ключ для кеша
        cache_key = f"{icon_name}_{color}_{size.width()}x{size.height()}"
        
        # Проверяем кеш
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]        # Пытаемся получить иконку из Lucide
        icon = None
        if self.lucide_manager is self and hasattr(self, 'lucide_icons'):
            # Используем встроенный менеджер Lucide иконок
            try:
                if icon_name in self.lucide_icons:
                    # Создаем QIcon из SVG данных
                    svg_data = self.lucide_icons[icon_name]
                    if color:
                        # Заменяем цвет в SVG, если указан
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtGui import QPixmap, QPainter
                        
                        # Создаем временный QPixmap для отрисовки иконки
                        pixmap = QPixmap(size)
                        pixmap.fill(Qt.GlobalColor.transparent)
                        
                        # Создаем рендерер SVG
                        renderer = QSvgRenderer(bytes(svg_data, 'utf-8'))
                        
                        # Отрисовываем SVG на QPixmap с нужным цветом
                        painter = QPainter(pixmap)
                        renderer.render(painter)
                        
                        # Создаем QIcon из QPixmap
                        icon = QIcon(pixmap)
                        painter.end()
                    else:
                        # Создаем QIcon напрямую из SVG данных, если цвет не указан
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtGui import QPixmap, QPainter

                        pixmap = QPixmap(size)
                        pixmap.fill(Qt.GlobalColor.transparent)
                        
                        renderer = QSvgRenderer(bytes(svg_data, 'utf-8'))
                        
                        painter = QPainter(pixmap)
                        renderer.render(painter)
                        painter.end()
                        
                        icon = QIcon(pixmap)
                    
                    logger.debug(f"Загружена Lucide иконка: {icon_name}")
                else:
                    logger.debug(f"Lucide иконка не найдена: {icon_name}")
            except Exception as e:
                logger.error(f"Ошибка при создании иконки {icon_name} из SVG: {e}")
                icon = None
        elif self.lucide_manager and self.lucide_manager is not self:
            # Используем внешний менеджер Lucide иконок, если он есть
            try:
                if hasattr(self.lucide_manager, "get_icon"):
                    icon = self.lucide_manager.get_icon(icon_name, color, size)
                elif hasattr(self.lucide_manager, "get_lucide_icon"):
                    icon = self.lucide_manager.get_lucide_icon(icon_name, color, size)
            except Exception as e:
                logger.debug(f"Ошибка при получении иконки {icon_name} из внешнего LucideIconManager: {e}")
                icon = None
        
        # Если иконка не получена, используем fallback
        if icon is None:
            # Пытаемся загрузить SVG файл
            icon = self._load_svg_icon(icon_name, size)
            
        # Если все еще нет иконки, используем fallback
        if icon is None:
            # Создаем fallback иконки при первом обращении
            self._create_fallback_icons()
            
            # Проверяем fallback иконки
            if icon_name in self.fallback_icons:
                icon = self.fallback_icons[icon_name]
            else:
                # Создаем универсальную fallback иконку
                icon = self._create_fallback_icon(icon_name, size)
          # Кешируем и возвращаем результат
        self.icon_cache[cache_key] = icon
        return icon

    def get_lucide_icon(self, icon_name: str, color: Optional[str] = None, size: Union[QSize, int] = 24) -> QIcon:
        """
        Совместимый шим-метод для Lucide: перенаправляет в get_icon.
        Нужен для совместимости с внешними вызовами и статической типизацией (Pyright).
        """
        return self.get_icon(icon_name, color, size)
    
    def _load_svg_icon(self, icon_name: str, size: QSize) -> Optional[QIcon]:
        """Загружает SVG иконку из файловой системы"""
        # Пути для поиска иконок
        icon_paths = [
            Path(__file__).parent.parent / "assets" / "icons" / "lucide" / f"{icon_name}.svg",
            Path(__file__).parent.parent.parent.parent / "GopiAI" / "GopiAI-Assets" / "gopiai" / "assets" / "icons" / "lucide" / f"{icon_name}.svg"        ]
        
        for svg_path in icon_paths:
            if svg_path.exists():
                # print(f"[OK] Загружаем SVG иконку: {svg_path}")
                icon = QIcon(str(svg_path))
                if not icon.isNull():
                    return icon
                else:
                    # print(f"[ERROR] Не удалось загрузить SVG: {svg_path}")
                    pass
        
        # print(f"[ERROR] SVG иконка не найдена: {icon_name}")
        return None
    
    def _create_fallback_icon(self, icon_name: str, size: QSize) -> QIcon:
        """Создает универсальную fallback иконку с первой буквой имени"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем рамку
        painter.setPen(QColor("#888888"))
        painter.drawRect(1, 1, size.width() - 2, size.height() - 2)
        
        # Рисуем первую букву
        if icon_name:
            font = painter.font()
            font.setPixelSize(size.width() // 2)
            painter.setFont(font)
            painter.drawText(
                0, 0, size.width(), size.height(), 
                Qt.AlignmentFlag.AlignCenter, 
                icon_name[0].upper()
            )       
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    # Методы для создания базовых иконок
    def _create_file_plus_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Новый файл'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем документ
        painter.setPen(QColor("#444444"))
        painter.drawRect(size.width() // 4, size.height() // 8, 
                         size.width() // 2, size.height() * 3 // 4)
        
        # Рисуем +
        painter.drawLine(size.width() * 3 // 8, size.height() // 2, 
                         size.width() * 5 // 8, size.height() // 2)
        painter.drawLine(size.width() // 2, size.height() * 3 // 8,
                         size.width() // 2, size.height() * 5 // 8)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_folder_open_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Открыть папку'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем папку
        painter.setPen(QColor("#444444"))
        painter.drawRect(size.width() // 6, size.height() // 3, 
                         size.width() * 2 // 3, size.height() // 2)
        painter.drawLine(size.width() // 6, size.height() // 3,
                        size.width() // 3, size.height() // 4)
        painter.drawLine(size.width() // 3, size.height() // 4,
                        size.width() * 5 // 6, size.height() // 4)
        painter.drawLine(size.width() * 5 // 6, size.height() // 4,
                        size.width() * 5 // 6, size.height() // 3)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_save_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Сохранить'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем дискету
        painter.setPen(QColor("#444444"))
        painter.drawRect(size.width() // 4, size.height() // 4, 
                         size.width() // 2, size.height() // 2)
        
        # Рисуем внутреннюю часть
        painter.drawRect(size.width() // 3, size.height() // 3, 
                         size.width() // 3, size.height() // 4)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_settings_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Настройки'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем шестеренку
        painter.setPen(QColor("#444444"))
        
        # Круг в центре
        center_x = size.width() // 2
        center_y = size.height() // 2
        radius = min(size.width(), size.height()) // 4
        
        painter.drawEllipse(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2)
        
        # Линии "зубцы"
        for i in range(8):
            angle = i * 45 * 3.14159 / 180
            painter.drawLine(
                center_x + int(radius * 1.2 * (i % 2 + 1) * (0 if i % 2 else 1)),
                center_y,
                center_x + int(radius * 1.8 * (i % 2 + 1) * (0 if i % 2 else 1)),
                center_y
            )
            painter.drawLine(
                center_x,
                center_y + int(radius * 1.2 * (i % 2 + 1) * (0 if i % 2 else 1)),
                center_x,
                center_y + int(radius * 1.8 * (i % 2 + 1) * (0 if i % 2 else 1))
            )
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_close_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Закрыть' (X)"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем X
        painter.setPen(QColor("#444444"))
        margin = size.width() // 4
        painter.drawLine(margin, margin, 
                         size.width() - margin, size.height() - margin)
        painter.drawLine(margin, size.height() - margin,
                         size.width() - margin, margin)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_plus_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Плюс'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем +
        painter.setPen(QColor("#444444"))
        margin = size.width() // 4
        painter.drawLine(margin, size.height() // 2, 
                         size.width() - margin, size.height() // 2)
        painter.drawLine(size.width() // 2, margin,
                         size.width() // 2, size.height() - margin)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_minus_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Минус'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем -
        painter.setPen(QColor("#444444"))
        margin = size.width() // 4
        painter.drawLine(margin, size.height() // 2, 
                         size.width() - margin, size.height() // 2)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_menu_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Меню'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем три линии
        painter.setPen(QColor("#444444"))
        margin = size.width() // 6
        line_height = size.height() // 3
        
        painter.drawLine(margin, line_height, 
                         size.width() - margin, line_height)
        painter.drawLine(margin, line_height * 2, 
                         size.width() - margin, line_height * 2)
        painter.drawLine(margin, line_height * 3, 
                         size.width() - margin, line_height * 3)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_maximize_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Развернуть'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем прямоугольник
        painter.setPen(QColor("#444444"))
        margin = size.width() // 4
        
        painter.drawRect(margin, margin, 
                         size.width() - margin * 2, 
                         size.height() - margin * 2)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
    
    def _create_minimize_icon(self, size: QSize) -> QIcon:
        """Создает иконку 'Свернуть'"""
        icon = QIcon()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем линию внизу
        painter.setPen(QColor("#444444"))
        margin = size.width() // 4
        
        painter.drawLine(margin, size.height() * 2 // 3, 
                         size.width() - margin, size.height() * 2 // 3)
        
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon


# Функция-хелпер для получения иконки
def get_icon(icon_name: str, color: Optional[str] = None, size: Union[QSize, int] = 24) -> QIcon:
    """
    Получает иконку по имени из универсального менеджера иконок
    
    Args:
        icon_name: Имя иконки
        color: Цвет иконки (опционально)
        size: Размер иконки в пикселях или QSize
        
    Returns:
        QIcon: Иконка
    """
    return UniversalIconManager.instance().get_icon(icon_name, color, size)
