#!/usr/bin/env python
"""
Визуализатор графа зависимостей модулей проекта

Этот скрипт создает визуализацию графа зависимостей между модулями Python
на основе данных, сгенерированных скриптом find_unused_files.py.

Визуализация выполняется в нескольких форматах:
1. HTML - интерактивная визуализация с помощью PyVis
2. PNG/SVG - статические изображения с помощью Graphviz
3. TXT - текстовое описание основных зависимостей

Дополнительно скрипт выполняет:
- Анализ структуры импортов
- Выявление циклических зависимостей
- Определение ключевых модулей

Результаты сохраняются в директорию 'dependency_reports'
"""

import os
import sys
import json
import networkx as nx
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Для визуализации
try:
    import matplotlib.pyplot as plt
    from pyvis.network import Network
    import graphviz as gv
    HAS_VISUALIZATION = True
except ImportError:
    print("ВНИМАНИЕ: Не найдены библиотеки визуализации (pyvis, graphviz).")
    print("Будет создан только текстовый отчет.")
    HAS_VISUALIZATION = False

# Константы
IMPORTS_REPORT_DIR = "imports_reports"
OUTPUT_DIR = "dependency_reports"
MAX_FILENAME_LENGTH = 40  # Максимальная длина имени файла для отображения

# Создаем директорию для отчетов, если она не существует
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Отметка времени для имен файлов
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def find_latest_graph_data() -> dict:
    """Находит и загружает последние данные графа из директории imports_reports"""
    if not Path(IMPORTS_REPORT_DIR).exists():
        print(f"Директория {IMPORTS_REPORT_DIR} не найдена")
        return {}

    all_files = list(Path(IMPORTS_REPORT_DIR).glob("imports_graph_*.json"))
    if not all_files:
        print(f"Файлы графа зависимостей не найдены в {IMPORTS_REPORT_DIR}")
        return {}

    # Сортируем по времени модификации (от новых к старым)
    latest_file = max(all_files, key=lambda p: p.stat().st_mtime)
    print(f"Загружаем данные графа из {latest_file}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Ошибка при загрузке данных графа: {str(e)}")
        return {}


def shorten_filename(filename, max_length=MAX_FILENAME_LENGTH):
    """Сокращает длинные имена файлов для лучшего отображения"""
    if len(filename) <= max_length:
        return filename

    parts = filename.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return filename

    # Сокращаем средние части пути
    middle_parts = parts[1:-1]
    if len(middle_parts) > 2:
        middle_parts = [middle_parts[0], "...", middle_parts[-1]]

    return "/".join([parts[0]] + middle_parts + [parts[-1]])


def build_networkx_graph(graph_data: dict) -> nx.DiGraph:
    """Строит граф NetworkX на основе JSON данных"""
    G = nx.DiGraph()

    # Добавляем узлы
    for node in graph_data.get("nodes", []):
        node_id = node.get("id", "")
        is_unused = node.get("unused", False)

        short_name = shorten_filename(node_id)

        G.add_node(
            node_id,
            label=short_name,
            title=node_id,  # Полное имя для всплывающих подсказок
            is_unused=is_unused,
            color="red" if is_unused else "green"
        )

    # Добавляем связи
    for link in graph_data.get("links", []):
        source = link.get("source", "")
        target = link.get("target", "")

        if source and target and source in G and target in G:
            G.add_edge(source, target)

    return G


def analyze_graph(G: nx.DiGraph) -> dict:
    """
    Анализирует граф зависимостей и возвращает различные метрики
    """
    results = {}

    # Основные метрики графа
    results["node_count"] = G.number_of_nodes()
    results["edge_count"] = G.number_of_edges()

    # 1. Находим изолированные узлы (не используются и не импортируют)
    isolated_nodes = [node for node, degree in G.degree() if degree == 0]
    results["isolated_nodes"] = isolated_nodes
    results["isolated_count"] = len(isolated_nodes)

    # 2. Ключевые модули (по количеству импортирующих их модулей)
    in_degree = dict(G.in_degree())
    key_modules = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:20]
    results["key_modules"] = key_modules

    # 3. Модули с наибольшим числом зависимостей
    out_degree = dict(G.out_degree())
    heavy_dependents = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:20]
    results["heavy_dependents"] = heavy_dependents

    # 4. Выявление циклических зависимостей
    try:
        cycles = list(nx.simple_cycles(G))
        results["cycles"] = cycles
        results["cycle_count"] = len(cycles)
    except Exception:
        results["cycles"] = []
        results["cycle_count"] = 0

    # 5. Компоненты связности
    component_nodes = list(nx.weakly_connected_components(G))
    results["components"] = [list(comp) for comp in component_nodes]
    results["component_count"] = len(component_nodes)

    # 6. Самый длинный путь
    try:
        longest_path = nx.dag_longest_path(G)
        results["longest_path"] = longest_path
        results["longest_path_length"] = len(longest_path)
    except Exception:
        # Граф может быть не направленным ациклическим (DAG)
        results["longest_path"] = []
        results["longest_path_length"] = 0

    # 7. Анализ по директориям
    dir_stats = defaultdict(lambda: {"count": 0, "in_degree": 0, "out_degree": 0})
    for node in G.nodes():
        dir_name = os.path.dirname(node).replace("\\", "/").split("/")[0]
        if not dir_name:
            dir_name = "root"

        dir_stats[dir_name]["count"] += 1
        dir_stats[dir_name]["in_degree"] += in_degree.get(node, 0)
        dir_stats[dir_name]["out_degree"] += out_degree.get(node, 0)

    results["dir_stats"] = dict(dir_stats)

    return results


def create_text_report(G: nx.DiGraph, analysis: dict) -> str:
    """Создает текстовый отчет по графу зависимостей"""
    lines = [
        "ОТЧЕТ О ЗАВИСИМОСТЯХ МОДУЛЕЙ",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "ОБЩАЯ СТАТИСТИКА:",
        f"- Всего модулей: {analysis['node_count']}",
        f"- Всего зависимостей: {analysis['edge_count']}",
        f"- Изолированных модулей: {analysis['isolated_count']}",
        f"- Количество подграфов: {analysis['component_count']}",
        f"- Циклических зависимостей: {analysis['cycle_count']}",
        ""
    ]

    # Статистика по директориям
    lines.append("СТАТИСТИКА ПО ДИРЕКТОРИЯМ:")
    dir_stats = analysis["dir_stats"]
    for dir_name, stats in sorted(dir_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        lines.append(f"- {dir_name}: {stats['count']} модулей, {stats['in_degree']} входящих, {stats['out_degree']} исходящих зависимостей")

    lines.append("")

    # Ключевые модули (которые импортируются больше всего)
    lines.append("КЛЮЧЕВЫЕ МОДУЛИ (наиболее импортируемые):")
    for module, count in analysis["key_modules"][:10]:
        lines.append(f"- {module}: {count} импортов")

    lines.append("")

    # Модули с наибольшим числом импортов
    lines.append("МОДУЛИ С НАИБОЛЬШИМ ЧИСЛОМ ЗАВИСИМОСТЕЙ:")
    for module, count in analysis["heavy_dependents"][:10]:
        lines.append(f"- {module}: импортирует {count} модулей")

    lines.append("")

    # Циклические зависимости
    if analysis["cycles"]:
        lines.append("ЦИКЛИЧЕСКИЕ ЗАВИСИМОСТИ:")
        for i, cycle in enumerate(analysis["cycles"][:5]):
            lines.append(f"- Цикл {i+1}: {' -> '.join([shorten_filename(n) for n in cycle])} -> {shorten_filename(cycle[0])}")

        if len(analysis["cycles"]) > 5:
            lines.append(f"...и еще {len(analysis['cycles']) - 5} циклов")

    lines.append("")

    # Изолированные модули
    if analysis["isolated_nodes"]:
        lines.append("ИЗОЛИРОВАННЫЕ МОДУЛИ (не импортируются и не импортируют):")
        for i, node in enumerate(analysis["isolated_nodes"][:20]):
            lines.append(f"- {shorten_filename(node)}")

        if len(analysis["isolated_nodes"]) > 20:
            lines.append(f"...и еще {len(analysis['isolated_nodes']) - 20} модулей")

    lines.append("")

    # Рекомендации по оптимизации зависимостей
    lines.append("РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:")

    if analysis["cycles"]:
        lines.append("1. Устранить циклические зависимости:")
        for i, cycle in enumerate(analysis["cycles"][:3]):
            lines.append(f"   - Цикл {i+1}: {' -> '.join([shorten_filename(n) for n in cycle])} -> {shorten_filename(cycle[0])}")

    # Рекомендации по модулям с большим количеством зависимостей
    if analysis["heavy_dependents"]:
        lines.append("2. Рассмотреть разделение модулей с большим количеством зависимостей:")
        for module, count in analysis["heavy_dependents"][:3]:
            if count > 5:  # Порог для рекомендации
                lines.append(f"   - {shorten_filename(module)}: импортирует {count} модулей")

    # Рекомендации по изолированным модулям
    if analysis["isolated_nodes"]:
        lines.append("3. Оценить необходимость изолированных модулей:")
        lines.append(f"   - Проверить {len(analysis['isolated_nodes'])} изолированных модулей на полезность")

    return "\n".join(lines)


def create_pyvis_visualization(G: nx.DiGraph, output_path: str):
    """Создает интерактивную HTML визуализацию с помощью PyVis"""
    if not HAS_VISUALIZATION:
        return False

    try:
        # Создаем сеть PyVis
        net = Network(
            height="800px",
            width="100%",
            directed=True,
            notebook=False,
            heading="Граф зависимостей модулей GopiAI"
        )

        # Добавляем узлы
        for node, attrs in G.nodes(data=True):
            color = "red" if attrs.get("is_unused", False) else "lightgreen"
            title = attrs.get("title", node)
            label = attrs.get("label", shorten_filename(node))

            net.add_node(
                node,
                label=label,
                title=title,
                color=color
            )

        # Добавляем связи
        for source, target in G.edges():
            net.add_edge(source, target)

        # Настройки физики для улучшения расположения
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -100,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 100}
          },
          "edges": {
            "color": {"inherit": true},
            "smooth": {"enabled": false}
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """)

        # Сохраняем HTML-файл
        net.save_graph(output_path)
        print(f"HTML-визуализация сохранена в {output_path}")
        return True
    except Exception as e:
        print(f"Ошибка при создании HTML-визуализации: {str(e)}")
        return False


def create_graphviz_visualization(G: nx.DiGraph, output_path_base: str):
    """Создает статическую визуализацию с помощью Graphviz"""
    if not HAS_VISUALIZATION:
        return False

    try:
        # Создаем объект Graphviz
        dot = gv.Digraph(
            name="GopiAI Dependencies",
            comment="Граф зависимостей модулей проекта GopiAI",
            format="png"
        )

        # Настройки графа
        dot.attr(
            rankdir="LR",
            size="11,11",
            ratio="fill",
            fontname="Arial",
            fontsize="10"
        )

        # Группируем узлы по директориям
        node_groups = defaultdict(list)
        for node, attrs in G.nodes(data=True):
            parts = node.replace("\\", "/").split("/")
            if len(parts) > 1:
                group = parts[0]  # Используем первый уровень директории как группу
            else:
                group = "root"

            node_groups[group].append((node, attrs))

        # Добавляем узлы с группировкой
        for group, nodes in node_groups.items():
            with dot.subgraph(name=f"cluster_{group}") as c:
                c.attr(label=group, style="filled", color="lightgrey", fontname="Arial")

                for node, attrs in nodes:
                    label = attrs.get("label", shorten_filename(node))
                    color = "red" if attrs.get("is_unused", False) else "lightgreen"

                    c.node(
                        node,
                        label=label,
                        shape="box",
                        style="filled",
                        fillcolor=color,
                        fontname="Arial",
                        fontsize="8"
                    )

        # Добавляем связи
        for source, target in G.edges():
            dot.edge(source, target)

        # Настройки для контроля размера графа
        nodes_count = G.number_of_nodes()
        if nodes_count > 100:
            # Для больших графов используем dot layout
            dot.attr(layout="dot")

        # Сохраняем визуализацию в различных форматах
        dot.render(output_path_base, view=False)

        # Также попробуем сохранить в SVG (более компактный)
        dot.format = "svg"
        dot.render(output_path_base + "_svg", view=False)

        print(f"Graphviz-визуализация сохранена в {output_path_base}.png и {output_path_base}_svg.svg")
        return True
    except Exception as e:
        print(f"Ошибка при создании Graphviz-визуализации: {str(e)}")
        return False


def create_cyclic_dependencies_visualization(G: nx.DiGraph, cycles, output_path_base: str):
    """Создает визуализацию циклических зависимостей"""
    if not HAS_VISUALIZATION or not cycles:
        return False

    try:
        # Создаем объект Graphviz
        dot = gv.Digraph(
            name="GopiAI Cyclic Dependencies",
            comment="Циклические зависимости модулей проекта GopiAI",
            format="png"
        )

        # Настройки графа
        dot.attr(
            rankdir="LR",
            size="8,8",
            ratio="fill",
            fontname="Arial",
            fontsize="10"
        )

        # Создаем подграф для каждого цикла
        for i, cycle in enumerate(cycles[:10]):  # Ограничиваем до 10 циклов
            with dot.subgraph(name=f"cluster_cycle_{i}") as c:
                c.attr(label=f"Цикл {i+1}", style="filled", color="lightpink", fontname="Arial")

                # Добавляем узлы
                for node in cycle:
                    short_name = shorten_filename(node)
                    c.node(
                        node,
                        label=short_name,
                        shape="box",
                        style="filled",
                        fillcolor="salmon",
                        fontname="Arial",
                        fontsize="8"
                    )

                # Добавляем связи между узлами в цикле
                for j in range(len(cycle)):
                    source = cycle[j]
                    target = cycle[(j+1) % len(cycle)]
                    c.edge(source, target, color="red", penwidth="2.0")

        # Сохраняем визуализацию
        cycles_path = f"{output_path_base}_cycles"
        dot.render(cycles_path, view=False)

        print(f"Визуализация циклических зависимостей сохранена в {cycles_path}.png")
        return True
    except Exception as e:
        print(f"Ошибка при создании визуализации циклических зависимостей: {str(e)}")
        return False


def main():
    """Основная функция скрипта"""
    print(f"Визуализатор графа зависимостей модулей проекта")
    print("-" * 70)

    # Находим и загружаем последние данные графа
    graph_data = find_latest_graph_data()
    if not graph_data:
        print("Ошибка: Не удалось загрузить данные графа зависимостей")
        print("Запустите сначала скрипт find_unused_files.py для создания графа")
        return 1

    print(f"Данные графа успешно загружены")

    # Строим граф из загруженных данных
    G = build_networkx_graph(graph_data)
    print(f"Построен граф с {G.number_of_nodes()} узлами и {G.number_of_edges()} связями")

    # Анализируем граф
    print("Выполняем анализ графа зависимостей...")
    analysis = analyze_graph(G)

    # Пути для сохранения результатов
    text_report_path = Path(OUTPUT_DIR) / f"dependencies_report_{timestamp}.txt"
    html_path = Path(OUTPUT_DIR) / f"dependencies_graph_{timestamp}.html"
    graphviz_base_path = str(Path(OUTPUT_DIR) / f"dependencies_graphviz_{timestamp}")

    # Создаем дополнительный JSON-отчет с анализом
    json_report_path = Path(OUTPUT_DIR) / f"dependencies_analysis_{timestamp}.json"
    with open(json_report_path, 'w', encoding='utf-8') as f:
        # Преобразуем непреобразуемые типы в строки
        serializable_analysis = {k: v for k, v in analysis.items()
                                if k not in ["longest_path", "components"]}
        json.dump(serializable_analysis, f, indent=2)
    print(f"Анализ зависимостей сохранен в {json_report_path}")

    # Создаем текстовый отчет
    text_report = create_text_report(G, analysis)
    text_report_path.write_text(text_report, encoding="utf-8")
    print(f"Текстовый отчет сохранен в {text_report_path}")

    # Создаем HTML-визуализацию с PyVis
    if HAS_VISUALIZATION:
        print("Создаем интерактивную HTML-визуализацию...")
        create_pyvis_visualization(G, str(html_path))

        print("Создаем статическую визуализацию с помощью Graphviz...")
        create_graphviz_visualization(G, graphviz_base_path)

        # Создаем визуализацию циклических зависимостей
        if analysis["cycles"]:
            print("Создаем визуализацию циклических зависимостей...")
            create_cyclic_dependencies_visualization(G, analysis["cycles"], graphviz_base_path)

    print("\nВизуализация завершена!")
    print(f"Результаты сохранены в директорию: {OUTPUT_DIR}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
