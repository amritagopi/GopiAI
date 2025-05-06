"""
Конфигурация для песочницы
"""

from typing import Dict, Optional
from dataclasses import dataclass

# В идеале импортировать из app.config, но для избежания циклических импортов
# определяем здесь

@dataclass
class SandboxSettings:
    """Настройки песочницы исполнения"""
    use_sandbox: bool = False
    image: str = "python:3.12-slim"
    work_dir: str = "/workspace"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout: int = 300
    network_enabled: bool = False
