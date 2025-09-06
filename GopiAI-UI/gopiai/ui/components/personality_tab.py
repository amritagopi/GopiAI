#!/usr/bin/env python3
"""
Personality Tab для GopiAI UI
Вкладка для редактирования описания ассистента Гипатии
"""

import logging
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPlainTextEdit, QMessageBox
)
from PySide6.QtGui import QFont

from gopiai.ui.utils.icon_helpers import create_icon_button

logger = logging.getLogger(__name__)

class PersonalityTab(QWidget):
    """Вкладка для редактирования персонализации Гипатии"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.personality_file = None
        
        self._find_personality_file()
        self._setup_ui()
        self._setup_connections()
        self._load_personality_text()
        
        logger.info("PersonalityTab инициализирован")
    
    def _find_personality_file(self):
        """Находит файл Personality"""
        try:
            # Список возможных путей к файлу Personality
            candidates = []
            
            # 1) Проверяем GOPI_AI_MODULES окружение
            gopi_ai_modules = os.environ.get("GOPI_AI_MODULES")
            if gopi_ai_modules:
                candidates.append(os.path.join(gopi_ai_modules, "GopiAI-CrewAI", "tools", "gopiai_integration", "Personality"))
            
            # 2) Проверяем GOPI_AI_ROOT окружение
            gopi_ai_root = os.environ.get("GOPI_AI_ROOT")
            if gopi_ai_root:
                candidates.append(os.path.join(gopi_ai_root, "GopiAI-CrewAI", "tools", "gopiai_integration", "Personality"))
            
            # 3) Проверяем относительный путь от UI директории
            ui_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            candidates.extend([
                os.path.join(ui_dir, "GopiAI-CrewAI", "tools", "gopiai_integration", "Personality"),
                os.path.join(ui_dir, "..", "GopiAI-CrewAI", "tools", "gopiai_integration", "Personality")
            ])
            
            # 4) Проверяем текущий рабочий каталог и известные пути
            candidates.extend([
                os.path.join(os.getcwd(), "GopiAI-CrewAI", "tools", "gopiai_integration", "Personality"),
                "/home/amritagopi/GopiAI/GopiAI-CrewAI/tools/gopiai_integration/Personality",
                "c:\\Users\\crazy\\GOPI_AI_MODULES\\GopiAI-CrewAI\\tools\\gopiai_integration\\Personality"
            ])

            for path in candidates:
                if os.path.exists(path):
                    self.personality_file = path
                    logger.info(f"Найден файл Personality: {path}")
                    break
            
            if not self.personality_file:
                logger.error("Файл Personality не найден")
                
        except Exception as e:
            logger.error(f"Ошибка поиска Personality: {e}")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Персонализация Гипатии")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Описание
        desc_label = QLabel("Здесь вы можете редактировать личность и характер ассистента Гипатии. Текст отображается в удобном для чтения виде без технических элементов.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Текстовое поле для редактирования
        self.personality_editor = QPlainTextEdit()
        self.personality_editor.setPlaceholderText("Загрузка описания личности Гипатии...")
        
        # Устанавливаем читабельный шрифт (не моноширинный)
        font = QFont()
        font.setFamily("Segoe UI")  # Используем системный шрифт
        font.setPointSize(11)
        self.personality_editor.setFont(font)
        
        layout.addWidget(self.personality_editor)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.load_btn = create_icon_button("folder-open", "Перезагрузить описание личности из файла")
        buttons_layout.addWidget(self.load_btn)
        
        self.save_btn = create_icon_button("save", "Сохранить изменения в файл Personality")
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = create_icon_button("rotate-ccw", "Отменить несохранённые изменения")
        buttons_layout.addWidget(self.reset_btn)
        
        buttons_layout.addStretch()
        
        # Статус
        self.status_label = QLabel("Готов к редактированию")
        buttons_layout.addWidget(self.status_label)
        
        layout.addLayout(buttons_layout)
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.load_btn.clicked.connect(self._load_personality_text)
        self.save_btn.clicked.connect(self._save_personality_text)
        self.reset_btn.clicked.connect(self._reset_personality_text)
    
    def _load_personality_text(self):
        """Загружает текст персонализации из файла Personality"""
        if not self.personality_file or not os.path.exists(self.personality_file):
            self.status_label.setText("Ошибка: файл Personality не найден")
            return
        
        try:
            # Читаем весь файл Personality
            with open(self.personality_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Убираем первую строку с комментарием, если она есть
            lines = file_content.splitlines()
            if lines and lines[0].startswith('#'):
                # Пропускаем первую строку и пустую строку после неё (если есть)
                start_idx = 1
                if len(lines) > 1 and lines[1].strip() == '':
                    start_idx = 2
                personality_text = '\n'.join(lines[start_idx:])
            else:
                personality_text = file_content
            
            # Удаляем завершающие тройные кавычки если есть
            personality_text = personality_text.rstrip()
            if personality_text.endswith('"""'):
                personality_text = personality_text[:-3].rstrip()
            
            self.personality_editor.setPlainText(personality_text)
            self.status_label.setText("Текст загружен успешно")
            logger.info("Текст персонализации загружен из файла Personality")
        
        except Exception as e:
            self.status_label.setText(f"Ошибка загрузки: {e}")
            logger.error(f"Ошибка загрузки персонализации: {e}")
    
    def _save_personality_text(self):
        """Сохраняет изменения в файл Personality"""
        if not self.personality_file or not os.path.exists(self.personality_file):
            self.status_label.setText("Ошибка: файл Personality не найден")
            return
        
        # Подтверждение сохранения
        reply = QMessageBox.question(
            self, 
            "Подтверждение сохранения",
            "Вы уверены, что хотите сохранить изменения в файл Personality?\n\nЭто изменит описание личности ассистента Гипатии.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Получаем новый текст из редактора
            new_personality_text = self.personality_editor.toPlainText().rstrip()
            
            # Добавляем заголовочный комментарий обратно
            file_content = "# Гипатия\n\n" + new_personality_text + "\n"
            
            # Сохраняем в файл
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                f.write(file_content)

            self.status_label.setText("Изменения сохранены успешно")
            logger.info("Персонализация сохранена в файл Personality")
            
            # Сообщение об успехе
            QMessageBox.information(
                self,
                "Сохранение завершено",
                "Изменения персонализации Гипатии сохранены в файл Personality.\n\nИзменения будут применены при следующем обращении к системе."
            )
        
        except Exception as e:
            self.status_label.setText(f"Ошибка сохранения: {e}")
            logger.error(f"Ошибка сохранения персонализации: {e}")
            
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Не удалось сохранить изменения:\n\n{e}"
            )
    
    def _reset_personality_text(self):
        """Сбрасывает текст к исходному состоянию"""
        reply = QMessageBox.question(
            self,
            "Подтверждение сброса",
            "Вы уверены, что хотите сбросить все изменения?\n\nВсе несохраненные изменения будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._load_personality_text()
            logger.info("Текст персонализации сброшен")


def test_personality_tab():
    """Тестовая функция для вкладки персонализации"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = PersonalityTab()
    widget.setWindowTitle("Personality Tab Test")
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_personality_tab()
