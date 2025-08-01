"""
Менеджер состояния для синхронизации настроек провайдера/модели между UI и backend.

Этот модуль обеспечивает:
- Сохранение текущего провайдера и модели в ~/.gopiai_state.json
- Загрузку состояния при запуске приложения
- Потокобезопасные операции чтения/записи
- Валидацию данных состояния
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Путь к файлу состояния в домашней директории пользователя
STATE_FILE_PATH = Path.home() / ".gopiai_state.json"

@dataclass
class ProviderModelState:
    """Структура данных для хранения состояния провайдера и модели."""
    provider: str
    model_id: str
    last_updated: str
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует состояние в словарь для JSON сериализации."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderModelState':
        """Создаёт объект состояния из словаря."""
        return cls(
            provider=data.get('provider', 'gemini'),
            model_id=data.get('model_id', ''),
            last_updated=data.get('last_updated', datetime.now().isoformat()),
            version=data.get('version', '1.0')
        )


class StateManager:
    """
    Менеджер для управления состоянием провайдера/модели.
    
    Обеспечивает потокобезопасные операции чтения и записи состояния
    в файл ~/.gopiai_state.json.
    """
    
    def __init__(self, state_file_path: Optional[Path] = None):
        """
        Инициализирует менеджер состояния.
        
        Args:
            state_file_path: Путь к файлу состояния (по умолчанию ~/.gopiai_state.json)
        """
        self.state_file_path = state_file_path or STATE_FILE_PATH
        self._lock = threading.RLock()
        self._current_state: Optional[ProviderModelState] = None
        
        logger.info(f"[StateManager] Инициализирован с файлом состояния: {self.state_file_path}")
    
    def load_state(self) -> ProviderModelState:
        """
        Загружает состояние из файла.
        
        Returns:
            ProviderModelState: Текущее состояние или состояние по умолчанию
        """
        with self._lock:
            try:
                if self.state_file_path.exists():
                    logger.debug(f"[StateManager] Загружаем состояние из {self.state_file_path}")
                    
                    with open(self.state_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Валидация структуры данных
                    if not isinstance(data, dict):
                        raise ValueError("Файл состояния содержит некорректные данные")
                    
                    state = ProviderModelState.from_dict(data)
                    self._current_state = state
                    
                    logger.info(f"[StateManager] Загружено состояние: провайдер={state.provider}, модель={state.model_id}")
                    return state
                    
                else:
                    logger.info(f"[StateManager] Файл состояния не найден, создаём состояние по умолчанию")
                    return self._create_default_state()
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"[StateManager] Ошибка при загрузке состояния: {e}")
                logger.info(f"[StateManager] Создаём резервную копию повреждённого файла")
                
                # Создаём резервную копию повреждённого файла
                if self.state_file_path.exists():
                    backup_path = self.state_file_path.with_suffix('.json.backup')
                    self.state_file_path.rename(backup_path)
                    logger.info(f"[StateManager] Резервная копия сохранена: {backup_path}")
                
                return self._create_default_state()
                
            except Exception as e:
                logger.error(f"[StateManager] Неожиданная ошибка при загрузке состояния: {e}")
                return self._create_default_state()
    
    def save_state(self, provider: str, model_id: str) -> bool:
        """
        Сохраняет состояние в файл.
        
        Args:
            provider: Название провайдера (например, 'gemini', 'openrouter')
            model_id: Идентификатор модели
            
        Returns:
            bool: True если сохранение прошло успешно, False в противном случае
        """
        with self._lock:
            try:
                # Валидация входных данных
                if not provider or not isinstance(provider, str):
                    raise ValueError(f"Некорректный провайдер: {provider}")
                
                if not model_id or not isinstance(model_id, str):
                    raise ValueError(f"Некорректный model_id: {model_id}")
                
                # Создаём новое состояние
                state = ProviderModelState(
                    provider=provider.strip(),
                    model_id=model_id.strip(),
                    last_updated=datetime.now().isoformat()
                )
                
                # Создаём директорию если она не существует
                self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Сохраняем в файл с атомарной записью
                temp_path = self.state_file_path.with_suffix('.tmp')
                
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
                
                # Атомарно перемещаем временный файл
                temp_path.replace(self.state_file_path)
                
                self._current_state = state
                
                logger.info(f"[StateManager] Состояние сохранено: провайдер={provider}, модель={model_id}")
                return True
                
            except Exception as e:
                logger.error(f"[StateManager] Ошибка при сохранении состояния: {e}")
                
                # Удаляем временный файл если он существует
                temp_path = self.state_file_path.with_suffix('.tmp')
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception:
                        pass
                
                return False
    
    def get_current_state(self) -> Optional[ProviderModelState]:
        """
        Возвращает текущее состояние без загрузки из файла.
        
        Returns:
            ProviderModelState или None если состояние не загружено
        """
        with self._lock:
            return self._current_state
    
    def _create_default_state(self) -> ProviderModelState:
        """
        Создаёт состояние по умолчанию.
        
        Returns:
            ProviderModelState: Состояние по умолчанию
        """
        default_state = ProviderModelState(
            provider="gemini",
            model_id="gemini-1.5-flash",
            last_updated=datetime.now().isoformat()
        )
        
        self._current_state = default_state
        
        # Сохраняем состояние по умолчанию в файл
        self.save_state(default_state.provider, default_state.model_id)
        
        logger.info(f"[StateManager] Создано состояние по умолчанию: {default_state.provider}/{default_state.model_id}")
        return default_state
    
    def reset_to_default(self) -> ProviderModelState:
        """
        Сбрасывает состояние к значениям по умолчанию.
        
        Returns:
            ProviderModelState: Новое состояние по умолчанию
        """
        with self._lock:
            logger.info("[StateManager] Сброс состояния к значениям по умолчанию")
            return self._create_default_state()
    
    def validate_state_file(self) -> bool:
        """
        Проверяет корректность файла состояния.
        
        Returns:
            bool: True если файл корректен, False в противном случае
        """
        try:
            if not self.state_file_path.exists():
                return False
            
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем наличие обязательных полей
            required_fields = ['provider', 'model_id', 'last_updated']
            for field in required_fields:
                if field not in data:
                    return False
            
            return True
            
        except Exception as e:
            logger.debug(f"[StateManager] Валидация файла состояния не прошла: {e}")
            return False


# Глобальный экземпляр менеджера состояния
_state_manager_instance: Optional[StateManager] = None

def get_state_manager() -> StateManager:
    """
    Возвращает глобальный экземпляр менеджера состояния (singleton).
    
    Returns:
        StateManager: Экземпляр менеджера состояния
    """
    global _state_manager_instance
    
    if _state_manager_instance is None:
        _state_manager_instance = StateManager()
    
    return _state_manager_instance


# Удобные функции для быстрого доступа
def load_provider_model_state() -> ProviderModelState:
    """Загружает текущее состояние провайдера/модели."""
    return get_state_manager().load_state()

def save_provider_model_state(provider: str, model_id: str) -> bool:
    """Сохраняет состояние провайдера/модели."""
    return get_state_manager().save_state(provider, model_id)

def get_current_provider_model() -> Optional[ProviderModelState]:
    """Возвращает текущее состояние без загрузки из файла."""
    return get_state_manager().get_current_state()