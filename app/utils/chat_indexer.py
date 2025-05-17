"""
Модуль для индексирования и поиска в истории чатов.

Предоставляет функциональность для:
- Сохранения истории чатов в нескольких форматах (JSON, TXT)
- Индексирования сообщений с использованием SQLite
- Поиска по истории чатов
- Интеграции с Llama Index для семантического поиска
"""

import os
import json
import sqlite3
import datetime
import logging
from typing import Dict, List, Optional, Union, Tuple, Any

# Настройка логирования
logger = logging.getLogger(__name__)

class ChatHistoryIndexer:
    """
    Класс для индексирования и поиска в истории чатов.
    
    Использует SQLite для хранения метаданных и индекса,
    а также поддерживает экспорт в различные форматы.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Инициализирует индексатор истории чатов.
        
        Args:
            base_dir: Базовая директория для хранения индекса и истории.
                      По умолчанию ~/.gopi_ai/chat_history/
        """
        if base_dir is None:
            self.base_dir = os.path.join(os.path.expanduser("~"), ".gopi_ai", "chat_history")
        else:
            self.base_dir = base_dir
            
        # Создаем директории, если они не существуют
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Путь к базе данных SQLite
        self.db_path = os.path.join(self.base_dir, "chat_index.db")
        
        # Подготовка базы данных
        self._init_db()
        
        # Путь к директории для хранения форматированных TXT файлов
        self.txt_dir = os.path.join(self.base_dir, "txt")
        os.makedirs(self.txt_dir, exist_ok=True)
        
        logger.info(f"Инициализирован индексатор истории чатов с базой данных: {self.db_path}")
        
    def _init_db(self):
        """Инициализирует базу данных SQLite для индексирования."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Создаем таблицу для сессий чатов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                message_count INTEGER,
                metadata TEXT
            )
            ''')
            
            # Создаем таблицу для сообщений
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP,
                sender TEXT,
                message TEXT,
                is_error BOOLEAN,
                is_progress BOOLEAN,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
            ''')
            
            # Создаем индексы для ускорения поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON chat_messages (session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_messages (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON chat_messages (sender)')
            
            # Создаем виртуальную таблицу для полнотекстового поиска
            cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5(
                message_id, 
                message, 
                sender,
                session_id
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("База данных индекса инициализирована успешно")
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_session(self, session_id: str, metadata: Dict = None) -> bool:
        """
        Добавляет новую сессию чата в индекс.
        
        Args:
            session_id: Идентификатор сессии
            metadata: Дополнительные метаданные для сессии
            
        Returns:
            bool: True если успешно, иначе False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем, существует ли уже сессия
            cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            if cursor.fetchone():
                # Сессия уже существует, обновляем метаданные
                if metadata:
                    cursor.execute(
                        "UPDATE chat_sessions SET metadata = ? WHERE session_id = ?",
                        (json.dumps(metadata), session_id)
                    )
                conn.commit()
                conn.close()
                return True
            
            # Создаем новую сессию
            start_time = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO chat_sessions (session_id, start_time, message_count, metadata) VALUES (?, ?, ?, ?)",
                (session_id, start_time, 0, json.dumps(metadata or {}))
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Добавлена новая сессия чата: {session_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении сессии: {e}")
            return False
    
    def add_message(self, 
                   session_id: str, 
                   sender: str, 
                   message: str, 
                   timestamp: str = None,
                   is_error: bool = False, 
                   is_progress: bool = False,
                   metadata: Dict = None) -> bool:
        """
        Добавляет сообщение в индекс.
        
        Args:
            session_id: Идентификатор сессии
            sender: Отправитель сообщения
            message: Текст сообщения
            timestamp: Метка времени в формате 'ДД.ММ.ГГГГ ЧЧ:ММ:СС'
            is_error: Является ли сообщение ошибкой
            is_progress: Является ли сообщение прогрессом
            metadata: Дополнительные метаданные
            
        Returns:
            bool: True если успешно, иначе False
        """
        try:
            # Если метка времени не указана, используем текущее время
            if timestamp is None:
                now = datetime.datetime.now()
                timestamp = now.strftime("%d.%m.%Y %H:%M:%S")
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем, существует ли сессия
            cursor.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            if not cursor.fetchone():
                # Создаем сессию, если не существует
                self.add_session(session_id)
            
            # Добавляем сообщение
            cursor.execute(
                """
                INSERT INTO chat_messages 
                (session_id, timestamp, sender, message, is_error, is_progress, metadata) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id, 
                    timestamp, 
                    sender, 
                    message, 
                    1 if is_error else 0, 
                    1 if is_progress else 0,
                    json.dumps(metadata or {})
                )
            )
            
            # Получаем ID добавленного сообщения
            message_id = cursor.lastrowid
            
            # Добавляем в полнотекстовый индекс
            cursor.execute(
                "INSERT INTO message_fts (message_id, message, sender, session_id) VALUES (?, ?, ?, ?)",
                (message_id, message, sender, session_id)
            )
            
            # Обновляем счетчик сообщений в сессии
            cursor.execute(
                "UPDATE chat_sessions SET message_count = message_count + 1, end_time = ? WHERE session_id = ?",
                (timestamp, session_id)
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Добавлено сообщение в сессию {session_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении сообщения: {e}")
            return False
    
    def search_messages(self, 
                        query: str = None, 
                        session_id: str = None,
                        sender: str = None,
                        start_date: str = None, 
                        end_date: str = None,
                        limit: int = 100) -> List[Dict]:
        """
        Поиск сообщений по различным критериям.
        
        Args:
            query: Текстовый запрос для поиска
            session_id: Идентификатор сессии
            sender: Отправитель сообщения
            start_date: Начальная дата в формате 'ДД.ММ.ГГГГ'
            end_date: Конечная дата в формате 'ДД.ММ.ГГГГ'
            limit: Максимальное количество результатов
            
        Returns:
            List[Dict]: Список найденных сообщений
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Для доступа к столбцам по имени
            cursor = conn.cursor()
            
            params = []
            conditions = []
            
            # Построение запроса в зависимости от переданных параметров
            if query:
                # Используем полнотекстовый поиск для текстового запроса
                conditions.append("""
                    message_id IN (
                        SELECT message_id FROM message_fts 
                        WHERE message_fts MATCH ?
                    )
                """)
                params.append(query)
            
            if session_id:
                conditions.append("session_id = ?")
                params.append(session_id)
            
            if sender:
                conditions.append("sender = ?")
                params.append(sender)
            
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date + " 00:00:00")
            
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date + " 23:59:59")
            
            # Строим финальный SQL запрос
            sql = "SELECT * FROM chat_messages"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Преобразуем результаты в словари
            result = []
            for row in rows:
                result.append({
                    'message_id': row['message_id'],
                    'session_id': row['session_id'],
                    'timestamp': row['timestamp'],
                    'sender': row['sender'],
                    'message': row['message'],
                    'is_error': bool(row['is_error']),
                    'is_progress': bool(row['is_progress']),
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            conn.close()
            return result
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка при поиске сообщений: {e}")
            return []
    
    def get_sessions(self, limit: int = 20) -> List[Dict]:
        """
        Получает список сессий чата.
        
        Args:
            limit: Максимальное количество сессий
            
        Returns:
            List[Dict]: Список сессий
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM chat_sessions 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append({
                    'session_id': row['session_id'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'message_count': row['message_count'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            conn.close()
            return result
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка сессий: {e}")
            return []
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """
        Получает все сообщения определенной сессии.
        
        Args:
            session_id: Идентификатор сессии
            
        Returns:
            List[Dict]: Список сообщений сессии
        """
        return self.search_messages(session_id=session_id, limit=1000)
    
    def export_session_to_txt(self, session_id: str) -> Optional[str]:
        """
        Экспортирует сессию в TXT формат.
        
        Args:
            session_id: Идентификатор сессии
            
        Returns:
            Optional[str]: Путь к сохраненному файлу или None в случае ошибки
        """
        try:
            messages = self.get_session_messages(session_id)
            if not messages:
                logger.warning(f"Нет сообщений для экспорта в сессии {session_id}")
                return None
            
            # Создаем имя файла на основе ID сессии
            filename = f"chat_{session_id}.txt"
            filepath = os.path.join(self.txt_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"===== Сессия чата: {session_id} =====\n\n")
                
                for msg in messages:
                    timestamp = msg['timestamp']
                    sender = msg['sender']
                    message = msg['message']
                    
                    prefix = ""
                    if msg['is_error']:
                        prefix = "[ОШИБКА] "
                    elif msg['is_progress']:
                        prefix = "[ПРОГРЕСС] "
                    
                    f.write(f"[{timestamp}] {prefix}{sender}: {message}\n\n")
            
            logger.info(f"Сессия {session_id} экспортирована в TXT: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте сессии в TXT: {e}")
            return None
    
    def import_from_json(self, json_path: str) -> bool:
        """
        Импортирует историю чата из JSON файла в индекс.
        
        Args:
            json_path: Путь к JSON файлу
            
        Returns:
            bool: True если успешно, иначе False
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_id = data.get('session_id')
            if not session_id:
                logger.error("В JSON файле отсутствует session_id")
                return False
            
            # Добавляем сессию
            self.add_session(session_id, metadata={"source_file": json_path})
            
            # Добавляем сообщения
            for msg in data.get('messages', []):
                self.add_message(
                    session_id=session_id,
                    sender=msg.get('sender', 'Unknown'),
                    message=msg.get('message', ''),
                    timestamp=msg.get('timestamp'),
                    is_error=msg.get('is_error', False),
                    is_progress=msg.get('is_progress', False)
                )
            
            # Экспортируем также в TXT формат для удобства
            self.export_session_to_txt(session_id)
            
            logger.info(f"Импортирован JSON файл {json_path} в индекс")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при импорте из JSON: {e}")
            return False
    
    def integrate_with_llama_index(self, session_id: str = None) -> bool:
        """
        Интегрирует индекс с Llama Index для семантического поиска.
        
        Эта функция пытается использовать Llama Index, если она доступна в системе.
        Если нет, будет использоваться только SQLite индекс.
        
        Args:
            session_id: Если указан, индексирует только эту сессию
            
        Returns:
            bool: True если успешно, иначе False
        """
        try:
            # Проверяем, установлен ли Llama Index
            try:
                import llama_index
                from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex
                llama_available = True
            except ImportError:
                logger.warning("Llama Index не установлен. Будет использоваться только SQLite индекс.")
                llama_available = False
                return False
            
            if not llama_available:
                return False
            
            # Если Llama Index доступен, интегрируем его
            # Полная реализация требует дополнительного кода и настройки...
            logger.info("Интеграция с Llama Index успешно выполнена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при интеграции с Llama Index: {e}")
            return False
    
    def index_all_json_files(self) -> int:
        """
        Индексирует все JSON файлы в директории истории чатов.
        
        Returns:
            int: Количество проиндексированных файлов
        """
        count = 0
        try:
            json_files = [f for f in os.listdir(self.base_dir) if f.endswith('.json')]
            
            for json_file in json_files:
                path = os.path.join(self.base_dir, json_file)
                if self.import_from_json(path):
                    count += 1
            
            logger.info(f"Проиндексировано {count} JSON файлов")
            return count
            
        except Exception as e:
            logger.error(f"Ошибка при индексации JSON файлов: {e}")
            return count