"""
Система сохранения и управления конфигурациями CrewAI
Позволяет сохранять настройки агентов, команд и флоу для повторного использования
"""

import json
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ConfigType(Enum):
    """Типы конфигураций"""
    AGENT = "agent"
    CREW = "crew"
    WORKFLOW = "workflow"
    TEMPLATE = "template"

@dataclass
class ConfigMetadata:
    """Метаданные конфигурации"""
    id: str
    name: str
    description: str
    config_type: ConfigType
    version: str
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    is_public: bool = False
    usage_count: int = 0

@dataclass
class SavedConfig:
    """Сохраненная конфигурация"""
    metadata: ConfigMetadata
    config_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сериализации"""
        return {
            "metadata": {
                **asdict(self.metadata),
                "config_type": self.metadata.config_type.value,
                "created_at": self.metadata.created_at.isoformat(),
                "updated_at": self.metadata.updated_at.isoformat()
            },
            "config_data": self.config_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SavedConfig':
        """Создает из словаря"""
        metadata_dict = data["metadata"]
        metadata = ConfigMetadata(
            id=metadata_dict["id"],
            name=metadata_dict["name"],
            description=metadata_dict["description"],
            config_type=ConfigType(metadata_dict["config_type"]),
            version=metadata_dict["version"],
            author=metadata_dict["author"],
            created_at=datetime.fromisoformat(metadata_dict["created_at"]),
            updated_at=datetime.fromisoformat(metadata_dict["updated_at"]),
            tags=metadata_dict["tags"],
            is_public=metadata_dict.get("is_public", False),
            usage_count=metadata_dict.get("usage_count", 0)
        )
        
        return cls(metadata=metadata, config_data=data["config_data"])

class ConfigManager:
    """Менеджер конфигураций"""
    
    def __init__(self, configs_dir: Optional[Path] = None):
        if configs_dir is None:
            configs_dir = Path.home() / ".gopiai" / "configs"
        
        self.configs_dir = configs_dir
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем поддиректории для разных типов
        for config_type in ConfigType:
            (self.configs_dir / config_type.value).mkdir(exist_ok=True)
        
        logger.info(f"ConfigManager инициализирован: {self.configs_dir}")
    
    def save_config(
        self, 
        name: str, 
        config_data: Dict[str, Any], 
        config_type: ConfigType,
        description: str = "",
        author: str = "user",
        tags: Optional[List[str]] = None,
        is_public: bool = False
    ) -> str:
        """
        Сохраняет конфигурацию
        
        Returns:
            str: ID сохраненной конфигурации
        """
        config_id = str(uuid.uuid4())
        now = datetime.now()
        
        if tags is None:
            tags = []
        
        metadata = ConfigMetadata(
            id=config_id,
            name=name,
            description=description,
            config_type=config_type,
            version="1.0.0",
            author=author,
            created_at=now,
            updated_at=now,
            tags=tags,
            is_public=is_public
        )
        
        saved_config = SavedConfig(metadata=metadata, config_data=config_data)
        
        # Путь к файлу
        config_file = self.configs_dir / config_type.value / f"{config_id}.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(saved_config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация сохранена: {name} ({config_id})")
            return config_id
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации {name}: {e}")
            raise
    
    def load_config(self, config_id: str) -> Optional[SavedConfig]:
        """Загружает конфигурацию по ID"""
        # Ищем во всех типах конфигураций
        for config_type in ConfigType:
            config_file = self.configs_dir / config_type.value / f"{config_id}.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    config = SavedConfig.from_dict(data)
                    
                    # Увеличиваем счетчик использования
                    config.metadata.usage_count += 1
                    self.update_config(config)
                    
                    return config
                    
                except Exception as e:
                    logger.error(f"Ошибка загрузки конфигурации {config_id}: {e}")
        
        return None
    
    def list_configs(
        self, 
        config_type: Optional[ConfigType] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ConfigMetadata]:
        """Возвращает список сохраненных конфигураций"""
        configs = []
        
        # Определяем директории для поиска
        if config_type:
            dirs_to_search = [config_type.value]
        else:
            dirs_to_search = [ct.value for ct in ConfigType]
        
        for dir_name in dirs_to_search:
            config_dir = self.configs_dir / dir_name
            if not config_dir.exists():
                continue
            
            for config_file in config_dir.glob("*.json"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    metadata_dict = data["metadata"]
                    metadata = ConfigMetadata(
                        id=metadata_dict["id"],
                        name=metadata_dict["name"],
                        description=metadata_dict["description"],
                        config_type=ConfigType(metadata_dict["config_type"]),
                        version=metadata_dict["version"],
                        author=metadata_dict["author"],
                        created_at=datetime.fromisoformat(metadata_dict["created_at"]),
                        updated_at=datetime.fromisoformat(metadata_dict["updated_at"]),
                        tags=metadata_dict["tags"],
                        is_public=metadata_dict.get("is_public", False),
                        usage_count=metadata_dict.get("usage_count", 0)
                    )
                    
                    # Применяем фильтры
                    if author and metadata.author != author:
                        continue
                    
                    if tags and not any(tag in metadata.tags for tag in tags):
                        continue
                    
                    configs.append(metadata)
                    
                except Exception as e:
                    logger.error(f"Ошибка чтения конфигурации {config_file}: {e}")
        
        # Сортируем по дате обновления (новые сверху)
        configs.sort(key=lambda c: c.updated_at, reverse=True)
        
        return configs
    
    def update_config(self, saved_config: SavedConfig) -> bool:
        """Обновляет существующую конфигурацию"""
        config_id = saved_config.metadata.id
        config_type = saved_config.metadata.config_type
        
        saved_config.metadata.updated_at = datetime.now()
        
        config_file = self.configs_dir / config_type.value / f"{config_id}.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(saved_config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация обновлена: {saved_config.metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления конфигурации {config_id}: {e}")
            return False
    
    def delete_config(self, config_id: str) -> bool:
        """Удаляет конфигурацию"""
        # Ищем во всех типах конфигураций
        for config_type in ConfigType:
            config_file = self.configs_dir / config_type.value / f"{config_id}.json"
            if config_file.exists():
                try:
                    config_file.unlink()
                    logger.info(f"Конфигурация удалена: {config_id}")
                    return True
                except Exception as e:
                    logger.error(f"Ошибка удаления конфигурации {config_id}: {e}")
        
        return False
    
    def export_config(self, config_id: str, export_path: Path) -> bool:
        """Экспортирует конфигурацию в файл"""
        config = self.load_config(config_id)
        if not config:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфигурация экспортирована: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта конфигурации {config_id}: {e}")
            return False
    
    def import_config(self, import_path: Path, new_name: Optional[str] = None) -> Optional[str]:
        """Импортирует конфигурацию из файла"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = SavedConfig.from_dict(data)
            
            # Генерируем новый ID
            config.metadata.id = str(uuid.uuid4())
            
            if new_name:
                config.metadata.name = new_name
            
            # Сохраняем как новую конфигурацию
            return self.save_config(
                name=config.metadata.name,
                config_data=config.config_data,
                config_type=config.metadata.config_type,
                description=config.metadata.description,
                author=config.metadata.author,
                tags=config.metadata.tags,
                is_public=config.metadata.is_public
            )
            
        except Exception as e:
            logger.error(f"Ошибка импорта конфигурации {import_path}: {e}")
            return None
    
    def search_configs(self, query: str) -> List[ConfigMetadata]:
        """Поиск конфигураций по названию или описанию"""
        all_configs = self.list_configs()
        query_lower = query.lower()
        
        matching_configs = []
        for config in all_configs:
            if (query_lower in config.name.lower() or 
                query_lower in config.description.lower() or
                any(query_lower in tag.lower() for tag in config.tags)):
                matching_configs.append(config)
        
        return matching_configs
    
    def get_popular_configs(self, config_type: Optional[ConfigType] = None, limit: int = 10) -> List[ConfigMetadata]:
        """Возвращает популярные конфигурации по количеству использований"""
        configs = self.list_configs(config_type=config_type)
        configs.sort(key=lambda c: c.usage_count, reverse=True)
        return configs[:limit]
    
    def get_recent_configs(self, config_type: Optional[ConfigType] = None, limit: int = 10) -> List[ConfigMetadata]:
        """Возвращает последние конфигурации"""
        configs = self.list_configs(config_type=config_type)
        return configs[:limit]  # Уже отсортированы по дате

class ConfigTemplates:
    """Встроенные шаблоны конфигураций"""
    
    @staticmethod
    def get_agent_templates() -> List[Dict[str, Any]]:
        """Возвращает шаблоны агентов"""
        return [
            {
                "name": "Исследователь",
                "config": {
                    "role": "Исследователь",
                    "goal": "Находить достоверную информацию по любой теме",
                    "backstory": "Опытный исследователь с навыками критического мышления.",
                    "tools": ["search_tool", "web_search_tool"],
                    "verbose": True,
                    "allow_delegation": False
                },
                "description": "Агент для поиска и анализа информации",
                "tags": ["исследование", "поиск", "анализ"]
            },
            {
                "name": "Аналитик данных",
                "config": {
                    "role": "Аналитик данных",
                    "goal": "Анализировать данные и создавать отчеты",
                    "backstory": "Эксперт по анализу данных и статистике.",
                    "tools": ["file_read_tool", "directory_tool", "code_execution"],
                    "verbose": True,
                    "allow_delegation": False
                },
                "description": "Агент для анализа данных и создания отчетов",
                "tags": ["данные", "анализ", "отчеты"]
            },
            {
                "name": "Контент-райтер",
                "config": {
                    "role": "Контент-райтер",
                    "goal": "Создавать качественный контент",
                    "backstory": "Опытный писатель с пониманием аудитории.",
                    "tools": ["search_tool", "web_search_tool"],
                    "verbose": True,
                    "allow_delegation": False
                },
                "description": "Агент для создания текстового контента",
                "tags": ["контент", "написание", "текст"]
            }
        ]
    
    @staticmethod
    def get_crew_templates() -> List[Dict[str, Any]]:
        """Возвращает шаблоны команд"""
        return [
            {
                "name": "Исследовательская команда",
                "config": {
                    "agents": ["researcher", "data_analyst", "content_writer"],
                    "workflow_type": "sequential",
                    "tasks": [
                        "Исследовать тему",
                        "Проанализировать данные", 
                        "Создать отчет"
                    ]
                },
                "description": "Команда для глубокого исследования и анализа",
                "tags": ["исследование", "анализ", "отчет"]
            },
            {
                "name": "Команда разработки",
                "config": {
                    "agents": ["code_reviewer", "qa_engineer", "tech_lead"],
                    "workflow_type": "hierarchical",
                    "tasks": [
                        "Провести код-ревью",
                        "Протестировать функциональность",
                        "Составить план улучшений"
                    ]
                },
                "description": "Команда для анализа и улучшения кода",
                "tags": ["разработка", "код", "качество"]
            }
        ]

# Глобальный экземпляр менеджера конфигураций
config_manager = ConfigManager()

def save_agent_config(name: str, agent_config: Dict[str, Any], **kwargs) -> str:
    """Удобная функция для сохранения конфигурации агента"""
    return config_manager.save_config(
        name=name,
        config_data=agent_config,
        config_type=ConfigType.AGENT,
        **kwargs
    )

def save_crew_config(name: str, crew_config: Dict[str, Any], **kwargs) -> str:
    """Удобная функция для сохранения конфигурации команды"""
    return config_manager.save_config(
        name=name,
        config_data=crew_config,
        config_type=ConfigType.CREW,
        **kwargs
    )

def load_agent_config(config_id: str) -> Optional[Dict[str, Any]]:
    """Удобная функция для загрузки конфигурации агента"""
    config = config_manager.load_config(config_id)
    return config.config_data if config else None

def load_crew_config(config_id: str) -> Optional[Dict[str, Any]]:
    """Удобная функция для загрузки конфигурации команды"""
    config = config_manager.load_config(config_id)
    return config.config_data if config else None

# Пример использования
if __name__ == "__main__":
    # Создаем менеджер конфигураций
    cm = ConfigManager()
    
    # Сохраняем конфигурацию агента
    agent_config = {
        "role": "Тестовый агент",
        "goal": "Тестировать систему",
        "backstory": "Агент для тестирования",
        "tools": ["search_tool"],
        "verbose": True
    }
    
    config_id = cm.save_config(
        name="Тестовый агент",
        config_data=agent_config,
        config_type=ConfigType.AGENT,
        description="Агент для тестирования системы",
        tags=["тест", "агент"]
    )
    
    print(f"Конфигурация сохранена с ID: {config_id}")
    
    # Загружаем конфигурацию
    loaded_config = cm.load_config(config_id)
    if loaded_config:
        print(f"Загружена конфигурация: {loaded_config.metadata.name}")
    
    # Список конфигураций
    configs = cm.list_configs(config_type=ConfigType.AGENT)
    print(f"Найдено конфигураций агентов: {len(configs)}")