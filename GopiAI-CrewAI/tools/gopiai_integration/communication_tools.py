"""
📡 GopiAI Communication Tool для CrewAI
Продвинутые инструменты для коммуникации между агентами и системами
"""

import os
import json
import time
import asyncio
from typing import Type, Any, List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool

class CommunicationInput(BaseModel):
    """Схема входных данных для коммуникации"""
    action: str = Field(description="Действие: send, receive, broadcast, notify, status, list_agents")
    recipient: str = Field(default="", description="Получатель сообщения (agent_id, 'all', 'ui')")
    message: str = Field(description="Сообщение или запрос")
    message_type: str = Field(default="info", description="Тип: info, task, alert, result, error")
    priority: int = Field(default=3, description="Приоритет от 1 (низкий) до 5 (критический)")
    metadata: str = Field(default="{}", description="Дополнительные данные в формате JSON")

class GopiAICommunicationTool(BaseTool):
    """
    Продвинутая система коммуникации для CrewAI агентов
    
    Возможности:
    - Отправка сообщений между агентами
    - Уведомления пользователя через UI
    - Broadcast сообщения
    - Мониторинг статуса агентов
    - Асинхронная коммуникация
    - Очереди сообщений
    """
    
    name: str = "gopiai_communication"
    description: str = """Система коммуникации между агентами и с UI GopiAI.
    
    Действия:
    - send: отправить сообщение агенту (recipient=agent_id, message=текст)
    - receive: получить сообщения для агента (recipient=agent_id)
    - broadcast: отправить всем агентам (message=текст)
    - notify: уведомить пользователя через UI (message=текст)
    - status: проверить статус агента (recipient=agent_id)
    - list_agents: список активных агентов
    
    Типы сообщений:
    - info: информационное
    - task: задача для выполнения
    - alert: предупреждение
    - result: результат работы
    - error: ошибка
    
    Приоритеты:
    - 1: низкий
    - 2: обычный
    - 3: средний (по умолчанию)
    - 4: высокий
    - 5: критический
    
    Примеры:
    - send: recipient="researcher_agent", message="Найди информацию о CrewAI"
    - notify: message="Задача выполнена успешно", message_type="result"
    - broadcast: message="Система обновляется", message_type="alert"
    """
    args_schema: Type[BaseModel] = CommunicationInput
    
    messages_path: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../communication"), description="Путь к директории сообщений")
    message_queue_file: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../communication/message_queue.json"), description="Файл очереди сообщений")
    agent_status_file: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../communication/agent_status.json"), description="Файл статусов агентов")
    ui_notifications_file: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../communication/ui_notifications.json"), description="Файл уведомлений UI")
        
    def __init__(self, **data):
        super().__init__(**data)
        # Не инициализируем пути вручную!
        # Для инициализации файлов вызывайте self.init_files() вручную после создания экземпляра

    def init_files(self):
        self._ensure_communication_files()
        
    def _ensure_communication_files(self):
        """Создает файлы коммуникации если их нет"""
        os.makedirs(self.messages_path, exist_ok=True)
        
        # Очередь сообщений
        if not os.path.exists(self.message_queue_file):
            with open(self.message_queue_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "messages": [],
                    "metadata": {"created": datetime.now().isoformat()}
                }, f)
        
        # Статусы агентов
        if not os.path.exists(self.agent_status_file):
            with open(self.agent_status_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "agents": {},
                    "metadata": {"created": datetime.now().isoformat()}
                }, f)
        
        # Уведомления UI
        if not os.path.exists(self.ui_notifications_file):
            with open(self.ui_notifications_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "notifications": [],
                    "metadata": {"created": datetime.now().isoformat()}
                }, f)
        
    def _run(self, action: str, recipient: str = "", message: str = "", 
             message_type: str = "info", priority: int = 3, metadata: str = "{}") -> str:
        """
        Выполнение коммуникационного действия
        """
        try:
            if action == "send":
                return self._send_message(recipient, message, message_type, priority, metadata)
            elif action == "receive":
                return self._receive_messages(recipient)
            elif action == "broadcast":
                return self._broadcast_message(message, message_type, priority, metadata)
            elif action == "notify":
                return self._notify_ui(message, message_type, priority, metadata)
            elif action == "status":
                return self._get_agent_status(recipient)
            elif action == "list_agents":
                return self._list_active_agents()
            else:
                return f"❌ Неизвестное действие: {action}"
                
        except Exception as e:
            return f"❌ Ошибка коммуникации: {str(e)}"
    
    def _load_message_queue(self) -> Dict:
        """Загружает очередь сообщений"""
        try:
            with open(self.message_queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"messages": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_message_queue(self, queue_data: Dict):
        """Сохраняет очередь сообщений"""
        with open(self.message_queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, ensure_ascii=False, indent=2)
    
    def _load_agent_status(self) -> Dict:
        """Загружает статусы агентов"""
        try:
            with open(self.agent_status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"agents": {}, "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_agent_status(self, status_data: Dict):
        """Сохраняет статусы агентов"""
        with open(self.agent_status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    def _load_ui_notifications(self) -> Dict:
        """Загружает уведомления UI"""
        try:
            with open(self.ui_notifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"notifications": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_ui_notifications(self, notifications_data: Dict):
        """Сохраняет уведомления UI"""
        with open(self.ui_notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications_data, f, ensure_ascii=False, indent=2)
    
    def _send_message(self, recipient: str, message: str, message_type: str, 
                     priority: int, metadata: str) -> str:
        """Отправка сообщения агенту"""
        if not recipient or not message:
            return "❌ Укажите получателя и сообщение"
        
        try:
            # Парсим метаданные
            try:
                meta_dict = json.loads(metadata)
            except (json.JSONDecodeError, TypeError, ValueError):
                meta_dict = {}
            
            # Загружаем очередь
            queue_data = self._load_message_queue()
            
            # Создаем сообщение
            new_message = {
                "id": len(queue_data["messages"]) + 1,
                "sender": "system",  # В будущем можно передавать ID отправителя
                "recipient": recipient,
                "message": message,
                "message_type": message_type,
                "priority": priority,
                "metadata": meta_dict,
                "timestamp": datetime.now().isoformat(),
                "status": "pending",
                "delivered": False
            }
            
            queue_data["messages"].append(new_message)
            self._save_message_queue(queue_data)
            
            # Обновляем статус получателя
            self._update_agent_status(recipient, "message_waiting", {
                "last_message": datetime.now().isoformat(),
                "priority": priority
            })
            
            return f"✅ Сообщение отправлено агенту '{recipient}' (приоритет: {priority})"
            
        except Exception as e:
            return f"❌ Ошибка отправки: {str(e)}"
    
    def _receive_messages(self, agent_id: str) -> str:
        """Получение сообщений для агента"""
        if not agent_id:
            return "❌ Укажите ID агента"
        
        try:
            queue_data = self._load_message_queue()
            
            # Фильтруем сообщения для агента
            agent_messages = []
            for message in queue_data["messages"]:
                if (message["recipient"] == agent_id or message["recipient"] == "all") and not message["delivered"]:
                    agent_messages.append(message)
                    # Помечаем как доставленное
                    message["delivered"] = True
                    message["status"] = "delivered"
            
            if not agent_messages:
                return f"📭 Нет новых сообщений для агента '{agent_id}'"
            
            # Сохраняем обновленную очередь
            self._save_message_queue(queue_data)
            
            # Формируем ответ
            messages_text = []
            for msg in agent_messages[:10]:  # Максимум 10 сообщений
                priority_emoji = ["", "🔵", "🟢", "🟡", "🟠", "🔴"][min(msg["priority"], 5)]
                type_emoji = {
                    "info": "ℹ️",
                    "task": "📋",
                    "alert": "⚠️",
                    "result": "✅",
                    "error": "❌"
                }.get(msg["message_type"], "📄")
                
                messages_text.append(f"{priority_emoji}{type_emoji} [{msg['message_type'].upper()}] {msg['message']}")
            
            return f"📬 Новые сообщения для '{agent_id}' ({len(agent_messages)}):\\n\\n" + "\\n\\n".join(messages_text)
            
        except Exception as e:
            return f"❌ Ошибка получения: {str(e)}"
    
    def _broadcast_message(self, message: str, message_type: str, priority: int, metadata: str) -> str:
        """Отправка сообщения всем агентам"""
        if not message:
            return "❌ Укажите сообщение для broadcast"
        
        return self._send_message("all", message, message_type, priority, metadata)
    
    def _notify_ui(self, message: str, message_type: str, priority: int, metadata: str) -> str:
        """Уведомление пользователя через UI"""
        if not message:
            return "❌ Укажите сообщение для уведомления"
        
        try:
            # Парсим метаданные
            try:
                meta_dict = json.loads(metadata)
            except (json.JSONDecodeError, TypeError, ValueError):
                meta_dict = {}
            
            # Загружаем уведомления
            notifications_data = self._load_ui_notifications()
            
            # Создаем уведомление
            notification = {
                "id": len(notifications_data["notifications"]) + 1,
                "message": message,
                "message_type": message_type,
                "priority": priority,
                "metadata": meta_dict,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            notifications_data["notifications"].append(notification)
            
            # Оставляем только последние 100 уведомлений
            if len(notifications_data["notifications"]) > 100:
                notifications_data["notifications"] = notifications_data["notifications"][-100:]
            
            self._save_ui_notifications(notifications_data)
            
            priority_text = ["", "низкий", "обычный", "средний", "высокий", "критический"][min(priority, 5)]
            return f"✅ Уведомление отправлено в UI (приоритет: {priority_text})"
            
        except Exception as e:
            return f"❌ Ошибка уведомления: {str(e)}"
    
    def _get_agent_status(self, agent_id: str) -> str:
        """Получение статуса агента"""
        if not agent_id:
            return "❌ Укажите ID агента"
        
        try:
            status_data = self._load_agent_status()
            
            if agent_id not in status_data["agents"]:
                return f"❓ Агент '{agent_id}' не найден в системе"
            
            agent_info = status_data["agents"][agent_id]
            
            status_text = f"🤖 Статус агента '{agent_id}':\\n"
            status_text += f"📊 Состояние: {agent_info.get('status', 'unknown')}\\n"
            status_text += f"⏰ Последняя активность: {agent_info.get('last_activity', 'неизвестно')}\\n"
            status_text += f"💬 Сообщений в очереди: {agent_info.get('messages_pending', 0)}\\n"
            
            if agent_info.get('current_task'):
                status_text += f"📋 Текущая задача: {agent_info['current_task']}\\n"
            
            return status_text
            
        except Exception as e:
            return f"❌ Ошибка получения статуса: {str(e)}"
    
    def _list_active_agents(self) -> str:
        """Список активных агентов"""
        try:
            status_data = self._load_agent_status()
            
            if not status_data["agents"]:
                return "📭 Нет зарегистрированных агентов"
            
            agent_list = []
            for agent_id, agent_info in status_data["agents"].items():
                status_emoji = {
                    "active": "🟢",
                    "busy": "🟡",
                    "idle": "🔵",
                    "error": "🔴",
                    "offline": "⚫"
                }.get(agent_info.get('status'), "❓")
                
                agent_list.append(f"{status_emoji} {agent_id} - {agent_info.get('status', 'unknown')}")
            
            return f"🤖 Активные агенты ({len(agent_list)}):\\n" + "\\n".join(agent_list)
            
        except Exception as e:
            return f"❌ Ошибка получения списка: {str(e)}"
    
    def _update_agent_status(self, agent_id: str, status: str, extra_info: Optional[Dict] = None):
        """Обновление статуса агента"""
        try:
            status_data = self._load_agent_status()
            
            if agent_id not in status_data["agents"]:
                status_data["agents"][agent_id] = {}
            
            status_data["agents"][agent_id].update({
                "status": status,
                "last_activity": datetime.now().isoformat()
            })
            
            if extra_info:
                status_data["agents"][agent_id].update(extra_info)
            
            self._save_agent_status(status_data)
            
        except Exception:
            pass  # Не критично если не удалось обновить статус


# Экспорт инструментов
__all__ = [
    "GopiAICommunicationTool"
]


if __name__ == "__main__":
    # Тест инструментов
    print("🧪 Тестирование GopiAI Communication Tools...")
    
    # Тест коммуникации
    comm = GopiAICommunicationTool()
    
    # Уведомление UI
    result = comm._run("notify", message="Тест системы коммуникации", message_type="info", priority=3)
    print(f"Notify test: {result}")
    
    # Отправка сообщения
    result = comm._run("send", "test_agent", "Привет! Это тестовое сообщение", "task", 4)
    print(f"Send test: {result}")
    
    # Получение сообщений
    result = comm._run("receive", "test_agent")
    print(f"Receive test: {result}")
    
    # Список агентов
    result = comm._run("list_agents")
    print(f"List agents test: {result}")
    
    print("✅ Все инструменты готовы!")