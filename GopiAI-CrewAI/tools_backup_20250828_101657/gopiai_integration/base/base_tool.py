"""
🔧 GopiAI Base Tool
Базовый класс для всех инструментов GopiAI-CrewAI с улучшенным логированием и обработкой ошибок
"""

import os
import sys
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from pydantic import BaseModel, Field
import json
import tempfile
import subprocess

# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool
CREWAI_AVAILABLE = True

class GopiAIBaseTool(BaseTool):
    """
    Базовый класс для всех GopiAI инструментов CrewAI
    
    Особенности:
    - Единая система логирования
    - Стандартизированная обработка ошибок
    - Метрики производительности
    - Базовый интерфейс для всех инструментов
    """
    
    name: str = Field(default="gopiai_base_tool", description="Базовый класс для всех GopiAI инструментов")
    description: str = Field(default="Базовый класс для всех GopiAI инструментов", description="Описание инструмента")
    verbose: bool = Field(default=False, description="Подробный вывод сообщений")
    
    def __init__(self, **data):
        try:
            super().__init__(**data)
        except Exception as e:
            print(f"WARNING: Error initializing base class: {e}")
            # Устанавливаем атрибуты вручную, если super().__init__ не сработал
            for key, value in data.items():
                setattr(self, key, value)
            
            # Устанавливаем значения по умолчанию для обязательных атрибутов
            if not hasattr(self, "name"):
                self.name = "gopiai_base_tool"
            if not hasattr(self, "description"):
                self.description = "Базовый класс для всех GopiAI инструментов"
            if not hasattr(self, "verbose"):
                self.verbose = False
                
        self.logger = self._setup_logger(logging.INFO)
        self.metrics = {
            "calls": 0,
            "errors": 0,
            "total_time": 0,
            "last_call": None
        }
        self.logger.info(f"Tool {self.__class__.__name__} initialized")
    
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """
        Настройка логгера для инструмента
        
        Args:
            log_level: Logging level
            
        Returns:
            Configured logger
        """
        logger_name = f"gopiai.tools.{self.__class__.__name__}"
        logger = logging.getLogger(logger_name)
        
        # Проверяем, не настроен ли уже логгер
        if not logger.handlers:
            logger.setLevel(log_level)
            
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # File handler
            log_file = os.path.join(log_dir, f"{self.__class__.__name__.lower()}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            
            # Консольный обработчик
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)  # В консоль только ошибки
            
            # Форматтер
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Добавляем обработчики
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def run(self, *args, **kwargs) -> str:
        """
        Основной метод запуска инструмента с метриками и обработкой ошибок
        
        Returns:
            Результат работы инструмента
        """
        start_time = time.time()
        self.metrics["calls"] += 1
        self.metrics["last_call"] = datetime.now()
        
        try:
            self.logger.info(f"Запуск {self.__class__.__name__} с аргументами: {args}, {kwargs}")
            
            if self.verbose:
                print(f"🔧 Запуск {self.__class__.__name__}...")
                
            result = self._run(*args, **kwargs)
            
            execution_time = time.time() - start_time
            self.metrics["total_time"] += execution_time
            
            self.logger.info(f"Успешное выполнение за {execution_time:.2f}с: {result[:100] if isinstance(result, str) else str(result)[:100]}...")
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            execution_time = time.time() - start_time
            
            error_msg = f"Ошибка в {self.__class__.__name__}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            # Пытаемся выполнить fallback, если он есть
            try:
                if hasattr(self, '_fallback') and callable(getattr(self, '_fallback')):
                    self.logger.info("Попытка выполнить fallback...")
                    fallback_result = self._fallback(*args, **kwargs, error=e)
                    self.logger.info(f"Fallback успешен: {fallback_result[:100] if isinstance(fallback_result, str) else str(fallback_result)[:100]}...")
                    return fallback_result
            except Exception as fallback_error:
                self.logger.error(f"Ошибка в fallback: {str(fallback_error)}")
            
            # Если fallback не сработал или его нет, возвращаем сообщение об ошибке
            return f"Ошибка при выполнении инструмента '{self.__class__.__name__}': {e}"
    
    def _run(self, *args, **kwargs) -> str:
        """
        Метод для переопределения в дочерних классах
        
        Returns:
            Результат работы инструмента
        """
        raise NotImplementedError("Метод _run должен быть переопределен в дочернем классе")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик использования инструмента
        
        Returns:
            Словарь с метриками
        """
        if self.metrics["calls"] > 0:
            avg_time = self.metrics["total_time"] / self.metrics["calls"]
        else:
            avg_time = 0
            
        return {
            "name": self.__class__.__name__,
            "calls": self.metrics["calls"],
            "errors": self.metrics["errors"],
            "error_rate": self.metrics["errors"] / self.metrics["calls"] if self.metrics["calls"] > 0 else 0,
            "avg_time": avg_time,
            "total_time": self.metrics["total_time"],
            "last_call": self.metrics["last_call"].isoformat() if self.metrics["last_call"] else None
        }
    
    def reset_metrics(self) -> None:
        """Сброс метрик инструмента"""
        self.metrics = {
            "calls": 0,
            "errors": 0,
            "total_time": 0,
            "last_call": None
        }
        self.logger.info(f"Метрики {self.__class__.__name__} сброшены")

    def execute(self, *args, **kwargs) -> Any:
        """Выполнить инструмент с заданными параметрами"""
        raise NotImplementedError("Метод execute должен быть переопределен в подклассе")
    
    def safe_execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Безопасное выполнение инструмента с обработкой ошибок"""
        try:
            result = self.execute(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def run_node_script(self, script_path: str, input_data: Union[str, Dict], 
                       timeout: int = 60, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Запускает скрипт Node.js и передает ему данные через временный файл
        
        Args:
            script_path: Путь к JavaScript файлу
            input_data: Данные для передачи в скрипт (строка или словарь)
            timeout: Таймаут выполнения в секундах
            cwd: Рабочая директория
            
        Returns:
            Dict с результатами выполнения
        """
        try:
            # Создаем временный файл для входных данных
            with tempfile.NamedTemporaryFile(suffix='.json', mode='w', encoding='utf-8', delete=False) as temp_input:
                # Сериализуем данные в JSON если это словарь
                if isinstance(input_data, dict):
                    json.dump(input_data, temp_input, ensure_ascii=False)
                else:
                    temp_input.write(str(input_data))
                temp_input_path = temp_input.name
                
            # Создаем временный файл для выходных данных
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_output:
                temp_output_path = temp_output.name
                
            # Настройка окружения для правильной кодировки
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Запускаем Node.js, передавая пути к временным файлам как аргументы
            cmd = ["node", script_path, temp_input_path, temp_output_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            
            # Проверяем код возврата
            if result.returncode != 0:
                error_message = f"Ошибка Node.js ({result.returncode}): {result.stderr}"
                print(f"❌ {error_message}")
                return {"success": False, "error": error_message, "stdout": result.stdout, "stderr": result.stderr}
            
            # Читаем результат из выходного файла
            try:
                with open(temp_output_path, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
                return {"success": True, "result": output_data}
            except json.JSONDecodeError as e:
                return {
                    "success": False, 
                    "error": f"Ошибка формата JSON в выходном файле: {e}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Превышен таймаут выполнения ({timeout} сек)"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка запуска скрипта: {str(e)}"}
        finally:
            # Удаляем временные файлы
            for path in [temp_input_path, temp_output_path]:
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                except (OSError, IOError) as e:
                    # Игнорируем ошибки удаления временных файлов
                    pass


# Пример использования
if __name__ == "__main__":
    # Настройка корневого логгера для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Тестовый класс
    class TestTool(GopiAIBaseTool):
        name = "test_tool"
        description = "Тестовый инструмент"
        
        def _run(self, action, value=""):
            if action == "echo":
                return f"Echo: {value}"
            elif action == "error":
                raise ValueError("Тестовая ошибка")
            else:
                return f"Неизвестное действие: {action}"
        
        def _fallback(self, action, value="", error=None):
            return f"Fallback для {action}: {error}"
    
    # Создаем и тестируем
    tool = TestTool(verbose=True)
    
    print("=== Тест успешного выполнения ===")
    result = tool.run("echo", "Hello World")
    print(f"Результат: {result}")
    
    print("\n=== Тест обработки ошибки ===")
    result = tool.run("error")
    print(f"Результат: {result}")
    
    print("\n=== Метрики ===")
    print(tool.get_metrics())