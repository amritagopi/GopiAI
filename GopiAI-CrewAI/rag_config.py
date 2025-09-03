"""
RAG Configuration for GopiAI Server

This module configures the txtai-based RAG system for the server.
"""

# --- START OF FILE rag_config.py ---

import os
from pathlib import Path

# Определяем корневую директорию проекта (там, где лежит этот файл)
# Это делает пути независимыми от того, откуда вы запускаете сервер
PROJECT_ROOT = Path(__file__).parent

# Папка для хранения всех данных памяти, теперь внутри проекта
MEMORY_BASE_DIR = PROJECT_ROOT / "memory"
MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Путь к файлу с историей чатов
# Сервер будет искать его относительно своего расположения
CHATS_FILE_PATH = MEMORY_BASE_DIR / "chats.json"

# Путь к папке с векторным индексом
VECTOR_INDEX_PATH = MEMORY_BASE_DIR / "vectors"

# Модель для создания эмбеддингов (переход на легковесную модель для экономии памяти)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 22MB вместо 420MB

if __name__ == "__main__":
    print("--- RAG Server Configuration ---")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Memory Directory: {MEMORY_BASE_DIR}")
    print(f"Chats File: {CHATS_FILE_PATH}")
    print(f"Vector Index: {VECTOR_INDEX_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
# --- END OF FILE rag_config.py ---