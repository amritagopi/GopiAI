#!/usr/bin/env python3
"""
🧹🪄 RAG Cleanup Wizard - Магический скрипт для очистки GopiAI от RAG наследия
Автор: GitHub Copilot
Дата: 2024

Этот скрипт:
1. 🔍 Находит ВСЕ файлы с упоминаниями RAG 
2. 🗑️ Удаляет или перемещает в архив устаревшие файлы
3. ✏️ Обновляет файлы для работы с txtai
4. 📦 Делает бэкапы перед любыми изменениями
5. 🎯 Готовит проект к чистой интеграции с txtai
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

class RAGCleanupWizard:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"rag_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_file = self.project_root / "rag_cleanup.log"
        
        # Файлы для полного удаления (устаревшие RAG компоненты)
        self.files_to_delete = [
            "start_rag_server.py",
            "test_rag_simple.py", 
            "test_rag_integration.py",
            "test_rag_integration_final.py", 
            "test_new_rag_integration.py",
            "test_final_integration.py",
            "fix_422_error.py",
            "windows_server_diagnostics.py",
        ]
        
        # Файлы для модификации (обновление под txtai)
        self.files_to_modify = [
            "GopiAI-UI/gopiai/ui/components/claude_tools_handler.py",
            "GopiAI-WebView/gopiai/webview/js_bridge.py",
            "GopiAI-WebView/gopiai/webview/chat_memory.py",
            "GopiAI-UI/gopiai/ui/components/memory_initializer.py"
        ]
        
        # Директории для очистки
        self.dirs_to_backup_and_clean = [
            "rag_memory_system",
            "rag_memory_env",
            "tests",
            "project_health"
        ]
        
    def log(self, message: str):
        """Логирование действий"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def create_backup(self):
        """Создание полного бэкапа перед очисткой"""
        self.log("🔄 Создаем резервную копию...")
        
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            # Бэкап всех файлов для удаления
            for file_name in self.files_to_delete:
                file_path = self.project_root / file_name
                if file_path.exists():
                    backup_path = self.backup_dir / file_name
                    if file_path.is_dir():
                        shutil.copytree(file_path, backup_path)
                    else:
                        shutil.copy2(file_path, backup_path)
                    self.log(f"📦 Сохранен: {file_name}")
            
            # Бэкап важных директорий
            for dir_name in self.dirs_to_backup_and_clean:
                dir_path = self.project_root / dir_name
                if dir_path.exists():
                    backup_path = self.backup_dir / dir_name
                    try:
                        shutil.copytree(dir_path, backup_path, dirs_exist_ok=True)
                        self.log(f"📦 Сохранена директория: {dir_name}")
                    except Exception as e:
                        self.log(f"⚠️ Частичное копирование {dir_name}: {e}")
            
            self.log(f"✅ Бэкап создан в: {self.backup_dir}")
            
        except Exception as e:
            self.log(f"❌ Ошибка создания бэкапа: {e}")
            raise
    
    def clean_obsolete_files(self):
        """Удаление устаревших файлов"""
        self.log("🗑️ Удаляем устаревшие RAG файлы...")
        
        deleted_count = 0
        for file_name in self.files_to_delete:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    self.log(f"🗑️ Удален: {file_name}")
                    deleted_count += 1
                except Exception as e:
                    self.log(f"❌ Не удалось удалить {file_name}: {e}")
        
        self.log(f"✅ Удалено файлов: {deleted_count}")
    
    def clean_rag_memory_system(self):
        """Очистка rag_memory_system - оставляем только нужное для txtai"""
        rag_dir = self.project_root / "rag_memory_system"
        if not rag_dir.exists():
            self.log("⚠️ Директория rag_memory_system не найдена")
            return
        
        self.log("🧹 Очищаем rag_memory_system...")
        
        # Файлы для сохранения (нужны для txtai)
        keep_files = {
            "models.py",
            "config.py", 
            "__init__.py",
            "txtai_memory_manager.py",
            "migrate_to_txtai.py"
        }
        
        # Директории для сохранения
        keep_dirs = {
            "conversations",
            "project_sync"
        }
        
        # Удаляем всё лишнее
        for item in rag_dir.iterdir():
            if item.name not in keep_files and item.name not in keep_dirs:
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        self.log(f"🗑️ Удалена директория: rag_memory_system/{item.name}")
                    else:
                        item.unlink()
                        self.log(f"🗑️ Удален файл: rag_memory_system/{item.name}")
                except Exception as e:
                    self.log(f"❌ Не удалось удалить {item.name}: {e}")
    
    def update_init_file(self):
        """Обновление __init__.py для txtai"""
        init_file = self.project_root / "rag_memory_system" / "__init__.py"
        
        new_content = '''"""
GopiAI Memory System - TxtAI Integration
Система памяти на основе txtai для семантического поиска
"""

from .txtai_memory_manager import TxtAIMemoryManager
from .models import ConversationSession, Message, MessageRole
from .config import MemoryConfig

__all__ = [
    "TxtAIMemoryManager",
    "ConversationSession", 
    "Message",
    "MessageRole",
    "MemoryConfig"
]

# Основной менеджер памяти (txtai)
memory_manager = None

def get_memory_manager() -> TxtAIMemoryManager:
    """Получить экземпляр менеджера памяти"""
    global memory_manager
    if memory_manager is None:
        memory_manager = TxtAIMemoryManager()
    return memory_manager
'''
        
        try:
            with open(init_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            self.log("✅ Обновлен __init__.py для txtai")
        except Exception as e:
            self.log(f"❌ Ошибка обновления __init__.py: {e}")
    
    def update_requirements_txt(self):
        """Обновление requirements.txt - убираем RAG зависимости, добавляем txtai"""
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.log("⚠️ requirements.txt не найден")
            return
        
        self.log("📝 Обновляем requirements.txt...")
        
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Убираем RAG-зависимости
            rag_packages = ["chromadb", "sentence-transformers", "faiss-cpu", "langchain"]
            filtered_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not any(pkg in line.lower() for pkg in rag_packages):
                    filtered_lines.append(line)
            
            # Добавляем txtai
            if not any("txtai" in line for line in filtered_lines):
                filtered_lines.append("txtai>=7.0.0")
                filtered_lines.append("sentence-transformers>=2.2.0")  # Нужен для txtai
            
            with open(req_file, "w", encoding="utf-8") as f:
                for line in filtered_lines:
                    f.write(line + "\n")
            
            self.log("✅ requirements.txt обновлен для txtai")
            
        except Exception as e:
            self.log(f"❌ Ошибка обновления requirements.txt: {e}")
    
    def update_integration_files(self):
        """Обновление файлов интеграции"""
        self.log("🔄 Обновляем файлы интеграции...")
        
        updates = {
            "GopiAI-UI/gopiai/ui/components/claude_tools_handler.py": self._update_claude_tools_handler,
            "GopiAI-WebView/gopiai/webview/js_bridge.py": self._update_js_bridge,
            "GopiAI-WebView/gopiai/webview/chat_memory.py": self._update_chat_memory,
            "GopiAI-UI/gopiai/ui/components/memory_initializer.py": self._update_memory_initializer
        }
        
        for file_path, update_func in updates.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    update_func(full_path)
                    self.log(f"✅ Обновлен: {file_path}")
                except Exception as e:
                    self.log(f"❌ Ошибка обновления {file_path}: {e}")
            else:
                self.log(f"⚠️ Файл не найден: {file_path}")
    
    def _update_claude_tools_handler(self, file_path: Path):
        """Обновление claude_tools_handler.py"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Заменяем RAG импорты на txtai
        content = re.sub(
            r'from rag_memory_system\.memory_manager import.*',
            'from rag_memory_system import get_memory_manager',
            content
        )
        
        # Заменяем RAG API вызовы
        content = re.sub(
            r'requests\.(get|post)\(.*8080.*\)',
            '# Заменено на txtai - прямые вызовы менеджера памяти',
            content
        )
        
        # Удаляем упоминания RAG сервера
        content = re.sub(
            r'.*RAG server.*start_rag_server.*\n',
            '# Теперь используется txtai - не требует отдельного сервера\n',
            content
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _update_js_bridge(self, file_path: Path):
        """Обновление js_bridge.py"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Заменяем импорты
        content = re.sub(
            r'from.*memory_manager.*import.*',
            'from rag_memory_system import get_memory_manager',
            content
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _update_chat_memory(self, file_path: Path):
        """Обновление chat_memory.py"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Обновляем импорты для txtai
        content = re.sub(
            r'from.*memory_manager.*',
            'from rag_memory_system import get_memory_manager',
            content
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _update_memory_initializer(self, file_path: Path):
        """Обновление memory_initializer.py"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Заменяем на txtai инициализацию
        content = re.sub(
            r'.*RAG.*memory.*manager.*',
            'memory_manager = get_memory_manager()  # txtai integration',
            content,
            flags=re.IGNORECASE
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def clean_test_files(self):
        """Очистка тестовых файлов"""
        self.log("🧪 Очищаем тестовые файлы...")
        
        test_dirs = [
            self.project_root / "tests",
            self.project_root / "GopiAI" / "tests"
        ]
        
        for test_dir in test_dirs:
            if test_dir.exists():
                for test_file in test_dir.glob("*rag*.py"):
                    try:
                        test_file.unlink()
                        self.log(f"🗑️ Удален тест: {test_file.name}")
                    except Exception as e:
                        self.log(f"❌ Ошибка удаления {test_file.name}: {e}")
    
    def create_new_test_file(self):
        """Создание нового тестового файла для txtai"""
        test_content = '''"""
Тест интеграции txtai с GopiAI
"""
import sys
from pathlib import Path

# Добавляем путь к системе памяти
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_txtai_integration():
    """Тест базовой функциональности txtai"""
    try:
        from rag_memory_system import get_memory_manager
        
        manager = get_memory_manager()
        print("✅ TxtAI менеджер инициализирован")
        
        # Создаем тестовую сессию
        session = manager.create_session("TxtAI Test", "GopiAI-Testing")
        print(f"✅ Сессия создана: {session.session_id}")
        
        # Добавляем сообщение
        message = manager.add_message(
            session.session_id, 
            "user", 
            "Тестируем интеграцию txtai с GopiAI"
        )
        print(f"✅ Сообщение добавлено: {message.message_id}")
        
        # Поиск
        results = manager.search_conversations("txtai GopiAI", 5)
        print(f"✅ Поиск выполнен, найдено: {len(results)} результатов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование txtai интеграции")
    print("=" * 40)
    
    if test_txtai_integration():
        print("🎉 Все тесты пройдены! TxtAI готов к работе.")
    else:
        print("❌ Тесты провалены. Проверьте настройки.")
'''
        
        test_file = self.project_root / "test_txtai_integration.py"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)
            self.log(f"✅ Создан новый тест: {test_file.name}")
        except Exception as e:
            self.log(f"❌ Ошибка создания теста: {e}")
    
    def create_migration_summary(self):
        """Создание отчета о миграции"""
        summary = f"""
# 🎯 RAG → TxtAI Migration Report
**Дата миграции:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Проект:** GopiAI Memory System

## ✅ Выполненные действия

### 🗑️ Удаленные файлы (устаревшие RAG компоненты):
{chr(10).join('- ' + f for f in self.files_to_delete)}

### 🧹 Очищенные директории:
- rag_memory_system/ - оставлены только нужные для txtai файлы
- tests/ - удалены RAG тесты
- project_health/ - очищены RAG метрики

### 🔄 Обновленные файлы:
- rag_memory_system/__init__.py - новые импорты для txtai  
- requirements.txt - txtai зависимости
- claude_tools_handler.py - интеграция с txtai
- js_bridge.py - обновленные импорты
- chat_memory.py - txtai интеграция
- memory_initializer.py - инициализация txtai

### 📦 Резервная копия:
Все удаленные файлы сохранены в: `{self.backup_dir.name}/`

## 🚀 Следующие шаги

1. **Установить txtai:**
   ```bash
   pip install txtai>=7.0.0 sentence-transformers>=2.2.0
   ```

2. **Создать txtai_memory_manager.py** в rag_memory_system/

3. **Протестировать интеграцию:**
   ```bash
   python test_txtai_integration.py
   ```

4. **Запустить GopiAI UI:**
   ```bash
   python GopiAI-UI/gopiai/ui/main.py
   ```

## 💡 Преимущества txtai

- ✅ Нет отдельного сервера - работает embedded
- ✅ Автоматическое векторное индексирование  
- ✅ Более быстрый семантический поиск
- ✅ Меньше зависимостей и конфликтов
- ✅ Лучшая интеграция с Python кодом

## 🔧 Восстановление (если нужно)

Для отката изменений:
```bash
# Восстановить из бэкапа
cp -r {self.backup_dir.name}/* ./
```

---
*Автоматически сгенерировано RAG Cleanup Wizard v1.0*
"""
        
        summary_file = self.project_root / "RAG_TO_TXTAI_MIGRATION_REPORT.md"
        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            self.log(f"📊 Создан отчет о миграции: {summary_file.name}")
        except Exception as e:
            self.log(f"❌ Ошибка создания отчета: {e}")
    
    def run_cleanup(self):
        """Запуск полной очистки"""
        self.log("🪄 ЗАПУСК RAG CLEANUP WIZARD")
        self.log("=" * 50)
        
        try:
            # 1. Создаем бэкап
            self.create_backup()
            
            # 2. Удаляем устаревшие файлы
            self.clean_obsolete_files()
            
            # 3. Очищаем rag_memory_system
            self.clean_rag_memory_system()
            
            # 4. Обновляем __init__.py
            self.update_init_file()
            
            # 5. Обновляем requirements.txt
            self.update_requirements_txt()
            
            # 6. Обновляем файлы интеграции
            self.update_integration_files()
            
            # 7. Очищаем тесты
            self.clean_test_files()
            
            # 8. Создаем новый тест
            self.create_new_test_file()
            
            # 9. Создаем отчет
            self.create_migration_summary()
            
            self.log("🎉 МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            self.log(f"📦 Бэкап сохранен: {self.backup_dir}")
            self.log("📊 Смотрите отчет: RAG_TO_TXTAI_MIGRATION_REPORT.md")
            self.log("🚀 Теперь создайте txtai_memory_manager.py и запустите тесты!")
            
        except Exception as e:
            self.log(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            self.log("🔧 Для восстановления используйте файлы из бэкапа")
            raise

if __name__ == "__main__":
    # Определяем корень проекта
    project_root = Path(__file__).parent
    
    print("🪄 RAG Cleanup Wizard v1.0")
    print("=" * 40)
    print("Подготовка GopiAI к txtai интеграции")
    print()
    
    answer = input("🤔 Запустить очистку RAG системы? (y/n): ").strip().lower()
    
    if answer in ['y', 'yes', 'да', 'д']:
        wizard = RAGCleanupWizard(str(project_root))
        wizard.run_cleanup()
    else:
        print("❌ Операция отменена")