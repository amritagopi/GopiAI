"""
Менеджер неограниченных инструментов для AI ассистента.
Управляет инструментами без ограничений безопасности.
"""

from typing import List, Dict, Any, Optional
from crewai.tools.base_tool import BaseTool
import logging

from .unrestricted_filesystem_tool import UnrestrictedFileSystemTool
from .unrestricted_code_executor import UnrestrictedCodeExecutor


class UnrestrictedToolsManager:
    """
    Менеджер для управления неограниченными инструментами AI ассистента.
    Предоставляет полный доступ к системе без ограничений безопасности.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Инициализирует все неограниченные инструменты"""
        try:
            # Инструмент файловой системы
            self._tools['filesystem'] = UnrestrictedFileSystemTool()
            
            # Исполнитель кода
            self._tools['code_executor'] = UnrestrictedCodeExecutor()
            
            self.logger.info("Неограниченные инструменты инициализированы успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации инструментов: {str(e)}")
    
    def get_all_tools(self) -> List[BaseTool]:
        """Возвращает список всех доступных инструментов"""
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Возвращает конкретный инструмент по имени"""
        return self._tools.get(tool_name)
    
    def get_tool_names(self) -> List[str]:
        """Возвращает список имен всех инструментов"""
        return list(self._tools.keys())
    
    def execute_filesystem_operation(self, operation: str, **kwargs) -> str:
        """Выполняет операцию с файловой системой"""
        try:
            filesystem_tool = self._tools.get('filesystem')
            if not filesystem_tool:
                return "Инструмент файловой системы недоступен"
            
            return filesystem_tool._run(operation=operation, **kwargs)
            
        except Exception as e:
            return f"Ошибка выполнения операции файловой системы: {str(e)}"
    
    def execute_code(self, code: str, language: str = "python", **kwargs) -> str:
        """Выполняет код"""
        try:
            code_executor = self._tools.get('code_executor')
            if not code_executor:
                return "Исполнитель кода недоступен"
            
            return code_executor._run(code=code, language=language, **kwargs)
            
        except Exception as e:
            return f"Ошибка выполнения кода: {str(e)}"
    
    def get_tools_info(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает информацию о всех инструментах"""
        tools_info = {}
        
        for name, tool in self._tools.items():
            tools_info[name] = {
                'name': tool.name,
                'description': tool.description,
                'class': tool.__class__.__name__,
                'available': True
            }
        
        return tools_info
    
    def create_agent_tools_list(self) -> List[BaseTool]:
        """Создает список инструментов для агента CrewAI"""
        return self.get_all_tools()


# Глобальный экземпляр менеджера
unrestricted_tools_manager = UnrestrictedToolsManager()


def get_unrestricted_tools() -> List[BaseTool]:
    """Функция для получения списка неограниченных инструментов"""
    return unrestricted_tools_manager.get_all_tools()


def execute_filesystem_command(operation: str, **kwargs) -> str:
    """Быстрая функция для выполнения команд файловой системы"""
    return unrestricted_tools_manager.execute_filesystem_operation(operation, **kwargs)


def execute_code_command(code: str, language: str = "python", **kwargs) -> str:
    """Быстрая функция для выполнения кода"""
    return unrestricted_tools_manager.execute_code(code, language, **kwargs)


# Примеры использования для документации
USAGE_EXAMPLES = {
    "filesystem_operations": [
        {
            "description": "Чтение файла",
            "example": "execute_filesystem_command('read', path='/path/to/file.txt')"
        },
        {
            "description": "Запись файла",
            "example": "execute_filesystem_command('write', path='/path/to/file.txt', content='Hello World')"
        },
        {
            "description": "Выполнение команды",
            "example": "execute_filesystem_command('execute', command='ls -la /tmp')"
        },
        {
            "description": "Поиск файлов",
            "example": "execute_filesystem_command('search', path='/home', pattern='*.py', recursive=True)"
        }
    ],
    "code_execution": [
        {
            "description": "Выполнение Python кода",
            "example": "execute_code_command('print(\"Hello World\")', language='python')"
        },
        {
            "description": "Выполнение bash команды",
            "example": "execute_code_command('ls -la', language='bash')"
        },
        {
            "description": "Установка пакетов и выполнение кода",
            "example": "execute_code_command('import requests; print(requests.get(\"https://api.github.com\").status_code)', install_packages=['requests'])"
        }
    ]
}