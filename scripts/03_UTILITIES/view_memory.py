#!/usr/bin/env python3
"""
Просмотр содержимого памяти GOPI_AI
"""

import json
import os
from pathlib import Path

def view_memory():
    """Показать все данные в памяти"""
    
    # Определяем путь к файлу памяти в зависимости от ОС
    if os.name == 'nt':  # Windows
        memory_file = Path("C:/Users/crazy/GOPI_AI_MODULES/GopiAI-CrewAI/memory/chats.json")
    else:  # Linux/Mac
        memory_file = Path.home() / ".gopiai" / "memory" / "chats.json"
    
    print(f"🔍 Ищу файл памяти: {memory_file}")
    
    if not memory_file.exists():
        print("❌ Файл памяти не найден!")
        return
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем формат данных
        if isinstance(data, list):
            # Новый формат - список сообщений
            chats = data
            # Создаем словарь сессий на основе сообщений
            sessions = {}
            for msg in chats:
                session_id = msg.get('session_id')
                if session_id and session_id not in sessions:
                    sessions[session_id] = {
                        'title': f"Сессия {session_id}",
                        'created_at': msg.get('timestamp', ''),
                        'message_count': sum(1 for m in chats if m.get('session_id') == session_id)
                    }
        else:
            # Старый формат - словарь с ключами 'chats' и 'sessions'
            chats = data.get('chats', [])
            sessions = data.get('sessions', {})
        
        print("🧠 СОДЕРЖИМОЕ ПАМЯТИ GOPI_AI")
        print("=" * 60)
        print(f"📊 Всего сообщений: {len(chats)}")
        print(f"📁 Всего сессий: {len(sessions)}")
        print()
        
        # Показываем сессии
        print("📂 СЕССИИ:")
        print("-" * 30)
        for session_id, session in sessions.items():
            print(f"🗂️  {session.get('title', 'Без названия')}")
            print(f"   ID: {session_id}")
            print(f"   Создана: {session.get('created_at', 'Неизвестно')}")
            print(f"   Сообщений: {session.get('message_count', 'Неизвестно')}")
            print()
        
        # Показываем все сообщения
        print("💬 ВСЕ СООБЩЕНИЯ:")
        print("-" * 40)
        
        for i, chat in enumerate(chats, 1):
            # Находим название сессии
            session_title = "Unknown Session"
            session_id = chat.get('session_id', '')
            if session_id in sessions:
                session_title = sessions[session_id].get('title', 'Без названия')
            
            role_emoji = "👤" if chat.get('role') == 'user' else "🤖"
            print(f"{i}. [{session_title}] {role_emoji} {chat.get('role', 'unknown').upper()}:")
            print(f"   \"{chat.get('content', '')}\"")
            print(f"   {chat.get('timestamp', 'Неизвестно')}")
            print()
        
        if not chats:
            print("📭 Пока что сообщений нет!")
            
    except Exception as e:
        print(f"❌ Ошибка чтения памяти: {e}")

if __name__ == "__main__":
    view_memory()
