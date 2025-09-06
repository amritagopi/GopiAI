"""
Local MCP Tools - локальные MCP инструменты
Восстановлено из коммита 2f0fe4256d7f0d5bf2168a4db56d6b6def937860
"""

import logging
import os
import platform
import subprocess
from typing import Dict, Any, List
from datetime import datetime

from .terminal_tool import TerminalTool

logger = logging.getLogger(__name__)

class LocalMCPTools:
    """Менеджер локальных MCP инструментов"""
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
        logger.info(f"🔧 LocalMCPTools инициализирован с {len(self.tools)} инструментами")
    
    def _initialize_tools(self):
        """Инициализирует все локальные инструменты"""
        
        # Terminal tool
        self.tools['terminal'] = TerminalTool()
        
        # System info tool
        self.tools['system_info'] = SystemInfoTool()
        
        # Time helper tool
        self.tools['time_helper'] = TimeHelperTool()
        
        # Project helper tool
        self.tools['project_helper'] = ProjectHelperTool()
        
        logger.info(f"Инициализированы инструменты: {list(self.tools.keys())}")
    
    def get_available_tools(self) -> List[str]:
        """Возвращает список доступных инструментов"""
        return list(self.tools.keys())
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный инструмент с параметрами"""
        if tool_name not in self.tools:
            logger.error(f"❌ Инструмент '{tool_name}' не найден")
            return {
                "success": False,
                "error": f"Инструмент '{tool_name}' не найден"
            }
        
        tool = self.tools[tool_name]
        logger.info(f"🔧 Вызов инструмента: {tool_name}")
        
        try:
            if hasattr(tool, 'execute'):
                return tool.execute(params)
            elif hasattr(tool, '_run'):
                return tool._run(params.get('command', ''))
            else:
                return {
                    "success": False,
                    "error": f"Инструмент '{tool_name}' не имеет метода выполнения"
                }
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении инструмента '{tool_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }

class SystemInfoTool:
    """Инструмент для получения системной информации"""
    
    def __init__(self):
        self.name = "system_info"
        self.description = "Получает информацию о системе"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Возвращает системную информацию"""
        try:
            info = {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "current_directory": os.getcwd(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Дополнительная информация для Linux/Unix
            if platform.system() in ['Linux', 'Darwin']:
                try:
                    info["uptime"] = subprocess.check_output(['uptime'], text=True).strip()
                except:
                    pass
                
                try:
                    info["memory"] = subprocess.check_output(['free', '-h'], text=True)
                except:
                    pass
            
            return {
                "success": True,
                "data": info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class TimeHelperTool:
    """Инструмент для работы со временем"""
    
    def __init__(self):
        self.name = "time_helper"
        self.description = "Утилиты для работы со временем"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет операции со временем"""
        try:
            operation = params.get('operation', 'current_time')
            
            if operation == 'current_time':
                now = datetime.now()
                return {
                    "success": True,
                    "data": {
                        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "iso_format": now.isoformat(),
                        "timestamp": now.timestamp(),
                        "weekday": now.strftime("%A"),
                        "timezone": str(now.astimezone().tzinfo)
                    }
                }
            
            elif operation == 'format_time':
                time_str = params.get('time', datetime.now().isoformat())
                format_str = params.get('format', '%Y-%m-%d %H:%M:%S')
                
                if isinstance(time_str, str):
                    dt = datetime.fromisoformat(time_str)
                else:
                    dt = datetime.now()
                
                return {
                    "success": True,
                    "data": {
                        "formatted_time": dt.strftime(format_str),
                        "original": time_str
                    }
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Неизвестная операция: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ProjectHelperTool:
    """Инструмент для работы с проектом"""
    
    def __init__(self):
        self.name = "project_helper" 
        self.description = "Утилиты для работы с проектом GopiAI"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет операции с проектом"""
        try:
            action = params.get('action', 'health_check')
            
            if action == 'health_check':
                return self._health_check()
            elif action == 'project_info':
                return self._project_info()
            else:
                return {
                    "success": False,
                    "error": f"Неизвестное действие: {action}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _health_check(self) -> Dict[str, Any]:
        """Проверяет состояние проекта"""
        health_info = {
            "timestamp": datetime.now().isoformat(),
            "working_directory": os.getcwd(),
            "project_components": {},
            "environment_variables": {}
        }
        
        # Проверяем наличие ключевых файлов проекта
        key_files = [
            "GopiAI-CrewAI/crewai_api_server.py",
            "GopiAI-UI/gopiai/ui/main.py",
            ".env"
        ]
        
        for file_path in key_files:
            health_info["project_components"][file_path] = os.path.exists(file_path)
        
        # Проверяем переменные окружения
        env_vars = ["GEMINI_API_KEY", "TAVILY_API_KEY"]
        for var in env_vars:
            value = os.getenv(var)
            health_info["environment_variables"][var] = bool(value and len(value) > 10)
        
        # Определяем общий статус
        files_ok = all(health_info["project_components"].values())
        env_ok = health_info["environment_variables"].get("GEMINI_API_KEY", False)
        
        overall_status = "healthy" if files_ok and env_ok else "needs_attention"
        
        return {
            "success": True,
            "data": {
                "status": overall_status,
                "details": health_info
            }
        }
    
    def _project_info(self) -> Dict[str, Any]:
        """Возвращает информацию о проекте"""
        info = {
            "name": "GopiAI",
            "version": "2.0-gemini",
            "components": ["GopiAI-CrewAI", "GopiAI-UI", "GopiAI-Assets"],
            "primary_llm": "Gemini API",
            "architecture": "Modular AI Platform"
        }
        
        return {
            "success": True,
            "data": info
        }

def get_local_mcp_tools() -> LocalMCPTools:
    """Фабричная функция для создания экземпляра LocalMCPTools"""
    return LocalMCPTools()