"""
GeminiDirectClient - прямой клиент для Gemini API с обходом ограничений безопасности
Основан на рабочем коде из коммита 2f0fe4256d7f0d5bf2168a4db56d6b6def937860
"""

import logging
import os
import json
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiDirectClient:
    """Прямой клиент для Gemini API с обходом safety restrictions"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        logger.info(f"🔥 Инициализирован GeminiDirectClient для модели: {model}")
    
    def generate_text(self, messages: List[Dict[str, Any]]) -> str:
        """
        Генерирует текст с использованием прямого вызова Gemini API
        БЕЗ safety settings для обхода ограничений
        """
        try:
            # Конвертируем сообщения в формат Gemini
            gemini_messages = self._convert_to_gemini_format(messages)
            
            # URL для генерации
            url = f"{self.base_url}/{self.model}:generateContent"
            
            # Заголовки
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            # Данные запроса - БЕЗ safetySettings!
            data = {
                "contents": gemini_messages,
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                    "stopSequences": []
                }
                # Намеренно НЕ добавляем safetySettings - это и есть обход!
            }
            
            logger.info(f"🚀 Отправляем запрос к Gemini API: {url}")
            logger.debug(f"Данные запроса: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            
            # Отправляем запрос
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            result_text = parts[0]['text']
                            logger.info(f"✅ Получен ответ от Gemini (длина: {len(result_text)} символов)")
                            return result_text
                
                # Если нет текста в ответе, проверяем на блокировку
                if 'promptFeedback' in response_data:
                    feedback = response_data['promptFeedback']
                    if 'blockReason' in feedback:
                        logger.warning(f"⚠️ Запрос заблокирован Gemini: {feedback['blockReason']}")
                        return f"Запрос был заблокирован системой безопасности Gemini: {feedback['blockReason']}"
                
                logger.error(f"❌ Неожиданный формат ответа от Gemini: {response_data}")
                return "Получен неожиданный формат ответа от Gemini API"
                
            else:
                logger.error(f"❌ Ошибка HTTP {response.status_code}: {response.text}")
                return f"Ошибка API Gemini: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при обращении к Gemini API")
            return "Превышено время ожидания ответа от Gemini API"
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка сети при обращении к Gemini API: {e}")
            return f"Ошибка сети: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка GeminiDirectClient: {e}")
            logger.error(f"Traceback:", exc_info=True)
            return f"Внутренняя ошибка клиента: {str(e)}"
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Конвертирует сообщения в формат, понятный Gemini API
        """
        gemini_messages = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content')
            
            # Пропускаем системные сообщения - объединяем с пользовательским
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
                        first_part['text'] = f"СИСТЕМНЫЙ ПРОМПТ: {system_prompt}\n\nЗАПРОС ПОЛЬЗОВАТЕЛЯ: {first_part['text']}"
                    break
        
        logger.debug(f"Конвертировано {len(messages)} сообщений в {len(gemini_messages)} Gemini сообщений")
        return gemini_messages