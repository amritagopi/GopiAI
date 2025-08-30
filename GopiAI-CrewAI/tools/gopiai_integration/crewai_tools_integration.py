"""
🔧 CrewAI Tools Integration with Dynamic Instructions
Интеграция системы динамической подгрузки инструкций в workflow CrewAI
"""

import logging
import functools
from typing import Any, Dict, List, Optional, Callable
from crewai import Agent, Task, Crew
from crewai.tools.agent_tools import StructuredTool as BaseTool

from .tools_instruction_manager import get_tools_instruction_manager

logger = logging.getLogger(__name__)

class CrewAIToolsInstructionIntegrator:
    """
    Интегратор для внедрения динамических инструкций в CrewAI workflow.
    Перехватывает вызовы инструментов и добавляет детальные инструкции.
    """
    
    def __init__(self):
        """Инициализация интегратора"""
        self.logger = logging.getLogger(__name__)
        self.tools_manager = get_tools_instruction_manager()
        self.original_tool_methods = {}
        self.logger.info("✅ CrewAI Tools Instruction Integrator инициализирован")
    
    def enhance_tool_with_instructions(self, tool: BaseTool) -> BaseTool:
        """
        Улучшает инструмент, добавляя динамическую подгрузку инструкций.
        
        Args:
            tool (BaseTool): Оригинальный инструмент CrewAI
            
        Returns:
            BaseTool: Улучшенный инструмент с динамическими инструкциями
        """
        # Определяем название инструмента для поиска инструкций
        tool_name = self._get_tool_name(tool)
        
        # Сохраняем оригинальный метод _run
        if hasattr(tool, '_run') and tool_name not in self.original_tool_methods:
            self.original_tool_methods[tool_name] = tool._run
            
            # Создаем обертку с инструкциями
            def enhanced_run(*args, **kwargs):
                # Получаем детальные инструкции для инструмента
                detailed_instructions = self.tools_manager.get_tool_detailed_instructions(tool_name)
                
                if detailed_instructions:
                    self.logger.info(f"📖 Подгружены инструкции для {tool_name}")
                    
                    # Добавляем инструкции в контекст инструмента
                    if hasattr(tool, 'description'):
                        original_description = tool.description
                        tool.description = f"{original_description}\n\n{detailed_instructions}"
                    
                    try:
                        # Выполняем оригинальный метод
                        result = self.original_tool_methods[tool_name](*args, **kwargs)
                        
                        # Восстанавливаем оригинальное описание
                        if hasattr(tool, 'description'):
                            tool.description = original_description
                            
                        return result
                    except Exception as e:
                        # Восстанавливаем описание даже при ошибке
                        if hasattr(tool, 'description'):
                            tool.description = original_description
                        raise e
                else:
                    # Если инструкций нет, выполняем как обычно
                    return self.original_tool_methods[tool_name](*args, **kwargs)
            
            # Заменяем метод _run на улучшенный
            tool._run = enhanced_run
            
        return tool
    
    def _get_tool_name(self, tool: BaseTool) -> str:
        """
        Определяет название инструмента для поиска инструкций.
        
        Args:
            tool (BaseTool): Инструмент CrewAI
            
        Returns:
            str: Название инструмента
        """
        # Пытаемся определить тип инструмента по классу
        tool_class_name = tool.__class__.__name__.lower()
        
        # Маппинг классов инструментов к названиям в ToolsInstructionManager
        tool_mapping = {
            'gopiaifilestool': 'filesystem_tools',
            'gopiaifilestool': 'filesystem_tools', 
            'gopiailocalmcptool': 'local_mcp_tools',
            'gopiaibrowsertool': 'browser_tools',
            'gopiaiwebsearchtool': 'web_search',
            'gopiaipageanalyzertool': 'page_analyzer'
        }
        
        # Поиск по точному совпадению
        for class_pattern, tool_name in tool_mapping.items():
            if class_pattern in tool_class_name:
                return tool_name
        
        # Если точного совпадения нет, пытаемся найти по ключевым словам
        if 'file' in tool_class_name or 'filesystem' in tool_class_name:
            return 'filesystem_tools'
        elif 'browser' in tool_class_name:
            return 'browser_tools'
        elif 'search' in tool_class_name or 'web' in tool_class_name:
            return 'web_search'
        elif 'mcp' in tool_class_name:
            return 'local_mcp_tools'
        elif 'analyzer' in tool_class_name or 'analysis' in tool_class_name:
            return 'page_analyzer'
        
        # По умолчанию возвращаем имя класса
        return tool_class_name
    
    def enhance_agent_tools(self, agent: Agent) -> Agent:
        """
        Улучшает все инструменты агента, добавляя динамические инструкции.
        
        Args:
            agent (Agent): Агент CrewAI
            
        Returns:
            Agent: Агент с улучшенными инструментами
        """
        if hasattr(agent, 'tools') and agent.tools:
            enhanced_tools = []
            for tool in agent.tools:
                enhanced_tool = self.enhance_tool_with_instructions(tool)
                enhanced_tools.append(enhanced_tool)
            
            agent.tools = enhanced_tools
            self.logger.info(f"✅ Улучшено {len(enhanced_tools)} инструментов для агента {agent.role}")
        
        return agent
    
    def enhance_crew_agents(self, crew: Crew) -> Crew:
        """
        Улучшает всех агентов в команде, добавляя динамические инструкции к их инструментам.
        
        Args:
            crew (Crew): Команда CrewAI
            
        Returns:
            Crew: Команда с улучшенными агентами
        """
        if hasattr(crew, 'agents') and crew.agents:
            enhanced_agents = []
            for agent in crew.agents:
                enhanced_agent = self.enhance_agent_tools(agent)
                enhanced_agents.append(enhanced_agent)
            
            crew.agents = enhanced_agents
            self.logger.info(f"✅ Улучшена команда с {len(enhanced_agents)} агентами")
        
        return crew


# Глобальный экземпляр интегратора
_tools_integrator = None

def get_tools_integrator() -> CrewAIToolsInstructionIntegrator:
    """
    Возвращает глобальный экземпляр интегратора инструкций.
    
    Returns:
        CrewAIToolsInstructionIntegrator: Экземпляр интегратора
    """
    global _tools_integrator
    if _tools_integrator is None:
        _tools_integrator = CrewAIToolsInstructionIntegrator()
    return _tools_integrator


def enhance_crew_with_instructions(crew: Crew) -> Crew:
    """
    Удобная функция для улучшения команды динамическими инструкциями.
    
    Args:
        crew (Crew): Команда CrewAI
        
    Returns:
        Crew: Команда с динамическими инструкциями
    """
    integrator = get_tools_integrator()
    return integrator.enhance_crew_agents(crew)


def enhance_agent_with_instructions(agent: Agent) -> Agent:
    """
    Удобная функция для улучшения агента динамическими инструкциями.
    
    Args:
        agent (Agent): Агент CrewAI
        
    Returns:
        Agent: Агент с динамическими инструкциями
    """
    integrator = get_tools_integrator()
    return integrator.enhance_agent_tools(agent)


# Декоратор для автоматического улучшения команд
def with_dynamic_instructions(func: Callable) -> Callable:
    """
    Декоратор для автоматического добавления динамических инструкций к командам.
    
    Args:
        func (Callable): Функция, возвращающая Crew или Agent
        
    Returns:
        Callable: Обернутая функция с динамическими инструкциями
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        if isinstance(result, Crew):
            return enhance_crew_with_instructions(result)
        elif isinstance(result, Agent):
            return enhance_agent_with_instructions(result)
        else:
            logger.warning(f"⚠️ Декоратор @with_dynamic_instructions применен к функции, возвращающей {type(result)}")
            return result
    
    return wrapper


if __name__ == "__main__":
    # Пример использования
    from tools.gopiai_integration.filesystem_tools import GopiAIFileSystemTool
    from tools.gopiai_integration.browser_tools import GopiAIBrowserTool
    
    # Создаем агента с инструментами
    agent = Agent(
        role='Test Agent',
        goal='Test dynamic instructions',
        backstory='Testing agent for dynamic instructions',
        tools=[GopiAIFileSystemTool(), GopiAIBrowserTool()],
        verbose=True
    )
    
    # Улучшаем агента динамическими инструкциями
    enhanced_agent = enhance_agent_with_instructions(agent)
    
    print("✅ Агент улучшен динамическими инструкциями!")
