#!/usr/bin/env python3
"""
Model Configuration Manager для GopiAI
Управляет переключением между провайдерами (Gemini/OpenRouter) и конфигурациями моделей
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Типы провайдеров моделей"""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GOOGLE = "google"  # Для совместимости с существующим кодом

@dataclass
class ModelConfiguration:
    """Конфигурация модели"""
    provider: ModelProvider
    model_id: str
    display_name: str
    api_key_env: str
    is_active: bool = True
    is_default: bool = False
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь"""
        data = asdict(self)
        data['provider'] = self.provider.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Создает конфигурацию из словаря"""
        data = data.copy()
        data['provider'] = ModelProvider(data['provider'])
        return cls(**data)
    
    def get_litellm_model_name(self) -> str:
        """Возвращает имя модели для LiteLLM"""
        if self.provider == ModelProvider.OPENROUTER:
            if self.model_id.startswith('openrouter/'):
                return self.model_id
            return f"openrouter/{self.model_id}"
        elif self.provider in [ModelProvider.GEMINI, ModelProvider.GOOGLE]:
            return self.model_id
        else:
            return self.model_id
    
    def is_available(self) -> bool:
        """Проверяет, доступна ли конфигурация (есть ли API ключ)"""
        api_key = os.getenv(self.api_key_env)
        return api_key is not None and api_key.strip() != ""

class ModelConfigurationManager:
    """Менеджер конфигураций моделей"""
    
    CONFIG_FILE = "model_configurations.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Инициализация менеджера конфигураций
        
        Args:
            config_dir: Директория для хранения конфигураций
        """
        if config_dir is None:
            # Используем директорию проекта
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / self.CONFIG_FILE
        
        self._configurations: Dict[str, ModelConfiguration] = {}
        self._current_provider: ModelProvider = ModelProvider.GEMINI
        self._current_model_id: Optional[str] = None
        
        self._load_configurations()
        self._ensure_default_configurations()
        
        logger.info(f"🔧 ModelConfigurationManager инициализирован (конфиг: {self.config_file})")
    
    def _ensure_default_configurations(self):
        """Создает конфигурации по умолчанию, если их нет"""
        default_configs = [
            # Gemini конфигурации
            ModelConfiguration(
                provider=ModelProvider.GEMINI,
                model_id="gemini-2.0-flash-exp",
                display_name="Gemini 2.0 Flash (Experimental)",
                api_key_env="GOOGLE_API_KEY",
                is_default=True,
                parameters={"temperature": 0.7, "max_tokens": 8192}
            ),
            ModelConfiguration(
                provider=ModelProvider.GEMINI,
                model_id="gemini-1.5-pro",
                display_name="Gemini 1.5 Pro",
                api_key_env="GOOGLE_API_KEY",
                parameters={"temperature": 0.7, "max_tokens": 8192}
            ),
            ModelConfiguration(
                provider=ModelProvider.GEMINI,
                model_id="gemini-1.5-flash",
                display_name="Gemini 1.5 Flash",
                api_key_env="GOOGLE_API_KEY",
                parameters={"temperature": 0.7, "max_tokens": 8192}
            ),
        ]
        
        # Добавляем конфигурации, которых еще нет
        for config in default_configs:
            config_key = f"{config.provider.value}_{config.model_id}"
            if config_key not in self._configurations:
                self._configurations[config_key] = config
                logger.info(f"➕ Добавлена конфигурация по умолчанию: {config.display_name}")
        
        # Устанавливаем текущую конфигурацию, если не установлена
        if not self._current_model_id:
            default_config = self.get_default_configuration()
            if default_config:
                self._current_provider = default_config.provider
                self._current_model_id = default_config.model_id
                logger.info(f"🎯 Установлена конфигурация по умолчанию: {default_config.display_name}")
    
    def _load_configurations(self):
        """Загружает конфигурации из файла"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Загружаем конфигурации
                configs_data = data.get('configurations', {})
                for key, config_data in configs_data.items():
                    try:
                        config = ModelConfiguration.from_dict(config_data)
                        self._configurations[key] = config
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка загрузки конфигурации {key}: {e}")
                
                # Загружаем текущие настройки
                current_data = data.get('current', {})
                if 'provider' in current_data:
                    self._current_provider = ModelProvider(current_data['provider'])
                if 'model_id' in current_data:
                    self._current_model_id = current_data['model_id']
                
                logger.info(f"📋 Загружено {len(self._configurations)} конфигураций")
            else:
                logger.info("📝 Файл конфигураций не найден, будет создан новый")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигураций: {e}")
            self._configurations = {}
    
    def _save_configurations(self):
        """Сохраняет конфигурации в файл"""
        try:
            # Создаем директорию, если не существует
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            data = {
                'configurations': {
                    key: config.to_dict() 
                    for key, config in self._configurations.items()
                },
                'current': {
                    'provider': self._current_provider.value,
                    'model_id': self._current_model_id
                },
                'version': '1.0',
                'last_updated': str(Path(__file__).stat().st_mtime)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Конфигурации сохранены в {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения конфигураций: {e}")
    
    def add_configuration(self, config: ModelConfiguration) -> str:
        """
        Добавляет новую конфигурацию
        
        Args:
            config: Конфигурация модели
            
        Returns:
            Ключ добавленной конфигурации
        """
        config_key = f"{config.provider.value}_{config.model_id}"
        self._configurations[config_key] = config
        self._save_configurations()
        
        logger.info(f"➕ Добавлена конфигурация: {config.display_name}")
        
        return config_key
    
    def remove_configuration(self, config_key: str) -> bool:
        """
        Удаляет конфигурацию
        
        Args:
            config_key: Ключ конфигурации
            
        Returns:
            True, если конфигурация была удалена
        """
        if config_key in self._configurations:
            config = self._configurations[config_key]
            del self._configurations[config_key]
            self._save_configurations()
            
            logger.info(f"🗑️ Удалена конфигурация: {config.display_name}")
            
            # Если удалили текущую конфигурацию, переключаемся на другую
            if (self._current_provider.value, self._current_model_id) == (config.provider.value, config.model_id):
                self._switch_to_default()
            
            return True
        
        return False
    
    def get_configuration(self, config_key: str) -> Optional[ModelConfiguration]:
        """Возвращает конфигурацию по ключу"""
        return self._configurations.get(config_key)
    
    def get_configurations_by_provider(self, provider: ModelProvider) -> List[ModelConfiguration]:
        """Возвращает все конфигурации для указанного провайдера"""
        return [
            config for config in self._configurations.values()
            if config.provider == provider
        ]
    
    def get_available_configurations(self) -> List[ModelConfiguration]:
        """Возвращает только доступные конфигурации (с API ключами)"""
        return [
            config for config in self._configurations.values()
            if config.is_available()
        ]
    
    def get_all_configurations(self) -> List[ModelConfiguration]:
        """Возвращает все конфигурации"""
        return list(self._configurations.values())
    
    def get_default_configuration(self) -> Optional[ModelConfiguration]:
        """Возвращает конфигурацию по умолчанию"""
        # Ищем конфигурацию с флагом is_default
        for config in self._configurations.values():
            if config.is_default and config.is_available():
                return config
        
        # Если нет конфигурации по умолчанию, берем первую доступную
        available_configs = self.get_available_configurations()
        if available_configs:
            return available_configs[0]
        
        return None
    
    def get_current_configuration(self) -> Optional[ModelConfiguration]:
        """Возвращает текущую активную конфигурацию"""
        if self._current_model_id:
            config_key = f"{self._current_provider.value}_{self._current_model_id}"
            return self._configurations.get(config_key)
        
        return self.get_default_configuration()
    
    def set_current_configuration(self, provider: Union[ModelProvider, str], model_id: str) -> bool:
        """
        Устанавливает текущую конфигурацию
        
        Args:
            provider: Провайдер модели (ModelProvider или строка)
            model_id: ID модели
            
        Returns:
            True, если конфигурация была установлена
        """
        # Преобразуем строку в ModelProvider, если необходимо
        if isinstance(provider, str):
            try:
                provider = ModelProvider(provider)
            except ValueError:
                logger.warning(f"⚠️ Неизвестный провайдер: {provider}")
                return False
        
        config_key = f"{provider.value}_{model_id}"
        
        if config_key in self._configurations:
            config = self._configurations[config_key]
            
            # Устанавливаем конфигурацию даже если API ключ не доступен
            # Это позволит переключаться между моделями даже если ключи не настроены
            self._current_provider = provider
            self._current_model_id = model_id
            self._save_configurations()
            
            if config.is_available():
                logger.info(f"🎯 Установлена текущая конфигурация: {config.display_name}")
            else:
                logger.warning(f"⚠️ Установлена конфигурация, но API ключ недоступен: {config.display_name}")
            
            return True
        else:
            # Если конфигурация не найдена, создаем новую
            try:
                # Определяем API ключ на основе провайдера
                api_key_env = "OPENROUTER_API_KEY" if provider == ModelProvider.OPENROUTER else "GEMINI_API_KEY"
                
                # Создаем новую конфигурацию
                new_config = ModelConfiguration(
                    provider=provider,
                    model_id=model_id,
                    display_name=f"{provider.value}/{model_id}",
                    api_key_env=api_key_env,
                    is_default=False
                )
                
                # Добавляем конфигурацию
                self.add_configuration(new_config)
                
                # Устанавливаем как текущую
                self._current_provider = provider
                self._current_model_id = model_id
                self._save_configurations()
                
                logger.info(f"✅ Создана и установлена новая конфигурация: {provider.value}/{model_id}")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Не удалось создать конфигурацию: {provider.value}/{model_id}: {e}")
                return False
    
    def set_current_model(self, provider: Optional[Union[ModelProvider, str]], model_id: str) -> bool:
        """
        ALIAS для обратной совместимости: Устанавливает текущую модель
        
        Args:
            provider: Провайдер модели (может быть None, тогда определяется автоматически)
            model_id: ID модели
            
        Returns:
            True, если модель была установлена
        """
        # Если провайдер не указан, пробуем определить по model_id
        if provider is None:
            if model_id.startswith('openrouter/'):
                provider = ModelProvider.OPENROUTER
                model_id = model_id.replace('openrouter/', '')
            elif any(gemini_id in model_id.lower() for gemini_id in ['gemini', 'google']):
                provider = ModelProvider.GEMINI
            else:
                # По умолчанию используем OPENROUTER
                provider = ModelProvider.OPENROUTER
        
        return self.set_current_configuration(provider, model_id)
    
    def switch_to_provider(self, provider: Union[ModelProvider, str]) -> bool:
        """
        Переключается на указанного провайдера
        
        Args:
            provider: Провайдер для переключения (ModelProvider или строка)
            
        Returns:
            True, если переключение успешно
        """
        # Преобразуем строку в ModelProvider, если необходимо
        if isinstance(provider, str):
            try:
                provider = ModelProvider(provider)
            except ValueError:
                logger.warning(f"⚠️ Неизвестный провайдер: {provider}")
                return False
        
        # Получаем все конфигурации для провайдера (даже если API ключ не доступен)
        # Это позволит переключаться между провайдерами даже если ключи не настроены
        all_configs = self.get_configurations_by_provider(provider)
        
        if all_configs:
            # Берем первую конфигурацию или конфигурацию по умолчанию
            target_config = None
            for config in all_configs:
                if config.is_default:
                    target_config = config
                    break
            
            if not target_config:
                target_config = all_configs[0]
            
            # Устанавливаем текущий провайдер и модель, даже если API ключ не доступен
            self._current_provider = provider
            self._current_model_id = target_config.model_id
            self._save_configurations()
            
            logger.info(f"🔄 Переключение на провайдера {provider.value}, модель: {target_config.model_id}")
            return True
        else:
            logger.warning(f"⚠️ Нет конфигураций для провайдера {provider.value}")
            return False
    
    def _switch_to_default(self):
        """Переключается на конфигурацию по умолчанию"""
        default_config = self.get_default_configuration()
        if default_config:
            self._current_provider = default_config.provider
            self._current_model_id = default_config.model_id
            self._save_configurations()
            logger.info(f"🔄 Переключение на конфигурацию по умолчанию: {default_config.display_name}")
    
    def add_openrouter_models(self, models: List[Any]):
        """
        Добавляет модели OpenRouter в конфигурации
        
        Args:
            models: Список моделей OpenRouter
        """
        added_count = 0
        
        for model in models:
            # Проверяем, есть ли уже такая конфигурация
            config_key = f"openrouter_{model.id}"
            
            if config_key not in self._configurations:
                config = ModelConfiguration(
                    provider=ModelProvider.OPENROUTER,
                    model_id=model.id,
                    display_name=model.get_display_name(),
                    api_key_env="OPENROUTER_API_KEY",
                    is_active=model.is_active,
                    parameters={
                        "temperature": 0.7,
                        "max_tokens": min(model.context_length // 2, 4096) if model.context_length > 0 else 2048
                    }
                )
                
                self._configurations[config_key] = config
                added_count += 1
        
        if added_count > 0:
            self._save_configurations()
            logger.info(f"➕ Добавлено {added_count} конфигураций OpenRouter моделей")
    
    def get_current_litellm_config(self) -> Dict[str, Any]:
        """
        Возвращает конфигурацию для LiteLLM
        
        Returns:
            Словарь с параметрами для LiteLLM
        """
        current_config = self.get_current_configuration()
        
        if not current_config:
            logger.warning("⚠️ Нет текущей конфигурации, используем Gemini по умолчанию")
            return {
                "model": "gemini-2.0-flash-exp",
                "api_key": os.getenv("GOOGLE_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 4096
            }
        
        # Примечание: parameters гарантированно dict благодаря default_factory=dict
        # Для статического анализатора явно приводим к dict, чтобы убрать предупреждение распаковки
        params: Dict[str, Any] = current_config.parameters or {}
        config = {
            "model": current_config.get_litellm_model_name(),
            "api_key": os.getenv(current_config.api_key_env),
            **params
        }
        
        logger.debug(f"🔧 LiteLLM конфигурация: {current_config.display_name}")
        
        return config
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Возвращает статус всех провайдеров"""
        status = {}
        
        for provider in ModelProvider:
            configs = self.get_configurations_by_provider(provider)
            available_configs = [c for c in configs if c.is_available()]
            
            status[provider.value] = {
                "total_models": len(configs),
                "available_models": len(available_configs),
                "has_api_key": len(available_configs) > 0,
                "is_current": self._current_provider == provider
            }
        
        return status
    
    def validate_configuration(self, config: ModelConfiguration) -> List[str]:
        """
        Валидирует конфигурацию
        
        Args:
            config: Конфигурация для валидации
            
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        if not config.model_id:
            errors.append("Не указан ID модели")
        
        if not config.display_name:
            errors.append("Не указано отображаемое имя")
        
        if not config.api_key_env:
            errors.append("Не указана переменная окружения для API ключа")
        
        if not config.is_available():
            errors.append(f"API ключ не найден в переменной окружения {config.api_key_env}")
        
        return errors

# Глобальный экземпляр менеджера
_global_manager: Optional[ModelConfigurationManager] = None

def get_model_config_manager() -> ModelConfigurationManager:
    """Возвращает глобальный экземпляр менеджера конфигураций"""
    global _global_manager
    
    if _global_manager is None:
        _global_manager = ModelConfigurationManager()
    
    return _global_manager

def test_model_config_manager():
    """Тестовая функция для проверки менеджера конфигураций"""
    print("🧪 === ТЕСТ MODEL CONFIGURATION MANAGER ===")
    
    manager = get_model_config_manager()
    
    # Тест получения конфигураций
    print("\n1. Тестируем получение конфигураций...")
    all_configs = manager.get_all_configurations()
    available_configs = manager.get_available_configurations()
    
    print(f"📋 Всего конфигураций: {len(all_configs)}")
    print(f"✅ Доступных конфигураций: {len(available_configs)}")
    
    # Тест текущей конфигурации
    print("\n2. Тестируем текущую конфигурацию...")
    current_config = manager.get_current_configuration()
    
    if current_config:
        print(f"🎯 Текущая конфигурация: {current_config.display_name}")
        print(f"🔧 Провайдер: {current_config.provider.value}")
        print(f"🆔 Модель: {current_config.model_id}")
        print(f"🔑 API ключ: {current_config.api_key_env}")
        print(f"✅ Доступна: {current_config.is_available()}")
    else:
        print("❌ Нет текущей конфигурации")
    
    # Тест статуса провайдеров
    print("\n3. Тестируем статус провайдеров...")
    status = manager.get_provider_status()
    
    for provider, info in status.items():
        print(f"🔧 {provider.upper()}:")
        print(f"  📊 Моделей: {info['available_models']}/{info['total_models']}")
        print(f"  🔑 API ключ: {'✅' if info['has_api_key'] else '❌'}")
        print(f"  🎯 Активен: {'✅' if info['is_current'] else '❌'}")
    
    # Тест LiteLLM конфигурации
    print("\n4. Тестируем LiteLLM конфигурацию...")
    litellm_config = manager.get_current_litellm_config()
    
    print(f"🔧 Модель для LiteLLM: {litellm_config.get('model', 'не указана')}")
    print(f"🔑 API ключ: {'✅ установлен' if litellm_config.get('api_key') else '❌ не найден'}")
    print(f"🌡️ Temperature: {litellm_config.get('temperature', 'не указана')}")
    
    print("\n✅ Все тесты завершены!")

if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_model_config_manager()
