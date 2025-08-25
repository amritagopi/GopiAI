"""
🚀 Tool Dispatcher
Централизованный диспетчер для вызова всех инструментов, агентов и флоу
Единая точка входа с поддержкой режимов авто/принудительно
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .tool_aliases import get_tool_alias_manager, ToolAliasManager
from .intent_parser import get_intent_parser, IntentParser, IntentMatch, IntentMode

logger = logging.getLogger(__name__)

class DispatchResult(Enum):
    """Результаты диспетчеризации"""
    SUCCESS = "success"
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_UNAVAILABLE = "tool_unavailable"
    EXECUTION_ERROR = "execution_error"
    PERMISSION_DENIED = "permission_denied"
    INVALID_PARAMS = "invalid_params"

@dataclass
class ToolCall:
    """Информация о вызове инструмента"""
    tool_name: str                    # Каноническое название
    original_name: str               # Исходное название от пользователя
    mode: IntentMode                 # Режим вызова
    params: Dict[str, Any]           # Параметры
    context: Dict[str, Any]          # Контекст (метаданные, история и т.д.)
    timestamp: float                 # Время вызова
    user_text: str                   # Исходный текст пользователя

@dataclass
class DispatchResponse:
    """Ответ диспетчера"""
    result: DispatchResult           # Результат выполнения
    tool_call: ToolCall             # Информация о вызове
    response_data: Any              # Данные ответа
    error_message: Optional[str]    # Сообщение об ошибке
    execution_time: float           # Время выполнения в секундах
    suggestions: List[str]          # Предложения альтернативных инструментов

class ToolDispatcher:
    """
    Центральный диспетчер инструментов.
    Обеспечивает единую точку входа для всех tool_calls с поддержкой:
    - Нормализации названий через алиасы
    - Автоматического и принудительного режимов
    - Распознавания намерений
    - Защиты от галлюцинаций
    - Подробного логирования
    """
    
    def __init__(self, smart_delegator=None):
        self.logger = logging.getLogger(__name__)
        self.alias_manager: ToolAliasManager = get_tool_alias_manager()
        self.intent_parser: IntentParser = get_intent_parser()
        self.smart_delegator = smart_delegator  # Ссылка на SmartDelegator для выполнения
        
        # Статистика
        self.call_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'auto_calls': 0,
            'forced_calls': 0,
            'tool_usage': {}
        }
        
        # ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ
        self.call_limits = {
            'max_calls_per_request': 50,  # Максимум вызовов за один запрос
            'max_same_tool_calls': 10,    # Максимум одинаковых вызовов подряд
            'request_call_count': 0,      # Счетчик вызовов в текущем запросе
            'last_tool_calls': [],        # История последних вызовов
            'current_request_id': None    # ID текущего запроса
        }
        
        self.logger.info("✅ ToolDispatcher инициализирован с защитой от зацикливания")
    
    def dispatch_tool_call(self, 
                          tool_name: str, 
                          params: Dict[str, Any] = None,
                          user_text: str = "",
                          mode: IntentMode = IntentMode.AUTO,
                          context: Dict[str, Any] = None) -> DispatchResponse:
        """
        Основной метод диспетчеризации tool_call.
        
        Args:
            tool_name (str): Название инструмента (может быть алиасом)
            params (Dict[str, Any]): Параметры для инструмента
            user_text (str): Исходный текст пользователя
            mode (IntentMode): Режим вызова
            context (Dict[str, Any]): Контекст выполнения
            
        Returns:
            DispatchResponse: Результат выполнения
        """
        start_time = time.time()
        params = params or {}
        context = context or {}
        
        # ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ: Проверяем лимиты вызовов
        request_id = context.get('request_id', 'unknown')
        if self.call_limits['current_request_id'] != request_id:
            # Новый запрос - сбрасываем счетчики
            self.call_limits['current_request_id'] = request_id
            self.call_limits['request_call_count'] = 0
            self.call_limits['last_tool_calls'] = []
        
        # Увеличиваем счетчик вызовов
        self.call_limits['request_call_count'] += 1
        
        # Проверяем превышение общего лимита вызовов
        if self.call_limits['request_call_count'] > self.call_limits['max_calls_per_request']:
            error_msg = f"🚫 ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ: Превышен лимит вызовов ({self.call_limits['max_calls_per_request']}) за запрос"
            self.logger.error(error_msg)
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=ToolCall(tool_name=tool_name, original_name=tool_name, mode=mode, 
                                 params=params, context=context, timestamp=start_time, user_text=user_text),
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
        
        # Нормализуем название инструмента
        canonical_name = self.alias_manager.normalize_tool_name(tool_name)
        
        # Проверяем повторяющиеся вызовы одного инструмента
        tool_signature = f"{canonical_name or tool_name}:{str(sorted(params.items()))}"
        self.call_limits['last_tool_calls'].append(tool_signature)
        
        # Оставляем только последние N вызовов для анализа
        if len(self.call_limits['last_tool_calls']) > self.call_limits['max_same_tool_calls']:
            self.call_limits['last_tool_calls'] = self.call_limits['last_tool_calls'][-self.call_limits['max_same_tool_calls']:]
        
        # Проверяем, не повторяется ли один и тот же вызов слишком часто
        same_calls_count = self.call_limits['last_tool_calls'].count(tool_signature)
        if same_calls_count >= self.call_limits['max_same_tool_calls']:
            error_msg = f"🚫 ЗАЩИТА ОТ ЗАЦИКЛИВАНИЯ: Обнаружено {same_calls_count} одинаковых вызовов {canonical_name or tool_name}"
            self.logger.error(error_msg)
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=ToolCall(tool_name=canonical_name or tool_name, original_name=tool_name, mode=mode, 
                                 params=params, context=context, timestamp=start_time, user_text=user_text),
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
        
        # Создаем объект вызова
        tool_call = ToolCall(
            tool_name=canonical_name or tool_name,
            original_name=tool_name,
            mode=mode,
            params=params,
            context=context,
            timestamp=start_time,
            user_text=user_text
        )
        
        # Обновляем статистику
        self._update_stats(tool_call)
        
        # Логируем вызов
        self.logger.info(f"🔧 Диспетчеризация: {tool_name} -> {canonical_name} (режим: {mode.value})")
        self.logger.debug(f"📝 Параметры: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        # Проверяем, найден ли инструмент
        if not canonical_name:
            suggestions = self.alias_manager.get_suggestions(tool_name)
            error_msg = f"Инструмент '{tool_name}' не найден"
            if suggestions:
                error_msg += f". Возможно, вы имели в виду: {', '.join(suggestions)}"
            
            response = DispatchResponse(
                result=DispatchResult.TOOL_NOT_FOUND,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=suggestions
            )
            
            self.logger.warning(f"❌ {error_msg}")
            return response
        
        # Выполняем инструмент
        try:
            response_data = self._execute_tool(canonical_name, params, context)
            
            response = DispatchResponse(
                result=DispatchResult.SUCCESS,
                tool_call=tool_call,
                response_data=response_data,
                error_message=None,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
            
            self.logger.info(f"✅ Инструмент {canonical_name} выполнен успешно за {response.execution_time:.2f}с")
            return response
            
        except Exception as e:
            error_msg = f"Ошибка выполнения инструмента {canonical_name}: {str(e)}"
            
            response = DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
            
            self.logger.error(f"❌ {error_msg}")
            self.logger.debug(f"🔍 Трассировка ошибки:", exc_info=True)
            return response
    
    def dispatch_by_intent(self, 
                          user_text: str,
                          forced_tool: Optional[str] = None,
                          context: Dict[str, Any] = None,
                          min_confidence: float = 0.5) -> Optional[DispatchResponse]:
        """
        Диспетчеризация на основе распознавания намерений.
        
        Args:
            user_text (str): Текст пользователя
            forced_tool (Optional[str]): Принудительно выбранный инструмент
            context (Dict[str, Any]): Контекст
            min_confidence (float): Минимальная уверенность для автовызова
            
        Returns:
            Optional[DispatchResponse]: Результат или None если намерение не распознано
        """
        self.logger.info(f"🧠 Анализ намерений для текста: '{user_text[:100]}...'")
        
        # Получаем лучшее совпадение намерения
        intent_match = self.intent_parser.get_best_match(
            user_text, 
            forced_tool=forced_tool,
            min_confidence=min_confidence
        )
        
        if not intent_match:
            self.logger.info("🤷 Намерение не распознано или уверенность слишком низкая")
            return None
        
        self.logger.info(f"🎯 Распознано намерение: {intent_match.tool_name} (уверенность: {intent_match.confidence:.2f})")
        
        # Объединяем извлеченные параметры с контекстом
        params = intent_match.extracted_params.copy()
        if context:
            params.update(context.get('tool_params', {}))
        
        # Диспетчеризуем вызов
        return self.dispatch_tool_call(
            tool_name=intent_match.tool_name,
            params=params,
            user_text=user_text,
            mode=intent_match.mode,
            context=context or {}
        )

    def dispatch_agent_call(self,
                            agent_name: str,
                            params: Dict[str, Any] = None,
                            user_text: str = "",
                            mode: IntentMode = IntentMode.AUTO,
                            context: Dict[str, Any] = None) -> DispatchResponse:
        """
        Диспетчеризация вызова агента (через SmartDelegator/AgentTemplateSystem).
        Возвращает честные ошибки, если агент не найден или не доступен.
        """
        start_time = time.time()
        params = params or {}
        context = context or {}

        # Формируем псевдо-вызов для логирования/статистики
        tool_call = ToolCall(
            tool_name=agent_name,
            original_name=agent_name,
            mode=mode,
            params=params,
            context=context,
            timestamp=start_time,
            user_text=user_text
        )
        self._update_stats(tool_call)

        self.logger.info(f"👤 Диспетчеризация агента: {agent_name} (режим: {mode.value})")
        self.logger.debug(f"📝 Параметры агента: {json.dumps(params, ensure_ascii=False, indent=2)}")

        if not self.smart_delegator:
            error_msg = "SmartDelegator не инициализирован"
            self.logger.error(f"❌ {error_msg}")
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )

        # Проверяем доступность агента
        try:
            if (not getattr(self.smart_delegator, "_is_agent_available", None)) or \
               (not self.smart_delegator._is_agent_available(agent_name)):
                error_msg = f"Агент '{agent_name}' не найден или недоступен"
                self.logger.warning(f"❌ {error_msg}")
                return DispatchResponse(
                    result=DispatchResult.TOOL_NOT_FOUND,
                    tool_call=tool_call,
                    response_data=None,
                    error_message=error_msg,
                    execution_time=time.time() - start_time,
                    suggestions=[]
                )
        except Exception as e:
            error_msg = f"Ошибка проверки доступности агента: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )

        # Выполнение агента
        try:
            result = self.smart_delegator._call_agent(agent_name, params, context)
            return DispatchResponse(
                result=DispatchResult.SUCCESS,
                tool_call=tool_call,
                response_data=result,
                error_message=None,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
        except Exception as e:
            error_msg = f"Ошибка выполнения агента {agent_name}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.logger.debug("🔍 Трассировка ошибки:", exc_info=True)
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )

    def dispatch_flow_call(self,
                           flow_name: str,
                           params: Dict[str, Any] = None,
                           user_text: str = "",
                           mode: IntentMode = IntentMode.AUTO,
                           context: Dict[str, Any] = None) -> DispatchResponse:
        """
        Диспетчеризация вызова флоу (Crew/Workflow) через SmartDelegator.
        Требует валидных конфигураций агентов и задач внутри params.
        """
        start_time = time.time()
        params = params or {}
        context = context or {}

        tool_call = ToolCall(
            tool_name=flow_name,
            original_name=flow_name,
            mode=mode,
            params=params,
            context=context,
            timestamp=start_time,
            user_text=user_text
        )
        self._update_stats(tool_call)

        self.logger.info(f"🔁 Диспетчеризация флоу: {flow_name} (режим: {mode.value})")
        self.logger.debug(f"📝 Параметры флоу: {json.dumps(params, ensure_ascii=False, indent=2)}")

        if not self.smart_delegator:
            error_msg = "SmartDelegator не инициализирован"
            self.logger.error(f"❌ {error_msg}")
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )

        try:
            result = self.smart_delegator._call_flow(flow_name, params, context)
            return DispatchResponse(
                result=DispatchResult.SUCCESS,
                tool_call=tool_call,
                response_data=result,
                error_message=None,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
        except Exception as e:
            error_msg = f"Ошибка выполнения флоу {flow_name}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.logger.debug("🔍 Трассировка ошибки:", exc_info=True)
            return DispatchResponse(
                result=DispatchResult.EXECUTION_ERROR,
                tool_call=tool_call,
                response_data=None,
                error_message=error_msg,
                execution_time=time.time() - start_time,
                suggestions=[]
            )
    
    def suggest_tools(self, user_text: str, max_suggestions: int = 3) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Предлагает инструменты для текста без выполнения.
        
        Args:
            user_text (str): Текст пользователя
            max_suggestions (int): Максимум предложений
            
        Returns:
            List[Tuple[str, float, Dict[str, Any]]]: Список (tool_name, confidence, params)
        """
        suggestions = self.intent_parser.suggest_tools(user_text, max_suggestions)
        
        result = []
        for suggestion in suggestions:
            result.append((
                suggestion.tool_name,
                suggestion.confidence,
                suggestion.extracted_params
            ))
        
        self.logger.info(f"💡 Предложено {len(result)} инструментов для: '{user_text[:50]}...'")
        return result
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Выполняет инструмент через SmartDelegator.
        
        Args:
            tool_name (str): Каноническое название инструмента
            params (Dict[str, Any]): Параметры
            context (Dict[str, Any]): Контекст
            
        Returns:
            Any: Результат выполнения инструмента
            
        Raises:
            Exception: Если инструмент недоступен или выполнение не удалось
        """
        if not self.smart_delegator:
            raise Exception("SmartDelegator не инициализирован")
        
        # Проверяем доступность инструмента
        if not self._is_tool_available(tool_name):
            raise Exception(f"Инструмент {tool_name} недоступен")
        
        # Определяем сервер для инструмента (локальный по умолчанию)
        server_name = context.get('server_name', 'local')
        
        # Вызываем инструмент через SmartDelegator
        result = self.smart_delegator._call_tool(tool_name, server_name, params)
        
        return result
    
    def _is_tool_available(self, tool_name: str) -> bool:
        """
        Проверяет доступность инструмента.
        
        Args:
            tool_name (str): Название инструмента
            
        Returns:
            bool: True если инструмент доступен
        """
        if not self.smart_delegator:
            return False
        
        # Проверяем в CrewAI инструментах
        if (self.smart_delegator.crewai_tools_available and 
            self.smart_delegator.crewai_tools):
            available_crewai = self.smart_delegator.crewai_tools.get_available_tools()
            if tool_name in available_crewai:
                return True
        
        # Проверяем в локальных MCP инструментах
        if (self.smart_delegator.local_tools_available and 
            self.smart_delegator.local_tools):
            available_local = self.smart_delegator.local_tools.get_available_tools()
            if tool_name in available_local:
                return True
        
        # Проверяем в внешних MCP инструментах
        if (self.smart_delegator.mcp_available and 
            self.smart_delegator.mcp_manager):
            tool = self.smart_delegator.mcp_manager.get_tool_by_name(tool_name)
            if tool:
                return True
        
        return False
    
    def _update_stats(self, tool_call: ToolCall) -> None:
        """Обновляет статистику вызовов"""
        self.call_stats['total_calls'] += 1
        
        if tool_call.mode == IntentMode.AUTO:
            self.call_stats['auto_calls'] += 1
        elif tool_call.mode == IntentMode.FORCED:
            self.call_stats['forced_calls'] += 1
        
        tool_name = tool_call.tool_name
        if tool_name not in self.call_stats['tool_usage']:
            self.call_stats['tool_usage'][tool_name] = 0
        self.call_stats['tool_usage'][tool_name] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования диспетчера.
        
        Returns:
            Dict[str, Any]: Статистика
        """
        return self.call_stats.copy()
    
    def get_available_tools(self) -> List[str]:
        """
        Возвращает список всех доступных инструментов.
        
        Returns:
            List[str]: Список канонических названий инструментов
        """
        return list(self.alias_manager.get_canonical_tools())
    
    def get_tool_aliases(self, tool_name: str) -> List[str]:
        """
        Возвращает все алиасы для инструмента.
        
        Args:
            tool_name (str): Каноническое название инструмента
            
        Returns:
            List[str]: Список алиасов
        """
        return self.alias_manager.get_all_aliases(tool_name)
    
    def validate_tool_params(self, tool_name: str, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Валидирует параметры для инструмента.
        
        Args:
            tool_name (str): Название инструмента
            params (Dict[str, Any]): Параметры
            
        Returns:
            Tuple[bool, Optional[str]]: (валидны ли параметры, сообщение об ошибке)
        """
        # Базовая валидация - можно расширить для каждого инструмента
        if not isinstance(params, dict):
            return False, "Параметры должны быть словарем"
        
        # Специфичные проверки для некоторых инструментов
        if tool_name == 'execute_shell':
            if 'command' not in params:
                return False, "Для execute_shell требуется параметр 'command'"
        
        elif tool_name == 'web_scraper':
            if 'url' not in params:
                return False, "Для web_scraper требуется параметр 'url'"
        
        elif tool_name == 'file_operations':
            if 'path' not in params:
                return False, "Для file_operations требуется параметр 'path'"
        
        return True, None
    
    def create_honest_error_response(self, tool_name: str, error: str) -> str:
        """
        Создает честный ответ об ошибке вместо галлюцинации.
        
        Args:
            tool_name (str): Название инструмента
            error (str): Описание ошибки
            
        Returns:
            str: Честное сообщение об ошибке
        """
        return f"""❌ **Ошибка выполнения инструмента**

**Инструмент:** {tool_name}
**Ошибка:** {error}

Я не могу выполнить этот запрос из-за указанной ошибки."""


# Глобальный экземпляр диспетчера
_tool_dispatcher = None

def get_tool_dispatcher(smart_delegator=None) -> ToolDispatcher:
    """
    Возвращает глобальный экземпляр диспетчера инструментов.
    
    Args:
        smart_delegator: Экземпляр SmartDelegator для выполнения инструментов
        
    Returns:
        ToolDispatcher: Экземпляр диспетчера
    """
    global _tool_dispatcher
    if _tool_dispatcher is None:
        _tool_dispatcher = ToolDispatcher(smart_delegator)
    elif smart_delegator and not _tool_dispatcher.smart_delegator:
        _tool_dispatcher.smart_delegator = smart_delegator
    return _tool_dispatcher
