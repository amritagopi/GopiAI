"""
Менеджер ошибок для системы анализа и категоризации типичных ошибок

Предоставляет единый интерфейс для работы с системой анализа ошибок.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple
import json
import time
import os
import traceback
from datetime import datetime

from app.agent.error_analysis_system import (
    ErrorInstance, ErrorCategory, ErrorStorage, ErrorAnalyzer,
    ErrorSeverity, ErrorSource
)
from app.logger import logger


class ErrorManager:
    """
    Класс для управления системой анализа и категоризации ошибок.
    """

    def __init__(self, error_dir: str = "data/errors"):
        """
        Инициализирует менеджер ошибок.

        Args:
            error_dir: Директория для хранения данных об ошибках
        """
        self.error_dir = error_dir
        self.storage = ErrorStorage(error_dir)
        self.analyzer = ErrorAnalyzer(self.storage)

        # Добавляем хранилище для отслеживания недавних ошибок
        # формат: {хеш_сообщения: {'count': количество, 'last_time': время_последней_ошибки}}
        self.recent_errors = {}
        # Настройки для предотвращения дублирования
        self.deduplication_window = 300  # 5 минут в секундах
        self.clear_recent_errors_interval = 3600  # 1 час в секундах
        self.last_cleanup_time = time.time()

        # Настройки автоматической очистки
        self.auto_cleanup_days = 90  # Дни для автоматической очистки
        self.last_auto_cleanup = None  # Время последней автоматической очистки

        # Настройки для напоминаний
        self.reminder_file = os.path.join(error_dir, "reminders.json")
        self.reminders = self._load_reminders()

        # Загружаем существующие данные
        self.storage.load()

        # Инициализируем базовые категории, если их еще нет
        self._initialize_default_categories()

        # Проверяем необходимость очистки данных
        self._check_auto_cleanup()

        # Проверяем необходимость создания напоминаний
        self._check_reminders()

        logger.info("Error Manager initialized")

    def _initialize_default_categories(self) -> None:
        """
        Инициализирует базовые категории ошибок, если их еще нет в хранилище.
        """
        default_categories = [
            {
                "name": "Permission Denied",
                "description": "Errors related to insufficient permissions",
                "patterns": [r"permission denied", r"access denied", r"not authorized"],
                "keywords": ["permission", "access", "denied", "unauthorized"],
                "source": ErrorSource.PERMISSION,
                "severity": ErrorSeverity.HIGH
            },
            {
                "name": "File Not Found",
                "description": "Errors related to missing files or directories",
                "patterns": [r"no such file", r"file not found", r"directory not found"],
                "keywords": ["file", "directory", "not found", "missing"],
                "source": ErrorSource.EXECUTION,
                "severity": ErrorSeverity.MEDIUM
            },
            {
                "name": "Invalid Argument",
                "description": "Errors related to invalid arguments or parameters",
                "patterns": [r"invalid argument", r"invalid parameter", r"illegal argument"],
                "keywords": ["invalid", "argument", "parameter", "illegal"],
                "source": ErrorSource.EXECUTION,
                "severity": ErrorSeverity.MEDIUM
            },
            {
                "name": "Timeout",
                "description": "Errors related to operation timeouts",
                "patterns": [r"timeout", r"timed out"],
                "keywords": ["timeout", "timed out", "too slow"],
                "source": ErrorSource.EXECUTION,
                "severity": ErrorSeverity.MEDIUM
            },
            {
                "name": "Connection Error",
                "description": "Errors related to network connections",
                "patterns": [r"connection refused", r"network error", r"connection failed"],
                "keywords": ["connection", "network", "refused", "failed"],
                "source": ErrorSource.EXECUTION,
                "severity": ErrorSeverity.HIGH
            },
            {
                "name": "Planning Error",
                "description": "Errors that occur during the planning phase",
                "patterns": [r"planning error", r"failed to create plan"],
                "keywords": ["planning", "plan", "failed"],
                "source": ErrorSource.PLANNING,
                "severity": ErrorSeverity.HIGH
            },
            {
                "name": "Reasoning Error",
                "description": "Errors in logical reasoning or inference",
                "patterns": [r"reasoning error", r"inference failed", r"logical error"],
                "keywords": ["reasoning", "inference", "logical", "failed"],
                "source": ErrorSource.REASONING,
                "severity": ErrorSeverity.HIGH
            },
            {
                "name": "Tool Execution Error",
                "description": "Errors that occur during tool execution",
                "patterns": [r"tool execution failed", r"tool call error"],
                "keywords": ["tool", "execution", "failed", "error"],
                "source": ErrorSource.TOOL_CALL,
                "severity": ErrorSeverity.MEDIUM
            }
        ]

        # Добавляем категории, если их еще нет
        for cat_data in default_categories:
            # Проверяем, существует ли уже категория с таким именем
            exists = any(cat.name == cat_data["name"] for cat in self.storage.categories.values())
            if not exists:
                category = ErrorCategory(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    patterns=cat_data.get("patterns", []),
                    keywords=cat_data.get("keywords", []),
                    source=cat_data.get("source"),
                    severity=cat_data.get("severity")
                )
                self.storage.add_category(category)
                logger.info(f"Added default error category: {cat_data['name']}")

        # Сохраняем обновленные категории
        if len(default_categories) > 0:
            self.storage.save()

    def log_error(
        self,
        message: str,
        source: Union[ErrorSource, str],
        severity: Union[ErrorSeverity, str] = ErrorSeverity.MEDIUM,
        task_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        auto_categorize: bool = True,
        prevent_duplicates: bool = True
    ) -> str:
        """
        Регистрирует новую ошибку в системе.

        Args:
            message: Сообщение об ошибке
            source: Источник ошибки
            severity: Уровень серьезности
            task_id: ID задачи, при выполнении которой произошла ошибка
            stack_trace: Трассировка стека (если доступна)
            context: Контекст выполнения при возникновении ошибки
            auto_categorize: Автоматически категоризировать ошибку
            prevent_duplicates: Предотвращать дублирование похожих ошибок

        Returns:
            ID зарегистрированной ошибки
        """
        # Конвертируем строковые перечисления в объекты Enum
        if isinstance(source, str):
            try:
                source = ErrorSource(source)
            except ValueError:
                source = ErrorSource.OTHER

        if isinstance(severity, str):
            try:
                severity = ErrorSeverity(severity)
            except ValueError:
                severity = ErrorSeverity.MEDIUM

        # Проверяем на дублирование, если включено
        if prevent_duplicates:
            # Очищаем старые записи о недавних ошибках
            self._clean_recent_errors()

            # Создаем простой хеш из сообщения и источника
            error_hash = f"{message[:100]}_{source.value}"

            # Проверяем, была ли такая ошибка недавно
            if error_hash in self.recent_errors:
                recent_error = self.recent_errors[error_hash]
                current_time = time.time()

                # Если ошибка произошла недавно (в пределах окна дедупликации)
                if current_time - recent_error['last_time'] < self.deduplication_window:
                    # Увеличиваем счетчик и обновляем время
                    recent_error['count'] += 1
                    recent_error['last_time'] = current_time

                    # Логируем информацию о дубликате
                    logger.info(f"Duplicate error detected: {message[:100]} (count: {recent_error['count']})")

                    # Если у нас есть ID для этой ошибки, возвращаем его
                    if 'error_id' in recent_error:
                        return recent_error['error_id']

        # Создаем экземпляр ошибки
        error = ErrorInstance(
            message=message,
            source=source,
            severity=severity,
            task_id=task_id,
            stack_trace=stack_trace,
            context=context
        )

        # Категоризируем ошибку, если нужно
        if auto_categorize:
            category_id = self.analyzer.categorize_error(error)
            if category_id:
                error.category_id = category_id
                category = self.storage.get_category(category_id)
                if category:
                    logger.info(f"Error categorized as: {category.name}")

        # Добавляем ошибку в хранилище
        error_id = self.storage.add_error(error)

        # Логируем информацию об ошибке
        category_name = "Uncategorized"
        if error.category_id and error.category_id in self.storage.categories:
            category_name = self.storage.categories[error.category_id].name

        logger.error(f"Error logged [{category_name}]: {message}")

        # Если включена дедупликация, сохраняем информацию об этой ошибке
        if prevent_duplicates:
            self.recent_errors[error_hash] = {
                'count': 1,
                'last_time': time.time(),
                'error_id': error_id
            }

        # Сохраняем обновленные данные
        self.storage.save()

        return error_id

    def _clean_recent_errors(self):
        """
        Очищает список недавних ошибок от устаревших записей
        """
        current_time = time.time()

        # Если прошло достаточно времени с последней очистки
        if current_time - self.last_cleanup_time > self.clear_recent_errors_interval:
            keys_to_remove = []

            # Находим устаревшие записи
            for error_hash, data in self.recent_errors.items():
                # Если прошло больше времени, чем окно дедупликации
                if current_time - data['last_time'] > self.deduplication_window:
                    keys_to_remove.append(error_hash)

            # Удаляем устаревшие записи
            for key in keys_to_remove:
                del self.recent_errors[key]

            # Обновляем время последней очистки
            self.last_cleanup_time = current_time

            logger.info(f"Cleaned {len(keys_to_remove)} outdated error records")

    def log_exception(
        self,
        exception: Exception,
        source: ErrorSource,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        auto_categorize: bool = True
    ) -> str:
        """
        Регистрирует исключение как ошибку.

        Args:
            exception: Исключение для регистрации
            source: Источник ошибки
            task_id: ID задачи, при выполнении которой произошла ошибка
            context: Контекст выполнения при возникновении ошибки
            auto_categorize: Автоматически категоризировать ошибку

        Returns:
            ID зарегистрированной ошибки
        """
        # Получаем сообщение и трассировку стека
        message = str(exception)
        stack_trace = traceback.format_exc()

        # Определяем уровень серьезности на основе типа исключения
        severity = ErrorSeverity.MEDIUM
        if isinstance(exception, (PermissionError, OSError)):
            severity = ErrorSeverity.HIGH
        elif isinstance(exception, (ValueError, TypeError, KeyError, IndexError)):
            severity = ErrorSeverity.MEDIUM
        elif isinstance(exception, (TimeoutError, ConnectionError)):
            severity = ErrorSeverity.HIGH

        # Регистрируем ошибку
        return self.log_error(
            message=message,
            source=source,
            severity=severity,
            task_id=task_id,
            stack_trace=stack_trace,
            context=context,
            auto_categorize=auto_categorize
        )

    def resolve_error(self, error_id: str, resolution: str) -> bool:
        """
        Отмечает ошибку как разрешенную.

        Args:
            error_id: ID ошибки
            resolution: Описание решения

        Returns:
            True в случае успеха, иначе False
        """
        error = self.storage.get_error(error_id)
        if not error:
            logger.warning(f"Error {error_id} not found")
            return False

        error.mark_as_resolved(resolution)
        self.storage.save()

        logger.info(f"Error {error_id} marked as resolved")
        return True

    def add_error_category(
        self,
        name: str,
        description: str,
        patterns: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        source: Optional[ErrorSource] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> str:
        """
        Добавляет новую категорию ошибок.

        Args:
            name: Имя категории
            description: Описание категории
            patterns: Регулярные выражения для сопоставления
            keywords: Ключевые слова для сопоставления
            source: Основной источник ошибок данной категории
            severity: Стандартный уровень серьезности для ошибок категории

        Returns:
            ID новой категории
        """
        category = ErrorCategory(
            name=name,
            description=description,
            patterns=patterns,
            keywords=keywords,
            source=source,
            severity=severity
        )

        category_id = self.storage.add_category(category)
        self.storage.save()

        logger.info(f"Added new error category: {name}")
        return category_id

    def get_error_statistics(
        self,
        time_period: Optional[int] = None,
        source: Optional[ErrorSource] = None
    ) -> Dict[str, Any]:
        """
        Получает статистику ошибок.

        Args:
            time_period: Период анализа в днях (None - все время)
            source: Источник ошибок для анализа (None - все источники)

        Returns:
            Словарь со статистикой ошибок
        """
        return self.analyzer.analyze_error_trends(time_period, source)

    def categorize_uncategorized_errors(self) -> int:
        """
        Категоризирует все некатегоризированные ошибки.

        Returns:
            Количество категоризированных ошибок
        """
        count = 0

        # Получаем все некатегоризированные ошибки
        uncategorized = [err for err in self.storage.errors.values() if not err.category_id]

        for error in uncategorized:
            category_id = self.analyzer.categorize_error(error)
            if category_id:
                error.category_id = category_id
                count += 1

        if count > 0:
            self.storage.save()
            logger.info(f"Categorized {count} previously uncategorized errors")

        return count

    def suggest_error_resolution(self, error_id: str) -> Optional[str]:
        """
        Предлагает возможное решение проблемы на основе похожих ошибок.

        Args:
            error_id: ID ошибки

        Returns:
            Предлагаемое решение или None, если не удалось найти
        """
        error = self.storage.get_error(error_id)
        if not error:
            logger.warning(f"Error {error_id} not found")
            return None

        resolution = self.analyzer.suggest_resolution(error)
        if resolution:
            logger.info(f"Suggested resolution for error {error_id}")
        else:
            logger.info(f"No resolution found for error {error_id}")

        return resolution

    def learn_from_similar_errors(self, error_message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Находит похожие ошибки и извлекает из них информацию для обучения.

        Args:
            error_message: Сообщение об ошибке для поиска похожих
            limit: Максимальное количество результатов

        Returns:
            Список похожих ошибок с полезной информацией для обучения
        """
        # Создаем временный экземпляр ошибки для анализа
        temp_error = ErrorInstance(
            message=error_message,
            source=ErrorSource.OTHER,
            severity=ErrorSeverity.MEDIUM
        )

        # Получаем похожие ошибки
        similar = self.analyzer.get_similar_errors(temp_error, limit)

        # Формируем результаты с дополнительной информацией для обучения
        results = []
        for item in similar:
            error_data = item["error"]
            resolved = error_data.get("resolved", False)

            result = {
                "error_message": error_data.get("message", ""),
                "similarity": item["similarity"],
                "resolved": resolved,
                "resolution": error_data.get("resolution") if resolved else None,
                "category": None
            }

            # Добавляем информацию о категории, если есть
            category_id = error_data.get("category_id")
            if category_id:
                category = self.storage.get_category(category_id)
                if category:
                    result["category"] = {
                        "name": category.name,
                        "description": category.description
                    }

            results.append(result)

        return results

    def detect_error_patterns(self, time_period: Optional[int] = 30) -> List[Dict[str, Any]]:
        """
        Выявляет повторяющиеся паттерны ошибок за указанный период.

        Args:
            time_period: Период анализа в днях (None - все время)

        Returns:
            Список выявленных паттернов с метаданными
        """
        # Получаем статистику ошибок
        stats = self.analyzer.analyze_error_trends(time_period)

        # Анализируем паттерны
        patterns = []

        # Часто встречающиеся категории ошибок
        category_stats = stats.get("by_category", {})
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            if count >= 3:  # Минимальный порог для паттерна
                patterns.append({
                    "type": "category_frequency",
                    "category": category,
                    "count": count,
                    "description": f"Frequent occurrence of '{category}' errors"
                })

        # Источники ошибок
        source_stats = stats.get("by_source", {})
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            if count >= 5:  # Более высокий порог для источников
                patterns.append({
                    "type": "source_frequency",
                    "source": source,
                    "count": count,
                    "description": f"High number of errors from '{source}' source"
                })

        # Общие паттерны в сообщениях
        common_patterns = stats.get("common_patterns", [])
        if common_patterns:
            patterns.append({
                "type": "message_patterns",
                "patterns": common_patterns[:5],
                "description": "Common patterns in error messages"
            })

        # Низкий показатель разрешения
        resolution_rate = stats.get("resolution_rate", 0)
        if resolution_rate < 0.5 and stats.get("total_errors", 0) > 10:
            patterns.append({
                "type": "low_resolution",
                "resolution_rate": resolution_rate,
                "description": f"Low error resolution rate ({resolution_rate:.2%})"
            })

        return patterns

    def export_learning_dataset(self, output_file: str) -> bool:
        """
        Экспортирует данные об ошибках и их разрешениях в формат для обучения.

        Args:
            output_file: Путь к файлу для экспорта

        Returns:
            True в случае успеха, иначе False
        """
        try:
            # Собираем данные для обучения
            dataset = []

            # Получаем все разрешенные ошибки
            resolved_errors = [err for err in self.storage.errors.values() if err.resolved and err.resolution]

            for error in resolved_errors:
                category_name = "Uncategorized"
                if error.category_id and error.category_id in self.storage.categories:
                    category_name = self.storage.categories[error.category_id].name

                item = {
                    "error_message": error.message,
                    "source": error.source.value,
                    "severity": error.severity.value,
                    "category": category_name,
                    "resolution": error.resolution
                }

                dataset.append(item)

            # Сохраняем данные в файл
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported learning dataset with {len(dataset)} entries to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export learning dataset: {str(e)}")
            return False

    def import_learning_dataset(self, input_file: str) -> int:
        """
        Импортирует данные для обучения.

        Args:
            input_file: Путь к файлу с данными

        Returns:
            Количество импортированных записей
        """
        try:
            # Загружаем данные из файла
            with open(input_file, 'r', encoding='utf-8') as f:
                dataset = json.load(f)

            count = 0
            for item in dataset:
                try:
                    # Создаем категорию, если не существует
                    category_name = item.get("category", "Unknown")
                    category_id = None

                    # Ищем существующую категорию с таким именем
                    for cat_id, cat in self.storage.categories.items():
                        if cat.name == category_name:
                            category_id = cat_id
                            break

                    # Если категория не найдена, создаем новую
                    if not category_id and category_name != "Uncategorized":
                        category = ErrorCategory(
                            name=category_name,
                            description=f"Errors related to {category_name.lower()}",
                            keywords=[category_name.lower()]
                        )
                        category_id = self.storage.add_category(category)

                    # Создаем запись об ошибке
                    try:
                        source = ErrorSource(item.get("source", "other"))
                    except ValueError:
                        source = ErrorSource.OTHER

                    try:
                        severity = ErrorSeverity(item.get("severity", "medium"))
                    except ValueError:
                        severity = ErrorSeverity.MEDIUM

                    error = ErrorInstance(
                        message=item["error_message"],
                        source=source,
                        severity=severity,
                        category_id=category_id,
                        resolution=item.get("resolution")
                    )

                    # Если есть решение, отмечаем ошибку как разрешенную
                    if item.get("resolution"):
                        error.resolved = True
                        error.resolved_at = time.time()

                    # Добавляем ошибку в хранилище
                    self.storage.add_error(error)
                    count += 1

                except KeyError as e:
                    logger.warning(f"Skipping incomplete dataset entry: {str(e)}")
                    continue

            # Сохраняем обновленные данные
            if count > 0:
                self.storage.save()
                logger.info(f"Imported {count} entries from learning dataset")

            return count
        except Exception as e:
            logger.error(f"Failed to import learning dataset: {str(e)}")
            return 0

    def _load_reminders(self) -> Dict[str, Any]:
        """
        Загружает напоминания из файла

        Returns:
            Словарь с напоминаниями
        """
        if not os.path.exists(self.reminder_file):
            # Создаем базовые напоминания
            reminders = {
                "category_check": {
                    "title": "Проверка категорий ошибок",
                    "description": "Рекомендуется периодически проверять категории ошибок и обновлять их",
                    "last_check": None,
                    "check_interval_days": 30,
                    "instructions": self._get_category_check_instructions()
                },
                "error_cleanup": {
                    "title": "Очистка старых данных об ошибках",
                    "description": "Рекомендуется периодически очищать устаревшие данные об ошибках",
                    "last_check": None,
                    "check_interval_days": 30,
                    "instructions": self._get_cleanup_instructions()
                }
            }

            # Сохраняем напоминания
            self._save_reminders(reminders)
            return reminders

        try:
            with open(self.reminder_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load reminders: {str(e)}")
            return {}

    def _save_reminders(self, reminders: Dict[str, Any]) -> None:
        """
        Сохраняет напоминания в файл

        Args:
            reminders: Словарь с напоминаниями
        """
        try:
            os.makedirs(os.path.dirname(self.reminder_file), exist_ok=True)
            with open(self.reminder_file, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save reminders: {str(e)}")

    def _get_category_check_instructions(self) -> str:
        """
        Возвращает инструкции для проверки категорий ошибок

        Returns:
            Текст инструкций
        """
        return (
            "Инструкции по проверке категорий ошибок:\n\n"
            "1. Откройте файл categories.json из директории data/errors\n"
            "2. Просмотрите все категории и их описания\n"
            "3. Проверьте, есть ли новые типы ошибок, которые стоит добавить\n"
            "4. Убедитесь, что шаблоны и ключевые слова актуальны\n"
            "5. Обновите файл, если необходимо\n\n"
            "Для автоматического анализа можно использовать нейросеть, скопировав следующий промпт:\n\n"
            "\"Проанализируй файл категорий ошибок JSON и предложи улучшения. "
            "Нужно добавить новые категории для распространенных ошибок, "
            "улучшить шаблоны и ключевые слова для существующих категорий.\""
        )

    def _get_cleanup_instructions(self) -> str:
        """
        Возвращает инструкции для очистки данных об ошибках

        Returns:
            Текст инструкций
        """
        return (
            "Инструкции по очистке данных об ошибках:\n\n"
            "1. Автоматическая очистка удаляет ошибки старше 90 дней\n"
            "2. Если вы хотите сохранить важные ошибки, измените их уровень на HIGH или CRITICAL\n"
            "3. Для ручной очистки вызовите метод cleanup_errors()\n"
            "4. Перед очисткой рекомендуется создать резервную копию данных\n\n"
            "Пример кода для очистки:\n"
            "```python\n"
            "from app.agent.error_manager import ErrorManager\n"
            "manager = ErrorManager()\n"
            "manager.create_backup()\n"
            "manager.cleanup_errors(days=60)  # Очистка ошибок старше 60 дней\n"
            "```"
        )

    def _check_reminders(self) -> None:
        """
        Проверяет необходимость создания напоминаний
        """
        current_time = time.time()

        for reminder_id, reminder in self.reminders.items():
            last_check = reminder.get("last_check")
            check_interval = reminder.get("check_interval_days", 30) * 24 * 60 * 60  # Дни в секунды

            # Если проверка еще не выполнялась или прошло достаточно времени
            if last_check is None or (current_time - last_check > check_interval):
                logger.info(f"Reminder triggered: {reminder.get('title')}")

                # Здесь можно добавить код для отображения напоминания в UI
                # Например, отправить уведомление или добавить сообщение в лог

                # Обновляем время последней проверки
                self.reminders[reminder_id]["last_check"] = current_time

        # Сохраняем обновленные напоминания
        self._save_reminders(self.reminders)

    def _check_auto_cleanup(self) -> None:
        """
        Проверяет необходимость автоматической очистки данных
        """
        # Загружаем настройки автоматической очистки
        auto_cleanup_config_file = os.path.join(self.error_dir, "cleanup_config.json")

        if os.path.exists(auto_cleanup_config_file):
            try:
                with open(auto_cleanup_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auto_cleanup_days = config.get("days", 90)
                    self.last_auto_cleanup = config.get("last_cleanup")
            except Exception as e:
                logger.error(f"Failed to load auto cleanup config: {str(e)}")

        current_time = time.time()
        cleanup_interval = 30 * 24 * 60 * 60  # 30 дней в секундах

        # Если очистка еще не выполнялась или прошло достаточно времени
        if self.last_auto_cleanup is None or (current_time - self.last_auto_cleanup > cleanup_interval):
            logger.info("Performing automatic cleanup of old errors")

            # Создаем резервную копию перед очисткой
            self.storage.create_backup()

            # Выполняем очистку
            cleaned_count = self.storage.clean_old_errors(days_threshold=self.auto_cleanup_days)

            # Обновляем время последней очистки
            self.last_auto_cleanup = current_time

            # Сохраняем конфигурацию
            try:
                with open(auto_cleanup_config_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "days": self.auto_cleanup_days,
                        "last_cleanup": self.last_auto_cleanup
                    }, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to save auto cleanup config: {str(e)}")

    def cleanup_errors(self, days: int = 90, backup: bool = True) -> int:
        """
        Очищает старые данные об ошибках

        Args:
            days: Количество дней, старше которого удаляются ошибки
            backup: Создавать резервную копию перед очисткой

        Returns:
            Количество удаленных ошибок
        """
        if backup:
            self.storage.create_backup()

        return self.storage.clean_old_errors(days_threshold=days)

    def create_backup(self) -> bool:
        """
        Создает резервную копию данных об ошибках

        Returns:
            True если резервная копия создана успешно
        """
        return self.storage.create_backup()

    def get_reminders(self) -> Dict[str, Any]:
        """
        Возвращает напоминания для пользователя

        Returns:
            Словарь с напоминаниями
        """
        return self.reminders
