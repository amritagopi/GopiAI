#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа логической связанности компонентов проекта GopiAI.

Этот скрипт анализирует импорты и вызовы между различными компонентами проекта,
чтобы убедиться, что каждый важный компонент подключен и работает правильно.
Особое внимание уделяется модулям GopiAI_Flow, scripts и config.
"""

import argparse
import ast
import importlib
import importlib.util
import inspect
import json
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

# Настройки логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("component_connections.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ComponentAnalyzer")

# Ключевые модули, которые требуют особого внимания
KEY_MODULES = [
    "GopiAI_Flow",
    "scripts",
    "config",
    "app/agent",
    "app/flow",
    "app/pocketflow",
    "app/ui"
]

# Точки входа в приложение
ENTRY_POINTS = [
    "main.py",
    "run_flow.py",
    "run_pocketflow.py",
    "run_with_venv.py",
    "run_mcp.py",
    "run_mcp_server.py"
]


class ComponentAnalyzer:
    """Класс для анализа связанности компонентов проекта."""

    def __init__(self, project_root=None):
        """Инициализация анализатора компонентов."""
        self.project_root = Path(project_root or os.getcwd())
        self.modules = {}  # Имя модуля -> путь к файлу
        self.imports = defaultdict(list)  # Имя модуля -> список импортов
        self.calls = defaultdict(list)  # Имя модуля -> список вызовов
        self.entry_points = {}  # Имя точки входа -> список импортов
        self.dependency_graph = nx.DiGraph()
        self.execution_paths = {}  # Результаты анализа исполнения

        # Загрузка существующей информации о зависимостях, если доступна
        if os.path.exists("dependency_reports/imports.json"):
            self.load_existing_dependency_info()

    def load_existing_dependency_info(self):
        """Загружает существующую информацию о зависимостях."""
        try:
            with open("dependency_reports/imports.json", "r", encoding="utf-8") as f:
                import_data = json.load(f)

            logger.info("Загружены существующие данные о зависимостях")

            # Преобразуем данные в нужный формат
            for module, imports in import_data.items():
                if isinstance(imports, list):
                    self.imports[module] = imports
        except Exception as e:
            logger.warning(f"Ошибка при загрузке существующих данных о зависимостях: {e}")

    def find_python_modules(self):
        """Находит все Python-модули в проекте."""
        logger.info("Поиск Python-модулей в проекте...")
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Пропускаем директории venv и __pycache__
            dirs[:] = [d for d in dirs if d != "venv" and d != "__pycache__" and not d.startswith(".")]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)

                    # Преобразуем путь к файлу в имя модуля
                    module_name = self.path_to_module_name(rel_path)
                    self.modules[module_name] = rel_path
                    python_files.append(rel_path)

        logger.info(f"Найдено {len(python_files)} Python-файлов")
        return python_files

    def path_to_module_name(self, path):
        """Преобразует путь к файлу в имя модуля."""
        # Заменяем слеши на точки и удаляем расширение .py
        module_name = path.replace("\\", ".").replace("/", ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]
        return module_name

    def module_name_to_path(self, module_name):
        """Преобразует имя модуля в путь к файлу."""
        # Заменяем точки на слеши и добавляем расширение .py
        path = module_name.replace(".", "/")
        if not path.endswith(".py"):
            path += ".py"
        return path

    def analyze_imports(self):
        """Анализирует импорты во всех модулях."""
        logger.info("Анализ импортов в модулях...")

        for module_name, file_path in self.modules.items():
            try:
                with open(os.path.join(self.project_root, file_path), "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=file_path)

                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for name in node.names:
                            imports.append(f"{module}.{name.name}")

                # Фильтрация импортов - оставляем только внутренние модули проекта
                project_imports = [imp for imp in imports if any(m in imp for m in self.modules.keys())]
                self.imports[module_name] = project_imports

                # Обновляем граф зависимостей
                self.dependency_graph.add_node(module_name)
                for imported_module in project_imports:
                    # Добавляем только если импортированный модуль существует в проекте
                    if imported_module in self.modules:
                        self.dependency_graph.add_edge(module_name, imported_module)

            except Exception as e:
                logger.error(f"Ошибка при анализе импортов в модуле {module_name}: {e}")

        logger.info(f"Проанализированы импорты в {len(self.imports)} модулях")

    def analyze_calls(self):
        """Анализирует вызовы функций в модулях."""
        logger.info("Анализ вызовов функций...")

        for module_name, file_path in self.modules.items():
            try:
                with open(os.path.join(self.project_root, file_path), "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=file_path)

                calls = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            # Прямой вызов функции
                            calls.append(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            # Вызов метода объекта
                            if isinstance(node.func.value, ast.Name):
                                calls.append(f"{node.func.value.id}.{node.func.attr}")

                self.calls[module_name] = calls

            except Exception as e:
                logger.error(f"Ошибка при анализе вызовов в модуле {module_name}: {e}")

        logger.info(f"Проанализированы вызовы в {len(self.calls)} модулях")

    def analyze_entry_points(self):
        """Анализирует точки входа в приложение."""
        logger.info("Анализ точек входа...")

        for entry_point in ENTRY_POINTS:
            try:
                if os.path.exists(os.path.join(self.project_root, entry_point)):
                    module_name = self.path_to_module_name(entry_point)

                    # Если точка входа уже проанализирована в импортах
                    if module_name in self.imports:
                        self.entry_points[module_name] = self.imports[module_name]
                    else:
                        # Анализируем импорты в точке входа
                        with open(os.path.join(self.project_root, entry_point), "r", encoding="utf-8", errors="ignore") as f:
                            tree = ast.parse(f.read(), filename=entry_point)

                        imports = []
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    imports.append(name.name)
                            elif isinstance(node, ast.ImportFrom):
                                module = node.module or ""
                                for name in node.names:
                                    imports.append(f"{module}.{name.name}")

                        self.entry_points[module_name] = imports

            except Exception as e:
                logger.error(f"Ошибка при анализе точки входа {entry_point}: {e}")

        logger.info(f"Проанализировано {len(self.entry_points)} точек входа")

    def trace_execution_paths(self):
        """Определяет пути исполнения из точек входа."""
        logger.info("Построение путей исполнения...")

        for entry_point, imports in self.entry_points.items():
            # Начинаем с пустого пути
            path = []
            visited = set()

            # Рекурсивно трассируем вызовы
            self._trace_imports(entry_point, path, visited)

            self.execution_paths[entry_point] = path

        logger.info(f"Построены пути исполнения для {len(self.execution_paths)} точек входа")

    def _trace_imports(self, module_name, path, visited, depth=0, max_depth=10):
        """Рекурсивно трассирует импорты из модуля."""
        if module_name in visited or depth > max_depth:
            return

        visited.add(module_name)
        path.append(module_name)

        # Получаем импорты модуля
        imports = self.imports.get(module_name, [])

        # Рекурсивно трассируем импорты
        for imported_module in imports:
            if imported_module in self.modules:
                self._trace_imports(imported_module, path, visited, depth + 1, max_depth)

    def is_component_used(self, component_path):
        """Проверяет, используется ли компонент в проекте."""
        # Преобразуем путь к компоненту в имя модуля
        component_modules = []

        # Если путь к директории, то ищем все модули внутри нее
        if os.path.isdir(os.path.join(self.project_root, component_path)):
            for module_name in self.modules:
                if module_name.startswith(component_path.replace("/", ".")):
                    component_modules.append(module_name)
        else:
            # Если путь к файлу, то просто преобразуем в имя модуля
            component_modules = [self.path_to_module_name(component_path)]

        # Проверяем, есть ли импорты этих модулей в других модулях
        for module_name, imports in self.imports.items():
            for component_module in component_modules:
                if component_module in imports:
                    return True, module_name

        return False, None

    def check_key_modules(self):
        """Проверяет подключение ключевых модулей."""
        logger.info("Проверка подключения ключевых модулей...")

        results = {}
        for module_path in KEY_MODULES:
            is_used, used_in = self.is_component_used(module_path)
            imports_from = []

            # Собираем информацию о том, какие модули импортируются из ключевого модуля
            for module_name in self.modules:
                if module_name.startswith(module_path.replace("/", ".")):
                    imports_from.extend(self.imports.get(module_name, []))

            results[module_path] = {
                "is_used": is_used,
                "used_in": used_in,
                "imports_count": len(set(imports_from))
            }

        return results

    def find_disconnected_components(self):
        """Находит несвязанные компоненты в графе зависимостей."""
        # Строим неориентированный граф для поиска компонент связности
        undirected_graph = self.dependency_graph.to_undirected()

        # Находим компоненты связности
        connected_components = list(nx.connected_components(undirected_graph))

        # Фильтруем компоненты, исключая изолированные узлы
        significant_components = [
            component for component in connected_components
            if len(component) > 1
        ]

        # Находим изолированные модули
        isolated_modules = [
            component for component in connected_components
            if len(component) == 1
        ]

        return {
            "significant_components": significant_components,
            "isolated_modules": isolated_modules
        }

    def find_problematic_connections(self):
        """Находит проблемные связи между компонентами."""
        problematic = {}

        # Проверяем циклические зависимости
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            if cycles:
                problematic["cycles"] = cycles
        except Exception as e:
            logger.warning(f"Ошибка при поиске циклических зависимостей: {e}")

        # Проверяем неиспользуемые модули
        unused_modules = []
        for module_name in self.modules:
            # Модуль не импортируется другими модулями и не является точкой входа
            if (module_name not in self.entry_points and
                not any(module_name in imports for imports in self.imports.values())):
                unused_modules.append(module_name)

        if unused_modules:
            problematic["unused_modules"] = unused_modules

        return problematic

    def analyze_project(self):
        """Выполняет полный анализ проекта."""
        # Находим все Python-модули
        self.find_python_modules()

        # Анализируем импорты
        self.analyze_imports()

        # Анализируем вызовы функций
        self.analyze_calls()

        # Анализируем точки входа
        self.analyze_entry_points()

        # Отслеживаем пути исполнения
        self.trace_execution_paths()

        # Проверяем ключевые модули
        key_modules_status = self.check_key_modules()

        # Находим несвязанные компоненты
        disconnected_components = self.find_disconnected_components()

        # Находим проблемные связи
        problematic_connections = self.find_problematic_connections()

        # Формируем отчет
        report = {
            "project_info": {
                "root": str(self.project_root),
                "modules_count": len(self.modules),
                "entry_points": list(self.entry_points.keys())
            },
            "key_modules_status": key_modules_status,
            "disconnected_components": {
                "significant_count": len(disconnected_components["significant_components"]),
                "isolated_count": len(disconnected_components["isolated_modules"]),
                "isolated_modules": [list(m)[0] for m in disconnected_components["isolated_modules"]]
            },
            "problematic_connections": problematic_connections
        }

        return report

    def generate_graph_visualization(self, output_dir="component_connections_reports"):
        """Генерирует визуализацию графа зависимостей."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logger.info("Генерация визуализации графа зависимостей...")

        # Создаем граф для визуализации (ограничиваем его для лучшей читаемости)
        viz_graph = nx.DiGraph()

        # Добавляем только узлы для ключевых модулей и их непосредственные связи
        key_modules_nodes = []
        for module_path in KEY_MODULES:
            for module_name in self.modules:
                if module_name.startswith(module_path.replace("/", ".")):
                    key_modules_nodes.append(module_name)
                    viz_graph.add_node(module_name)

        # Добавляем связи между ключевыми модулями
        for source in key_modules_nodes:
            for target in self.imports.get(source, []):
                if target in key_modules_nodes:
                    viz_graph.add_edge(source, target)

        # Сохраняем граф в формате GraphML
        nx.write_graphml(viz_graph, os.path.join(output_dir, "key_modules_graph.graphml"))

        # Создаем PNG-изображение графа
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(viz_graph, seed=42)
        nx.draw(viz_graph, pos, with_labels=True, node_color='lightblue',
                node_size=1000, font_size=8, arrows=True, arrowsize=10)
        plt.title("Граф зависимостей между ключевыми модулями")
        plt.savefig(os.path.join(output_dir, "key_modules_graph.png"), dpi=300, bbox_inches='tight')
        plt.close()

        # Создаем HTML-отчет с интерактивным графом
        self._generate_html_report(viz_graph, output_dir)

        logger.info(f"Визуализация сохранена в директории {output_dir}")

    def _generate_html_report(self, graph, output_dir):
        """Генерирует HTML-отчет с интерактивным графом."""
        try:
            import pyvis.network as net

            # Создаем сетевую визуализацию
            network = net.Network(height="700px", width="100%", notebook=False, directed=True)

            # Добавляем узлы и связи
            for node in graph.nodes():
                # Определяем группу узла на основе пути
                group = node.split('.')[0] if '.' in node else node
                network.add_node(node, title=node, group=group)

            for edge in graph.edges():
                network.add_edge(edge[0], edge[1])

            # Настраиваем физику и параметры отображения
            network.repulsion(node_distance=100, central_gravity=0.2, spring_length=200)

            # Сохраняем HTML-файл
            network.save_graph(os.path.join(output_dir, "interactive_key_modules_graph.html"))

            logger.info("HTML-отчет с интерактивным графом успешно создан")
        except ImportError:
            logger.warning("Не удалось создать HTML-отчет. Установите пакет pyvis: pip install pyvis")

    def generate_report(self, output_dir="component_connections_reports"):
        """Генерирует отчет о связанности компонентов."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Выполняем анализ проекта
        report_data = self.analyze_project()

        # Сохраняем отчет в JSON-формате
        json_report_path = os.path.join(output_dir, "component_connections_report.json")
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        # Генерируем текстовый отчет
        text_report_path = os.path.join(output_dir, "component_connections_report.txt")
        self._generate_text_report(report_data, text_report_path)

        # Генерируем визуализацию графа
        self.generate_graph_visualization(output_dir)

        logger.info(f"Отчет сохранен в директории {output_dir}")
        return json_report_path

    def _generate_text_report(self, report_data, output_path):
        """Генерирует текстовый отчет на основе данных анализа."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== ОТЧЕТ ПО ЛОГИЧЕСКОЙ СВЯЗАННОСТИ КОМПОНЕНТОВ ===\n\n")

            # Информация о проекте
            f.write("=== ИНФОРМАЦИЯ О ПРОЕКТЕ ===\n")
            f.write(f"Корневая директория: {report_data['project_info']['root']}\n")
            f.write(f"Количество модулей: {report_data['project_info']['modules_count']}\n")
            f.write(f"Точки входа: {', '.join(report_data['project_info']['entry_points'])}\n\n")

            # Статус ключевых модулей
            f.write("=== СТАТУС КЛЮЧЕВЫХ МОДУЛЕЙ ===\n")
            for module_path, status in report_data['key_modules_status'].items():
                f.write(f"- {module_path}:\n")
                f.write(f"  Используется: {'Да' if status['is_used'] else 'Нет'}\n")
                f.write(f"  Используется в: {status['used_in'] or 'Нигде'}\n")
                f.write(f"  Количество импортов: {status['imports_count']}\n\n")

            # Несвязанные компоненты
            f.write("=== НЕСВЯЗАННЫЕ КОМПОНЕНТЫ ===\n")
            f.write(f"Значимые несвязанные компоненты: {report_data['disconnected_components']['significant_count']}\n")
            f.write(f"Изолированные модули: {report_data['disconnected_components']['isolated_count']}\n")
            if report_data['disconnected_components']['isolated_modules']:
                f.write("Список изолированных модулей:\n")
                for module in report_data['disconnected_components']['isolated_modules']:
                    f.write(f"- {module}\n")
            f.write("\n")

            # Проблемные связи
            f.write("=== ПРОБЛЕМНЫЕ СВЯЗИ ===\n")
            if 'cycles' in report_data['problematic_connections']:
                f.write(f"Циклические зависимости: {len(report_data['problematic_connections']['cycles'])}\n")
                f.write("Примеры циклов:\n")
                for i, cycle in enumerate(report_data['problematic_connections']['cycles'][:5]):
                    f.write(f"  {i+1}. {' -> '.join(cycle)} -> {cycle[0]}\n")
                if len(report_data['problematic_connections']['cycles']) > 5:
                    f.write(f"  ... и еще {len(report_data['problematic_connections']['cycles']) - 5} циклов\n")
            else:
                f.write("Циклические зависимости не обнаружены\n")

            if 'unused_modules' in report_data['problematic_connections']:
                f.write(f"\nНеиспользуемые модули: {len(report_data['problematic_connections']['unused_modules'])}\n")
                f.write("Примеры неиспользуемых модулей:\n")
                for i, module in enumerate(report_data['problematic_connections']['unused_modules'][:10]):
                    f.write(f"  {i+1}. {module}\n")
                if len(report_data['problematic_connections']['unused_modules']) > 10:
                    f.write(f"  ... и еще {len(report_data['problematic_connections']['unused_modules']) - 10} модулей\n")
            else:
                f.write("\nНеиспользуемых модулей не обнаружено\n")

            # Рекомендации
            f.write("\n=== РЕКОМЕНДАЦИИ ===\n")
            f.write("1. Устранить циклические зависимости между модулями\n")
            f.write("2. Проверить неиспользуемые модули и либо подключить их к проекту, либо удалить\n")
            f.write("3. Улучшить связанность основных компонентов проекта\n")
            f.write("4. Оптимизировать структуру импортов для уменьшения сложности системы\n")

            # Как использовать отчет
            f.write("\n=== КАК ИСПОЛЬЗОВАТЬ ОТЧЕТ ===\n")
            f.write("1. Изучите визуализацию графа зависимостей в файле interactive_key_modules_graph.html\n")
            f.write("2. Проанализируйте статус ключевых модулей и убедитесь, что они правильно подключены\n")
            f.write("3. Обратите внимание на циклические зависимости и неиспользуемые модули\n")
            f.write("4. Проведите рефакторинг кода для улучшения структуры и связности компонентов\n")


def main():
    parser = argparse.ArgumentParser(
        description='Анализ логической связанности компонентов проекта GopiAI'
    )
    parser.add_argument('--project-root', default=None,
                      help='Корневая директория проекта (по умолчанию - текущая директория)')
    parser.add_argument('--output-dir', default='component_connections_reports',
                      help='Директория для сохранения отчетов')

    args = parser.parse_args()

    logger.info("Запуск анализа логической связанности компонентов...")

    # Проверяем наличие необходимых пакетов
    try:
        import networkx
    except ImportError:
        logger.error("Отсутствует пакет networkx. Установите его: pip install networkx")
        sys.exit(1)

    try:
        import matplotlib
    except ImportError:
        logger.error("Отсутствует пакет matplotlib. Установите его: pip install matplotlib")
        sys.exit(1)

    analyzer = ComponentAnalyzer(args.project_root)
    report_path = analyzer.generate_report(args.output_dir)

    logger.info(f"Анализ завершен. Отчет сохранен в {report_path}")
    print(f"\nАнализ завершен. Отчет сохранен в {report_path}")


if __name__ == "__main__":
    main()
