"""
Модуль дерева мыслей для Reasoning Agent

Предоставляет возможность создания, хранения и навигации по дереву мыслей,
что позволяет агенту работать со сложными структурами рассуждений.
"""

from typing import Dict, Any, List, Optional, Set, Tuple, Union
import json
import time
import uuid

from app.logger import logger


class ThoughtNode:
    """
    Узел в дереве мыслей

    Представляет отдельную мысль или рассуждение с поддержкой иерархической
    структуры, альтернативных путей и метаданных.
    """

    def __init__(
        self,
        content: str,
        node_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        node_type: str = "thought",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует узел дерева мыслей

        Args:
            content: Текст мысли/рассуждения
            node_id: Уникальный идентификатор узла (если None, генерируется автоматически)
            parent_id: Идентификатор родительского узла (None для корневого узла)
            node_type: Тип узла ("thought", "question", "decision", "conclusion", и т.д.)
            metadata: Дополнительные метаданные для узла
        """
        self.content = content
        self.node_id = node_id if node_id else str(uuid.uuid4())
        self.parent_id = parent_id
        self.node_type = node_type
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.children: List[str] = []  # Список ID дочерних узлов
        self.alternatives: List[str] = []  # Список ID альтернативных узлов
        self.is_alternative = False  # Флаг, является ли узел альтернативным путем

    def add_child(self, child_id: str) -> None:
        """
        Добавляет дочерний узел

        Args:
            child_id: Идентификатор дочернего узла
        """
        if child_id not in self.children:
            self.children.append(child_id)

    def add_alternative(self, alternative_id: str) -> None:
        """
        Добавляет альтернативный узел

        Args:
            alternative_id: Идентификатор альтернативного узла
        """
        if alternative_id not in self.alternatives:
            self.alternatives.append(alternative_id)

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует узел в словарь для сериализации

        Returns:
            Словарь с данными узла
        """
        return {
            "node_id": self.node_id,
            "content": self.content,
            "parent_id": self.parent_id,
            "node_type": self.node_type,
            "created_at": self.created_at,
            "children": self.children,
            "alternatives": self.alternatives,
            "metadata": self.metadata,
            "is_alternative": self.is_alternative
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThoughtNode":
        """
        Создает узел из словаря

        Args:
            data: Словарь с данными узла

        Returns:
            Созданный узел
        """
        node = cls(
            content=data["content"],
            node_id=data["node_id"],
            parent_id=data["parent_id"],
            node_type=data["node_type"],
            metadata=data.get("metadata", {})
        )

        node.created_at = data.get("created_at", time.time())
        node.children = data.get("children", [])
        node.alternatives = data.get("alternatives", [])
        node.is_alternative = data.get("is_alternative", False)

        return node


class ThoughtTree:
    """
    Дерево мыслей для представления сложных рассуждений

    Обеспечивает структуру данных для хранения и навигации по иерархии
    рассуждений, включая альтернативные пути и ветвления.
    """

    def __init__(self, root_content: Optional[str] = None):
        """
        Инициализирует дерево мыслей

        Args:
            root_content: Содержимое корневого узла (при None создается пустой корень)
        """
        self.nodes: Dict[str, ThoughtNode] = {}

        # Создаем корневой узел
        if root_content:
            self.root = ThoughtNode(
                content=root_content,
                node_type="root"
            )
            self.nodes[self.root.node_id] = self.root
        else:
            self.root = None

        self.current_node_id: Optional[str] = self.root.node_id if self.root else None
        self.active_path: List[str] = [self.current_node_id] if self.current_node_id else []
        self.metadata: Dict[str, Any] = {}

        # Словарь обратных вызовов
        self.callbacks: Dict[str, callable] = {}

    def add_root_node(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Создает корневой узел дерева (синоним для create_root)

        Args:
            content: Содержимое корневого узла
            metadata: Дополнительные метаданные

        Returns:
            ID созданного корневого узла
        """
        return self.create_root(content, metadata)

    def create_root(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Создает корневой узел дерева

        Args:
            content: Содержимое корневого узла
            metadata: Дополнительные метаданные

        Returns:
            ID созданного корневого узла
        """
        if self.root:
            logger.warning("Root node already exists. Replacing it.")

        self.root = ThoughtNode(
            content=content,
            node_type="root",
            metadata=metadata
        )

        self.nodes[self.root.node_id] = self.root
        self.current_node_id = self.root.node_id
        self.active_path = [self.current_node_id]

        # Вызываем обратный вызов, если он установлен
        self._trigger_callback("on_node_added", self.root)

        return self.root.node_id

    def add_node(
        self,
        content: str,
        parent_id: Optional[str] = None,
        node_type: str = "thought",
        metadata: Optional[Dict[str, Any]] = None,
        is_alternative: bool = False
    ) -> str:
        """
        Добавляет новый узел в дерево (синоним для add_thought)

        Args:
            content: Содержимое узла
            parent_id: ID родительского узла (если None, используется текущий узел)
            node_type: Тип узла
            metadata: Дополнительные метаданные
            is_alternative: Добавить как альтернативу, а не как дочерний узел

        Returns:
            ID созданного узла
        """
        return self.add_thought(content, parent_id, node_type, metadata, is_alternative)

    def add_thought(
        self,
        content: str,
        parent_id: Optional[str] = None,
        node_type: str = "thought",
        metadata: Optional[Dict[str, Any]] = None,
        as_alternative: bool = False
    ) -> str:
        """
        Добавляет новую мысль в дерево

        Args:
            content: Содержимое мысли
            parent_id: ID родительского узла (если None, используется текущий узел)
            node_type: Тип узла
            metadata: Дополнительные метаданные
            as_alternative: Добавить как альтернативу, а не как дочерний узел

        Returns:
            ID созданного узла
        """
        # Проверяем наличие корневого узла
        if not self.root:
            return self.create_root(content, metadata)

        # Определяем родительский узел
        if parent_id is None:
            parent_id = self.current_node_id

        if parent_id not in self.nodes:
            logger.error(f"Parent node {parent_id} not found")
            return ""

        # Создаем новый узел
        new_node = ThoughtNode(
            content=content,
            parent_id=parent_id,
            node_type=node_type,
            metadata=metadata
        )

        # Устанавливаем флаг альтернативы
        new_node.is_alternative = as_alternative

        # Добавляем узел в дерево
        self.nodes[new_node.node_id] = new_node

        # Связываем с родительским узлом
        parent_node = self.nodes[parent_id]
        if as_alternative:
            parent_node.add_alternative(new_node.node_id)
        else:
            parent_node.add_child(new_node.node_id)

        # Обновляем текущий узел и активный путь
        self.current_node_id = new_node.node_id

        if not as_alternative:
            if parent_id in self.active_path:
                # Если родитель в активном пути, добавляем к нему
                index = self.active_path.index(parent_id)
                self.active_path = self.active_path[:index+1] + [new_node.node_id]
            else:
                # Иначе создаем новый активный путь
                self.active_path = [self.root.node_id]
                current = self.root.node_id

                # Строим путь от корня к новому узлу
                while current != new_node.node_id:
                    children = self.nodes[current].children
                    if not children:
                        break

                    # Находим ребенка, который ведет к новому узлу
                    for child_id in children:
                        if child_id == new_node.node_id or self._is_ancestor(child_id, new_node.node_id):
                            self.active_path.append(child_id)
                            current = child_id
                            break
                    else:
                        break

        # Вызываем обратный вызов, если он установлен
        self._trigger_callback("on_node_added", new_node)

        return new_node.node_id

    def set_callback(self, event_name: str, callback: callable) -> None:
        """
        Устанавливает функцию обратного вызова для события

        Args:
            event_name: Название события ('on_node_added', 'on_navigate', и т.д.)
            callback: Функция, которая будет вызвана при наступлении события
        """
        self.callbacks[event_name] = callback

    def _trigger_callback(self, event_name: str, *args, **kwargs) -> None:
        """
        Вызывает функцию обратного вызова для события

        Args:
            event_name: Название события
            *args, **kwargs: Аргументы для передачи в функцию
        """
        callback = self.callbacks.get(event_name)
        if callback:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in callback {event_name}: {str(e)}")

    def _is_ancestor(self, potential_ancestor_id: str, node_id: str) -> bool:
        """
        Проверяет, является ли один узел предком другого

        Args:
            potential_ancestor_id: ID потенциального предка
            node_id: ID проверяемого узла

        Returns:
            True, если potential_ancestor_id является предком node_id
        """
        if node_id not in self.nodes:
            return False

        current = self.nodes[node_id]
        while current.parent_id:
            if current.parent_id == potential_ancestor_id:
                return True
            current = self.nodes[current.parent_id]

        return False

    def get_node(self, node_id: str) -> Optional[ThoughtNode]:
        """
        Получает узел по ID

        Args:
            node_id: ID узла

        Returns:
            Узел или None, если не найден
        """
        return self.nodes.get(node_id)

    def get_current_node(self) -> Optional[ThoughtNode]:
        """
        Получает текущий активный узел

        Returns:
            Текущий узел или None
        """
        if not self.current_node_id:
            return None
        return self.nodes.get(self.current_node_id)

    def navigate_to(self, node_id: str) -> bool:
        """
        Переходит к указанному узлу

        Args:
            node_id: ID целевого узла

        Returns:
            True в случае успеха, False если узел не найден
        """
        if node_id not in self.nodes:
            return False

        self.current_node_id = node_id

        # Обновляем активный путь
        if node_id == self.root.node_id:
            self.active_path = [node_id]
        elif self._is_in_active_path(node_id):
            # Если узел уже в активном пути, усекаем путь
            index = self.active_path.index(node_id)
            self.active_path = self.active_path[:index+1]
        else:
            # Создаем новый путь от корня к текущему узлу
            path = self._find_path_to_node(node_id)
            if path:
                self.active_path = path

        # Вызываем обратный вызов, если он установлен
        node = self.nodes.get(node_id)
        if node:
            self._trigger_callback("on_navigate", node)

        return True

    def _is_in_active_path(self, node_id: str) -> bool:
        """
        Проверяет, находится ли узел в активном пути

        Args:
            node_id: ID проверяемого узла

        Returns:
            True, если узел в активном пути
        """
        return node_id in self.active_path

    def _find_path_to_node(self, node_id: str) -> List[str]:
        """
        Находит путь от корня к указанному узлу

        Args:
            node_id: ID целевого узла

        Returns:
            Список ID узлов, образующих путь от корня к целевому узлу
        """
        if node_id not in self.nodes:
            return []

        path = []
        current = node_id

        # Идем от узла к корню, собирая путь
        while current:
            path.append(current)
            node = self.nodes.get(current)
            if not node or not node.parent_id:
                break
            current = node.parent_id

        # Разворачиваем путь, чтобы он шел от корня к узлу
        return list(reversed(path))

    def get_children(self, node_id: Optional[str] = None) -> List[ThoughtNode]:
        """
        Получает дочерние узлы указанного узла

        Args:
            node_id: ID родительского узла (если None, используется текущий узел)

        Returns:
            Список дочерних узлов
        """
        if node_id is None:
            node_id = self.current_node_id

        if not node_id or node_id not in self.nodes:
            return []

        node = self.nodes[node_id]
        return [self.nodes[child_id] for child_id in node.children if child_id in self.nodes]

    def get_alternatives(self, node_id: Optional[str] = None) -> List[ThoughtNode]:
        """
        Получает альтернативные узлы для указанного узла

        Args:
            node_id: ID узла (если None, используется текущий узел)

        Returns:
            Список альтернативных узлов
        """
        if node_id is None:
            node_id = self.current_node_id

        if not node_id or node_id not in self.nodes:
            return []

        node = self.nodes[node_id]
        return [self.nodes[alt_id] for alt_id in node.alternatives if alt_id in self.nodes]

    def get_active_path(self) -> List[ThoughtNode]:
        """
        Получает текущий активный путь в дереве

        Returns:
            Список узлов в активном пути
        """
        return [self.nodes[node_id] for node_id in self.active_path if node_id in self.nodes]

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует дерево в словарь для сериализации

        Returns:
            Словарь с данными дерева
        """
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "root_id": self.root.node_id if self.root else None,
            "current_node_id": self.current_node_id,
            "active_path": self.active_path,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThoughtTree":
        """
        Создает дерево из словаря

        Args:
            data: Словарь с данными дерева

        Returns:
            Созданное дерево
        """
        tree = cls()

        # Загружаем узлы
        tree.nodes = {
            node_id: ThoughtNode.from_dict(node_data)
            for node_id, node_data in data.get("nodes", {}).items()
        }

        # Устанавливаем корневой узел
        root_id = data.get("root_id")
        if root_id and root_id in tree.nodes:
            tree.root = tree.nodes[root_id]

        # Устанавливаем текущий узел и активный путь
        tree.current_node_id = data.get("current_node_id")
        tree.active_path = data.get("active_path", [])
        tree.metadata = data.get("metadata", {})

        return tree

    def to_json(self) -> str:
        """
        Сериализует дерево в JSON

        Returns:
            JSON-строка с данными дерева
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "ThoughtTree":
        """
        Создает дерево из JSON-строки

        Args:
            json_str: JSON-строка с данными дерева

        Returns:
            Созданное дерево
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_visual_representation(self, max_depth: int = -1, include_alternatives: bool = True) -> str:
        """
        Создает текстовое визуальное представление дерева

        Args:
            max_depth: Максимальная глубина визуализации (-1 для неограниченной)
            include_alternatives: Включать ли альтернативные узлы

        Returns:
            Строка с визуализацией дерева
        """
        if not self.root:
            return "Empty tree"

        lines = []

        def _add_node(node_id: str, depth: int, prefix: str = "", is_alternative: bool = False):
            if max_depth >= 0 and depth > max_depth:
                return

            if node_id not in self.nodes:
                return

            node = self.nodes[node_id]

            # Маркер для текущего узла
            current_marker = " *" if node_id == self.current_node_id else ""

            # Маркер для типа узла
            type_marker = f"[{node.node_type}]" if node.node_type != "thought" else ""

            # Маркер для альтернативы
            alt_marker = " (alt)" if is_alternative else ""

            # Сокращаем содержимое, если оно слишком длинное
            content = node.content[:80] + "..." if len(node.content) > 80 else node.content
            content = content.replace("\n", " ")

            # Добавляем строку узла
            lines.append(f"{prefix}{content}{current_marker}{alt_marker} {type_marker}")

            # Рассчитываем префикс для дочерних узлов
            child_prefix = prefix + "  "

            # Добавляем дочерние узлы
            for i, child_id in enumerate(node.children):
                _add_node(child_id, depth + 1, child_prefix)

            # Добавляем альтернативные узлы, если требуется
            if include_alternatives:
                for alt_id in node.alternatives:
                    _add_node(alt_id, depth + 1, child_prefix, True)

        # Начинаем с корневого узла
        _add_node(self.root.node_id, 0)

        return "\n".join(lines)
