"""
Модуль для обратной совместимости с кодом, использующим FlowVisualizationDialog.
Этот файл переэкспортирует функцию show_flow_visualizer_dialog из flow_visualizer.py
как FlowVisualizationDialog для поддержки существующего кода.
"""

from .flow_visualizer import show_flow_visualizer_dialog

# Для обратной совместимости с main_window.py
FlowVisualizationDialog = show_flow_visualizer_dialog
