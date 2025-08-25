"""
⚙️ Конфигурация инструментов GopiAI
Централизованная настройка всех инструментов
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class ToolsConfig:
    """Класс для управления конфигурацией инструментов"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        self.config = self._load_default_config()
        self._load_user_config()
        self._load_env_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию по умолчанию"""
        return {
            "filesystem": {
                "enabled": True,
                "safe_mode": True,
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "allowed_extensions": [".txt", ".json", ".csv", ".md", ".py", ".js", ".html", ".css"],
                "forbidden_paths": ["/etc", "/sys", "/proc", "C:\\Windows\\System32"],
                "backup_enabled": True
            },
            "terminal": {
                "enabled": True,
                "safe_mode": True,
                "timeout": 30,
                "allowed_commands": [
                    "ls", "dir", "pwd", "cd", "echo", "cat", "type", "find", "grep",
                    "mkdir", "touch", "cp", "copy", "mv", "move", "rm", "del",
                    "python", "pip", "node", "npm", "git"
                ],
                "forbidden_commands": [
                    "rm -rf /", "format", "fdisk", "shutdown", "reboot", "halt",
                    "dd", "mkfs", "chmod 777", "chown", "su", "sudo"
                ]
            },
            "web_search": {
                "enabled": True,
                "default_engine": "duckduckgo",
                "max_results": 20,
                "timeout": 10,
                "cache_enabled": True,
                "cache_ttl": 3600,  # 1 hour
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "web_viewer": {
                "enabled": True,
                "timeout": 10,
                "max_content_length": 1024 * 1024,  # 1MB
                "cache_enabled": True,
                "cache_ttl": 1800,  # 30 minutes
                "allowed_domains": [],  # Пустой список = все домены разрешены
                "forbidden_domains": ["localhost", "127.0.0.1", "0.0.0.0"]
            },
            "memory": {
                "enabled": False,  # Дополнительный инструмент
                "max_entries": 10000,
                "auto_cleanup": True,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            },
            "communication": {
                "enabled": False,  # Дополнительный инструмент
                "max_message_size": 1024,
                "queue_size": 100
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True,
                "max_log_size": 10 * 1024 * 1024  # 10MB
            }
        }
    
    def _load_user_config(self):
        """Загружает пользовательскую конфигурацию из файла"""
        config_paths = [
            Path.cwd() / "tools_config.json",
            Path.cwd() / "config" / "tools_config.json",
            Path(__file__).parent / "config" / "tools_config.json",
            Path.home() / ".gopiai" / "tools_config.json"
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                    self._merge_config(user_config)
                    print(f"✅ Загружена пользовательская конфигурация: {config_path}")
                    break
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки конфигурации {config_path}: {e}")
    
    def _load_env_config(self):
        """Загружает конфигурацию из переменных окружения"""
        env_mappings = {
            "SERPER_API_KEY": ("api_keys", "serper_api_key"),
            "SERPAPI_API_KEY": ("api_keys", "serpapi_api_key"),
            "OPENAI_API_KEY": ("api_keys", "openai_api_key"),
            "GOOGLE_API_KEY": ("api_keys", "google_api_key"),
            "GOPIAI_TERMINAL_UNSAFE": ("terminal", "safe_mode"),
            "GOPIAI_WEB_SEARCH_ENGINE": ("web_search", "default_engine"),
            "GOPIAI_LOG_LEVEL": ("logging", "level")
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if key == "safe_mode" and env_var == "GOPIAI_TERMINAL_UNSAFE":
                    # Инвертируем значение для safe_mode
                    value = not self._str_to_bool(value)
                elif key in ["serper_api_key", "serpapi_api_key", "openai_api_key", "google_api_key"]:
                    # API ключи остаются строками
                    pass
                else:
                    # Пытаемся преобразовать в подходящий тип
                    value = self._convert_value(value)
                
                self.config[section][key] = value
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Объединяет пользовательскую конфигурацию с базовой"""
        for section, settings in user_config.items():
            if section in self.config:
                if isinstance(settings, dict):
                    self.config[section].update(settings)
                else:
                    self.config[section] = settings
            else:
                self.config[section] = settings
    
    def _str_to_bool(self, value: str) -> bool:
        """Преобразует строку в boolean"""
        return str(value).lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    def _convert_value(self, value: str) -> Any:
        """Пытается преобразовать строковое значение в подходящий тип"""
        # Попытка преобразовать в число
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Попытка преобразовать в boolean
        if value.lower() in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
            return self._str_to_bool(value)
        
        # Остается строкой
        return value
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Получает значение конфигурации"""
        if key is None:
            return self.config.get(section, default)
        else:
            return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """Устанавливает значение конфигурации"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Проверяет, включен ли инструмент"""
        return self.get(tool_name, "enabled", False)
    
    def get_api_key(self, service: str) -> str:
        """Получает API ключ для сервиса"""
        return self.get("api_keys", f"{service}_api_key", None)
    
    def save_config(self, path: str = None):
        """Сохраняет текущую конфигурацию в файл"""
        if path is None:
            path = Path.cwd() / "tools_config.json"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Конфигурация сохранена: {path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Возвращает список всех доступных инструментов"""
        return [
            "filesystem", 
            "terminal", 
            "web_search", 
            "web_viewer", 
            "memory", 
            "communication",
            "simple_filesystem",
            "simple_code_executor",
            "command_executor",
            "code_interpreter"
        ]
    
    def get_active_tools(self) -> List[str]:
        """Возвращает список активных инструментов"""
        active_tools = []
        for tool_name in ["filesystem", "terminal", "web_search", "web_viewer", "memory", "communication"]:
            if self.is_tool_enabled(tool_name):
                active_tools.append(tool_name)
        return active_tools
    
    def print_status(self):
        """Выводит статус всех инструментов"""
        print("🔧 Статус инструментов GopiAI:")
        print("-" * 40)
        
        for tool_name in ["filesystem", "terminal", "web_search", "web_viewer", "memory", "communication"]:
            enabled = self.is_tool_enabled(tool_name)
            status = "✅ Включен" if enabled else "❌ Отключен"
            print(f"  {tool_name}: {status}")

        
        print("-" * 40)
        print(f"📊 Активных инструментов: {len(self.get_active_tools())}")

# Глобальный экземпляр конфигурации
_config = None

def get_config() -> ToolsConfig:
    """Возвращает глобальный экземпляр конфигурации"""
    global _config
    if _config is None:
        _config = ToolsConfig()
    return _config

def reload_config():
    """Перезагружает конфигурацию"""
    global _config
    _config = ToolsConfig()
    return _config

if __name__ == "__main__":
    # Демонстрация работы конфигурации
    config = get_config()
    config.print_status()
    
    print("\n📋 Примеры использования:")
    print(f"  Файловая система включена: {config.is_tool_enabled('filesystem')}")
    print(f"  Максимальный размер файла: {config.get('filesystem', 'max_file_size')}")
    print(f"  Поисковая система по умолчанию: {config.get('web_search', 'default_engine')}")
    try:
        print(f"  API ключ Serper: {'Установлен' if config.get_api_key('serper') else 'Не установлен'}")
    except:
        pass
