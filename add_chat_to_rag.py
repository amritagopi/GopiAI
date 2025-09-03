#!/usr/bin/env python3
"""
Скрипт для добавления истории чатов в RAG систему GopiAI
Разбивает большой файл на логические кусочки и индексирует их
"""

import json
import re
from pathlib import Path
from datetime import datetime


def split_chat_into_topics(chat_content: str) -> list:
    """Разбивает чат на темы по заголовкам"""
    
    # Ищем заголовки тем (строки без "user" или "ChatGPT" в начале)
    lines = chat_content.split('\n')
    topics = []
    current_topic = {'title': '', 'content': ''}
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Определяем заголовок темы (обычно первая строка без user/ChatGPT)
        if (not line.startswith('user') and 
            not line.startswith('ChatGPT') and 
            not line.startswith('tool') and
            not line.startswith('```') and
            not line.startswith('#') and
            len(current_content) == 0):
            
            # Сохраняем предыдущую тему если была
            if current_topic['content']:
                topics.append({
                    'title': current_topic['title'],
                    'content': current_topic['content'],
                    'chunk_size': len(current_topic['content'])
                })
            
            # Начинаем новую тему
            current_topic = {
                'title': line,
                'content': ''
            }
            current_content = []
            
        else:
            current_content.append(line)
            current_topic['content'] = '\n'.join(current_content)
    
    # Добавляем последнюю тему
    if current_topic['content']:
        topics.append({
            'title': current_topic['title'],
            'content': current_topic['content'],
            'chunk_size': len(current_topic['content'])
        })
    
    return topics


def chunk_large_topics(topics: list, max_chunk_size: int = 3000) -> list:
    """Разбивает большие темы на более мелкие кусочки"""
    
    chunked_topics = []
    
    for topic in topics:
        if topic['chunk_size'] <= max_chunk_size:
            chunked_topics.append(topic)
        else:
            # Разбиваем большую тему на части
            content = topic['content']
            lines = content.split('\n')
            
            chunk_lines = []
            current_chunk_size = 0
            chunk_num = 1
            
            for line in lines:
                if current_chunk_size + len(line) > max_chunk_size and chunk_lines:
                    # Сохраняем текущий кусочек
                    chunked_topics.append({
                        'title': f"{topic['title']} (часть {chunk_num})",
                        'content': '\n'.join(chunk_lines),
                        'chunk_size': current_chunk_size
                    })
                    
                    chunk_lines = [line]
                    current_chunk_size = len(line)
                    chunk_num += 1
                else:
                    chunk_lines.append(line)
                    current_chunk_size += len(line) + 1
            
            # Сохраняем последний кусочек
            if chunk_lines:
                chunked_topics.append({
                    'title': f"{topic['title']} (часть {chunk_num})" if chunk_num > 1 else topic['title'],
                    'content': '\n'.join(chunk_lines),
                    'chunk_size': current_chunk_size
                })
    
    return chunked_topics


def add_chunks_to_rag(chunks: list) -> bool:
    """Добавляет кусочки в RAG систему через файловую систему"""
    
    # Путь к файлу чатов RAG системы
    rag_chats_file = Path("/home/amritagopi/GopiAI/GopiAI-CrewAI/memory/chats.json")
    
    try:
        # Читаем существующие чаты
        if rag_chats_file.exists():
            with open(rag_chats_file, 'r', encoding='utf-8') as f:
                existing_chats = json.load(f)
        else:
            existing_chats = []
        
        # Добавляем новые кусочки
        for i, chunk in enumerate(chunks):
            chat_entry = {
                "id": f"imported_chat_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": f"Тема: {chunk['title']}\n\n{chunk['content']}",
                "metadata": {
                    "source": "imported_chat_history", 
                    "topic": chunk['title'],
                    "chunk_size": chunk['chunk_size'],
                    "imported": True
                }
            }
            existing_chats.append(chat_entry)
        
        # Сохраняем обновленный файл
        rag_chats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(rag_chats_file, 'w', encoding='utf-8') as f:
            json.dump(existing_chats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Добавлено {len(chunks)} кусочков в {rag_chats_file}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка добавления в RAG: {e}")
        return False


def main():
    """Основная функция"""
    
    chat_file = Path("/home/amritagopi/GopiAI/Chat_for_editing_chunks.txt")
    
    if not chat_file.exists():
        print(f"❌ Файл не найден: {chat_file}")
        return
    
    print(f"📖 Читаем файл: {chat_file}")
    with open(chat_file, 'r', encoding='utf-8') as f:
        chat_content = f.read()
    
    print(f"📝 Размер файла: {len(chat_content)} символов")
    
    # Разбиваем на темы
    print("🔍 Разбиваем на темы...")
    topics = split_chat_into_topics(chat_content)
    print(f"📋 Найдено тем: {len(topics)}")
    
    # Показываем статистику по темам
    for i, topic in enumerate(topics[:10]):  # Показываем только первые 10
        print(f"  {i+1}. {topic['title'][:50]}... ({topic['chunk_size']} символов)")
    
    if len(topics) > 10:
        print(f"  ... и еще {len(topics) - 10} тем")
    
    # Разбиваем большие темы на кусочки
    print("✂️ Разбиваем большие темы...")
    chunks = chunk_large_topics(topics, max_chunk_size=3000)
    print(f"📦 Итоговых кусочков: {len(chunks)}")
    
    # Статистика размеров
    total_chars = sum(chunk['chunk_size'] for chunk in chunks)
    avg_size = total_chars // len(chunks)
    max_size = max(chunk['chunk_size'] for chunk in chunks)
    print(f"📊 Средний размер кусочка: {avg_size} символов")
    print(f"📊 Максимальный размер: {max_size} символов")
    
    # Добавляем в RAG
    print("💾 Добавляем в RAG систему...")
    success = add_chunks_to_rag(chunks)
    
    if success:
        print("🎉 История чатов успешно добавлена в RAG!")
        print("🔄 Теперь нужно перезапустить сервер для переиндексации")
    else:
        print("❌ Не удалось добавить в RAG")


if __name__ == "__main__":
    main()