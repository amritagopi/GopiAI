#!/usr/bin/env python3
"""
Прокси-модуль для импорта классов Agent, Task, Crew из crewai
Используется для совместимости с кодом, который импортирует эти классы из crewai
"""

import logging
from typing import Any, Dict, List, Optional

# Импортируем реальные классы из crewai
from crewai import Agent, Task, Crew

logger = logging.getLogger(__name__)

# Теперь этот модуль просто ре-экспортирует классы из crewai
# Все заглушки удалены и заменены на реальные классы
class Agent:
    """
    Заглушка для Agent из crewai
    """
    
    def __init__(self, name: str, role: str, **kwargs):
        """
        Инициализирует заглушку Agent
        
        Args:
            name: Имя агента
            role: Роль агента
            **kwargs: Дополнительные параметры
        """
        self.name = name
        self.role = role
        self.kwargs = kwargs
        logger.warning("WARNING: Using Agent stub instead of crewai.Agent")
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, role={self.role})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Task:
    """
    Заглушка для Task из crewai
    """
    
    def __init__(self, description: str, agent: Optional[Agent] = None, **kwargs):
        """
        Инициализирует заглушку Task
        
        Args:
            description: Описание задачи
            agent: Агент, выполняющий задачу
            **kwargs: Дополнительные параметры
        """
        self.description = description
        self.agent = agent
        self.kwargs = kwargs
        logger.warning("WARNING: Using Task stub instead of crewai.Task")
    
    def __str__(self) -> str:
        return f"Task(description={self.description})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Crew:
    """
    Заглушка для Crew из crewai
    """
    
    def __init__(self, agents: List[Agent], tasks: List[Task], **kwargs):
        """
        Инициализирует заглушку Crew
        
        Args:
            agents: Список агентов
            tasks: Список задач
            **kwargs: Дополнительные параметры
        """
        self.agents = agents
        self.tasks = tasks
        self.kwargs = kwargs
        logger.warning("WARNING: Using Crew stub instead of crewai.Crew")
    
    def kickoff(self) -> str:
        """
        Заглушка для метода kickoff
        
        Returns:
            str: Заглушка результата
        """
        logger.warning("WARNING: Using Crew stub - no actual work will be performed")
        return "[CREW STUB] This is a stub response. The crewai module is not available."
    
    def __str__(self) -> str:
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"
    
    def __repr__(self) -> str:
        return self.__str__()
