"""
Инициализация модуля конфигурации

Загружает и предоставляет доступ к настройкам приложения.
"""

import os
import toml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.config.reasoning_config import ReasoningConfig, DEFAULT_REASONING_CONFIG, PersonalizationConfig

# Версия приложения
VERSION_STRING = "0.1.0"

# Корневая директория проекта
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Рабочая директория для проектов пользователя
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

# Папка с конфигурацией
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")

# Путь к файлу конфигурации
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.toml")

@dataclass
class LLMConfig:
    """Конфигурация для LLM"""
    model: str = "claude-3-sonnet-20240229"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    api_type: str = ""
    api_version: str = ""
    base_url: str = ""
    max_input_tokens: Optional[int] = None
    vision: bool = False

@dataclass
class ProxyConfig:
    """Конфигурация для прокси"""
    server: str = ""
    username: str = ""
    password: str = ""

@dataclass
class BrowserConfig:
    """Конфигурация для браузера"""
    headless: bool = False
    disable_security: bool = True
    chrome_instance_path: str = ""
    extra_chromium_args: Optional[List[str]] = None
    wss_url: Optional[str] = None
    cdp_url: Optional[str] = None
    proxy: Optional[ProxyConfig] = None

@dataclass
class Config:
    """
    Главный класс конфигурации приложения

    Содержит настройки LLM, браузера и reasoning
    """
    llm: Dict[str, LLMConfig] = field(default_factory=dict)
    browser_config: Optional[BrowserConfig] = None
    reasoning_config: ReasoningConfig = field(default_factory=lambda: DEFAULT_REASONING_CONFIG)

    @classmethod
    def load(cls) -> "Config":
        """
        Загружает конфигурацию из файла

        Returns:
            Загруженная конфигурация
        """
        if not os.path.exists(CONFIG_PATH):
            return cls()

        try:
            data = toml.load(CONFIG_PATH)

            config = cls()

            # Загрузка LLM настроек
            if "llm" in data:
                config.llm = {"default": LLMConfig(**data["llm"])}

            # Загрузка настроек браузера
            if "browser" in data:
                browser_data = data["browser"]
                proxy = None

                if "proxy" in browser_data:
                    proxy = ProxyConfig(**browser_data["proxy"])
                    del browser_data["proxy"]

                config.browser_config = BrowserConfig(**browser_data)
                config.browser_config.proxy = proxy

            # Загрузка настроек reasoning
            if "reasoning" in data:
                config.reasoning_config = ReasoningConfig.from_dict(data["reasoning"])

            return config
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return cls()

    def save(self) -> bool:
        """
        Сохраняет конфигурацию в файл

        Returns:
            True если сохранение успешно, False в противном случае
        """
        try:
            data = {}

            # Сохранение LLM настроек
            if "default" in self.llm:
                data["llm"] = {
                    "model": self.llm["default"].model,
                    "api_key": self.llm["default"].api_key,
                    "temperature": self.llm["default"].temperature,
                    "max_tokens": self.llm["default"].max_tokens,
                    "api_type": self.llm["default"].api_type,
                    "api_version": self.llm["default"].api_version,
                    "base_url": self.llm["default"].base_url,
                    "vision": self.llm["default"].vision
                }

                # Добавляем max_input_tokens только если он задан
                if self.llm["default"].max_input_tokens is not None:
                    data["llm"]["max_input_tokens"] = self.llm["default"].max_input_tokens

            # Сохранение настроек браузера
            if self.browser_config:
                data["browser"] = {
                    "headless": self.browser_config.headless,
                    "disable_security": self.browser_config.disable_security,
                    "chrome_instance_path": self.browser_config.chrome_instance_path
                }

                # Добавляем extra_chromium_args, если они заданы
                if self.browser_config.extra_chromium_args:
                    data["browser"]["extra_chromium_args"] = self.browser_config.extra_chromium_args

                # Добавляем wss_url, если он задан
                if self.browser_config.wss_url:
                    data["browser"]["wss_url"] = self.browser_config.wss_url

                # Добавляем cdp_url, если он задан
                if self.browser_config.cdp_url:
                    data["browser"]["cdp_url"] = self.browser_config.cdp_url

                if self.browser_config.proxy:
                    data["browser"]["proxy"] = {
                        "server": self.browser_config.proxy.server,
                        "username": self.browser_config.proxy.username,
                        "password": self.browser_config.proxy.password
                    }

            # Сохранение настроек reasoning
            data["reasoning"] = self.reasoning_config.to_dict()

            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                toml.dump(data, f)

            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False

    def ensure_directories(self) -> None:
        """
        Проверяет наличие необходимых директорий и создает их при необходимости
        """
        try:
            # Создаем директорию для хранения профилей персонализации
            if hasattr(self.reasoning_config, "personalization"):
                os.makedirs(self.reasoning_config.personalization.storage_dir, exist_ok=True)

            # Создаем другие необходимые директории
            data_dir = os.path.join(PROJECT_ROOT, "data")
            logs_dir = os.path.join(PROJECT_ROOT, "logs")

            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(logs_dir, exist_ok=True)

        except Exception as e:
            print(f"Ошибка при создании директорий: {e}")

# Глобальный экземпляр конфигурации
config = Config.load()

# Создаем необходимые директории
config.ensure_directories()
