import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def convert_to_gemini_format(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Конвертирует сообщения в формат, понятный Gemini API.
    """
    gemini_messages = []
    
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content')
        
        # Пропускаем системные сообщения - они будут обработаны отдельно
        if role == 'system':
            continue
            
        # Gemini использует 'user' и 'model' вместо 'user' и 'assistant'
        gemini_role = 'model' if role == 'assistant' else 'user'
        
        if isinstance(content, str):
            gemini_messages.append({
                'role': gemini_role,
                'parts': [{'text': content}]
            })
        elif isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append({'text': item})
                elif isinstance(item, dict) and 'type' in item:
                    if item['type'] == 'text':
                        parts.append({'text': item.get('text', '')})
                    elif item['type'] == 'image_url':
                        # Обработка изображений
                        url = item['image_url'].get('url', '')
                        if ',' in url:  # base64 data URL
                            mime, data = url.split(',', 1)
                            mime = mime.split(';')[0].split(':')[1]
                            parts.append({
                                'inline_data': {
                                    'mime_type': mime,
                                    'data': data
                                }
                            })
            
            if parts:
                gemini_messages.append({
                    'role': gemini_role,
                    'parts': parts
                })

    # Добавляем системный промпт в первое пользовательское сообщение
    system_prompt = None
    for msg in messages:
        if msg.get('role') == 'system':
            system_prompt = msg.get('content', '')
            break
    
    if system_prompt and gemini_messages:
        # Находим первое пользовательское сообщение и добавляем системный промпт
        for i, gmsg in enumerate(gemini_messages):
            if gmsg['role'] == 'user':
                # Добавляем системный промпт в начало
                first_part = gmsg['parts'][0]
                if 'text' in first_part:
                    first_part['text'] = f"СИСТЕМНЫЙ ПРОМПТ: {system_prompt}\\n\\nЗАПРОС ПОЛЬЗОВАТЕЛЯ: {first_part['text']}"
                break
    
    logger.debug(f"Конвертировано {len(messages)} сообщений в {len(gemini_messages)} Gemini сообщений")
    return gemini_messages