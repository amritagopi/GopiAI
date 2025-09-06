#!/usr/bin/env python3
"""
Тестовый crew для проверки интеграции CrewAI с GopiAI
"""
from typing import Dict, Any
from pathlib import Path

# Добавляем путь к GopiAI модулям
    # Заменено на использование path_manager: sys.path.append(str(Path(__file__).parent.parent.parent))

from crewai import Agent, Task, Crew, Process
import yaml

class TestCrew:
    """Тестовый crew для демонстрации базовой функциональности CrewAI"""
    
    def __init__(self):
        self.crew_dir = Path(__file__).parent
        self.agents_config = self._load_yaml("agents.yaml")
        self.tasks_config = self._load_yaml("tasks.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Загрузка YAML конфигурации"""
        with open(self.crew_dir / filename, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def create_agents(self) -> Dict[str, Agent]:
        """Создание агентов на основе YAML конфигурации"""
        agents = {}
        
        for agent_name, config in self.agents_config.items():
            agents[agent_name] = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=config['backstory'],
                verbose=config.get('verbose', True),
                allow_delegation=config.get('allow_delegation', False)
            )
            
        return agents
    
    def create_tasks(self, agents: Dict[str, Agent], inputs: Dict[str, Any]) -> list[Task]:
        """Создание задач на основе YAML конфигурации"""
        tasks = []
        task_objects = {}
        
        for task_name, config in self.tasks_config.items():
            # Подстановка переменных в описание
            description = config['description'].format(**inputs)
            expected_output = config['expected_output'].format(**inputs)
            
            # Получение агента
            agent = agents[config['agent']]
            
            # Создание задачи
            task = Task(
                description=description,
                expected_output=expected_output,
                agent=agent
            )
            
            # Установка контекста (зависимости от других задач)
            if 'context' in config:
                context_tasks = []
                for context_task_name in config['context']:
                    if context_task_name in task_objects:
                        context_tasks.append(task_objects[context_task_name])
                task.context = context_tasks
            
            # Настройка вывода в файл
            if 'output_file' in config:
                output_file = config['output_file'].format(**inputs)
                task.output_file = output_file
                
                # Создаем директорию для вывода
                output_dir = Path(output_file).parent
                output_dir.mkdir(parents=True, exist_ok=True)
            
            tasks.append(task)
            task_objects[task_name] = task
            
        return tasks
    
    def create_crew(self, agents: Dict[str, Agent], tasks: list[Task]) -> Crew:
        """Создание crew"""
        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def run(self, topic: str = "Искусственный интеллект") -> str:
        """Запуск crew с заданной темой"""
        print(f"🚀 Запуск тестового crew для темы: {topic}")
        
        # Входные данные
        inputs = {"topic": topic}
        
        # Создание агентов и задач
        agents = self.create_agents()
        tasks = self.create_tasks(agents, inputs)
        
        # Создание и запуск crew
        crew = self.create_crew(agents, tasks)
        result = crew.kickoff(inputs=inputs)
        
        print("✅ Crew завершил работу!")
        return str(result)

if __name__ == "__main__":
    # Простой тест
    test_crew = TestCrew()
    result = test_crew.run("CrewAI и многоагентные системы")
    print(f"\n📄 Результат:\n{result}")