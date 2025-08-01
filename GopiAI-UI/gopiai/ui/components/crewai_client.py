import urllib.parse
import re

"""
🔌 CrewAI API Client
Клиент для интеграции с CrewAI через REST API
"""

import requests
import requests.exceptions
import threading
import time
import json
import logging
import logging.handlers
import os
import sys
from pathlib import Path
import base64
from typing import Dict, Any, List, Optional, Union

# Настройка логирования для CrewAI клиента
logger = logging.getLogger(__name__)

# Импортируем менеджер памяти для работы с историей чата
from ..memory.manager import MemoryManager

# 🔧 ИСПРАВЛЕНИЕ АРХИТЕКТУРЫ: Убираем прямые импорты серверных модулей
# UI должен получать конфигурацию через API, а не импортировать серверные файлы

# Локальные заглушки для эмоционального классификатора
EMOTIONAL_CLASSIFIER_AVAILABLE = False
EmotionalClassifier = None
EmotionalState = None
TOOLS_INSTRUCTION_MANAGER_AVAILABLE = False

# Простая заглушка для эмоционального состояния
class SimpleEmotionalState:
    def __init__(self, emotion="neutral", confidence=0.5):
        self.emotion = emotion
        self.confidence = confidence
        
class SimpleEmotionalClassifier:
    """Простая локальная реализация эмоционального классификатора для UI"""
    def analyze_emotion(self, text, context=None):
        # Базовый анализ эмоций без серверных зависимостей
        emotion = "neutral"
        confidence = 0.5
        
        # Простые эвристики
        text_lower = text.lower()
        if any(word in text_lower for word in ['!', 'отлично', 'супер', 'круто']):
            emotion = "positive"
            confidence = 0.7
        elif any(word in text_lower for word in ['ошибка', 'проблема', 'не работает']):
            emotion = "negative"
            confidence = 0.7
            
        return {
            "emotion": emotion,
            "confidence": confidence,
            "analysis_method": "local_heuristic"
        }

# Инициализируем локальный эмоциональный классификатор
try:
    EmotionalClassifier = SimpleEmotionalClassifier
    EmotionalState = SimpleEmotionalState
    EMOTIONAL_CLASSIFIER_AVAILABLE = True
    logger.info("[INIT] ✅ Локальный эмоциональный классификатор инициализирован")
except Exception as e:
    logger.error(f"[INIT] ❌ Ошибка инициализации локального эмоционального классификатора: {e}")
    EMOTIONAL_CLASSIFIER_AVAILABLE = False

# Создаем директорию для логов, если её нет
# Используем текущую директорию или директорию приложения
try:
    # Пробуем получить путь к директории приложения
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    logs_dir = os.path.join(app_dir, 'logs')
    print(f"[DEBUG-LOGS-PATH] CrewAIClient пробуем путь 1: {logs_dir}")
    
    # Проверяем, что можем создать директорию по этому пути
    os.makedirs(logs_dir, exist_ok=True)
except Exception as e:
    print(f"[DEBUG-LOGS-PATH] Ошибка при создании первичного пути: {e}")
    
    # Используем текущую директорию
    logs_dir = os.path.join(os.getcwd(), 'logs')
    print(f"[DEBUG-LOGS-PATH] CrewAIClient используем текущую директорию: {logs_dir}")
    os.makedirs(logs_dir, exist_ok=True)

# Настраиваем файловый обработчик для логов CrewAI клиента
crewai_log_file = os.path.join(logs_dir, 'crewai_client.log')
file_handler = logging.FileHandler(crewai_log_file, mode='w', encoding='utf-8')  # mode='w' to overwrite

# Форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Устанавливаем уровень логирования для файла
file_handler.setLevel(logging.DEBUG)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)

# Устанавливаем уровень логирования для логгера
logger.setLevel(logging.DEBUG)

# --- NLP (spaCy) ---
try:
    import spacy
    # Загружаем обе модели (русскую и английскую)
    nlp_ru = spacy.load("ru_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy и языковые модели успешно загружены")
except Exception as e:
    logger.warning(f"⚠️ Не удалось загрузить spaCy или языковые модели: {e}")
    nlp_ru = None
    nlp_en = None

class CrewAIClient:
    """
    Клиент для взаимодействия с CrewAI API сервером

    Позволяет UI приложению использовать функциональность CrewAI,
    запущенного в отдельном окружении через REST API.
    """

    def __init__(self, base_url="http://127.0.0.1:5051"):  # Стандартный порт CrewAI API сервера
        self.base_url = base_url
        self.timeout = 30  # Таймаут для API запросов (в секундах)
        self._server_available = None
        self._last_check = 0
        
        # Кэш конфигурации моделей
        self._model_config_cache = None
        self._model_config_last_update = 0
        self._model_config_cache_ttl = 300  # 5 минут
        
        # Инициализация эмоционального классификатора
        self.emotional_classifier = None
        if EMOTIONAL_CLASSIFIER_AVAILABLE:
            try:
                # Используем локальный эмоциональный классификатор
                self.emotional_classifier = EmotionalClassifier()
                logger.info("[INIT] ✅ Локальный эмоциональный классификатор инициализирован")
            except Exception as e:
                logger.error(f"[INIT] ❌ Ошибка инициализации эмоционального классификатора: {e}")
                self.emotional_classifier = None
        
        # Загружаем конфигурацию моделей при инициализации
        try:
            self.load_model_config()
            logger.info("[INIT] ✅ Конфигурация моделей загружена через API")
        except Exception as e:
            logger.warning(f"[INIT] ⚠️ Не удалось загрузить конфигурацию моделей: {e}")

    def brave_search_site(self, query):
        """
        Ищет сайт по запросу через Brave Search API и возвращает первый найденный url.
        """
        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            logger.warning("BRAVE_API_KEY не найден в окружении!")
            return None
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 3}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Ищем первый внешний сайт (не brave.com)
                for item in data.get("web", {}).get("results", []):
                    link = item.get("url")
                    if link and not link.startswith("https://search.brave.com"):
                        return link
            else:
                logger.warning(f"Brave API error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Ошибка Brave Search: {e}")
        return None

    def is_available(self, force_check=False):
        """Проверяет доступность CrewAI API сервера"""
        # Перепроверяем чаще, если предыдущая попытка показала, что сервер недоступен.
        current_time = time.time()
        cache_window = 5 if self._server_available is False else 30  # 5 сек, если сервер был оффлайн
        if (not force_check
                and self._server_available is not None
                and (current_time - self._last_check) < cache_window):
            return self._server_available

        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
            self._server_available = response.status_code == 200
            self._last_check = current_time
            return self._server_available
        except requests.RequestException:
            self._server_available = False
            self._last_check = current_time
            return False

    def load_model_config(self, force_reload=False):
        """
        Загружает конфигурацию моделей через HTTP-запрос к API-эндпоинту /api/config/models
        
        Args:
            force_reload: Принудительная перезагрузка, игнорируя кэш
            
        Returns:
            dict: Конфигурация моделей или None при ошибке
        """
        current_time = time.time()
        
        # Проверяем кэш
        if (not force_reload 
            and self._model_config_cache is not None 
            and (current_time - self._model_config_last_update) < self._model_config_cache_ttl):
            logger.debug("[MODEL_CONFIG] 📋 Используем кэшированную конфигурацию моделей")
            return self._model_config_cache
        
        # Проверяем доступность сервера
        if not self.is_available():
            logger.warning("[MODEL_CONFIG] ⚠️ CrewAI API сервер недоступен")
            return self._model_config_cache  # Возвращаем кэшированную версию если есть
        
        try:
            logger.info("[MODEL_CONFIG] 🔄 Загружаем конфигурацию моделей через API...")
            response = requests.get(
                f"{self.base_url}/api/config/models", 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                config_data = response.json()
                
                # Обновляем кэш
                self._model_config_cache = config_data
                self._model_config_last_update = current_time
                
                logger.info(f"[MODEL_CONFIG] ✅ Конфигурация загружена: {config_data.get('active_count', 0)} активных моделей из {config_data.get('total_models', 0)}")
                logger.info(f"[MODEL_CONFIG] 📊 Провайдеры: {', '.join(config_data.get('providers', []))}")
                
                return config_data
            else:
                logger.error(f"[MODEL_CONFIG] ❌ Ошибка API: {response.status_code} - {response.text}")
                return self._model_config_cache  # Возвращаем кэшированную версию если есть
                
        except requests.RequestException as e:
            logger.error(f"[MODEL_CONFIG] ❌ Ошибка сетевого запроса: {e}")
            return self._model_config_cache  # Возвращаем кэшированную версию если есть
        except Exception as e:
            logger.error(f"[MODEL_CONFIG] ❌ Неожиданная ошибка: {e}")
            return self._model_config_cache  # Возвращаем кэшированную версию если есть
    
    def get_active_models(self):
        """
        Возвращает список активных моделей из конфигурации
        
        Returns:
            list: Список активных моделей или пустой список
        """
        config = self.load_model_config()
        if config:
            return config.get('active_models', [])
        return []
    
    def get_available_providers(self):
        """
        Возвращает список доступных провайдеров из конфигурации
        
        Returns:
            list: Список провайдеров или пустой список
        """
        config = self.load_model_config()
        if config:
            return config.get('providers', [])
        return []

    def analyze_emotion(self, message_text, context=None):
        """
        Анализирует эмоциональное состояние сообщения
        
        Args:
            message_text: Текст сообщения для анализа
            context: Контекст диалога (список предыдущих сообщений)
            
        Returns:
            dict: Результат анализа эмоций или None, если анализ невозможен
        """
        if not self.emotional_classifier or not message_text or not isinstance(message_text, str):
            return None
            
        try:
            # Проверяем, что сообщение не является командой
            if message_text.startswith(('/', '!', '#')):
                return None
                
            # Анализируем эмоциональное состояние через локальную заглушку
            analysis = self.emotional_classifier.analyze_emotion(message_text, context)
            
            # Возвращаем структурированные данные
            return {
                'primary_emotion': analysis.get('emotion', 'neutral'),
                'confidence': analysis.get('confidence', 0.5),
                'intensity': 0.5,  # По умолчанию
                'explanation': f"Локальный анализ: {analysis.get('analysis_method', 'unknown')}",
                'recommendations': []
            }
            
        except Exception as e:
            print(f"⚠️ Ошибка при анализе эмоций: {e}")
            return None
            
    def process_request(self, message: Union[str, Dict[str, Any]], force_crewai: bool = False, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Обработка всех типов CrewAI API и выбором оптимального обработчика
        
        Args:
            message: Входное сообщение (может быть строкой или JSON с данными)
            force_crewai: Принудительно отправить всё в CrewAI (игнорируя простые ответы)
            timeout: Таймаут ожидания в секундах
            
        Returns:
            dict: Ответ от API с полями 'response', 'command' (опционально) и 'emotion_analysis' (не всегда)
        """
        # Добавляем подробное логирование
        logger.debug(f"[REQUEST] Начало обработки сообщ. force_crewai={force_crewai}, timeout={timeout}")
        
        # Обрезаем сообщение в логах для читабельности
        if isinstance(message, dict):
            msg_text = message.get('message', '')
            msg_log = f"{msg_text[:50]}..." if len(msg_text) > 50 else msg_text
        else:
            msg_log = f"{message[:50]}..." if len(str(message)) > 50 else message
            
        logger.debug(f"[REQUEST] Сообщение: {msg_log}")
        
        if not self.is_available():
            logger.error("[REQUEST-ERROR] Сервер CrewAI недоступен")
            return {"response": "Ошибка: Сервер CrewAI недоступен", "error": "CrewAI server not available"}
            
        # Обработка JSON-строки, если она есть
        if isinstance(message, str):
            try:
                logger.debug("[REQUEST] Пробуем парсить JSON из строки")
                message_data = json.loads(message)
                if 'message' in message_data:
                    message = message_data
                    logger.debug("[REQUEST] Успешный парсинг JSON")
            except json.JSONDecodeError:
                logger.debug("[REQUEST] Не удалось парсить JSON, оборачиваем в простейший словарь")
                message = {"message": message}
        
        # Если message не словарь, делаем его словарем
        if not isinstance(message, dict):
            logger.debug("[REQUEST] Преобразуем не-словарь в словарь")
            message = {"message": str(message)}
            
        # --- ИСПРАВЛЕНО: Корректная инициализация MemoryManager и получение истории ---
        memory_manager = MemoryManager()

        # Новая обработка через MCP для инструментов
        if 'metadata' in message and 'tool' in message['metadata']:
            tool_type = message['metadata']['tool']
            args = message['metadata'].get('args', {})
            try:
                mcp_response = self.mcp_client.query({"type": tool_type, "args": args})
                logger.info(f"[MCP] Успешный запрос: {tool_type}")
                return {"response": mcp_response.get('result', ''), "from_mcp": True, "error": None}
            except Exception as e:
                logger.error(f"[MCP-ERROR] Ошибка: {str(e)}")
                return {"response": "", "error": str(e), "from_mcp": False}

        # === ИНТЕГРАЦИЯ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ В РЕАЛЬНЫЙ UI-ЧАТ ===
        # Проверяем, нужны ли детальные инструкции для инструментов
        dynamic_instructions = self._get_dynamic_tool_instructions(message.get('message', ''))
        
        # Добавляем метаданные, если их нет
        if 'metadata' not in message:
            message['metadata'] = {}
            
        # Добавляем динамические инструкции в метаданные запроса
        if dynamic_instructions:
            message['metadata']['dynamic_tool_instructions'] = dynamic_instructions
            logger.info(f"[DYNAMIC-TOOLS] ✅ Добавлены динамические инструкции для {len(dynamic_instructions)} инструментов")
            
        try:
            # Получаем ID сессии из переданных метаданных
            session_id = message.get('metadata', {}).get('session_id', 'default_session')
            logger.debug(f"[REQUEST] Получаем историю сообщений для сессии: {session_id}")
            
            # Получаем историю сообщений (последние 20 сообщений)
            chat_history = memory_manager.get_chat_history(session_id)
            if chat_history:
                # Берем только 20 сообщений
                chat_history = chat_history[-20:]
                logger.info(f"[REQUEST] Получено {len(chat_history)} сообщений из истории для сессии {session_id}")
                
                # Добавляем историю сообщений в переданные данные
                message['metadata']['chat_history'] = chat_history
                logger.debug(f"[REQUEST] История сообщений добавлена в запрос")
            else:
                logger.debug(f"[REQUEST] История сообщений для сессии {session_id} не найдена")
        except Exception as e:
            logger.error(f"[REQUEST-ERROR] Ошибка при получении истории сообщений: {e}")
            # Устанавливаем пустую историю в случае ошибки, чтобы не падать
            message['metadata']['chat_history'] = []
            
        logger.debug(f"[REQUEST] Продолжаем с отправкой запроса к CrewAI API")
            
        # Process attachments if present
        attachments = message.get('metadata', {}).get('attachments', [])
        processed_attachments = []
        for att in attachments:
            path = att['path']
            att_type = att['type']
            name = os.path.basename(path)
            if att_type == 'image':
                with open(path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                processed_attachments.append({'type': 'image', 'content': f'data:image/{os.path.splitext(name)[1][1:]};base64,{content}', 'name': name})
            elif att_type == 'file':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                processed_attachments.append({'type': 'text', 'content': content, 'name': name})
        if processed_attachments:
            message['metadata']['processed_attachments'] = processed_attachments

        # Извлекаем текст сообщения для анализа эмоций
        message_text = message.get('message', '')
        logger.debug(f"[REQUEST] Извлеченный текст сообщения: {message_text[:50]}..." if len(message_text) > 50 else message_text)
        
        # Анализируем эмоциональное состояние, если это не команда
        emotion_analysis = None
        if not any(message_text.startswith(prefix) for prefix in ('/', '!', '#')):
            logger.debug("[REQUEST] Анализ эмоционального состояния...")
            emotion_analysis = self.analyze_emotion(message_text)
            
            # Добавляем информацию об эмоциях в метаданные запроса
            if emotion_analysis:
                logger.debug(f"[REQUEST] Результат анализа эмоций: {emotion_analysis['primary_emotion']}")
                if 'metadata' not in message:
                    message['metadata'] = {}
                message['metadata']['emotion_analysis'] = emotion_analysis
        
        # Добавляем флаг асинхронной обработки
        message['async_processing'] = True
        logger.debug("[REQUEST] Установлен флаг async_processing=True")
        
        # Обрабатываем информацию о выбранной модели
        model_provider = message.get('metadata', {}).get('model_provider', 'gemini')
        model_id = message.get('metadata', {}).get('model_id')
        model_data = message.get('metadata', {}).get('model_data')
        
        logger.info(f"[MODEL] Запрос с провайдером: {model_provider}")
        if model_id:
            logger.info(f"[MODEL] Выбранная модель: {model_id}")
            
        # Добавляем информацию о модели в метаданные для сервера
        if model_provider == 'openrouter' and model_id:
            message['metadata']['preferred_provider'] = 'openrouter'
            message['metadata']['preferred_model'] = model_id
            if model_data:
                message['metadata']['model_info'] = {
                    'name': model_data.get('name', model_id),
                    'context_length': model_data.get('context_length', 4096),
                    'pricing': model_data.get('pricing', {})
                }
            logger.info(f"[MODEL] Настроен запрос для OpenRouter модели: {model_id}")
        else:
            message['metadata']['preferred_provider'] = 'gemini'
            logger.info(f"[MODEL] Используется провайдер по умолчанию: Gemini")
        
        # Добавляем системный промпт, если его нет
        system_prompt = (
            "Ты - полезный ассистент. "
            "Отвечай на русском языке. "
            "Будь вежливым и кратким. "
            "Если не знаешь ответа, так и скажи."
        )
        
        # Адаптируем системный промпт на основе эмоционального анализа
        if emotion_analysis:
            emotion = emotion_analysis['primary_emotion']
            logger.debug(f"[REQUEST] Адаптация системного промпта на основе эмоции: {emotion}")
            
            if emotion in ['depressed', 'sad', 'anxious']:
                system_prompt += " Пользователь выглядит расстроенным, прояви сочувствие и поддержку."
            elif emotion in ['angry', 'frustrated']:
                system_prompt += " Пользователь раздражен, сохраняй спокойствие и будь особенно вежливым."
            elif emotion == 'happy':
                system_prompt += " Пользователь в хорошем настроении, можно быть немного более неформальным."
        
        # Перемещаем system_prompt в metadata вместо корня запроса, так как сервер ожидает только message и metadata
        if 'metadata' not in message:
            message['metadata'] = {}
            
        # Добавляем system_prompt в metadata
        if 'system_prompt' in message:
            # Если system_prompt уже есть в корне запроса, перемещаем его в metadata
            message['metadata']['system_prompt'] = message.pop('system_prompt')
            logger.debug("[REQUEST] Пользовательский системный промпт перемещен в metadata")
        else:
            # Добавляем стандартный системный промпт в metadata
            message['metadata']['system_prompt'] = system_prompt
            logger.debug("[REQUEST] Добавлен стандартный системный промпт в metadata")
            
        logger.debug(f"[REQUEST] Подготовка к отправке запроса в CrewAI API")
        
        try:
            # Увеличиваем таймаут для первого запроса, так как сервер может обрабатывать его дольше
            first_request_timeout = max(30, (timeout or self.timeout) * 2)
            logger.debug(f"[REQUEST] Установлен таймаут {first_request_timeout} секунд для запроса")
            
            url = f"{self.base_url}/api/process"
            logger.debug(f"[REQUEST] Отправка POST запроса на {url} с заголовком Content-Type: application/json; charset=utf-8")
            
            response = requests.post(
                url,
                json=message,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=first_request_timeout
            )
            
            logger.debug(f"[REQUEST] Получен ответ от сервера: HTTP {response.status_code}")
            response.raise_for_status()
            
            # Обработка ответа
            result: Dict[str, Any] = response.json()
            logger.debug(f'Полный ответ Gemini: {result}')
            logger.debug(f"[REQUEST] Успешно парсим JSON ответ: {result}")
            
            # Если ответ содержит только текст, оборачиваем его в словарь
            if isinstance(result, str):
                logger.debug("[REQUEST] Получен текстовый ответ, преобразуем в словарь")
                result = {"response": result}
            
            # Проверяем, вернул ли сервер task_id для асинхронной обработки
            if 'task_id' in result and 'status' in result:
                logger.info(f"[TASK-START] [ASYNC] Получен task_id для асинхронной обработки: {result['task_id']}")
                logger.debug(f"[TASK-START] Начальный статус задачи: {result['status']}")
                return result
                
            # Если это синхронный ответ, добавляем анализ эмоций
            if 'metadata' in message and 'emotion_analysis' in message['metadata']:
                logger.debug("[REQUEST] Добавляем анализ эмоций в синхронный ответ")
                result['emotion_analysis'] = message['metadata']['emotion_analysis']
                
                # Добавляем рекомендации по ответу на основе эмоций
                recommendations = message['metadata']['emotion_analysis'].get('recommendations', [])
                if recommendations and 'metadata' not in result:
                    result['metadata'] = {}
                if recommendations:
                    logger.debug(f"[REQUEST] Добавлены рекомендации по ответу: {recommendations}")
                    result['metadata']['recommended_responses'] = recommendations
            
            # Добавляем обработку терминального вывода
            if isinstance(result, dict) and 'terminal_output' in result:
                term_out = result['terminal_output']
                formatted_output = f"Команда '{term_out['command']}' выполнена в терминале.\nВывод: {term_out['output']}\nОшибки: {term_out['error'] if term_out['error'] else 'Нет'}"
                result['response'] = formatted_output
                result['metadata'] = result.get('metadata', {})
                result['metadata']['terminal_output'] = term_out
                logger.info(f"[TERMINAL] Обработан терминальный вывод для команды: {term_out['command']}")
            
            # Убедимся, что ответ содержит хотя бы пустую строку, а не None
            if 'response' not in result or result['response'] is None:
                logger.debug("[REQUEST] Ответ не содержит 'response', добавляем пустую строку")
                result['response'] = ""
            else:
                logger.debug(f"[REQUEST] Получен ответ: {result['response'][:50]}..." if len(result['response']) > 50 else result['response'])
                
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[REQUEST-ERROR] Ошибка при отправке запроса в CrewAI: {str(e)}")
            return {
                "response": f"Ошибка при отправке запроса: {str(e)}",
                "error": "request_error",
                "processed_with_crewai": False
            }
            
    def check_task_status(self, task_id):
        """
        Проверяет статус асинхронной задачи
        
        Args:
            task_id: ID задачи для проверки
            
        Returns:
            dict: Состояние задачи или сообщение об ошибке
        """
        logger.debug(f"[TASK-CHECK] Проверка статуса задачи: {task_id}")
        
        if not self.is_available():
            logger.error(f"[TASK-CHECK] Сервер CrewAI недоступен при проверке задачи {task_id}")
            return {"error": "Сервер CrewAI недоступен", "status": "error"}
            
        try:
            url = f"{self.base_url}/api/task/{task_id}"
            logger.debug(f"[TASK-CHECK] Отправка GET запроса на: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"[TASK-CHECK] Получен ответ для задачи {task_id}: {result}")
                
                # Подробное логирование состояния задачи
                if result.get("done"):
                    # Извлекаем информацию о модели из ответа
                    task_result = result.get('result', {})
                    model_info = task_result.get('model_info', {})
                    
                    if model_info:
                        model_display = f"{model_info.get('display_name', 'Unknown')} ({model_info.get('provider', 'unknown')}/{model_info.get('model_id', 'unknown')})"
                        logger.info(f"[TASK-COMPLETE] ✅ Задача {task_id} завершена. Ответ от модели: {model_display}")
                        logger.info(f"[RESPONSE-FROM-MODEL] 🤖 Модель: {model_display} | Ответ: {task_result.get('response', '')[:100]}...")
                    else:
                        logger.info(f"[TASK-COMPLETE] Задача {task_id} завершена. Результат: {task_result.get('response', '')[:100]}...")
                else:
                    logger.info(f"[TASK-PROGRESS] Задача {task_id} в процессе. Статус: {result.get('status', 'неизвестно')}")
                
                return result
            else:
                logger.error(f"[TASK-ERROR] Ошибка при проверке статуса задачи {task_id}: HTTP {response.status_code} - {response.text}")
                return {"error": f"Ошибка сервера: {response.status_code}", "status": "error"}
                
        except requests.RequestException as e:
            logger.error(f"[TASK-ERROR] Ошибка соединения при проверке задачи {task_id}: {str(e)}")
            return {"error": f"Ошибка соединения: {str(e)}", "status": "error"}
            
    def index_documentation(self):
        """Запускает индексацию документации CrewAI"""
        if not self.is_available():
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/api/index_docs",
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"error_message": str(e), "processed_with_crewai": False}

    def _get_dynamic_tool_instructions(self, message_text: str) -> dict:
        """
        Анализирует сообщение пользователя и определяет, какие инструменты могут понадобиться.
        Возвращает словарь с детальными инструкциями для релевантных инструментов.
        
        Args:
            message_text: Текст сообщения пользователя
            
        Returns:
            dict: Словарь {tool_name: detailed_instructions} для релевантных инструментов
        """
        # tools_instruction_manager временно отключен после удаления MCP
        if not message_text:
            return {}
        
        # Возвращаем пустой словарь, так как tools_instruction_manager недоступен
        logger.debug("[DYNAMIC-TOOLS] tools_instruction_manager недоступен, возвращаем пустые инструкции")
        return {}

    def _handle_browser_command(self, message):
        """
        Обрабатывает команды браузера, начинающиеся с /browser или /браузер
        
{{ ... }}
            message: Полный текст сообщения с командой
            
        Returns:
            dict: Ответ с командой для браузера
        """
        # Удаляем префикс команды
        command = message.split(' ', 1)[1] if ' ' in message else ""
        
        # Простая проверка на URL
        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', command)
        
        # Если в команде есть URL, используем его, иначе ищем через поиск
        if url_match:
            url = url_match.group(0)
            return {
                "impl": "browser-use",
                "command": "go_to_url",
                "args": {"url": url},
                "response": f"Открываю: {url}"
            }
        elif command.strip():
            # Если это не URL, но есть текст команды - ищем через поиск
            return {
                "impl": "browser-use",
                "command": "search",
                "args": {"query": command},
                "response": f"Ищу в интернете: {command}"
            }
        else:
            # Если команда пустая после префикса
            return {
                "response": "Пожалуйста, укажите URL или поисковый запрос после /browser",
                "error": "invalid_browser_command"
            }

    def nlp_parse_command(self, message, lang_hint=None):
        """
        Пример базового NLP-парсинга команды с помощью spaCy.
        Возвращает список сущностей и ключевых слов.
        lang_hint: 'ru' или 'en' — если явно известно, иначе autodetect.
        """
        if nlp_ru is None or nlp_en is None:
            logger.warning("spaCy не инициализирован — NLP-парсинг недоступен")
            return None
        # Определяем язык (очень просто)
        lang = lang_hint
        if not lang:
            if any(ord(c) > 127 for c in message):
                lang = 'ru'
            else:
                lang = 'en'
        nlp = nlp_ru if lang == 'ru' else nlp_en
        doc = nlp(message)
        # Извлекаем сущности и ключевые слова
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        logger.info(f"[NLP] entities: {entities}, tokens: {tokens}")
        return {"entities": entities, "tokens": tokens, "lang": lang}

# Глобальный экземпляр клиента
crewai_client = CrewAIClient()