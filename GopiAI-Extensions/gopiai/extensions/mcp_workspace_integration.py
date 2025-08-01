"""
Интеграция Smart Workspace Indexer с MCP сервером

Автоматически индексирует рабочее пространство при операции setWorkspace
и предоставляет инструменты для работы с индексом.
"""

import os
import logging
from typing import Dict, Any, Optional

from .workspace_indexer import get_workspace_indexer, WorkspaceIndex

logger = logging.getLogger(__name__)

class MCPWorkspaceIntegration:
    """Интеграция индексатора рабочего пространства с MCP сервером"""
    
    def __init__(self):
        self.indexer = get_workspace_indexer()
        self.current_workspace_index: Optional[WorkspaceIndex] = None
        self.current_workspace_path: Optional[str] = None
        
        logger.info("[MCP-WORKSPACE] Интеграция с MCP сервером инициализирована")
    
    def on_workspace_set(self, workspace_path: str) -> Dict[str, Any]:
        """
        Обработчик события установки рабочего пространства
        
        Args:
            workspace_path: Путь к новому рабочему пространству
            
        Returns:
            Dict с информацией об индексации
        """
        logger.info(f"[MCP-WORKSPACE] Установка рабочего пространства: {workspace_path}")
        
        try:
            # Проверяем существование пути
            if not os.path.exists(workspace_path):
                return {
                    "success": False,
                    "error": f"Путь не существует: {workspace_path}",
                    "indexed": False
                }
            
            if not os.path.isdir(workspace_path):
                return {
                    "success": False,
                    "error": f"Путь не является директорией: {workspace_path}",
                    "indexed": False
                }
            
            # Выполняем индексацию
            self.current_workspace_index = self.indexer.index_workspace(workspace_path)
            self.current_workspace_path = workspace_path
            
            # Генерируем краткое описание
            summary = self.indexer.get_project_summary(self.current_workspace_index)
            
            logger.info(f"[MCP-WORKSPACE] Рабочее пространство проиндексировано: {summary}")
            
            return {
                "success": True,
                "indexed": True,
                "workspace_path": workspace_path,
                "project_summary": summary,
                "project_type": self.current_workspace_index.project_info.project_type,
                "primary_language": self.current_workspace_index.project_info.primary_language,
                "total_files": self.current_workspace_index.total_files,
                "total_size": self.current_workspace_index.total_size,
                "technologies": self.current_workspace_index.project_info.technologies,
                "frameworks": self.current_workspace_index.project_info.frameworks
            }
            
        except Exception as e:
            logger.error(f"[MCP-WORKSPACE] Ошибка индексации: {e}")
            return {
                "success": False,
                "error": str(e),
                "indexed": False
            }
    
    def get_workspace_context(self) -> Optional[str]:
        """
        Получает контекст текущего рабочего пространства для LLM
        
        Returns:
            Строка с контекстом или None, если рабочее пространство не установлено
        """
        if not self.current_workspace_index:
            return None
        
        return self.indexer.get_context_for_llm(self.current_workspace_index)
    
    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о текущем проекте
        
        Returns:
            Словарь с информацией о проекте или None
        """
        if not self.current_workspace_index:
            return None
        
        project = self.current_workspace_index.project_info
        
        return {
            "workspace_path": self.current_workspace_path,
            "project_type": project.project_type,
            "primary_language": project.primary_language,
            "technologies": project.technologies,
            "frameworks": project.frameworks,
            "build_tools": project.build_tools,
            "package_managers": project.package_managers,
            "entry_points": project.entry_points,
            "config_files": project.config_files[:10],  # Ограничиваем количество
            "test_directories": project.test_directories,
            "documentation_files": project.documentation_files[:10],
            "total_files": self.current_workspace_index.total_files,
            "total_size": self.current_workspace_index.total_size,
            "indexed_at": self.current_workspace_index.indexed_at.isoformat()
        }
    
    def get_file_tree_summary(self, max_depth: int = 3) -> Optional[str]:
        """
        Получает краткое описание структуры файлов
        
        Args:
            max_depth: Максимальная глубина отображения
            
        Returns:
            Строка с описанием структуры или None
        """
        if not self.current_workspace_index:
            return None
        
        return self.indexer.get_file_tree_summary(self.current_workspace_index, max_depth)
    
    def refresh_index(self, force: bool = False) -> Dict[str, Any]:
        """
        Обновляет индекс текущего рабочего пространства
        
        Args:
            force: Принудительное обновление кэша
            
        Returns:
            Результат обновления
        """
        if not self.current_workspace_path:
            return {
                "success": False,
                "error": "Рабочее пространство не установлено",
                "refreshed": False
            }
        
        try:
            logger.info(f"[MCP-WORKSPACE] Обновление индекса: {self.current_workspace_path}")
            
            self.current_workspace_index = self.indexer.index_workspace(
                self.current_workspace_path, 
                force_refresh=force
            )
            
            summary = self.indexer.get_project_summary(self.current_workspace_index)
            
            return {
                "success": True,
                "refreshed": True,
                "project_summary": summary,
                "total_files": self.current_workspace_index.total_files,
                "total_size": self.current_workspace_index.total_size
            }
            
        except Exception as e:
            logger.error(f"[MCP-WORKSPACE] Ошибка обновления индекса: {e}")
            return {
                "success": False,
                "error": str(e),
                "refreshed": False
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Очищает кэш индексатора
        
        Returns:
            Результат очистки
        """
        try:
            self.indexer.clear_cache()
            logger.info("[MCP-WORKSPACE] Кэш индексатора очищен")
            
            return {
                "success": True,
                "message": "Кэш индексатора очищен"
            }
            
        except Exception as e:
            logger.error(f"[MCP-WORKSPACE] Ошибка очистки кэша: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_files(self, pattern: str, max_results: int = 20) -> Dict[str, Any]:
        """
        Поиск файлов по паттерну в текущем рабочем пространстве
        
        Args:
            pattern: Паттерн для поиска (поддерживает wildcards)
            max_results: Максимальное количество результатов
            
        Returns:
            Результаты поиска
        """
        if not self.current_workspace_index:
            return {
                "success": False,
                "error": "Рабочее пространство не установлено",
                "results": []
            }
        
        try:
            import fnmatch
            
            def search_in_tree(node, pattern, results, max_results):
                if len(results) >= max_results:
                    return
                
                # Проверяем текущий узел
                if fnmatch.fnmatch(node.name.lower(), pattern.lower()):
                    results.append({
                        "name": node.name,
                        "path": node.path,
                        "is_directory": node.is_directory,
                        "size": node.size
                    })
                
                # Рекурсивно ищем в дочерних узлах
                if node.children:
                    for child in node.children:
                        search_in_tree(child, pattern, results, max_results)
            
            results = []
            search_in_tree(self.current_workspace_index.file_tree, pattern, results, max_results)
            
            return {
                "success": True,
                "pattern": pattern,
                "results": results,
                "total_found": len(results),
                "truncated": len(results) >= max_results
            }
            
        except Exception as e:
            logger.error(f"[MCP-WORKSPACE] Ошибка поиска файлов: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_technology_recommendations(self) -> Dict[str, Any]:
        """
        Получает рекомендации по технологиям на основе анализа проекта
        
        Returns:
            Рекомендации по технологиям
        """
        if not self.current_workspace_index:
            return {
                "success": False,
                "error": "Рабочее пространство не установлено",
                "recommendations": []
            }
        
        project = self.current_workspace_index.project_info
        recommendations = []
        
        # Рекомендации на основе типа проекта
        if project.project_type == 'node':
            if 'React' not in project.frameworks:
                recommendations.append({
                    "type": "framework",
                    "name": "React",
                    "reason": "Популярный фреймворк для Node.js проектов",
                    "priority": "medium"
                })
            
            if 'eslint' not in project.technologies:
                recommendations.append({
                    "type": "tool",
                    "name": "ESLint",
                    "reason": "Линтер для JavaScript кода",
                    "priority": "high"
                })
        
        elif project.project_type == 'python':
            if 'pytest' not in project.technologies:
                recommendations.append({
                    "type": "testing",
                    "name": "pytest",
                    "reason": "Популярный фреймворк для тестирования Python",
                    "priority": "high"
                })
            
            if not project.test_directories:
                recommendations.append({
                    "type": "structure",
                    "name": "tests/ directory",
                    "reason": "Рекомендуется создать директорию для тестов",
                    "priority": "medium"
                })
        
        # Общие рекомендации
        if 'git' not in project.technologies:
            recommendations.append({
                "type": "vcs",
                "name": "Git",
                "reason": "Система контроля версий необходима для любого проекта",
                "priority": "critical"
            })
        
        if not project.documentation_files:
            recommendations.append({
                "type": "documentation",
                "name": "README.md",
                "reason": "Документация проекта важна для понимания и использования",
                "priority": "high"
            })
        
        return {
            "success": True,
            "project_type": project.project_type,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }

# Глобальный экземпляр интеграции
_mcp_workspace_integration = None

def get_mcp_workspace_integration() -> MCPWorkspaceIntegration:
    """Получает глобальный экземпляр интеграции с MCP"""
    global _mcp_workspace_integration
    if _mcp_workspace_integration is None:
        _mcp_workspace_integration = MCPWorkspaceIntegration()
    return _mcp_workspace_integration

# MCP Tools для использования в сервере
def get_workspace_mcp_tools() -> Dict[str, Any]:
    """
    Возвращает инструменты MCP для работы с рабочим пространством
    
    Returns:
        Словарь с определениями инструментов MCP
    """
    return {
        "workspace_info": {
            "name": "workspace_info",
            "description": "Получает информацию о текущем рабочем пространстве",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "workspace_context": {
            "name": "workspace_context", 
            "description": "Получает полный контекст рабочего пространства для LLM",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "workspace_file_tree": {
            "name": "workspace_file_tree",
            "description": "Получает структуру файлов рабочего пространства",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "max_depth": {
                        "type": "number",
                        "description": "Максимальная глубина отображения (по умолчанию 3)",
                        "default": 3
                    }
                },
                "required": []
            }
        },
        "workspace_refresh": {
            "name": "workspace_refresh",
            "description": "Обновляет индекс рабочего пространства",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "force": {
                        "type": "boolean",
                        "description": "Принудительное обновление кэша",
                        "default": False
                    }
                },
                "required": []
            }
        },
        "workspace_search": {
            "name": "workspace_search",
            "description": "Поиск файлов в рабочем пространстве по паттерну",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Паттерн для поиска (поддерживает wildcards)"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Максимальное количество результатов",
                        "default": 20
                    }
                },
                "required": ["pattern"]
            }
        },
        "workspace_recommendations": {
            "name": "workspace_recommendations",
            "description": "Получает рекомендации по технологиям для проекта",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        "workspace_clear_cache": {
            "name": "workspace_clear_cache",
            "description": "Очищает кэш индексатора рабочего пространства",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

def handle_workspace_mcp_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик вызовов MCP инструментов для рабочего пространства
    
    Args:
        tool_name: Имя вызываемого инструмента
        arguments: Аргументы вызова
        
    Returns:
        Результат выполнения инструмента
    """
    integration = get_mcp_workspace_integration()
    
    try:
        if tool_name == "workspace_info":
            result = integration.get_project_info()
            if result is None:
                return {"error": "Рабочее пространство не установлено"}
            return result
        
        elif tool_name == "workspace_context":
            context = integration.get_workspace_context()
            if context is None:
                return {"error": "Рабочее пространство не установлено"}
            return {"context": context}
        
        elif tool_name == "workspace_file_tree":
            max_depth = arguments.get("max_depth", 3)
            tree = integration.get_file_tree_summary(max_depth)
            if tree is None:
                return {"error": "Рабочее пространство не установлено"}
            return {"file_tree": tree}
        
        elif tool_name == "workspace_refresh":
            force = arguments.get("force", False)
            return integration.refresh_index(force)
        
        elif tool_name == "workspace_search":
            pattern = arguments.get("pattern")
            max_results = arguments.get("max_results", 20)
            return integration.search_files(pattern, max_results)
        
        elif tool_name == "workspace_recommendations":
            return integration.get_technology_recommendations()
        
        elif tool_name == "workspace_clear_cache":
            return integration.clear_cache()
        
        else:
            return {"error": f"Неизвестный инструмент: {tool_name}"}
    
    except Exception as e:
        logger.error(f"[MCP-WORKSPACE] Ошибка выполнения {tool_name}: {e}")
        return {"error": str(e)}

# Экспорт основных функций
__all__ = [
    'MCPWorkspaceIntegration',
    'get_mcp_workspace_integration',
    'get_workspace_mcp_tools',
    'handle_workspace_mcp_call'
]