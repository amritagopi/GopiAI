# --- START OF FILE manager.py (УНИФИЦИРОВАННАЯ ВЕРСИЯ) ---

"""
Memory Manager for GopiAI UI

This module provides an interface for managing chat history for the current UI session.
Использует общую конфигурацию памяти с сервером CrewAI API для обеспечения
согласованности данных между клиентом и сервером.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Импортируем локальную конфигурацию памяти
from .memory_config import MEMORY_BASE_DIR, CHATS_FILE_PATH

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified memory management for GopiAI UI.
    Uses shared memory configuration with CrewAI API server.
    """
    
    def __init__(self):
        """Initialize the memory manager with shared configuration."""
        # Используем общую конфигурацию памяти
        logger.info(f"[UNIFIED-MEMORY] Initializing memory manager with shared config. Path: {MEMORY_BASE_DIR}")
        
        # Создаем директорию, если она не существует
        MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем структуры данных
        self.chats: List[Dict[str, Any]] = []
        self.sessions: Dict[str, Any] = {}
        
        # Загружаем историю из общего файла
        self._load_chat_history()
        
    def _load_chat_history(self):
        """
        Loads chat history from the shared chats.json file.
        Uses the same file as the CrewAI API server.
        """
        try:
            if CHATS_FILE_PATH.exists():
                with open(CHATS_FILE_PATH, 'r', encoding='utf-8') as f:
                    self.chats = json.load(f)
                logger.info(f"[UNIFIED-MEMORY] Loaded {len(self.chats)} messages from shared file: {CHATS_FILE_PATH}")
                
                # Создаем словарь сессий на основе загруженных чатов
                session_ids_raw = set(msg.get('session_id') for msg in self.chats if msg.get('session_id'))
                # Явно фильтруем и приводим к str, чтобы удовлетворить Pylance (ключи словаря строго строки)
                session_ids = [str(sid) for sid in session_ids_raw if isinstance(sid, (str, int))]
                for session_id in session_ids:
                    session_msgs = [msg for msg in self.chats if str(msg.get('session_id')) == session_id]
                    if session_msgs:
                        first_msg = min(session_msgs, key=lambda x: x.get('timestamp') or '0')
                        created_at = first_msg.get('timestamp') or datetime.now().isoformat()
                        self.sessions[session_id] = {
                            'id': session_id,
                            'title': (first_msg.get('content', '') or '')[:30],
                            'created_at': created_at
                        }
            else:
                logger.info(f"[UNIFIED-MEMORY] No shared chats file found at {CHATS_FILE_PATH}. Creating a new one.")
                # Создаем пустой файл
                with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"[UNIFIED-MEMORY] Error loading shared chat history: {e}")

    def add_message(self, session_id: str, role: str, content: str, **metadata) -> str:
        """
        Adds a message to the chat history and saves it to the shared file.
        """
        if not content.strip():
            return ""

        # Управляем сессиями
        if session_id not in self.sessions:
            sid = str(session_id)
            self.sessions[sid] = {  # type: ignore[type-arg]
                'id': sid, 
                'title': content[:30], # Название чата - первые 30 символов
                'created_at': datetime.now().isoformat()
            }
        
        message = {
            'id': str(uuid.uuid4()),
            'session_id': str(session_id),
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        self.chats.append(message)
        
        # Сохраняем в общий файл
        try:
            with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
            logger.info(f"[UNIFIED-MEMORY] Added message and saved to shared file: {CHATS_FILE_PATH}")
        except Exception as e:
            logger.error(f"[UNIFIED-MEMORY] Error saving to shared file: {e}")
            
        return message['id']

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Gets chat history for a session from the in-memory list."""
        if session_id:
            sid = str(session_id)
            # Фильтруем сообщения для текущей сессии (приводим к строке для надежного сравнения)
            session_messages = [msg for msg in self.chats if str(msg.get('session_id')) == sid]
            # Сортируем их по времени
            session_messages.sort(key=lambda x: x.get('timestamp') or '0')
            return session_messages
        return []
    
    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Возвращает сообщения сессии с поддержкой optional limit (совместимость с вызовами UI)."""
        messages = self.get_chat_history(session_id)
        if limit is not None:
            try:
                lim = int(limit)
                if lim > 0:
                    return messages[-lim:]
            except Exception:
                pass
        return messages

    # Дополнительные методы для работы с общей памятью
    def list_sessions(self) -> List[Dict]:
        return list(self.sessions.values())

    def get_session_title(self, session_id: str) -> str:
        return self.sessions.get(session_id, {}).get('title', 'New Chat')

    def update_session_title(self, session_id: str, title: str):
        if session_id in self.sessions:
            self.sessions[str(session_id)]['title'] = title
            self._save_data()

    def delete_session(self, session_id: str):
        if not session_id:
            return
        if session_id in self.sessions:
            del self.sessions[str(session_id)]
        self.chats = [msg for msg in self.chats if str(msg.get('session_id')) != str(session_id)]
        self._save_data()

    def _save_data(self):
        try:
            with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Error saving data: {e}')

# --- Singleton Instance ---
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """Returns the singleton instance of the MemoryManager."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance

# --- END OF FILE manager.py (УНИФИЦИРОВАННАЯ ВЕРСИЯ) ---
