"""
Тестирование модуля дерева мыслей (ThoughtTree)

Проверяет работу дерева мыслей, включая создание узлов,
навигацию, альтернативные пути и сериализацию.
"""

import os
import sys
import json
import tempfile
from typing import Dict, Any, List, Optional

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.thought_tree import ThoughtTree, ThoughtNode


class ThoughtTreeTester:
    """Класс для тестирования дерева мыслей"""

    def __init__(self):
        """Инициализирует тестовый класс"""
        self.thought_tree = None
        self.test_results = []

    def setup(self):
        """Настраивает тестовое окружение"""
        print("\n=== Setting up ThoughtTree test environment ===")

        try:
            # Создаем дерево мыслей
            self.thought_tree = ThoughtTree("Root thought for testing")

            print("Setup completed successfully")
            return True
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return False

    def test_create_root(self):
        """Тестирует создание корневого узла"""
        print("\n=== Testing root node creation ===")

        # Проверяем, что корневой узел создан
        has_root = self.thought_tree.root is not None
        correct_content = self.thought_tree.root.content == "Root thought for testing" if has_root else False
        correct_type = self.thought_tree.root.node_type == "root" if has_root else False

        self.test_results.append(("Root node creation", has_root))
        self.test_results.append(("Root node content", correct_content))
        self.test_results.append(("Root node type", correct_type))

        print(f"Has root: {has_root}")
        print(f"Correct content: {correct_content}")
        print(f"Correct type: {correct_type}")

    def test_add_thoughts(self):
        """Тестирует добавление мыслей"""
        print("\n=== Testing adding thoughts ===")

        # Добавляем мысли
        thought1_id = self.thought_tree.add_thought("First child thought", node_type="step")
        thought2_id = self.thought_tree.add_thought("Second child thought", node_type="decision")

        # Добавляем мысль к первой мысли
        thought3_id = self.thought_tree.add_thought("Child of first thought", parent_id=thought1_id)

        # Добавляем альтернативу ко второй мысли
        alt_thought_id = self.thought_tree.add_thought(
            "Alternative to second thought",
            parent_id=thought2_id,
            as_alternative=True
        )

        # Проверяем результаты
        has_thought1 = thought1_id in self.thought_tree.nodes
        has_thought2 = thought2_id in self.thought_tree.nodes
        has_thought3 = thought3_id in self.thought_tree.nodes
        has_alt_thought = alt_thought_id in self.thought_tree.nodes

        correct_parent1 = self.thought_tree.nodes[thought1_id].parent_id == self.thought_tree.root.node_id if has_thought1 else False
        correct_parent3 = self.thought_tree.nodes[thought3_id].parent_id == thought1_id if has_thought3 else False

        is_alternative = alt_thought_id in self.thought_tree.nodes[thought2_id].alternatives if has_alt_thought and has_thought2 else False

        thought_count = len(self.thought_tree.nodes)
        expected_count = 5  # Корень + 4 добавленных мысли

        self.test_results.append(("Add first thought", has_thought1))
        self.test_results.append(("Add second thought", has_thought2))
        self.test_results.append(("Add child thought", has_thought3))
        self.test_results.append(("Add alternative thought", has_alt_thought))
        self.test_results.append(("Correct parent for first thought", correct_parent1))
        self.test_results.append(("Correct parent for child thought", correct_parent3))
        self.test_results.append(("Alternative properly linked", is_alternative))
        self.test_results.append(("Correct thought count", thought_count == expected_count))

        print(f"Has first thought: {has_thought1}")
        print(f"Has second thought: {has_thought2}")
        print(f"Has child thought: {has_thought3}")
        print(f"Has alternative thought: {has_alt_thought}")
        print(f"Correct parent for first thought: {correct_parent1}")
        print(f"Correct parent for child thought: {correct_parent3}")
        print(f"Alternative properly linked: {is_alternative}")
        print(f"Thought count: {thought_count} (expected: {expected_count})")

    def test_navigation(self):
        """Тестирует навигацию по дереву мыслей"""
        print("\n=== Testing navigation ===")

        # Сохраняем текущий узел
        original_node_id = self.thought_tree.current_node_id

        # Добавляем мысли для навигации (если еще не добавлены)
        if len(self.thought_tree.nodes) <= 1:
            thought1_id = self.thought_tree.add_thought("Navigation test thought 1")
            thought2_id = self.thought_tree.add_thought("Navigation test thought 2", parent_id=thought1_id)
        else:
            # Берем существующие узлы для тестирования
            root_id = self.thought_tree.root.node_id
            children = self.thought_tree.get_children(root_id)
            thought1_id = children[0].node_id if children else None

            if thought1_id:
                children = self.thought_tree.get_children(thought1_id)
                thought2_id = children[0].node_id if children else None
            else:
                thought2_id = None

        # Переходим к корню
        nav_to_root = self.thought_tree.navigate_to(self.thought_tree.root.node_id)
        current_is_root = self.thought_tree.current_node_id == self.thought_tree.root.node_id if nav_to_root else False

        # Переходим к первой мысли (если она есть)
        nav_to_thought1 = False
        current_is_thought1 = False
        if thought1_id:
            nav_to_thought1 = self.thought_tree.navigate_to(thought1_id)
            current_is_thought1 = self.thought_tree.current_node_id == thought1_id if nav_to_thought1 else False

        # Переходим к несуществующему узлу
        nav_to_nonexistent = self.thought_tree.navigate_to("nonexistent_id")

        # Получаем активный путь
        active_path = self.thought_tree.get_active_path()
        path_has_current = any(node.node_id == self.thought_tree.current_node_id for node in active_path)

        self.test_results.append(("Navigate to root", nav_to_root))
        self.test_results.append(("Current is root after navigation", current_is_root))
        if thought1_id:
            self.test_results.append(("Navigate to thought", nav_to_thought1))
            self.test_results.append(("Current is thought after navigation", current_is_thought1))
        self.test_results.append(("Navigate to nonexistent fails", not nav_to_nonexistent))
        self.test_results.append(("Active path contains current", path_has_current))

        print(f"Navigate to root: {nav_to_root}")
        print(f"Current is root after navigation: {current_is_root}")
        if thought1_id:
            print(f"Navigate to thought: {nav_to_thought1}")
            print(f"Current is thought after navigation: {current_is_thought1}")
        print(f"Navigate to nonexistent fails: {not nav_to_nonexistent}")
        print(f"Active path contains current: {path_has_current}")
        print(f"Active path length: {len(active_path)}")

    def test_get_children_and_alternatives(self):
        """Тестирует получение дочерних и альтернативных узлов"""
        print("\n=== Testing getting children and alternatives ===")

        # Сбрасываем дерево для чистоты теста
        self.thought_tree = ThoughtTree("Root for children test")

        # Добавляем структуру для тестирования
        thought1_id = self.thought_tree.add_thought("Child 1")
        thought2_id = self.thought_tree.add_thought("Child 2")
        alt1_id = self.thought_tree.add_thought("Alternative 1", parent_id=thought1_id, as_alternative=True)
        alt2_id = self.thought_tree.add_thought("Alternative 2", parent_id=thought1_id, as_alternative=True)
        thought3_id = self.thought_tree.add_thought("Child of Child 1", parent_id=thought1_id)

        # Получаем дочерние узлы корня
        root_children = self.thought_tree.get_children(self.thought_tree.root.node_id)
        root_children_count = len(root_children)
        expected_root_children = 2

        # Получаем дочерние узлы первой мысли
        thought1_children = self.thought_tree.get_children(thought1_id)
        thought1_children_count = len(thought1_children)
        expected_thought1_children = 1

        # Получаем альтернативы первой мысли
        thought1_alternatives = self.thought_tree.get_alternatives(thought1_id)
        thought1_alt_count = len(thought1_alternatives)
        expected_thought1_alt = 2

        # Проверяем, что у второй мысли нет дочерних узлов и альтернатив
        thought2_children = self.thought_tree.get_children(thought2_id)
        thought2_alternatives = self.thought_tree.get_alternatives(thought2_id)

        self.test_results.append(("Root has correct number of children", root_children_count == expected_root_children))
        self.test_results.append(("Thought 1 has correct number of children", thought1_children_count == expected_thought1_children))
        self.test_results.append(("Thought 1 has correct number of alternatives", thought1_alt_count == expected_thought1_alt))
        self.test_results.append(("Thought 2 has no children", len(thought2_children) == 0))
        self.test_results.append(("Thought 2 has no alternatives", len(thought2_alternatives) == 0))

        print(f"Root has {root_children_count} children (expected: {expected_root_children})")
        print(f"Thought 1 has {thought1_children_count} children (expected: {expected_thought1_children})")
        print(f"Thought 1 has {thought1_alt_count} alternatives (expected: {expected_thought1_alt})")
        print(f"Thought 2 has {len(thought2_children)} children (expected: 0)")
        print(f"Thought 2 has {len(thought2_alternatives)} alternatives (expected: 0)")

    def test_serialization(self):
        """Тестирует сериализацию и десериализацию дерева мыслей"""
        print("\n=== Testing serialization ===")

        # Создаем новое дерево с метаданными
        tree = ThoughtTree("Serialization test root")
        tree.metadata = {"test_key": "test_value"}

        # Добавляем узлы с метаданными
        thought1_id = tree.add_thought(
            "Thought with metadata",
            metadata={"importance": "high", "tags": ["test", "serialization"]}
        )

        thought2_id = tree.add_thought("Another thought")
        alt_id = tree.add_thought("Alternative thought", parent_id=thought1_id, as_alternative=True)

        # Сериализуем в словарь
        tree_dict = tree.to_dict()

        # Создаем новое дерево из словаря
        new_tree = ThoughtTree.from_dict(tree_dict)

        # Проверяем, что деревья эквивалентны
        same_root_content = new_tree.root.content == tree.root.content
        same_node_count = len(new_tree.nodes) == len(tree.nodes)
        same_metadata = new_tree.metadata == tree.metadata
        thought1_preserved = thought1_id in new_tree.nodes
        metadata_preserved = new_tree.nodes[thought1_id].metadata.get("importance") == "high" if thought1_preserved else False

        # Тестируем JSON сериализацию
        tree_json = tree.to_json()
        json_tree = ThoughtTree.from_json(tree_json)

        json_serialization_works = len(json_tree.nodes) == len(tree.nodes)

        self.test_results.append(("Dict serialization - root content preserved", same_root_content))
        self.test_results.append(("Dict serialization - node count preserved", same_node_count))
        self.test_results.append(("Dict serialization - metadata preserved", same_metadata))
        self.test_results.append(("Dict serialization - thought node preserved", thought1_preserved))
        self.test_results.append(("Dict serialization - thought metadata preserved", metadata_preserved))
        self.test_results.append(("JSON serialization works", json_serialization_works))

        print(f"Root content preserved: {same_root_content}")
        print(f"Node count preserved: {same_node_count}")
        print(f"Metadata preserved: {same_metadata}")
        print(f"Thought node preserved: {thought1_preserved}")
        print(f"Thought metadata preserved: {metadata_preserved}")
        print(f"JSON serialization works: {json_serialization_works}")

    def test_file_serialization(self):
        """Тестирует сохранение и загрузку дерева мыслей в/из файла"""
        print("\n=== Testing file serialization ===")

        # Создаем тестовое дерево
        tree = ThoughtTree("File serialization test")
        tree.add_thought("Thought 1 for file test")
        tree.add_thought("Thought 2 for file test")

        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
            try:
                # Сохраняем дерево в файл
                temp_file.write(tree.to_json())
                temp_file.flush()

                # Создаем новое дерево и загружаем из файла
                new_tree = ThoughtTree()

                # Закрываем файл и загружаем его
                temp_file.close()

                with open(temp_path, 'r') as f:
                    json_data = f.read()

                new_tree = ThoughtTree.from_json(json_data)

                # Проверяем, что деревья эквивалентны
                same_root_content = new_tree.root.content == tree.root.content
                same_node_count = len(new_tree.nodes) == len(tree.nodes)

                self.test_results.append(("File serialization - root content preserved", same_root_content))
                self.test_results.append(("File serialization - node count preserved", same_node_count))

                print(f"Root content preserved: {same_root_content}")
                print(f"Node count preserved: {same_node_count}")

            finally:
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    def test_visualization(self):
        """Тестирует визуальное представление дерева"""
        print("\n=== Testing visualization ===")

        # Создаем дерево с несколькими уровнями
        tree = ThoughtTree("Visualization root")
        thought1_id = tree.add_thought("Level 1 - Thought 1")
        thought2_id = tree.add_thought("Level 1 - Thought 2")

        tree.add_thought("Level 2 - Child of Thought 1", parent_id=thought1_id)

        child2 = tree.add_thought("Level 2 - Child of Thought 2", parent_id=thought2_id)
        tree.add_thought("Level 3 - Grandchild", parent_id=child2)

        tree.add_thought("Level 1 - Alternative", parent_id=tree.root.node_id, as_alternative=True)

        # Получаем визуализацию
        visual_full = tree.get_visual_representation()
        visual_depth_1 = tree.get_visual_representation(max_depth=1)
        visual_no_alt = tree.get_visual_representation(include_alternatives=False)

        # Проверяем результаты
        has_visual = len(visual_full) > 0
        depth_1_shorter = len(visual_depth_1) < len(visual_full)
        no_alt_different = visual_no_alt != visual_full

        self.test_results.append(("Visualization generated", has_visual))
        self.test_results.append(("Depth-limited visualization shorter", depth_1_shorter))
        self.test_results.append(("No-alternatives visualization different", no_alt_different))

        print(f"Visualization generated: {has_visual}")
        print(f"Depth-limited visualization shorter: {depth_1_shorter}")
        print(f"No-alternatives visualization different: {no_alt_different}")

        if has_visual:
            print("\nSample visualization (first 3 lines):")
            lines = visual_full.split("\n")
            for i in range(min(3, len(lines))):
                print(lines[i])

    def teardown(self):
        """Освобождает ресурсы после тестирования"""
        print("\n=== Tearing down test environment ===")
        self.thought_tree = None
        print("Teardown completed successfully")

    def run_tests(self):
        """Запускает все тесты"""
        setup_success = self.setup()
        if not setup_success:
            print("Cannot run tests due to setup failure")
            return

        try:
            self.test_create_root()
            self.test_add_thoughts()
            self.test_navigation()
            self.test_get_children_and_alternatives()
            self.test_serialization()
            self.test_file_serialization()
            self.test_visualization()

            # Выводим результаты
            print("\n=== Test Results ===")
            for i, (test_name, result) in enumerate(self.test_results, 1):
                status = "PASSED" if result else "FAILED"
                print(f"{i}. {test_name}: {status}")

            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            print(f"\nPassed {passed}/{total} tests ({passed/total*100:.1f}%)")

        finally:
            self.teardown()


def main():
    """Главная функция для запуска тестов"""
    print("=== Starting ThoughtTree Tests ===")

    tester = ThoughtTreeTester()
    tester.run_tests()


if __name__ == "__main__":
    # Запускаем тесты
    main()
