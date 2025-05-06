#!/usr/bin/env python
"""
Тесты для компонентов пользовательского интерфейса
Reasoning Agent, включая ThoughtTreeWidget и SessionHistoryManager.
"""

import os
import sys
import unittest
import tempfile
import json
import time
from pathlib import Path
import shutil

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.thought_tree import ThoughtTree, ThoughtNode
from app.ui.thought_tree_widget import ThoughtTreeWidget, ThoughtTreeItem
from app.ui.session_history_manager import SessionHistoryManager, SessionRecord


# Создаем экземпляр приложения для тестов
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestThoughtTreeWidget(unittest.TestCase):
    """Тесты для виджета визуализации дерева мыслей."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем тестовое дерево мыслей
        self.thought_tree = ThoughtTree()
        root_id = self.thought_tree.add_root_node("Root node")
        child1_id = self.thought_tree.add_node("Child 1", parent_id=root_id)
        child2_id = self.thought_tree.add_node("Child 2", parent_id=root_id)
        self.thought_tree.add_node("Grandchild 1", parent_id=child1_id)
        self.thought_tree.add_node("Alternative path", parent_id=child1_id, is_alternative=True)

        # Создаем виджет
        self.widget = ThoughtTreeWidget()
        self.widget.set_thought_tree(self.thought_tree)
        self.widget.show()

    def tearDown(self):
        """Очистка после каждого теста."""
        self.widget.close()
        self.widget = None

    def test_tree_structure(self):
        """Проверяет, что структура дерева отображается корректно."""
        # Ожидаем один корневой элемент
        self.assertEqual(self.widget.tree_widget.topLevelItemCount(), 1)

        # Получаем корневой элемент
        root_item = self.widget.tree_widget.topLevelItem(0)
        self.assertIsNotNone(root_item)

        # Проверяем текст корневого элемента
        self.assertEqual(root_item.text(0), "Root node")

        # Проверяем количество дочерних элементов
        self.assertEqual(root_item.childCount(), 2)

        # Проверяем первого потомка
        child1 = root_item.child(0)
        self.assertIsNotNone(child1)
        self.assertEqual(child1.text(0), "Child 1")
        self.assertEqual(child1.childCount(), 2)  # Один обычный и один альтернативный

    def test_filter_functionality(self):
        """Проверяет работу фильтрации по типу узла."""
        # Устанавливаем тип для узлов
        root_node = self.thought_tree.nodes[self.thought_tree.root.node_id]
        root_node.node_type = "root"

        for node_id, node in self.thought_tree.nodes.items():
            if node_id != self.thought_tree.root.node_id:
                if node.is_alternative:
                    node.node_type = "decision_option"
                else:
                    node.node_type = "step_reasoning"

        # Обновляем виджет
        self.widget.refresh_tree()

        # Проверяем отображение всех узлов по умолчанию
        root_item = self.widget.tree_widget.topLevelItem(0)
        self.assertEqual(root_item.childCount(), 2)

        # Устанавливаем фильтр на тип "decision_option"
        index = self.widget.filter_combo.findData("decision_option")
        self.widget.filter_combo.setCurrentIndex(index)

        # Эмулируем применение фильтра (вручную вызываем метод)
        self.widget._apply_filter()

    def test_node_selection(self):
        """Проверяет выбор узла и отображение деталей."""
        # Выбираем корневой элемент
        root_item = self.widget.tree_widget.topLevelItem(0)
        self.widget.tree_widget.setCurrentItem(root_item)

        # Эмулируем выбор элемента
        self.widget._on_item_selected()

        # Проверяем, что отображаются детали для корневого узла
        self.assertEqual(self.widget.detail_view.type_value.text(), "root")


class TestSessionHistoryManager(unittest.TestCase):
    """Тесты для менеджера истории сессий."""

    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()

        # Создаем менеджер истории
        self.manager = SessionHistoryManager(history_dir=self.test_dir)

    def tearDown(self):
        """Очистка после каждого теста."""
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)

    def test_create_session(self):
        """Проверяет создание новой сессии."""
        # Создаем сессию
        session = self.manager.create_session("Test Session")

        # Проверяем, что сессия создана с указанным названием
        self.assertEqual(session.title, "Test Session")

        # Проверяем, что сессия добавлена в список
        self.assertIn(session.session_id, self.manager.sessions)

        # Проверяем, что индекс был сохранен
        index_path = self.manager._get_index_file_path()
        self.assertTrue(os.path.exists(index_path))

    def test_save_load_session(self):
        """Проверяет сохранение и загрузку сессии."""
        # Создаем сессию
        session = self.manager.create_session("Save Test")

        # Добавляем сообщения
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")

        # Добавляем план
        session.add_plan({"title": "Test Plan", "steps": []})

        # Создаем и добавляем дерево мыслей
        tree = ThoughtTree()
        root_id = tree.add_root_node("Root")
        tree.add_node("Child", parent_id=root_id)
        session.set_thought_tree(tree)

        # Сохраняем сессию
        result = self.manager.save_session(session)
        self.assertTrue(result)

        # Проверяем, что файл сессии создан
        session_path = self.manager._get_session_file_path(session.session_id)
        self.assertTrue(os.path.exists(session_path))

        # Загружаем сессию
        loaded_session = self.manager.load_session(session.session_id)

        # Проверяем данные
        self.assertEqual(loaded_session.title, "Save Test")
        self.assertEqual(len(loaded_session.dialogue), 2)
        self.assertEqual(len(loaded_session.plans), 1)

        # Проверяем дерево мыслей
        thought_tree = loaded_session.get_thought_tree()
        self.assertIsNotNone(thought_tree)
        self.assertEqual(len(thought_tree.nodes), 2)

    def test_get_sessions_list(self):
        """Проверяет получение списка сессий."""
        # Создаем несколько сессий
        session1 = self.manager.create_session("Session 1")
        session2 = self.manager.create_session("Session 2")
        session3 = self.manager.create_session("Session 3")

        # Получаем список сессий
        sessions_list = self.manager.get_sessions_list()

        # Проверяем количество сессий
        self.assertEqual(len(sessions_list), 3)

        # Проверяем сортировку (новые сначала)
        self.assertEqual(sessions_list[0]["session_id"], session3.session_id)
        self.assertEqual(sessions_list[1]["session_id"], session2.session_id)
        self.assertEqual(sessions_list[2]["session_id"], session1.session_id)

    def test_delete_session(self):
        """Проверяет удаление сессии."""
        # Создаем сессию
        session = self.manager.create_session("Delete Test")
        session_id = session.session_id

        # Сохраняем сессию
        self.manager.save_session(session)

        # Проверяем, что файл сессии создан
        session_path = self.manager._get_session_file_path(session_id)
        self.assertTrue(os.path.exists(session_path))

        # Удаляем сессию
        result = self.manager.delete_session(session_id)
        self.assertTrue(result)

        # Проверяем, что файл сессии удален
        self.assertFalse(os.path.exists(session_path))

        # Проверяем, что сессия удалена из списка
        self.assertNotIn(session_id, self.manager.sessions)


class TestSessionRecord(unittest.TestCase):
    """Тесты для класса записи сессии."""

    def test_session_record_creation(self):
        """Проверяет создание записи сессии."""
        # Создаем запись
        session = SessionRecord(
            session_id="test_id",
            title="Test Session"
        )

        # Проверяем базовые поля
        self.assertEqual(session.session_id, "test_id")
        self.assertEqual(session.title, "Test Session")
        self.assertIsNotNone(session.timestamp)
        self.assertEqual(len(session.dialogue), 0)
        self.assertEqual(len(session.plans), 0)
        self.assertEqual(len(session.thought_tree_data), 0)

    def test_add_message(self):
        """Проверяет добавление сообщений."""
        session = SessionRecord(
            session_id="test_id",
            title="Test Session"
        )

        # Добавляем сообщения
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")

        # Проверяем, что сообщения добавлены
        self.assertEqual(len(session.dialogue), 2)
        self.assertEqual(session.dialogue[0]["role"], "user")
        self.assertEqual(session.dialogue[0]["content"], "Hello")
        self.assertEqual(session.dialogue[1]["role"], "assistant")
        self.assertEqual(session.dialogue[1]["content"], "Hi there!")

    def test_add_plan(self):
        """Проверяет добавление планов."""
        session = SessionRecord(
            session_id="test_id",
            title="Test Session"
        )

        # Создаем тестовый план
        plan = {
            "title": "Test Plan",
            "steps": [
                {"id": 1, "title": "Step 1", "description": "Do something"},
                {"id": 2, "title": "Step 2", "description": "Do something else"}
            ]
        }

        # Добавляем план
        session.add_plan(plan)

        # Проверяем, что план добавлен
        self.assertEqual(len(session.plans), 1)
        self.assertEqual(session.plans[0]["title"], "Test Plan")
        self.assertEqual(len(session.plans[0]["steps"]), 2)

    def test_thought_tree_serialization(self):
        """Проверяет сериализацию и десериализацию дерева мыслей."""
        session = SessionRecord(
            session_id="test_id",
            title="Test Session"
        )

        # Создаем тестовое дерево мыслей
        tree = ThoughtTree()
        root_id = tree.add_root_node("Root node")
        child1_id = tree.add_node("Child 1", parent_id=root_id)
        child2_id = tree.add_node("Child 2", parent_id=root_id)

        # Устанавливаем дерево мыслей
        session.set_thought_tree(tree)

        # Проверяем, что данные дерева сохранены
        self.assertNotEqual(len(session.thought_tree_data), 0)

        # Восстанавливаем дерево
        restored_tree = session.get_thought_tree()

        # Проверяем структуру восстановленного дерева
        self.assertIsNotNone(restored_tree)
        self.assertEqual(len(restored_tree.nodes), 3)
        self.assertEqual(restored_tree.nodes[restored_tree.root.node_id].content, "Root node")

    def test_to_from_dict(self):
        """Проверяет преобразование в словарь и обратно."""
        session = SessionRecord(
            session_id="test_id",
            title="Test Session"
        )

        # Добавляем сообщения и план
        session.add_message("user", "Hello")
        session.add_plan({"title": "Test Plan", "steps": []})

        # Преобразуем в словарь
        data = session.to_dict()

        # Проверяем структуру словаря
        self.assertEqual(data["session_id"], "test_id")
        self.assertEqual(data["title"], "Test Session")
        self.assertEqual(len(data["dialogue"]), 1)
        self.assertEqual(len(data["plans"]), 1)

        # Создаем новую запись из словаря
        new_session = SessionRecord.from_dict(data)

        # Проверяем, что данные корректно восстановлены
        self.assertEqual(new_session.session_id, "test_id")
        self.assertEqual(new_session.title, "Test Session")
        self.assertEqual(len(new_session.dialogue), 1)
        self.assertEqual(len(new_session.plans), 1)


if __name__ == "__main__":
    unittest.main()
