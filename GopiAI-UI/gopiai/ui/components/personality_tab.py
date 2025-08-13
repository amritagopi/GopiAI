#!/usr/bin/env python3
"""
Personality Tab для GopiAI UI
Вкладка для редактирования описания ассистента Гипатии
"""

import logging
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from gopiai.ui.utils.icon_helpers import create_icon_button

logger = logging.getLogger(__name__)

class PersonalityTab(QWidget):
    """Вкладка для редактирования персонализации Гипатии"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.system_prompts_file = None
        self.personality_start_line = 72  # Строка начала описания Гипатии
        self.personality_end_line = 150   # Строка окончания описания Гипатии
        
        self._find_system_prompts_file()
        self._setup_ui()
        self._setup_connections()
        self._load_personality_text()
        
        logger.info("PersonalityTab инициализирован")
    
    def _find_system_prompts_file(self):
        """Находит файл system_prompts.py"""
        try:
            # Пробуем найти файл system_prompts.py
            # 1) Относительно текущего файла (предпочтительно)
            rel_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "GopiAI-CrewAI", "tools", "gopiai_integration", "system_prompts.py"
            )
            candidates = [rel_path]

            # 2) Через GOPI_AI_ROOT, если задан
            root = os.environ.get("GOPI_AI_ROOT")
            if root:
                candidates.append(os.path.join(root, "GopiAI-CrewAI", "tools", "gopiai_integration", "system_prompts.py"))

            for path in candidates:
                if os.path.exists(path):
                    self.system_prompts_file = path
                    logger.info(f"Найден файл system_prompts.py: {path}")
                    break
            
            if not self.system_prompts_file:
                logger.error("Файл system_prompts.py не найден")
                
        except Exception as e:
            logger.error(f"Ошибка поиска system_prompts.py: {e}")
    
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
        desc_label = QLabel("Здесь вы можете редактировать личность и характер ассистента Гипатии.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Текстовое поле для редактирования
        self.personality_editor = QPlainTextEdit()
        self.personality_editor.setPlaceholderText("Загрузка текста персонализации...")
        
        # Устанавливаем шрифт для лучшей читаемости
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.personality_editor.setFont(font)
        
        layout.addWidget(self.personality_editor)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.load_btn = create_icon_button("folder-open", "Загрузить текст персонализации из файла")
        buttons_layout.addWidget(self.load_btn)
        
        self.save_btn = create_icon_button("save", "Сохранить изменения в файл")
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = create_icon_button("rotate-ccw", "Сбросить к исходному тексту")
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
        """Загружает текст персонализации из файла"""
        if not self.system_prompts_file or not os.path.exists(self.system_prompts_file):
            self.status_label.setText("Ошибка: файл system_prompts.py не найден")
            return
        
        try:
            # 1) Считываем весь файл как текст (для безопасного парсинга тройных кавычек)
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                file_text = f.read()

            # 2) Находим функцию get_base_assistant_prompt и первую тройную кавычку внутри неё
            import re
            # Разрешаем опциональную return-аннотацию: def ...(...) -> ...:
            func_pattern = r"def\s+get_base_assistant_prompt\s*\([^)]*\)\s*(->[^:]+)?:\s*\n"
            func_match = re.search(func_pattern, file_text)
            if not func_match:
                # Фоллбэк: работаем по старой логике построчного среза
                lines = file_text.splitlines(keepends=False)
                if len(lines) >= self.personality_end_line:
                    personality_lines = lines[self.personality_start_line-1:self.personality_end_line]
                    self.personality_editor.setPlainText("\n".join(personality_lines).strip())
                    self.status_label.setText("Текст загружен (fallback)")
                    logger.warning("Fallback загрузки персонализации по абсолютным строкам")
                    return
                else:
                    self.status_label.setText("Ошибка: файл слишком короткий")
                    return

            # 3) Ищем первую тройную кавычку после определения функции
            start_idx = func_match.end()
            # Поддерживаем и """ и '''
            triple_start = file_text.find('"""', start_idx)
            q = '"""'
            if triple_start == -1:
                triple_start = file_text.find("'''", start_idx)
                q = "'''"
            if triple_start == -1:
                self.status_label.setText("Ошибка: не найдена начальная тройная кавычка в промпте")
                return

            # 4) Ищем соответствующую закрывающую тройную кавычку
            triple_end = file_text.find(q, triple_start + 3)
            if triple_end == -1:
                self.status_label.setText("Ошибка: не найдена закрывающая тройная кавычка в промпте")
                return

            prompt_body = file_text[triple_start + 3:triple_end]

            # 5) Нормализуем переносы строк и извлекаем только 72–150 строки ТЕЛА промпта
            body_lines = prompt_body.splitlines()
            # Гарантируем границы
            start_line = max(1, self.personality_start_line)
            end_line = max(start_line, self.personality_end_line)
            if len(body_lines) < start_line:
                self.status_label.setText("Ошибка: промпт короче ожидаемого (меньше 72 строк)")
                return
            slice_lines = body_lines[start_line-1: min(end_line, len(body_lines))]

            # 6) Убираем возможную общую табуляцию/отступ
            import textwrap
            personality_text = textwrap.dedent("\n".join(slice_lines)).strip()

            self.personality_editor.setPlainText(personality_text)
            self.status_label.setText("Текст загружен успешно")
            logger.info("Текст персонализации загружен из тела промпта")
        
        except Exception as e:
            self.status_label.setText(f"Ошибка загрузки: {e}")
            logger.error(f"Ошибка загрузки персонализации: {e}")
    
    def _save_personality_text(self):
        """Сохраняет изменения в файл"""
        if not self.system_prompts_file or not os.path.exists(self.system_prompts_file):
            self.status_label.setText("Ошибка: файл system_prompts.py не найден")
            return
        
        # Подтверждение сохранения
        reply = QMessageBox.question(
            self, 
            "Подтверждение сохранения",
            "Вы уверены, что хотите сохранить изменения в system_prompts.py?\n\nЭто изменит поведение ассистента Гипатии.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Читаем весь файл как текст для безопасной реконструкции
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                file_text = f.read()

            # Новый текст персонализации из редактора
            new_personality_text = self.personality_editor.toPlainText().rstrip()

            # Находим функцию и границы тела тройной кавычечной строки
            import re
            func_pattern = r"def\s+get_base_assistant_prompt\s*\([^)]*\)\s*(->[^:]+)?:\s*\n"
            func_match = re.search(func_pattern, file_text)
            if not func_match:
                self.status_label.setText("Ошибка: не найдена функция get_base_assistant_prompt()")
                return

            start_idx = func_match.end()
            # Поддерживаем и """ и '''
            triple_start = file_text.find('"""', start_idx)
            q = '"""'
            if triple_start == -1:
                triple_start = file_text.find("'''", start_idx)
                q = "'''"
            if triple_start == -1:
                self.status_label.setText("Ошибка: не найдена начальная тройная кавычка")
                return
            triple_end = file_text.find(q, triple_start + 3)
            if triple_end == -1:
                self.status_label.setText("Ошибка: не найдена закрывающая тройная кавычка")
                return

            before = file_text[:triple_start + 3]
            prompt_body = file_text[triple_start + 3:triple_end]
            after = file_text[triple_end:]

            body_lines = prompt_body.splitlines()
            start_line = max(1, self.personality_start_line)
            end_line = max(start_line, self.personality_end_line)

            # Расширяем список строк при необходимости пустыми строками, чтобы границы были корректны
            if len(body_lines) < end_line:
                body_lines += [""] * (end_line - len(body_lines))

            # Заменяем диапазон 72–150 новым текстом (построчно)
            new_lines_block = new_personality_text.splitlines()
            body_lines[start_line-1:end_line] = new_lines_block

            # Восстанавливаем тело промпта и весь файл
            new_prompt_body = "\n".join(body_lines)
            new_file_text = before + new_prompt_body + after

            with open(self.system_prompts_file, 'w', encoding='utf-8') as f:
                f.write(new_file_text)

            self.status_label.setText("Изменения сохранены успешно")
            logger.info("Персонализация сохранена в system_prompts.py (внутри тела промпта)")
            
            # Сообщение об успехе
            QMessageBox.information(
                self,
                "Сохранение завершено",
                "Изменения персонализации Гипатии сохранены.\n\nДля применения изменений может потребоваться перезапуск системы."
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
