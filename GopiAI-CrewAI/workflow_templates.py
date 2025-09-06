"""
Визуальные шаблоны флоу для GopiAI CrewAI
Готовые сценарии работы команд для популярных задач
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class FlowType(Enum):
    """Типы флоу"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel" 
    HIERARCHICAL = "hierarchical"
    CONDITIONAL = "conditional"

class TaskType(Enum):
    """Типы задач"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CODING = "coding"
    REVIEW = "review"
    PLANNING = "planning"

@dataclass
class FlowNode:
    """Узел в флоу"""
    id: str
    name: str
    description: str
    task_type: TaskType
    agent_role: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass 
class FlowTemplate:
    """Шаблон флоу"""
    id: str
    name: str
    description: str
    category: str
    flow_type: FlowType
    nodes: List[FlowNode]
    estimated_time: str
    complexity: str  # "low", "medium", "high"
    tags: List[str]

class WorkflowTemplates:
    """Коллекция готовых шаблонов флоу"""
    
    @staticmethod
    def get_all_templates() -> List[FlowTemplate]:
        """Возвращает все доступные шаблоны"""
        return [
            WorkflowTemplates.content_creation_flow(),
            WorkflowTemplates.research_analysis_flow(),
            WorkflowTemplates.code_review_flow(),
            WorkflowTemplates.product_development_flow(),
            WorkflowTemplates.market_research_flow(),
            WorkflowTemplates.technical_documentation_flow(),
            WorkflowTemplates.crisis_management_flow(),
            WorkflowTemplates.competitive_analysis_flow()
        ]
    
    @staticmethod
    def content_creation_flow() -> FlowTemplate:
        """Флоу создания контента: исследование → планирование → написание → редактирование"""
        return FlowTemplate(
            id="content_creation",
            name="Создание контента",
            description="Полный цикл создания качественного контента от исследования до публикации",
            category="Контент и маркетинг",
            flow_type=FlowType.SEQUENTIAL,
            estimated_time="2-4 часа",
            complexity="medium",
            tags=["контент", "написание", "исследование", "SEO"],
            nodes=[
                FlowNode(
                    id="research_phase",
                    name="Исследование темы",
                    description="Сбор актуальной информации и анализ конкурентов",
                    task_type=TaskType.RESEARCH,
                    agent_role="researcher",
                    inputs=["topic", "target_audience"],
                    outputs=["research_data", "competitor_analysis", "key_insights"],
                    dependencies=[]
                ),
                FlowNode(
                    id="content_planning",
                    name="Планирование контента",
                    description="Создание структуры и плана контента",
                    task_type=TaskType.PLANNING,
                    agent_role="content_strategist",
                    inputs=["research_data", "target_audience"],
                    outputs=["content_outline", "seo_keywords", "content_strategy"],
                    dependencies=["research_phase"]
                ),
                FlowNode(
                    id="content_writing",
                    name="Написание контента", 
                    description="Создание основного текста по плану",
                    task_type=TaskType.WRITING,
                    agent_role="content_writer",
                    inputs=["content_outline", "seo_keywords", "key_insights"],
                    outputs=["draft_content", "meta_description", "headers"],
                    dependencies=["content_planning"]
                ),
                FlowNode(
                    id="content_review",
                    name="Редактирование и оптимизация",
                    description="Проверка качества, SEO-оптимизация и финальная доработка",
                    task_type=TaskType.REVIEW,
                    agent_role="editor",
                    inputs=["draft_content", "seo_keywords", "content_strategy"],
                    outputs=["final_content", "seo_report", "publication_ready"],
                    dependencies=["content_writing"]
                )
            ]
        )
    
    @staticmethod 
    def research_analysis_flow() -> FlowTemplate:
        """Исследовательский флоу: сбор данных → анализ → выводы → отчет"""
        return FlowTemplate(
            id="research_analysis",
            name="Исследование и анализ",
            description="Глубокое исследование темы с аналитическими выводами",
            category="Исследования и аналитика",
            flow_type=FlowType.SEQUENTIAL,
            estimated_time="3-6 часов",
            complexity="high", 
            tags=["исследование", "анализ", "данные", "отчет"],
            nodes=[
                FlowNode(
                    id="data_collection",
                    name="Сбор данных",
                    description="Поиск и сбор релевантных данных из различных источников",
                    task_type=TaskType.RESEARCH,
                    agent_role="data_collector",
                    inputs=["research_question", "data_sources"],
                    outputs=["raw_data", "source_list", "data_quality_report"],
                    dependencies=[]
                ),
                FlowNode(
                    id="data_analysis", 
                    name="Анализ данных",
                    description="Статистический анализ и выявление паттернов",
                    task_type=TaskType.ANALYSIS,
                    agent_role="data_analyst",
                    inputs=["raw_data", "analysis_methods"],
                    outputs=["statistical_results", "patterns", "visualizations"],
                    dependencies=["data_collection"]
                ),
                FlowNode(
                    id="insights_extraction",
                    name="Извлечение инсайтов",
                    description="Интерпретация результатов и формулировка выводов",
                    task_type=TaskType.ANALYSIS,
                    agent_role="research_analyst",
                    inputs=["statistical_results", "patterns", "research_question"],
                    outputs=["key_insights", "implications", "recommendations"],
                    dependencies=["data_analysis"]
                ),
                FlowNode(
                    id="report_creation",
                    name="Создание отчета",
                    description="Подготовка финального исследовательского отчета",
                    task_type=TaskType.WRITING,
                    agent_role="report_writer",
                    inputs=["key_insights", "visualizations", "recommendations"],
                    outputs=["executive_summary", "detailed_report", "presentation"],
                    dependencies=["insights_extraction"]
                )
            ]
        )
    
    @staticmethod
    def code_review_flow() -> FlowTemplate:
        """Флоу code review: анализ → тестирование → документация → рекомендации"""
        return FlowTemplate(
            id="code_review",
            name="Ревью кода",
            description="Комплексная проверка качества кода и рекомендации по улучшению",
            category="Разработка ПО",
            flow_type=FlowType.PARALLEL,
            estimated_time="1-3 часа",
            complexity="medium",
            tags=["код", "качество", "безопасность", "тестирование"],
            nodes=[
                FlowNode(
                    id="code_analysis",
                    name="Анализ кода",
                    description="Проверка структуры, стиля и архитектуры кода",
                    task_type=TaskType.ANALYSIS,
                    agent_role="code_reviewer",
                    inputs=["source_code", "coding_standards"],
                    outputs=["code_quality_report", "style_issues", "architecture_feedback"],
                    dependencies=[]
                ),
                FlowNode(
                    id="security_audit",
                    name="Аудит безопасности",
                    description="Поиск уязвимостей и проблем безопасности",
                    task_type=TaskType.ANALYSIS,
                    agent_role="security_analyst",
                    inputs=["source_code", "security_standards"],
                    outputs=["security_report", "vulnerabilities", "security_recommendations"],
                    dependencies=[]
                ),
                FlowNode(
                    id="testing_strategy",
                    name="Стратегия тестирования",
                    description="Анализ покрытия тестами и разработка стратегии",
                    task_type=TaskType.PLANNING,
                    agent_role="qa_engineer", 
                    inputs=["source_code", "existing_tests"],
                    outputs=["test_coverage_report", "test_plan", "testing_recommendations"],
                    dependencies=[]
                ),
                FlowNode(
                    id="final_recommendations",
                    name="Итоговые рекомендации",
                    description="Объединение всех результатов и формирование рекомендаций",
                    task_type=TaskType.PLANNING,
                    agent_role="tech_lead",
                    inputs=["code_quality_report", "security_report", "test_coverage_report"],
                    outputs=["improvement_plan", "priority_issues", "refactoring_guide"],
                    dependencies=["code_analysis", "security_audit", "testing_strategy"]
                )
            ]
        )
    
    @staticmethod
    def product_development_flow() -> FlowTemplate:
        """Флоу разработки продукта: анализ требований → планирование → прототипирование → тестирование"""
        return FlowTemplate(
            id="product_development",
            name="Разработка продукта",
            description="Полный цикл разработки продукта от идеи до MVP",
            category="Продуктовая разработка",
            flow_type=FlowType.SEQUENTIAL,
            estimated_time="1-2 недели",
            complexity="high",
            tags=["продукт", "MVP", "требования", "прототип"],
            nodes=[
                FlowNode(
                    id="requirements_analysis",
                    name="Анализ требований",
                    description="Определение функциональных и нефункциональных требований",
                    task_type=TaskType.ANALYSIS,
                    agent_role="business_analyst",
                    inputs=["product_idea", "market_research", "user_feedback"],
                    outputs=["requirements_spec", "user_stories", "acceptance_criteria"],
                    dependencies=[]
                ),
                FlowNode(
                    id="technical_planning",
                    name="Техническое планирование",
                    description="Архитектура системы и план разработки",
                    task_type=TaskType.PLANNING,
                    agent_role="tech_architect",
                    inputs=["requirements_spec", "technical_constraints"],
                    outputs=["system_architecture", "tech_stack", "development_plan"],
                    dependencies=["requirements_analysis"]
                ),
                FlowNode(
                    id="prototyping",
                    name="Создание прототипа",
                    description="Разработка MVP с базовой функциональностью",
                    task_type=TaskType.CODING,
                    agent_role="developer",
                    inputs=["system_architecture", "user_stories", "tech_stack"],
                    outputs=["mvp_prototype", "api_documentation", "deployment_guide"],
                    dependencies=["technical_planning"]
                ),
                FlowNode(
                    id="testing_validation",
                    name="Тестирование и валидация",
                    description="Проверка работоспособности и соответствия требованиям",
                    task_type=TaskType.REVIEW,
                    agent_role="qa_engineer",
                    inputs=["mvp_prototype", "acceptance_criteria", "user_stories"],
                    outputs=["test_results", "bug_reports", "validation_report"],
                    dependencies=["prototyping"]
                )
            ]
        )
    
    @staticmethod
    def market_research_flow() -> FlowTemplate:
        """Флоу маркетингового исследования: анализ рынка → конкуренты → SWOT → стратегия"""
        return FlowTemplate(
            id="market_research",
            name="Маркетинговое исследование",
            description="Комплексный анализ рынка и конкурентной среды",
            category="Маркетинг и бизнес",
            flow_type=FlowType.HIERARCHICAL,
            estimated_time="1-2 недели", 
            complexity="high",
            tags=["рынок", "конкуренты", "SWOT", "стратегия"],
            nodes=[
                FlowNode(
                    id="market_analysis",
                    name="Анализ рынка",
                    description="Изучение размера рынка, трендов и возможностей",
                    task_type=TaskType.RESEARCH,
                    agent_role="market_analyst",
                    inputs=["industry", "target_market", "geographic_scope"],
                    outputs=["market_size", "growth_trends", "opportunities"],
                    dependencies=[]
                ),
                FlowNode(
                    id="competitor_analysis",
                    name="Анализ конкурентов",
                    description="Исследование основных игроков и их стратегий",
                    task_type=TaskType.ANALYSIS,
                    agent_role="competitive_analyst",
                    inputs=["competitor_list", "analysis_framework"],
                    outputs=["competitor_profiles", "positioning_map", "competitive_gaps"],
                    dependencies=[]
                ),
                FlowNode(
                    id="swot_analysis",
                    name="SWOT анализ",
                    description="Оценка сильных/слабых сторон, возможностей и угроз",
                    task_type=TaskType.ANALYSIS,
                    agent_role="strategic_analyst",
                    inputs=["market_size", "competitor_profiles", "internal_capabilities"],
                    outputs=["swot_matrix", "strategic_options", "risk_assessment"],
                    dependencies=["market_analysis", "competitor_analysis"]
                ),
                FlowNode(
                    id="strategy_formulation",
                    name="Формирование стратегии",
                    description="Разработка маркетинговой стратегии на основе анализа",
                    task_type=TaskType.PLANNING,
                    agent_role="strategy_consultant",
                    inputs=["swot_matrix", "strategic_options", "business_objectives"],
                    outputs=["marketing_strategy", "action_plan", "kpi_framework"],
                    dependencies=["swot_analysis"]
                )
            ]
        )
    
    @staticmethod
    def technical_documentation_flow() -> FlowTemplate:
        """Флоу создания технической документации"""
        return FlowTemplate(
            id="tech_documentation", 
            name="Техническая документация",
            description="Создание полной технической документации для проекта",
            category="Документация",
            flow_type=FlowType.SEQUENTIAL,
            estimated_time="3-5 дней",
            complexity="medium",
            tags=["документация", "API", "архитектура", "руководство"],
            nodes=[
                FlowNode(
                    id="code_analysis_doc",
                    name="Анализ кодовой базы",
                    description="Изучение структуры проекта и архитектуры",
                    task_type=TaskType.ANALYSIS,
                    agent_role="tech_writer",
                    inputs=["source_code", "existing_docs"],
                    outputs=["architecture_overview", "component_list", "dependencies"],
                    dependencies=[]
                ),
                FlowNode(
                    id="api_documentation",
                    name="Документирование API",
                    description="Создание подробной документации API",
                    task_type=TaskType.WRITING,
                    agent_role="api_documenter",
                    inputs=["api_endpoints", "code_examples"],
                    outputs=["api_reference", "endpoint_descriptions", "usage_examples"],
                    dependencies=["code_analysis_doc"]
                ),
                FlowNode(
                    id="user_guides",
                    name="Руководства пользователя",
                    description="Создание инструкций по использованию",
                    task_type=TaskType.WRITING,
                    agent_role="technical_writer",
                    inputs=["feature_list", "user_workflows", "screenshots"],
                    outputs=["installation_guide", "user_manual", "troubleshooting"],
                    dependencies=["code_analysis_doc"]
                ),
                FlowNode(
                    id="doc_review",
                    name="Ревью документации",
                    description="Проверка полноты и качества документации",
                    task_type=TaskType.REVIEW,
                    agent_role="doc_reviewer",
                    inputs=["api_reference", "user_manual", "installation_guide"],
                    outputs=["reviewed_docs", "improvement_suggestions", "final_documentation"],
                    dependencies=["api_documentation", "user_guides"]
                )
            ]
        )
    
    @staticmethod
    def crisis_management_flow() -> FlowTemplate:
        """Флоу антикризисного управления"""
        return FlowTemplate(
            id="crisis_management",
            name="Антикризисное управление",
            description="Быстрое реагирование и управление кризисными ситуациями",
            category="Управление рисками",
            flow_type=FlowType.CONDITIONAL,
            estimated_time="2-8 часов",
            complexity="high",
            tags=["кризис", "риски", "коммуникация", "восстановление"],
            nodes=[
                FlowNode(
                    id="crisis_assessment",
                    name="Оценка кризиса",
                    description="Быстрая оценка масштаба и воздействия кризиса",
                    task_type=TaskType.ANALYSIS,
                    agent_role="crisis_analyst",
                    inputs=["incident_report", "impact_indicators"],
                    outputs=["crisis_severity", "affected_areas", "immediate_risks"],
                    dependencies=[]
                ),
                FlowNode(
                    id="response_planning",
                    name="Планирование реагирования", 
                    description="Разработка плана немедленного реагирования",
                    task_type=TaskType.PLANNING,
                    agent_role="crisis_manager",
                    inputs=["crisis_severity", "available_resources", "stakeholders"],
                    outputs=["response_plan", "resource_allocation", "timeline"],
                    dependencies=["crisis_assessment"]
                ),
                FlowNode(
                    id="communication_strategy",
                    name="Коммуникационная стратегия",
                    description="Подготовка сообщений для различных аудиторий",
                    task_type=TaskType.WRITING,
                    agent_role="pr_specialist",
                    inputs=["crisis_severity", "stakeholders", "key_messages"],
                    outputs=["press_releases", "internal_communications", "social_media_strategy"],
                    dependencies=["crisis_assessment"]
                ),
                FlowNode(
                    id="recovery_planning",
                    name="Планирование восстановления",
                    description="Долгосрочный план восстановления после кризиса",
                    task_type=TaskType.PLANNING,
                    agent_role="recovery_specialist",
                    inputs=["response_plan", "damage_assessment", "business_priorities"],
                    outputs=["recovery_roadmap", "preventive_measures", "lessons_learned"],
                    dependencies=["response_planning", "communication_strategy"]
                )
            ]
        )
    
    @staticmethod
    def competitive_analysis_flow() -> FlowTemplate:
        """Флоу конкурентного анализа"""
        return FlowTemplate(
            id="competitive_analysis",
            name="Конкурентный анализ",
            description="Глубокий анализ конкурентов и их стратегий",
            category="Бизнес-аналитика",
            flow_type=FlowType.PARALLEL,
            estimated_time="1-2 недели",
            complexity="medium",
            tags=["конкуренты", "позиционирование", "стратегия", "рынок"],
            nodes=[
                FlowNode(
                    id="competitor_identification",
                    name="Выявление конкурентов",
                    description="Определение прямых и косвенных конкурентов",
                    task_type=TaskType.RESEARCH,
                    agent_role="market_researcher",
                    inputs=["industry_sector", "target_market", "product_category"],
                    outputs=["competitor_list", "competitive_landscape", "market_segments"],
                    dependencies=[]
                ),
                FlowNode(
                    id="product_comparison",
                    name="Сравнение продуктов",
                    description="Детальное сравнение продуктов и услуг",
                    task_type=TaskType.ANALYSIS,
                    agent_role="product_analyst",
                    inputs=["competitor_list", "feature_matrix", "pricing_data"],
                    outputs=["product_comparison", "feature_gaps", "value_propositions"],
                    dependencies=["competitor_identification"]
                ),
                FlowNode(
                    id="marketing_analysis",
                    name="Анализ маркетинга",
                    description="Изучение маркетинговых стратегий конкурентов",
                    task_type=TaskType.ANALYSIS,
                    agent_role="marketing_analyst",
                    inputs=["competitor_list", "marketing_channels", "campaign_data"],
                    outputs=["marketing_strategies", "channel_effectiveness", "messaging_analysis"],
                    dependencies=["competitor_identification"]
                ),
                FlowNode(
                    id="strategic_recommendations",
                    name="Стратегические рекомендации",
                    description="Формирование рекомендаций на основе анализа",
                    task_type=TaskType.PLANNING,
                    agent_role="strategy_consultant",
                    inputs=["product_comparison", "marketing_strategies", "competitive_landscape"],
                    outputs=["competitive_strategy", "differentiation_opportunities", "action_items"],
                    dependencies=["product_comparison", "marketing_analysis"]
                )
            ]
        )

class FlowVisualizer:
    """Визуализация флоу"""
    
    @staticmethod
    def get_flow_diagram(template: FlowTemplate) -> Dict[str, Any]:
        """Генерирует данные для визуализации флоу"""
        nodes = []
        edges = []
        
        # Создаем узлы
        for node in template.nodes:
            nodes.append({
                "id": node.id,
                "label": node.name,
                "description": node.description,
                "type": node.task_type.value,
                "agent_role": node.agent_role,
                "color": FlowVisualizer._get_node_color(node.task_type)
            })
        
        # Создаем связи
        for node in template.nodes:
            for dep in node.dependencies:
                edges.append({
                    "from": dep,
                    "to": node.id,
                    "label": "зависит от"
                })
        
        return {
            "template_info": {
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "complexity": template.complexity,
                "estimated_time": template.estimated_time
            },
            "nodes": nodes,
            "edges": edges,
            "layout": template.flow_type.value
        }
    
    @staticmethod
    def _get_node_color(task_type: TaskType) -> str:
        """Возвращает цвет узла по типу задачи"""
        colors = {
            TaskType.RESEARCH: "#3498db",      # Синий
            TaskType.ANALYSIS: "#e74c3c",     # Красный  
            TaskType.WRITING: "#2ecc71",      # Зеленый
            TaskType.CODING: "#f39c12",       # Оранжевый
            TaskType.REVIEW: "#9b59b6",       # Фиолетовый
            TaskType.PLANNING: "#1abc9c"      # Бирюзовый
        }
        return colors.get(task_type, "#95a5a6")  # Серый по умолчанию

# Примеры использования
def example_usage():
    """Примеры использования шаблонов флоу"""
    
    # Получаем все шаблоны
    templates = WorkflowTemplates.get_all_templates()
    print(f"Доступно шаблонов: {len(templates)}")
    
    # Выбираем шаблон создания контента
    content_template = WorkflowTemplates.content_creation_flow()
    
    # Генерируем диаграмму
    flow_diagram = FlowVisualizer.get_flow_diagram(content_template)
    
    print(f"Шаблон: {flow_diagram['template_info']['name']}")
    print(f"Узлов: {len(flow_diagram['nodes'])}")
    print(f"Связей: {len(flow_diagram['edges'])}")
    
    return flow_diagram