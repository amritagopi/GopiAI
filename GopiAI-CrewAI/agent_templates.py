"""
Шаблоны популярных агентов для GopiAI CrewAI
Готовые конфигурации для быстрого создания эффективных команд
"""

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, FileReadTool, DirectoryReadTool, WebsiteSearchTool

# Инструменты
search_tool = SerperDevTool()
file_read_tool = FileReadTool()
directory_tool = DirectoryReadTool()
web_search_tool = WebsiteSearchTool()

class AgentTemplates:
    """Коллекция готовых шаблонов агентов"""
    
    @staticmethod
    def data_analyst():
        """Аналитик данных - анализ файлов, отчеты, визуализация"""
        return Agent(
            role='Аналитик данных',
            goal='Анализировать данные и создавать информативные отчеты',
            backstory="""Ты опытный аналитик данных с глубокими знаниями в области 
            статистики, машинного обучения и визуализации данных. Ты умеешь извлекать 
            ценные инсайты из сложных наборов данных.""",
            tools=[file_read_tool, directory_tool],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def researcher():
        """Исследователь - поиск информации, факт-чекинг"""
        return Agent(
            role='Исследователь',
            goal='Находить достоверную и актуальную информацию по любой теме',
            backstory="""Ты профессиональный исследователь с навыками критического 
            мышления. Ты знаешь, как находить надежные источники информации и 
            проверять факты.""",
            tools=[search_tool, web_search_tool],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def code_reviewer():
        """Ревьюер кода - анализ качества, безопасность, оптимизация"""
        return Agent(
            role='Ревьюер кода',
            goal='Анализировать код на предмет качества, безопасности и производительности',
            backstory="""Ты старший разработчик с многолетним опытом в различных 
            языках программирования. Ты специализируешься на code review, знаешь 
            лучшие практики и паттерны безопасности.""",
            tools=[file_read_tool, directory_tool],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def content_writer():
        """Контент-райтер - создание текстов, статей, документации"""
        return Agent(
            role='Контент-райтер',
            goal='Создавать качественный и увлекательный контент',
            backstory="""Ты опытный писатель и редактор с глубоким пониманием 
            различных стилей письма. Ты умеешь адаптировать тон и стиль под 
            целевую аудиторию.""",
            tools=[search_tool, web_search_tool],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def qa_engineer():
        """Инженер по качеству - тестирование, багрепорты"""
        return Agent(
            role='Инженер по качеству',
            goal='Обеспечивать высокое качество продукта через тщательное тестирование',
            backstory="""Ты опытный QA инженер, который знает все виды тестирования: 
            функциональное, нагрузочное, безопасности. Ты умеешь создавать детальные 
            тест-кейсы и находить критические баги.""",
            tools=[file_read_tool, directory_tool],
            verbose=True,
            allow_delegation=False
        )
    
    @staticmethod
    def project_manager():
        """Проект-менеджер - планирование, координация, отчетность"""
        return Agent(
            role='Проект-менеджер',
            goal='Эффективно управлять проектами и координировать работу команды',
            backstory="""Ты опытный проект-менеджер с сертификацией PMP. Ты знаешь 
            различные методологии управления проектами и умеешь адаптировать их под 
            специфику каждого проекта.""",
            tools=[file_read_tool, search_tool],
            verbose=True,
            allow_delegation=True
        )

class CrewTemplates:
    """Готовые команды для популярных сценариев"""
    
    @staticmethod
    def research_team():
        """Исследовательская команда: исследователь + аналитик + райтер"""
        researcher = AgentTemplates.researcher()
        analyst = AgentTemplates.data_analyst()
        writer = AgentTemplates.content_writer()
        
        def create_research_tasks(topic):
            research_task = Task(
                description=f"Исследовать тему: {topic}. Найти актуальную информацию из надежных источников.",
                agent=researcher,
                expected_output="Структурированный отчет с фактами и источниками"
            )
            
            analysis_task = Task(
                description=f"Проанализировать собранную информацию о {topic} и выделить ключевые инсайты.",
                agent=analyst,
                expected_output="Аналитический отчет с выводами и рекомендациями"
            )
            
            writing_task = Task(
                description=f"Создать финальную статью о {topic} на основе исследования и анализа.",
                agent=writer,
                expected_output="Готовая статья в формате markdown"
            )
            
            return [research_task, analysis_task, writing_task]
        
        return {
            'agents': [researcher, analyst, writer],
            'task_generator': create_research_tasks,
            'name': 'Исследовательская команда',
            'description': 'Команда для глубокого исследования тем и создания качественного контента'
        }
    
    @staticmethod
    def development_team():
        """Команда разработки: ревьюер + QA + проект-менеджер"""
        reviewer = AgentTemplates.code_reviewer()
        qa = AgentTemplates.qa_engineer()
        pm = AgentTemplates.project_manager()
        
        def create_dev_tasks(project_path):
            review_task = Task(
                description=f"Провести code review проекта в {project_path}. Проверить качество, безопасность и соответствие стандартам.",
                agent=reviewer,
                expected_output="Детальный отчет по code review с рекомендациями"
            )
            
            qa_task = Task(
                description=f"Создать план тестирования для проекта в {project_path} и выявить потенциальные проблемы.",
                agent=qa,
                expected_output="План тестирования и список найденных проблем"
            )
            
            pm_task = Task(
                description=f"Создать план развития проекта {project_path} на основе результатов review и тестирования.",
                agent=pm,
                expected_output="Roadmap проекта с приоритизированными задачами"
            )
            
            return [review_task, qa_task, pm_task]
        
        return {
            'agents': [reviewer, qa, pm],
            'task_generator': create_dev_tasks,
            'name': 'Команда разработки',
            'description': 'Команда для анализа и улучшения существующих проектов'
        }
    
    @staticmethod
    def content_team():
        """Контент-команда: исследователь + райтер + аналитик"""
        researcher = AgentTemplates.researcher()
        writer = AgentTemplates.content_writer()
        analyst = AgentTemplates.data_analyst()
        
        def create_content_tasks(topic, target_audience):
            research_task = Task(
                description=f"Исследовать тему {topic} с фокусом на аудиторию: {target_audience}",
                agent=researcher,
                expected_output="Исследование с ключевыми фактами и трендами"
            )
            
            writing_task = Task(
                description=f"Написать увлекательный контент о {topic} для аудитории {target_audience}",
                agent=writer,
                expected_output="Готовый контент в нужном формате"
            )
            
            analysis_task = Task(
                description=f"Проанализировать эффективность контента о {topic} и дать рекомендации по улучшению",
                agent=analyst,
                expected_output="Анализ контента с метриками и рекомендациями"
            )
            
            return [research_task, writing_task, analysis_task]
        
        return {
            'agents': [researcher, writer, analyst],
            'task_generator': create_content_tasks,
            'name': 'Контент-команда',
            'description': 'Команда для создания качественного контента любого типа'
        }

class WorkflowPatterns:
    """Паттерны рабочих процессов"""
    
    @staticmethod
    def sequential_workflow(agents, tasks):
        """Последовательный рабочий процесс"""
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=2,
            process="sequential"
        )
    
    @staticmethod
    def hierarchical_workflow(agents, tasks, manager_agent):
        """Иерархический рабочий процесс с менеджером"""
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=2,
            process="hierarchical",
            manager_agent=manager_agent
        )

# Примеры использования
def example_usage():
    """Примеры использования шаблонов"""
    
    # Создание исследовательской команды
    research_crew_template = CrewTemplates.research_team()
    agents = research_crew_template['agents']
    tasks = research_crew_template['task_generator']("Искусственный интеллект в медицине")
    
    research_crew = WorkflowPatterns.sequential_workflow(agents, tasks)
    
    # Создание команды разработки
    dev_crew_template = CrewTemplates.development_team()
    dev_agents = dev_crew_template['agents']
    dev_tasks = dev_crew_template['task_generator']("/path/to/project")
    
    dev_crew = WorkflowPatterns.hierarchical_workflow(
        dev_agents, 
        dev_tasks, 
        dev_agents[2]  # Проект-менеджер как руководитель
    )
    
    return {
        'research_crew': research_crew,
        'development_crew': dev_crew
    }