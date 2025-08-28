"""
👥 GopiAI Agent Template System
Система шаблонов для быстрого создания специализированных агентов CrewAI
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
# Используем локальные заглушки вместо импорта из crewai
from .base.base_agent import Agent, Task, Crew

class AgentTemplateSystem:
    """
    Система шаблонов для быстрого создания агентов CrewAI
    
    Особенности:
    - Загрузка шаблонов из YAML файлов
    - Загрузка промптов из текстовых файлов
    - Создание агентов с кастомизацией
    - Поддержка различных инструментов
    """
    
    def __init__(self, verbose: bool = False):
        """
        Инициализация системы шаблонов
        
        Args:
            verbose: Подробный вывод сообщений
        """
        print("[DEBUG] AgentTemplateSystem.__init__ вызывается")
        self.verbose = verbose
        self.logger = self._setup_logger()
        
        # Загружаем шаблоны и промпты
        self.templates = self._load_templates()
        self.prompt_library = self._load_prompt_library()
        
        self.logger.info(f"Загружено {len(self.templates)} шаблонов и {len(self.prompt_library)} промптов")
        
        if self.verbose:
            print(f"✅ Загружено {len(self.templates)} шаблонов агентов")
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера"""
        logger = logging.getLogger("gopiai.agent_template_system")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Создаем директорию для логов, если её нет
            log_dir = os.path.join(os.path.dirname(__file__), "../logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Файловый обработчик
            log_file = os.path.join(log_dir, "agent_templates.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Форматтер
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
        
        return logger
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Загрузка шаблонов агентов из YAML файлов
        
        Returns:
            Словарь шаблонов агентов
        """
        templates = {}
        # Корректно вычисляем корень проекта (GopiAI-CrewAI)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        templates_dir = os.path.join(project_root, "templates/agents")
        print(f"[DEBUG] Путь к шаблонам: {templates_dir}")
        
        if not os.path.exists(templates_dir):
            self.logger.warning(f"Директория шаблонов не найдена: {templates_dir}")
            print(f"[DEBUG] Директория шаблонов не найдена: {templates_dir}")
            return templates
        
        print(f"[DEBUG] Файлы в директории шаблонов: {os.listdir(templates_dir)}")
        for file_name in os.listdir(templates_dir):
            if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                template_name = file_name.rsplit(".", 1)[0]
                template_path = os.path.join(templates_dir, file_name)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                        templates[template_name] = template_data
                        self.logger.info(f"Загружен шаблон: {template_name}")
                        print(f"[DEBUG] Загружен шаблон: {template_name}")
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки шаблона {template_name}: {str(e)}")
                    print(f"[DEBUG] Ошибка загрузки шаблона {template_name}: {str(e)}")
        
        return templates
    
    def _load_prompt_library(self) -> Dict[str, str]:
        """
        Загрузка библиотеки промптов из текстовых файлов
        
        Returns:
            Словарь промптов
        """
        prompts = {}
        prompts_dir = os.path.join(os.path.dirname(__file__), "../templates/prompts")
        
        if not os.path.exists(prompts_dir):
            self.logger.warning(f"Директория промптов не найдена: {prompts_dir}")
            return prompts
        
        for file_name in os.listdir(prompts_dir):
            if file_name.endswith(".txt"):
                prompt_name = file_name.rsplit(".", 1)[0]
                prompt_path = os.path.join(prompts_dir, file_name)
                
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        prompt_text = f.read()
                        prompts[prompt_name] = prompt_text
                        self.logger.info(f"Загружен промпт: {prompt_name}")
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки промпта {prompt_name}: {str(e)}")
        
        return prompts
    
    def list_available_templates(self) -> List[str]:
        """
        Получение списка доступных шаблонов
        
        Returns:
            Список имен шаблонов
        """
        return list(self.templates.keys())
    
    def list_available_prompts(self) -> List[str]:
        """
        Получение списка доступных промптов
        
        Returns:
            Список имен промптов
        """
        return list(self.prompt_library.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Получение информации о шаблоне
        
        Args:
            template_name: Имя шаблона
            
        Returns:
            Словарь с информацией о шаблоне
        """
        if template_name not in self.templates:
            self.logger.error(f"Шаблон не найден: {template_name}")
            return {}
        
        return self.templates[template_name]
    
    def create_agent_from_template(self, template_name: str, llm: Any, **kwargs) -> Optional[Agent]:
        """
        Создание агента из шаблона
        
        Args:
            template_name: Имя шаблона
            llm: Языковая модель для агента
            **kwargs: Дополнительные параметры для кастомизации агента
            
        Returns:
            Созданный агент или None в случае ошибки
        """
        if template_name not in self.templates:
            self.logger.error(f"Шаблон не найден: {template_name}")
            print(f"[DEBUG] Шаблон не найден: {template_name}")
            print(f"[DEBUG] Доступные шаблоны: {list(self.templates.keys())}")
            return None
        
        template = self.templates[template_name]
        
        try:
            # Базовые параметры агента
            role = kwargs.get("role", template.get("role", ""))
            goal = kwargs.get("goal", template.get("goal", ""))
            verbose = kwargs.get("verbose", template.get("verbose", False))
            allow_delegation = kwargs.get("allow_delegation", template.get("allow_delegation", False))
            
            # Обработка backstory с шаблонизацией
            backstory = ""
            backstory_template = template.get("backstory_template")
            
            if backstory_template and backstory_template in self.prompt_library:
                # Формируем контекст для шаблона
                context = {**template.get("parameters", {}), **kwargs}
                
                # Пытаемся заполнить шаблон
                try:
                    backstory = self.prompt_library[backstory_template].format(**context)
                except KeyError as e:
                    self.logger.warning(f"Отсутствует ключ в контексте шаблона: {e}")
                    # Используем шаблон как есть
                    backstory = self.prompt_library[backstory_template]
            else:
                backstory = kwargs.get("backstory", template.get("backstory", ""))
            
            # Создание набора инструментов
            tools = []
            for tool_name in template.get("tools", []):
                tool_instance = self._get_tool_instance(tool_name)
                if tool_instance:
                    tools.append(tool_instance)
            
            # Дополнительные параметры
            additional_params = {}
            
            if "max_iter" in template:
                additional_params["max_iter"] = kwargs.get("max_iter", template.get("max_iter"))
                
            if "max_execution_time" in template:
                additional_params["max_execution_time"] = kwargs.get("max_execution_time", template.get("max_execution_time"))
            
            if "temperature" in template:
                additional_params["temperature"] = kwargs.get("temperature", template.get("temperature"))
            
            # ЯВНЫЙ BINDING ИНСТРУМЕНТОВ К LLM
            llm_bound = llm
            try:
                if tools and hasattr(llm, "bind_tools") and callable(getattr(llm, "bind_tools")):
                    llm_bound = llm.bind_tools(tools)
                    self.logger.info(f"🔗 LLM привязан к {len(tools)} инструментам через .bind_tools() (agent template)")
                else:
                    self.logger.debug("ℹ️ .bind_tools() недоступен или список tools пуст — используем исходный LLM")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось привязать инструменты к LLM через .bind_tools(): {e}")
            
            # Создание агента
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                llm=llm_bound,
                verbose=verbose,
                allow_delegation=allow_delegation,
                **additional_params
            )
            
            self.logger.info(f"Создан агент из шаблона {template_name}: {role}")
            
            if self.verbose:
                print(f"✅ Создан агент: {role}")
                print(f"   Инструментов: {len(tools)}")
                print(f"   Backstory: {backstory[:50]}...")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Ошибка создания агента из шаблона {template_name}: {str(e)}")
            return None
    
    def _get_tool_instance(self, tool_name: str) -> Any:
        """
        Получение экземпляра инструмента по имени
        
        Args:
            tool_name: Имя инструмента
            
        Returns:
            Экземпляр инструмента или None
        """
        try:
            # Импортируем инструменты
            from gopiai_integration.browser_tools import GopiAIBrowserTool
            from gopiai_integration.filesystem_tools import GopiAIFileSystemTool
            from gopiai_integration.memory_tools import GopiAIMemoryTool
            from gopiai_integration.communication_tools import GopiAICommunicationTool
            from gopiai_integration.ai_router_tools import GopiAIRouterTool
            from gopiai_integration.terminal_tool import TerminalTool
            from gopiai_integration.huggingface_tools import GopiAIHuggingFaceTool
            
            # Сопоставление имен и классов инструментов
            tool_mapping = {
                "browser": GopiAIBrowserTool,
                "filesystem": GopiAIFileSystemTool,
                "memory": GopiAIMemoryTool,
                "communication": GopiAICommunicationTool,
                "router": GopiAIRouterTool,
                "terminal": TerminalTool,
                "huggingface": GopiAIHuggingFaceTool
            }
            
            if tool_name in tool_mapping:
                return tool_mapping[tool_name]()
            else:
                self.logger.warning(f"Неизвестный инструмент: {tool_name}")
                return None
                
        except ImportError as e:
            self.logger.error(f"Ошибка импорта инструмента {tool_name}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка создания инструмента {tool_name}: {str(e)}")
            return None
    
    def create_crew_from_templates(self, name: str, llm: Any, agent_configs: List[Dict[str, Any]], tasks: List[Task]) -> Optional[Crew]:
        """
        Создание команды из шаблонов агентов
        
        Args:
            name: Имя команды
            llm: Языковая модель для агентов
            agent_configs: Список конфигураций агентов (шаблон и параметры)
            tasks: Список задач для команды
            
        Returns:
            Созданная команда или None в случае ошибки
        """
        try:
            agents = []
            
            for config in agent_configs:
                template_name = config.get("template")
                if not template_name:
                    self.logger.error("Не указан шаблон агента")
                    continue
                
                agent = self.create_agent_from_template(template_name, llm, **config.get("parameters", {}))
                if agent:
                    agents.append(agent)
            
            if not agents:
                self.logger.error("Не удалось создать ни одного агента")
                return None
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True,
                name=name
            )
            
            self.logger.info(f"Создана команда {name} с {len(agents)} агентами и {len(tasks)} задачами")
            
            if self.verbose:
                print(f"✅ Создана команда: {name}")
                print(f"   Агентов: {len(agents)}")
                print(f"   Задач: {len(tasks)}")
            
            return crew
            
        except Exception as e:
            self.logger.error(f"Ошибка создания команды: {str(e)}")
            return None


# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание системы шаблонов
    template_system = AgentTemplateSystem(verbose=True)
    
    # Вывод доступных шаблонов
    print("\n📋 Доступные шаблоны агентов:")
    for template_name in template_system.list_available_templates():
        template_info = template_system.get_template_info(template_name)
        print(f"   - {template_name}: {template_info.get('role', 'Неизвестная роль')}")
    
    # Вывод доступных промптов
    print("\n📝 Доступные промпты:")
    for prompt_name in template_system.list_available_prompts():
        print(f"   - {prompt_name}")
    
    print("\n✅ Система шаблонов готова к использованию")
