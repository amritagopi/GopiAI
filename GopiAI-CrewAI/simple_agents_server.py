#!/usr/bin/env python3
"""
Простой сервер для предоставления списка агентов без CrewAI зависимостей
Временное решение для демонстрации работы AgentsTab
"""
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path

log_file = str(Path(__file__).parent / "simple_agents_server.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Мок-данные агентов и флоу
MOCK_AGENTS = [
    {
        'id': 'researcher',
        'name': 'Исследователь',
        'type': 'agent',
        'description': 'Опытный исследователь с навыками поиска и анализа информации',
        'role': 'researcher',
        'goal': 'Найти и проанализировать релевантную информацию',
        'tools': ['search_tool', 'web_search_tool']
    },
    {
        'id': 'data_analyst',
        'name': 'Аналитик данных',
        'type': 'agent',
        'description': 'Эксперт по анализу данных и статистике',
        'role': 'data_analyst',
        'goal': 'Анализировать данные и создавать отчеты',
        'tools': ['file_read_tool', 'directory_tool', 'code_execution']
    },
    {
        'id': 'content_writer',
        'name': 'Контент-райтер',
        'type': 'agent',
        'description': 'Опытный писатель с пониманием различных стилей письма',
        'role': 'content_writer',
        'goal': 'Создавать качественный и увлекательный контент',
        'tools': ['search_tool', 'web_search_tool']
    },
    {
        'id': 'code_reviewer',
        'name': 'Ревьюер кода',
        'type': 'agent',
        'description': 'Старший разработчик с многолетним опытом code review',
        'role': 'code_reviewer',
        'goal': 'Анализировать код на предмет качества и безопасности',
        'tools': ['file_read_tool', 'directory_tool', 'code_execution']
    },
    {
        'id': 'qa_engineer',
        'name': 'QA инженер',
        'type': 'agent',
        'description': 'Эксперт по тестированию и обеспечению качества',
        'role': 'qa_engineer',
        'goal': 'Обеспечивать высокое качество продукта',
        'tools': ['file_read_tool', 'directory_tool']
    },
    {
        'id': 'research_flow',
        'name': 'Исследовательский флоу',
        'type': 'flow',
        'description': 'Комплексный процесс исследования и анализа',
        'workflow_type': 'sequential',
        'agents': ['researcher', 'data_analyst', 'content_writer'],
        'estimated_time': '2-4 часа'
    },
    {
        'id': 'content_creation_flow',
        'name': 'Создание контента',
        'type': 'flow',
        'description': 'Полный цикл создания контента от идеи до публикации',
        'workflow_type': 'sequential',
        'agents': ['researcher', 'content_writer', 'code_reviewer'],
        'estimated_time': '3-5 часов'
    },
    {
        'id': 'development_flow',
        'name': 'Команда разработки',
        'type': 'flow',
        'description': 'Процесс анализа и улучшения кода',
        'workflow_type': 'hierarchical',
        'agents': ['code_reviewer', 'qa_engineer'],
        'estimated_time': '1-3 часа'
    }
]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "service": "Simple Agents Server",
        "status": "healthy",
        "agents_count": len([a for a in MOCK_AGENTS if a['type'] == 'agent']),
        "flows_count": len([a for a in MOCK_AGENTS if a['type'] == 'flow'])
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Получение списка агентов и флоу"""
    try:
        logger.info("🤖 Запрос списка агентов")
        
        # Фильтры из query параметров
        agent_type = request.args.get('type')  # 'agent' или 'flow'
        
        agents_list = MOCK_AGENTS.copy()
        
        # Применяем фильтр по типу если задан
        if agent_type:
            agents_list = [a for a in agents_list if a['type'] == agent_type]
        
        return jsonify({
            'agents': agents_list,
            'total_count': len(agents_list),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка агентов: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Получение списка инструментов (мок для совместимости)"""
    return jsonify({
        'tools': [
            {'id': 'search_tool', 'name': 'Поиск в интернете'},
            {'id': 'file_read_tool', 'name': 'Чтение файлов'},
            {'id': 'code_execution', 'name': 'Выполнение кода'}
        ],
        'status': 'success'
    })

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent_details(agent_id):
    """Получение детальной информации об агенте или флоу"""
    try:
        agent = next((a for a in MOCK_AGENTS if a['id'] == agent_id), None)
        
        if not agent:
            return jsonify({'error': 'Агент не найден'}), 404
            
        return jsonify({
            'agent': agent,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения агента {agent_id}: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Создание задачи (мок-реализация)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400
        
        task_id = "mock_task_12345"
        
        logger.info(f"📝 Мок-задача создана: {task_id}")
        
        return jsonify({
            'task_id': task_id,
            'status': 'created',
            'message': 'Мок-задача создана (реальное выполнение недоступно)'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания мок-задачи: {e}")
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/api/tasks', methods=['GET'])  
def list_tasks():
    """Список задач (мок-реализация)"""
    return jsonify({
        'tasks': [
            {
                'task_id': 'mock_task_12345',
                'status': 'completed',
                'created_at': '2025-09-05T16:30:00Z',
                'progress': 'Демо-задача завершена'
            }
        ],
        'total_count': 1
    })

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Статус задачи (мок-реализация)"""
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'progress': 'Демо-задача завершена',
        'result': 'Это мок-результат для демонстрации интерфейса AgentsTab',
        'created_at': '2025-09-05T16:30:00Z',
        'completed_at': '2025-09-05T16:31:00Z'
    })

if __name__ == '__main__':
    logger.info("🚀 Запуск простого сервера агентов...")
    logger.info("🔗 Доступные endpoints:")
    logger.info("   GET  /api/health - проверка здоровья")
    logger.info("   GET  /api/agents - список агентов и флоу")
    logger.info("   GET  /api/agents/<id> - детали агента")
    logger.info("   POST /api/tasks - создание мок-задачи")
    logger.info("   GET  /api/tasks - список мок-задач")
    logger.info("   GET  /api/tasks/<id> - статус мок-задачи")
    logger.info("")
    logger.info("🚀 Сервер готов к работе на http://localhost:5052")
    
    app.run(host='0.0.0.0', port=5052, debug=False)