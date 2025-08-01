"""
Система обработки ошибок для инструментов GopiAI.
Обеспечивает единообразную обработку ошибок и логирование.
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Типы ошибок в системе."""
    TOOL_EXECUTION = "tool_execution"
    COMMAND_SAFETY = "command_safety"
    FILE_OPERATION = "file_operation"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    SYSTEM_ERROR = "system_error"


class ErrorSeverity(Enum):
    """Уровни серьёзности ошибок."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorHandler:
    """
    Централизованная система обработки ошибок для инструментов.
    """

    def __init__(self):
        self.logger = logger
        self.error_count = 0
        self.last_errors = []
        self.max_error_history = 100
        
        self.logger.info("[ERROR-HANDLER] Инициализирована система обработки ошибок")

    def handle_tool_error(
        self, 
        error: Exception, 
        tool_name: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает ошибки выполнения инструментов.
        
        Args:
            error: Исключение
            tool_name: Имя инструмента
            context: Дополнительный контекст
            
        Returns:
            str: Пользовательское сообщение об ошибке
        """
        try:
            error_info = self._create_error_info(
                error=error,
                error_type=ErrorType.TOOL_EXECUTION,
                tool_name=tool_name,
                context=context
            )
            
            # Логирование ошибки
            self._log_error(error_info)
            
            # Сохранение в историю
            self._save_error_to_history(error_info)
            
            # Генерация пользовательского сообщения
            user_message = self._generate_user_message(error_info)
            
            return user_message
            
        except Exception as e:
            # Критическая ошибка в обработчике ошибок
            self.logger.critical(f"[ERROR-HANDLER] Критическая ошибка в обработчике: {e}")
            return f"Критическая ошибка системы: {str(error)}"

    def handle_command_safety_error(
        self, 
        command: str, 
        reason: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает ошибки безопасности команд.
        
        Args:
            command: Команда, которая была отклонена
            reason: Причина отклонения
            context: Дополнительный контекст
            
        Returns:
            str: Пользовательское сообщение об ошибке
        """
        try:
            error_info = self._create_error_info(
                error=None,
                error_type=ErrorType.COMMAND_SAFETY,
                tool_name="terminal",
                context={
                    "command": command,
                    "reason": reason,
                    **(context or {})
                }
            )
            
            # Логирование предупреждения о безопасности
            self._log_security_warning(error_info)
            
            # Сохранение в историю
            self._save_error_to_history(error_info)
            
            # Генерация пользовательского сообщения
            user_message = self._generate_security_message(command, reason)
            
            return user_message
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка обработки безопасности: {e}")
            return f"Команда '{command}' отклонена по соображениям безопасности: {reason}"

    def handle_file_operation_error(
        self, 
        error: Exception, 
        operation: str, 
        path: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает ошибки файловых операций.
        
        Args:
            error: Исключение
            operation: Тип операции
            path: Путь к файлу
            context: Дополнительный контекст
            
        Returns:
            str: Пользовательское сообщение об ошибке
        """
        try:
            error_info = self._create_error_info(
                error=error,
                error_type=ErrorType.FILE_OPERATION,
                tool_name="file_operations",
                context={
                    "operation": operation,
                    "path": path,
                    **(context or {})
                }
            )
            
            # Логирование ошибки
            self._log_error(error_info)
            
            # Сохранение в историю
            self._save_error_to_history(error_info)
            
            # Генерация пользовательского сообщения
            user_message = self._generate_file_error_message(error, operation, path)
            
            return user_message
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка обработки файловой операции: {e}")
            return f"Ошибка файловой операции '{operation}' для '{path}': {str(error)}"

    def handle_network_error(
        self, 
        error: Exception, 
        url: str, 
        operation: str = "request",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает сетевые ошибки.
        
        Args:
            error: Исключение
            url: URL, вызвавший ошибку
            operation: Тип операции
            context: Дополнительный контекст
            
        Returns:
            str: Пользовательское сообщение об ошибке
        """
        try:
            error_info = self._create_error_info(
                error=error,
                error_type=ErrorType.NETWORK_ERROR,
                tool_name="web_tools",
                context={
                    "url": url,
                    "operation": operation,
                    **(context or {})
                }
            )
            
            # Логирование ошибки
            self._log_error(error_info)
            
            # Сохранение в историю
            self._save_error_to_history(error_info)
            
            # Генерация пользовательского сообщения
            user_message = self._generate_network_error_message(error, url, operation)
            
            return user_message
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка обработки сетевой ошибки: {e}")
            return f"Сетевая ошибка при {operation} для {url}: {str(error)}"

    def handle_timeout_error(
        self, 
        operation: str, 
        timeout: int, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Обрабатывает ошибки таймаута.
        
        Args:
            operation: Операция, которая превысила таймаут
            timeout: Значение таймаута в секундах
            context: Дополнительный контекст
            
        Returns:
            str: Пользовательское сообщение об ошибке
        """
        try:
            error_info = self._create_error_info(
                error=None,
                error_type=ErrorType.TIMEOUT_ERROR,
                tool_name="system",
                context={
                    "operation": operation,
                    "timeout": timeout,
                    **(context or {})
                }
            )
            
            # Логирование ошибки
            self._log_error(error_info)
            
            # Сохранение в историю
            self._save_error_to_history(error_info)
            
            # Генерация пользовательского сообщения
            user_message = f"Операция '{operation}' превысила лимит времени выполнения ({timeout} сек). Попробуйте упростить запрос или увеличить таймаут."
            
            return user_message
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка обработки таймаута: {e}")
            return f"Операция '{operation}' превысила лимит времени выполнения ({timeout} сек)"

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику ошибок.
        
        Returns:
            Dict: Статистика ошибок
        """
        try:
            error_types = {}
            tool_errors = {}
            severity_counts = {}
            
            for error_info in self.last_errors:
                # Подсчёт по типам ошибок
                error_type = error_info.get("error_type", "unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
                # Подсчёт по инструментам
                tool_name = error_info.get("tool_name", "unknown")
                tool_errors[tool_name] = tool_errors.get(tool_name, 0) + 1
                
                # Подсчёт по серьёзности
                severity = error_info.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                "total_errors": self.error_count,
                "recent_errors": len(self.last_errors),
                "error_types": error_types,
                "tool_errors": tool_errors,
                "severity_counts": severity_counts,
                "last_error_time": self.last_errors[-1]["timestamp"] if self.last_errors else None
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка получения статистики: {e}")
            return {"error": f"Ошибка получения статистики: {str(e)}"}

    def clear_error_history(self) -> None:
        """Очищает историю ошибок."""
        try:
            self.last_errors.clear()
            self.error_count = 0
            self.logger.info("[ERROR-HANDLER] История ошибок очищена")
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка очистки истории: {e}")

    # Приватные методы

    def _create_error_info(
        self, 
        error: Optional[Exception], 
        error_type: ErrorType, 
        tool_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создаёт структурированную информацию об ошибке.
        
        Args:
            error: Исключение
            error_type: Тип ошибки
            tool_name: Имя инструмента
            context: Дополнительный контекст
            
        Returns:
            Dict: Информация об ошибке
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type.value,
            "tool_name": tool_name,
            "severity": self._determine_severity(error, error_type),
            "context": context or {}
        }
        
        if error:
            error_info.update({
                "error_class": error.__class__.__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            })
        
        return error_info

    def _determine_severity(self, error: Optional[Exception], error_type: ErrorType) -> str:
        """
        Определяет серьёзность ошибки.
        
        Args:
            error: Исключение
            error_type: Тип ошибки
            
        Returns:
            str: Уровень серьёзности
        """
        try:
            # Критические ошибки
            if error_type == ErrorType.SYSTEM_ERROR:
                return ErrorSeverity.CRITICAL.value
            
            # Высокая серьёзность
            if error_type in [ErrorType.PERMISSION_ERROR, ErrorType.COMMAND_SAFETY]:
                return ErrorSeverity.HIGH.value
            
            # Средняя серьёзность
            if error_type in [ErrorType.TIMEOUT_ERROR, ErrorType.NETWORK_ERROR]:
                return ErrorSeverity.MEDIUM.value
            
            # Низкая серьёзность
            return ErrorSeverity.LOW.value
            
        except Exception:
            return ErrorSeverity.MEDIUM.value

    def _log_error(self, error_info: Dict[str, Any]) -> None:
        """
        Логирует ошибку с соответствующим уровнем.
        
        Args:
            error_info: Информация об ошибке
        """
        try:
            severity = error_info.get("severity", "medium")
            tool_name = error_info.get("tool_name", "unknown")
            error_type = error_info.get("error_type", "unknown")
            error_message = error_info.get("error_message", "Unknown error")
            
            log_message = f"[{tool_name.upper()}] {error_type}: {error_message}"
            
            if severity == ErrorSeverity.CRITICAL.value:
                self.logger.critical(log_message)
            elif severity == ErrorSeverity.HIGH.value:
                self.logger.error(log_message)
            elif severity == ErrorSeverity.MEDIUM.value:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            # Дополнительное логирование контекста для отладки
            if error_info.get("context"):
                self.logger.debug(f"[{tool_name.upper()}] Контекст: {error_info['context']}")
                
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка логирования: {e}")

    def _log_security_warning(self, error_info: Dict[str, Any]) -> None:
        """
        Логирует предупреждения безопасности.
        
        Args:
            error_info: Информация об ошибке безопасности
        """
        try:
            context = error_info.get("context", {})
            command = context.get("command", "unknown")
            reason = context.get("reason", "unknown")
            
            self.logger.warning(f"[SECURITY] Команда отклонена: '{command}' - {reason}")
            
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка логирования безопасности: {e}")

    def _save_error_to_history(self, error_info: Dict[str, Any]) -> None:
        """
        Сохраняет ошибку в историю.
        
        Args:
            error_info: Информация об ошибке
        """
        try:
            self.last_errors.append(error_info)
            self.error_count += 1
            
            # Ограничиваем размер истории
            if len(self.last_errors) > self.max_error_history:
                self.last_errors.pop(0)
                
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка сохранения в историю: {e}")

    def _generate_user_message(self, error_info: Dict[str, Any]) -> str:
        """
        Генерирует пользовательское сообщение об ошибке.
        
        Args:
            error_info: Информация об ошибке
            
        Returns:
            str: Пользовательское сообщение
        """
        try:
            error_type = error_info.get("error_type", "unknown")
            tool_name = error_info.get("tool_name", "unknown")
            error_message = error_info.get("error_message", "Неизвестная ошибка")
            
            # Базовые шаблоны сообщений
            if error_type == ErrorType.TOOL_EXECUTION.value:
                return f"Ошибка выполнения инструмента '{tool_name}': {error_message}"
            elif error_type == ErrorType.VALIDATION_ERROR.value:
                return f"Ошибка валидации данных: {error_message}"
            elif error_type == ErrorType.PERMISSION_ERROR.value:
                return f"Ошибка доступа: {error_message}. Проверьте права доступа."
            elif error_type == ErrorType.SYSTEM_ERROR.value:
                return f"Системная ошибка: {error_message}. Обратитесь к администратору."
            else:
                return f"Ошибка в инструменте '{tool_name}': {error_message}"
                
        except Exception as e:
            self.logger.error(f"[ERROR-HANDLER] Ошибка генерации сообщения: {e}")
            return f"Произошла ошибка: {error_info.get('error_message', 'Неизвестная ошибка')}"

    def _generate_security_message(self, command: str, reason: str) -> str:
        """
        Генерирует сообщение о нарушении безопасности.
        
        Args:
            command: Отклонённая команда
            reason: Причина отклонения
            
        Returns:
            str: Сообщение о безопасности
        """
        return f"""🔒 Команда отклонена по соображениям безопасности

Команда: {command}
Причина: {reason}

Для выполнения команд доступен ограниченный набор безопасных операций. 
Если вам необходимо выполнить эту команду, обратитесь к администратору системы."""

    def _generate_file_error_message(self, error: Exception, operation: str, path: str) -> str:
        """
        Генерирует сообщение об ошибке файловой операции.
        
        Args:
            error: Исключение
            operation: Операция
            path: Путь к файлу
            
        Returns:
            str: Сообщение об ошибке
        """
        error_name = error.__class__.__name__
        
        if "FileNotFoundError" in error_name:
            return f"Файл или директория '{path}' не найдены"
        elif "PermissionError" in error_name:
            return f"Недостаточно прав для операции '{operation}' с '{path}'"
        elif "IsADirectoryError" in error_name:
            return f"'{path}' является директорией, а ожидался файл"
        elif "NotADirectoryError" in error_name:
            return f"'{path}' не является директорией"
        elif "OSError" in error_name:
            return f"Системная ошибка при операции '{operation}' с '{path}': {str(error)}"
        else:
            return f"Ошибка файловой операции '{operation}' для '{path}': {str(error)}"

    def _generate_network_error_message(self, error: Exception, url: str, operation: str) -> str:
        """
        Генерирует сообщение о сетевой ошибке.
        
        Args:
            error: Исключение
            url: URL
            operation: Операция
            
        Returns:
            str: Сообщение об ошибке
        """
        error_name = error.__class__.__name__
        
        if "ConnectionError" in error_name:
            return f"Не удалось подключиться к {url}. Проверьте интернет-соединение."
        elif "Timeout" in error_name:
            return f"Превышено время ожидания при обращении к {url}"
        elif "HTTPError" in error_name:
            return f"HTTP ошибка при обращении к {url}: {str(error)}"
        elif "URLError" in error_name:
            return f"Некорректный URL: {url}"
        else:
            return f"Сетевая ошибка при {operation} для {url}: {str(error)}"


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()