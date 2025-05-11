"""
Стратегии исследования файловой системы для GopiAI Reasoning Agent

Реализует стратегии для сбора и анализа информации из файловой системы.
"""

import asyncio
import time
import os
import re
from typing import Dict, Any, List, Optional, Union, Set, Tuple

from app.agent.exploration_strategy import (
    ExplorationStrategy, InformationSource, InformationItem,
    InformationCollection, ExplorationPhase
)
from app.agent.file_system_access import FileSystemAccess
from app.agent.text_editor_access import TextEditorAccess
from app.agent.thought_tree import ThoughtTree
from app.logger import logger


class FileExplorationStrategy(ExplorationStrategy):
    """
    Стратегия для исследования и сбора информации из файловой системы.

    Включает поиск, чтение и анализ файлов различных типов.
    """

    def __init__(
        self,
        file_system: FileSystemAccess,
        text_editor: Optional[TextEditorAccess] = None,
        thought_tree: Optional[ThoughtTree] = None,
        max_files: int = 20,
        max_file_size: int = 1024 * 1024,  # 1 MB
        default_extensions: Optional[List[str]] = None,
        search_timeout: float = 30.0
    ):
        """
        Инициализирует стратегию исследования файловой системы.

        Args:
            file_system: Модуль доступа к файловой системе (обязательный)
            text_editor: Модуль доступа к текстовому редактору
            thought_tree: Дерево мыслей для интеграции
            max_files: Максимальное количество файлов для обработки
            max_file_size: Максимальный размер файла (в байтах)
            default_extensions: Список расширений файлов по умолчанию для поиска
            search_timeout: Таймаут для поиска (в секундах)
        """
        super().__init__(
            name="file_exploration",
            description="Стратегия для исследования файловой системы",
            file_system=file_system,
            text_editor=text_editor,
            thought_tree=thought_tree
        )

        # Проверяем наличие обязательного компонента
        if not file_system:
            raise ValueError("FileExplorationStrategy requires file_system")

        self.max_files = max_files
        self.max_file_size = max_file_size
        self.search_timeout = search_timeout

        # Список расширений по умолчанию
        self.default_extensions = default_extensions or [
            ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv"
        ]

        # Настройки для специальных типов файлов
        self.binary_extensions = [
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip",
            ".tar", ".gz", ".rar", ".jpg", ".jpeg", ".png", ".gif"
        ]

        # Директории, которые следует игнорировать
        self.ignored_dirs = [
            ".git", ".svn", "node_modules", "venv", "__pycache__",
            "build", "dist", ".vscode", ".idea"
        ]

    async def explore(self, query: str, **kwargs) -> InformationCollection:
        """
        Выполняет исследование файловой системы на основе запроса.

        Args:
            query: Текст запроса для исследования
            **kwargs: Дополнительные параметры
                - extensions: Список расширений для поиска
                - directory: Директория для поиска (относительно корня)
                - max_files: Переопределение максимального количества файлов
                - include_binary: Флаг для включения бинарных файлов
                - recursive: Флаг для рекурсивного поиска
                - pattern: Регулярное выражение для поиска содержимого
                - max_depth: Максимальная глубина для рекурсивного поиска

        Returns:
            Коллекция собранной информации
        """
        start_time = time.time()

        # Обновляем параметры из kwargs, если они заданы
        extensions = kwargs.get("extensions", self.default_extensions)
        directory = kwargs.get("directory", ".")
        max_files = kwargs.get("max_files", self.max_files)
        include_binary = kwargs.get("include_binary", False)
        recursive = kwargs.get("recursive", True)
        pattern = kwargs.get("pattern", None)
        max_depth = kwargs.get("max_depth", 5)

        # Создаем новую коллекцию для результатов
        collection_name = f"file_exploration_{int(time.time())}"
        collection = InformationCollection(name=collection_name)

        # Добавляем информацию о запросе в дерево мыслей
        root_thought_id = self.add_to_thought_tree(
            content=f"Начинаем исследование файловой системы для запроса: '{query}'",
            node_type=f"exploration_{ExplorationPhase.INITIAL_QUERY.value}"
        )

        # Этап 1: Поиск файлов
        discovery_thought_id = self.add_to_thought_tree(
            content=f"Поиск файлов в директории '{directory}' с расширениями {extensions}",
            node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
            parent_id=root_thought_id
        )

        try:
            # Формируем полный список расширений для поиска
            if include_binary:
                all_extensions = extensions + [ext for ext in self.binary_extensions if ext not in extensions]
            else:
                all_extensions = extensions

            # Начинаем поиск файлов
            found_files = await self._find_files(
                directory=directory,
                extensions=all_extensions,
                recursive=recursive,
                max_depth=max_depth
            )

            # Добавляем информацию о найденных файлах в дерево мыслей
            self.add_to_thought_tree(
                content=f"Найдено {len(found_files)} файлов",
                node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
                parent_id=discovery_thought_id
            )

            # Если есть шаблон для поиска, применяем его
            filtered_files = found_files
            if pattern:
                pattern_thought_id = self.add_to_thought_tree(
                    content=f"Фильтрация файлов по шаблону: '{pattern}'",
                    node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
                    parent_id=discovery_thought_id
                )

                # Ищем файлы с заданным шаблоном
                filtered_files = await self._find_files_with_pattern(
                    files=found_files,
                    pattern=pattern,
                    max_files=max_files
                )

                self.add_to_thought_tree(
                    content=f"После фильтрации осталось {len(filtered_files)} файлов",
                    node_type=f"exploration_{ExplorationPhase.RESOURCE_DISCOVERY.value}",
                    parent_id=pattern_thought_id
                )

            # Этап 2: Чтение и анализ содержимого файлов
            collection_thought_id = self.add_to_thought_tree(
                content="Начинаем сбор информации из найденных файлов",
                node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                parent_id=root_thought_id
            )

            # Ограничиваем количество файлов
            if len(filtered_files) > max_files:
                filtered_files = filtered_files[:max_files]

            # Читаем содержимое файлов
            for file_path in filtered_files:
                # Проверяем размер файла
                file_info = await self.file_system.get_file_information(file_path)

                if not file_info.get("success", False):
                    logger.warning(f"Failed to get information for file {file_path}: {file_info.get('error', 'Unknown error')}")
                    continue

                file_size = file_info.get("size", 0)

                if file_size > self.max_file_size:
                    logger.info(f"Skipping file {file_path} due to size limit ({file_size} bytes)")
                    continue

                # Добавляем информацию о файле в дерево мыслей
                file_thought_id = self.add_to_thought_tree(
                    content=f"Анализ файла: {file_path}",
                    node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                    parent_id=collection_thought_id
                )

                # Получаем расширение файла
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()

                # Для текстовых файлов - читаем содержимое
                if ext not in self.binary_extensions:
                    # Читаем текстовый файл
                    content_result = await self.file_system.read_file_content(
                        file_path=file_path,
                        mode="text"
                    )

                    if not content_result.get("success", False):
                        logger.warning(f"Failed to read file {file_path}: {content_result.get('error', 'Unknown error')}")
                        continue

                    content = content_result.get("content", "")

                    # Добавляем информацию в коллекцию
                    if content:
                        item = InformationItem(
                            content=content,
                            source=InformationSource.FILES,
                            source_details={
                                "file_path": file_path,
                                "extension": ext,
                                "size": file_size,
                                "query": query
                            },
                            # Оценки будут обновлены при обработке
                            relevance_score=0.5,
                            confidence_score=0.8,
                            tags=["file", ext.replace(".", "")]
                        )

                        collection.add_item(item)

                        # Добавляем информацию о содержимом в дерево мыслей
                        content_summary = content[:200] + "..." if len(content) > 200 else content
                        self.add_to_thought_tree(
                            content=f"Собрана информация из файла: {content_summary}",
                            node_type=f"exploration_{ExplorationPhase.DATA_COLLECTION.value}",
                            parent_id=file_thought_id
                        )
                else:
                    # Для бинарных файлов - добавляем только информацию о файле
                    if include_binary:
                        item = InformationItem(
                            content=f"Binary file: {file_path}",
                            source=InformationSource.FILES,
                            source_details={
                                "file_path": file_path,
                                "extension": ext,
                                "size": file_size,
                                "binary": True,
                                "query": query
                            },
                            relevance_score=0.3,
                            confidence_score=0.7,
                            tags=["binary_file", ext.replace(".", "")]
                        )

                        collection.add_item(item)

            # Этап 3: Анализ собранной информации
            analysis_thought_id = self.add_to_thought_tree(
                content=f"Анализ собранной информации ({len(collection.items)} элементов)",
                node_type=f"exploration_{ExplorationPhase.DATA_ANALYSIS.value}",
                parent_id=root_thought_id
            )

            # Выполняем обработку результатов
            processed_results = await self.process_results(collection)

            # Добавляем информацию о результатах в дерево мыслей
            self.add_to_thought_tree(
                content=f"Результаты анализа: найдено {processed_results.get('relevant_items', 0)} релевантных элементов",
                node_type=f"exploration_{ExplorationPhase.INFORMATION_SYNTHESIS.value}",
                parent_id=analysis_thought_id
            )

            # Записываем успешное выполнение
            self._record_execution(
                query=query,
                result=processed_results,
                execution_time=time.time() - start_time,
                success=True
            )

            return collection

        except Exception as e:
            logger.error(f"Error during file exploration: {str(e)}")

            # Записываем ошибку в дерево мыслей
            self.add_to_thought_tree(
                content=f"Ошибка при исследовании: {str(e)}",
                node_type="exploration_error",
                parent_id=root_thought_id
            )

            # Записываем выполнение с ошибкой
            self._record_execution(
                query=query,
                result={"items_collected": len(collection.items), "error": str(e)},
                execution_time=time.time() - start_time,
                success=False
            )

            return collection

    async def process_results(self, collection: InformationCollection, **kwargs) -> Dict[str, Any]:
        """
        Обрабатывает результаты исследования.

        Args:
            collection: Коллекция с собранной информацией
            **kwargs: Дополнительные параметры для обработки
                - min_relevance: Минимальная оценка релевантности для фильтрации
                - min_confidence: Минимальная оценка достоверности для фильтрации
                - group_by_extension: Группировать результаты по расширению файла

        Returns:
            Словарь с обработанными результатами
        """
        min_relevance = kwargs.get("min_relevance", 0.3)
        min_confidence = kwargs.get("min_confidence", 0.4)
        group_by_extension = kwargs.get("group_by_extension", True)

        # Обновляем оценки релевантности и достоверности
        for item in collection.items.values():
            # Оценка релевантности на основе простого анализа
            item.update_scores(
                relevance=self._estimate_relevance(item),
                confidence=self._estimate_confidence(item)
            )

        # Фильтруем элементы по оценкам
        relevant_items = collection.filter_by_relevance(min_relevance)
        confident_items = collection.filter_by_confidence(min_confidence)

        # Элементы, которые одновременно релевантны и достоверны
        good_items = [
            item for item in relevant_items
            if item.confidence_score >= min_confidence
        ]

        # Группируем по расширению файла, если нужно
        extensions_stats = {}
        if group_by_extension:
            for item in collection.items.values():
                ext = item.source_details.get("extension", "").replace(".", "")
                if ext:
                    extensions_stats[ext] = extensions_stats.get(ext, 0) + 1

        # Суммаризируем результаты
        summary = collection.get_summary()

        result = {
            "items_collected": len(collection.items),
            "relevant_items": len(relevant_items),
            "confident_items": len(confident_items),
            "good_items": len(good_items),
            "sources": summary["sources"],
            "avg_relevance": summary["avg_relevance"],
            "avg_confidence": summary["avg_confidence"]
        }

        if group_by_extension:
            result["extensions"] = extensions_stats

        return result

    async def _find_files(
        self,
        directory: str,
        extensions: List[str],
        recursive: bool = True,
        max_depth: int = 5
    ) -> List[str]:
        """
        Находит файлы с заданными расширениями.

        Args:
            directory: Директория для поиска
            extensions: Список расширений для поиска
            recursive: Флаг для рекурсивного поиска
            max_depth: Максимальная глубина для рекурсивного поиска

        Returns:
            Список путей к найденным файлам
        """
        result = []
        curr_depth = 0

        async def _search_dir(dir_path: str, depth: int):
            nonlocal result

            # Проверяем ограничение глубины
            if depth > max_depth:
                return

            try:
                # Получаем содержимое директории
                dir_result = await self.file_system.list_directory_contents(dir_path)

                if not dir_result.get("success", False):
                    logger.warning(f"Failed to list directory {dir_path}: {dir_result.get('error', 'Unknown error')}")
                    return

                # Обрабатываем файлы
                for item in dir_result.get("items", []):
                    if item["type"] == "file":
                        # Проверяем расширение
                        _, ext = os.path.splitext(item["name"])
                        if ext.lower() in extensions:
                            # Формируем полный путь
                            file_path = os.path.join(dir_path, item["name"])
                            result.append(file_path)

                    # Рекурсивно обрабатываем поддиректории
                    elif recursive and item["type"] == "directory":
                        # Пропускаем игнорируемые директории
                        if item["name"] in self.ignored_dirs:
                            continue

                        # Рекурсивный поиск
                        subdir_path = os.path.join(dir_path, item["name"])
                        await _search_dir(subdir_path, depth + 1)

            except Exception as e:
                logger.error(f"Error searching directory {dir_path}: {str(e)}")

        # Начинаем поиск
        await _search_dir(directory, curr_depth)

        return result

    async def _find_files_with_pattern(
        self,
        files: List[str],
        pattern: str,
        max_files: int = 20
    ) -> List[str]:
        """
        Находит файлы, содержимое которых соответствует шаблону.

        Args:
            files: Список путей к файлам для проверки
            pattern: Регулярное выражение для поиска
            max_files: Максимальное количество файлов для возврата

        Returns:
            Список путей к найденным файлам
        """
        result = []

        try:
            # Компилируем регулярное выражение
            regex = re.compile(pattern)

            # Проверяем каждый файл
            for file_path in files:
                # Пропускаем бинарные файлы
                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.binary_extensions:
                    continue

                # Читаем содержимое файла
                content_result = await self.file_system.read_file_content(
                    file_path=file_path,
                    mode="text"
                )

                if not content_result.get("success", False):
                    continue

                content = content_result.get("content", "")

                # Проверяем наличие шаблона
                if content and regex.search(content):
                    result.append(file_path)

                    # Проверяем ограничение
                    if len(result) >= max_files:
                        break

        except Exception as e:
            logger.error(f"Error searching files with pattern: {str(e)}")

        return result

    def _estimate_relevance(self, item: InformationItem) -> float:
        """
        Оценивает релевантность элемента информации.

        Args:
            item: Элемент для оценки

        Returns:
            Оценка релевантности (0.0 - 1.0)
        """
        # Базовая оценка
        score = 0.5

        # Анализ типа файла
        file_ext = item.source_details.get("extension", "").lower()

        # Более высокая оценка для некоторых типов файлов
        if file_ext in [".md", ".txt", ".py", ".js", ".html", ".css", ".json"]:
            score += 0.1

        # Более низкая оценка для бинарных файлов
        if item.source_details.get("binary", False):
            score -= 0.2

        # Анализ содержимого
        content = item.content
        content_length = len(content)

        # Более длинное содержимое может быть более информативным
        if not item.source_details.get("binary", False):
            if content_length > 1000:
                score += 0.1
            elif content_length < 50:
                score -= 0.1

        # Ограничиваем значение от 0.0 до 1.0
        return max(0.0, min(1.0, score))

    def _estimate_confidence(self, item: InformationItem) -> float:
        """
        Оценивает достоверность элемента информации.

        Args:
            item: Элемент для оценки

        Returns:
            Оценка достоверности (0.0 - 1.0)
        """
        # Файлы обычно имеют высокую достоверность, так как они локальные
        score = 0.8

        # Более низкая достоверность для бинарных файлов
        if item.source_details.get("binary", False):
            score -= 0.1

        # Учитываем размер файла
        file_size = item.source_details.get("size", 0)
        if file_size == 0:
            score -= 0.2  # Пустой файл
        elif file_size > 1024 * 1024:
            score -= 0.1  # Очень большой файл

        # Ограничиваем значение от 0.0 до 1.0
        return max(0.0, min(1.0, score))
