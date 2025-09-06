#!/usr/bin/env python3
"""
Тестовая визуализация AgentsTab для проверки отображения
"""

import sys

# Добавляем путь к GopiAI-UI
sys.path.insert(0, '/home/amritagopi/GopiAI/GopiAI-UI')

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

def test_agents_tab():
    """Тестирует AgentsTab в отдельном окне"""
    
    app = QApplication(sys.argv)
    
    # Главное окно
    main_window = QMainWindow()
    main_window.setWindowTitle("Тест AgentsTab")
    main_window.setGeometry(100, 100, 800, 600)
    
    # Центральный виджет
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Кнопка для проверки сервера
    check_btn = QPushButton("Проверить подключение к серверу")
    layout.addWidget(check_btn)
    
    def check_server():
        import requests
        try:
            from gopiai.ui.utils.network import get_crewai_server_base_url
            api_base = get_crewai_server_base_url()
            print(f"API базовый URL: {api_base}")
            
            response = requests.get(f"{api_base}/api/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agents_count = len(data.get('agents', []))
                print(f"✅ Сервер доступен, загружено агентов: {agents_count}")
                for agent in data['agents'][:3]:
                    print(f"  - {agent['name']} ({agent['type']})")
            else:
                print(f"❌ Ошибка сервера: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
    
    check_btn.clicked.connect(check_server)
    
    try:
        # Импорт AgentsTab
        from gopiai.ui.components.agents_tab import AgentsTab
        
        # Создаем AgentsTab
        agents_tab = AgentsTab()
        layout.addWidget(agents_tab)
        
        # Информационная панель
        info_label = QPushButton("Загрузить агентов")
        layout.addWidget(info_label)
        
        def load_agents():
            try:
                agents_tab._load_agents()
                agents_count = len(agents_tab.agents_data)
                info_label.setText(f"Загружено агентов: {agents_count}")
                
                print(f"✅ AgentsTab: загружено {agents_count} агентов")
                
                # Попробуем получить прикрепленных агентов
                attached = agents_tab.get_attached_agents()
                print(f"Прикрепленных агентов: {len(attached)}")
                
                # Попробуем получить прикрепленный флоу
                attached_flow = agents_tab.get_attached_flow()
                if attached_flow:
                    print(f"Прикрепленный флоу: {attached_flow['name']}")
                else:
                    print("Нет прикрепленного флоу")
                    
            except Exception as e:
                print(f"❌ Ошибка загрузки агентов: {e}")
                import traceback
                traceback.print_exc()
        
        info_label.clicked.connect(load_agents)
        
        # Автоматическая загрузка при запуске
        load_agents()
        
        print("✅ AgentsTab успешно добавлен в интерфейс")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать AgentsTab: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка создания AgentsTab: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Показываем окно
    main_window.show()
    
    print("🚀 Тестовое окно запущено. Проверьте интерфейс.")
    print("Нажмите Ctrl+C для выхода.")
    
    # Запуск приложения
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Выход...")
        app.quit()

if __name__ == "__main__":
    test_agents_tab()