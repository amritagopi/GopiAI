#!/usr/bin/env python3
"""
Быстрое добавление истории чатов в RAG (оптимизированная версия)
"""

import json
from pathlib import Path
from datetime import datetime


def quick_chunk_by_size(content: str, chunk_size: int = 2500) -> list:
    """Быстрое разбиение по размеру без сложной логики"""
    
    chunks = []
    words = content.split()
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        
        if current_size + word_size > chunk_size and current_chunk:
            # Сохраняем кусочек
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'size': len(chunk_text)
            })
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    # Последний кусочек
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append({
            'content': chunk_text,
            'size': len(chunk_text)
        })
    
    return chunks


def add_to_rag_simple(chunks: list) -> bool:
    """Простое добавление в RAG"""
    
    rag_file = Path("/home/amritagopi/GopiAI/GopiAI-CrewAI/memory/chats.json")
    
    try:
        # Читаем существующие
        existing = []
        if rag_file.exists():
            with open(rag_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        # Добавляем новые
        timestamp = datetime.now().isoformat()
        for i, chunk in enumerate(chunks):
            entry = {
                "id": f"chat_import_{i+1}",
                "timestamp": timestamp,
                "role": "assistant",
                "content": chunk['content'],
                "metadata": {
                    "source": "imported_chat_history",
                    "chunk_id": i+1,
                    "size": chunk['size']
                }
            }
            existing.append(entry)
        
        # Сохраняем
        rag_file.parent.mkdir(parents=True, exist_ok=True)
        with open(rag_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=1)
        
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def main():
    """Быстрый импорт"""
    
    chat_file = Path("/home/amritagopi/GopiAI/Chat_for_editing_chunks.txt")
    
    print("📖 Читаем файл...")
    with open(chat_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 Размер: {len(content)} символов")
    
    # Быстрое разбиение
    print("✂️ Быстрое разбиение...")
    chunks = quick_chunk_by_size(content, chunk_size=2500)
    print(f"📦 Кусочков: {len(chunks)}")
    
    # Добавление в RAG
    print("💾 Добавляем в RAG...")
    success = add_to_rag_simple(chunks)
    
    if success:
        print(f"✅ Готово! Добавлено {len(chunks)} кусочков")
        print("🔄 Перезапустите сервер для переиндексации")
    else:
        print("❌ Ошибка")


if __name__ == "__main__":
    main()