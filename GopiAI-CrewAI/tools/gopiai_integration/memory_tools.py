"""
🧠 GopiAI Memory Tool для CrewAI
Интеграция CrewAI агентов с системой памяти и RAG GopiAI
"""

import os
import json
from typing import Type, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
# Импортируем BaseTool из crewai
from crewai.tools.agent_tools import StructuredTool as BaseTool

class MemoryInput(BaseModel):
    """Схема входных данных для работы с памятью"""
    action: str = Field(description="Действие: store, search, retrieve, list, delete, summarize, new_conversation, get_conversation_history")
    query: str = Field(description="Поисковый запрос или ключ")
    data: str = Field(default="", description="Данные для сохранения")
    category: str = Field(default="general", description="Категория: general, code, docs, research, conversation")
    importance: int = Field(default=5, description="Важность от 1 до 10")
    conversation_id: str = Field(default="default", description="Идентификатор беседы для группировки сообщений")

class GopiAIMemoryTool(BaseTool):
    """
    Мощный инструмент для работы с памятью и RAG системой GopiAI
    
    Возможности:
    - Сохранение и поиск информации
    - RAG (Retrieval-Augmented Generation)
    - Семантический поиск
    - Категоризация знаний
    - Долговременная память агентов
    """
    
    name: str = "gopiai_memory"
    description: str = """Работает с системой памяти и RAG GopiAI.
    
    Действия:
    - new_conversation: начать новую беседу (возвращает conversation_id)
    - store: сохранить информацию (data=текст, category=категория, conversation_id=идентификатор_беседы)
    - search: поиск по запросу (query=поисковый_запрос, conversation_id=идентификатор_беседы)
    - retrieve: получить по ключу (query=ключ, conversation_id=идентификатор_беседы)
    - list: список сохраненной информации (category=категория, conversation_id=идентификатор_беседы)
    - delete: удалить запись (query=ключ, conversation_id=идентификатор_беседы)
    - summarize: создать сводку (query=тема, conversation_id=идентификатор_беседы)
    - get_conversation_history: получить историю беседы (conversation_id=идентификатор_беседы)
    
    Категории:
    - general: общая информация
    - code: код и техническая документация
    - docs: документация проекта
    - research: результаты исследований
    - conversation: сообщения беседы
    
    Примеры:
    - new_conversation: (без параметров) - создать новую беседу
    - store: data="Привет, как дела?", category="conversation", conversation_id="123"
    - store: data="Важная информация", category="research", conversation_id="123"
    - search: query="настройка", conversation_id="123"
    - get_conversation_history: conversation_id="123"""
    args_schema: Type[BaseModel] = MemoryInput
    memory_path: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../../rag_memory_system"), description="Путь к директории памяти")
    local_memory_file: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../memory/crewai_memory.json"), description="Файл локальной памяти")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Не инициализируем пути вручную!
        # Для инициализации файлов вызывайте self.init_files() вручную после создания экземпляра

    def init_files(self):
        self._ensure_memory_file()
        
    def _ensure_memory_file(self):
        """Создает файл памяти если его нет"""
        os.makedirs(os.path.dirname(self.local_memory_file), exist_ok=True)
        if not os.path.exists(self.local_memory_file):
            with open(self.local_memory_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": [], "metadata": {"created": datetime.now().isoformat()}}, f)
        
    def _run(self, action: str, query: str = "", data: str = "", category: str = "general", 
             importance: int = 5, conversation_id: str = "default") -> str:
        """
        Выполнение операции с памятью
        """
        self.init_files()  # Автоматически инициализируем файлы при первом вызове
        try:
            if action == "new_conversation":
                return self._create_new_conversation()
            elif action == "store":
                # Для сообщений беседы автоматически добавляем метаданные
                if category == "conversation":
                    data = self._format_conversation_message(query, data)
                return self._store_memory(data, query, category, importance, conversation_id)
            elif action == "search":
                return self._search_memory(query, category, conversation_id)
            elif action == "retrieve":
                return self._retrieve_memory(query, conversation_id)
            elif action == "list":
                return self._list_memories(category, conversation_id)
            elif action == "delete":
                return self._delete_memory(query, conversation_id)
            elif action == "summarize":
                return self._summarize_memories(query, conversation_id)
            elif action == "get_conversation_history":
                return self._get_conversation_history(conversation_id)
            else:
                return f"❌ Неизвестное действие: {action}"
                
        except Exception as e:
            return f"❌ Ошибка памяти: {str(e)}"
    
    def _format_conversation_message(self, role: str, content: str) -> str:
        """Форматирует сообщение беседы с метаданными"""
        from datetime import datetime
        return json.dumps({
            "role": role,  # 'user' или 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False)

    def _create_new_conversation(self) -> str:
        """Создает новую беседу и возвращает её ID"""
        from uuid import uuid4
        conversation_id = str(uuid4())
        # Создаем запись о начале беседы
        self._store_memory(
            data=self._format_conversation_message("system", "Начало новой беседы"),
            key=f"conversation_start_{conversation_id}",
            category="conversation",
            importance=1,
            conversation_id=conversation_id
        )
        return conversation_id

    def _get_conversation_history(self, conversation_id: str) -> str:
        """Возвращает историю сообщений беседы"""
        memories = self._search_memories("", "conversation", conversation_id)
        if not memories:
            return "История беседы не найдена или пуста"
            
        # Сортируем сообщения по времени
        messages = []
        for mem in memories:
            try:
                msg = json.loads(mem["data"])
                messages.append((msg.get("timestamp", ""), msg.get("role", "unknown"), msg.get("content", "")))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
                
        messages.sort(key=lambda x: x[0])  # Сортировка по timestamp
        
        # Форматируем вывод
        result = []
        for _, role, content in messages:
            result.append(f"{role.upper()}: {content}")
            
        return "\n".join(result) if result else "История беседы пуста"

    def _load_local_memory(self) -> Dict:
        """Загружает локальную память"""
        try:
            with open(self.local_memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"memories": [], "metadata": {"created": datetime.now().isoformat()}}

    def _save_local_memory(self, memory_data: Dict):
        """Сохраняет локальную память"""
        with open(self.local_memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    def _store_memory(self, data: str, key: str, category: str = "general", 
                     importance: int = 5, conversation_id: str = "default") -> str:
        """Сохраняет информацию в память с привязкой к беседе"""
        memory = self._load_local_memory()
        
        # Создаем запись памяти
        memory_item = {
            "key": key,
            "data": data,
            "category": category,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        }
        
        # Добавляем в память
        memory["memories"].append(memory_item)
        
        # Ограничиваем размер истории беседы (последние 1000 сообщений на беседу)
        if category == "conversation":
            conv_memories = [m for m in memory["memories"] 
                           if m.get("category") == "conversation" 
                           and m.get("conversation_id") == conversation_id]
            if len(conv_memories) > 1000:
                # Удаляем самые старые сообщения сверх лимита
                conv_memories.sort(key=lambda x: x.get("timestamp", ""))
                for m in conv_memories[:-1000]:
                    if m in memory["memories"]:
                        memory["memories"].remove(m)
        
        # Сохраняем обратно
        self._save_local_memory(memory)
        return f"✅ Информация сохранена в память (категория: {category}, ключ: {key})"

    def _search_memories(self, query: str = "", category: str | None = None, 
                        conversation_id: str | None = None) -> List[Dict]:
        """Ищет информацию в памяти с фильтрацией по категории и беседе"""
        # Нормализуем входы, чтобы избежать .lower() на None
        norm_query = (query or "").lower()
        memory = self._load_local_memory()
        
        # Фильтрация по категории и беседе
        results: List[Dict] = []
        for mem in memory.get("memories", []):
            # Применяем фильтры
            if category is not None and mem.get("category") != category:
                continue
            if conversation_id is not None and mem.get("conversation_id") != conversation_id:
                continue
                
            # Если есть поисковый запрос, проверяем вхождение в данные или ключ
            data_str = str(mem.get("data", ""))
            key_str = str(mem.get("key", ""))
            if norm_query and (norm_query not in data_str.lower() and norm_query not in key_str.lower()):
                continue
                
            results.append(mem)
            
        return results

    def _search_memory(self, query: str, category: str | None = None, 
                      conversation_id: str | None = None) -> str:
        """Ищет информацию в памяти с фильтрацией по беседе"""
        # Гарантируем строковый тип для совместимости с сигнатурой _search_memories
        query = query or ""
        memories = self._search_memories(query, category, conversation_id)
        if not memories:
            return "Ничего не найдено в памяти."
            
        # Сортируем по важности и времени (новые и важные сначала)
        memories.sort(key=lambda x: (x.get("importance", 0), 
                                   x.get("timestamp", "")), 
                     reverse=True)
            
        # Форматируем результаты
        result = ["🔍 Найдены совпадения в памяти:"]
        for i, mem in enumerate(memories[:10], 1):  # Ограничиваем 10 результатами
            # Пытаемся распарсить JSON для сообщений беседы
            display_data = mem.get("data", "")
            if mem.get("category") == "conversation":
                try:
                    msg = json.loads(display_data)
                    display_data = f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
                    
            result.append(f"{i}. [Категория: {mem.get('category', 'неизвестно')}] "
                        f"{display_data[:200]}{'...' if len(display_data) > 200 else ''}")
            
        return "\n".join(result)

    def _retrieve_memory(self, key: str | None, conversation_id: str | None = None) -> str:
        """Получает информацию по ключу с учетом беседы"""
        key = key or ""
        memory = self._load_local_memory()
        
        # Ищем по ключу и conversation_id
        for mem in memory.get("memories", []):
            if mem.get("key") == key:
                if conversation_id is not None and mem.get("conversation_id") != conversation_id:
                    continue
                return f"🔑 Найдено по ключу '{key}':\n{mem.get('data', '')}"
                
        return f"❌ Запись с ключом '{key}' не найдена" + \
               (f" в беседе {conversation_id}" if conversation_id else "")

    def _delete_memory(self, key: str | None, conversation_id: str | None = None) -> str:
        """Удаляет информацию из памяти с учетом беседы"""
        key = key or ""
        memory = self._load_local_memory()
        
        # Ищем и удаляем по ключу и conversation_id
        removed = False
        for mem in memory["memories"][:]:
            if mem.get("key") == key:
                if conversation_id is not None and mem.get("conversation_id") != conversation_id:
                    continue
                memory["memories"].remove(mem)
                removed = True
                
        if removed:
            self._save_local_memory(memory)
            return f"✅ Запись с ключом '{key}' удалена" + \
                  (f" из беседы {conversation_id}" if conversation_id else "")
        else:
            return f"❌ Запись с ключом '{key}' не найдена" + \
                  (f" в беседе {conversation_id}" if conversation_id else "")

    def _summarize_memories(self, topic: str | None, conversation_id: str | None = None) -> str:
        """Создает сводку по теме с учетом контекста беседы"""
        # Получаем релевантные записи
        topic_str = topic or ""
        memories = self._search_memories(topic_str, conversation_id=conversation_id)
        
        if not memories:
            return f"Не найдено информации по теме '{topic}'" + \
                  (f" в беседе {conversation_id}" if conversation_id else "")
        
        # Сортируем по важности и времени
        memories.sort(key=lambda x: (x.get("importance", 0), 
                                   x.get("timestamp", "")), 
                     reverse=True)
        
        # Ограничиваем количество записей для сводки
        max_entries = 10
        if len(memories) > max_entries:
            memories = memories[:max_entries]
            
        # Формируем сводку
        result = [f"📝 Сводка по теме '{topic}':"]
        
        for i, mem in enumerate(memories, 1):
            # Для сообщений беседы форматируем особым образом
            if mem.get("category") == "conversation":
                try:
                    msg = json.loads(mem.get("data", "{}"))
                    content = f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                except (json.JSONDecodeError, KeyError, TypeError):
                    content = mem.get("data", "")
            else:
                content = mem.get("data", "")
                
            result.append(f"{i}. {content[:200]}{'...' if len(content) > 200 else ''}")
        
        total_found = len(self._search_memories(topic_str, conversation_id=conversation_id))
        if len(memories) < total_found:
            result.append(f"\nПоказано {len(memories)} из {total_found} записей. Уточните запрос для более точных результатов.")
            
        return "\n".join(result)

    def _list_memories(self, category: str | None = None, conversation_id: str | None = None) -> str:
        """Выводит список сохраненной информации с фильтрацией по категории и беседе"""
        memories = self._search_memories("", category, conversation_id)
        if not memories:
            filters = []
            if category:
                filters.append(f"категория: {category}")
            if conversation_id:
                filters.append(f"беседа: {conversation_id}")
                
            return "Нет сохраненной информации" + (f" с фильтрами: {', '.join(filters)}" if filters else "")
            
        # Группируем по категориям
        categories = {}
        for mem in memories:
            cat = mem.get("category", "без категории")
            conv_id = mem.get("conversation_id", "без беседы")
            
            if conversation_id:  # Если фильтр по беседе, не показываем её в группировке
                key = cat
            else:
                key = f"{cat} (беседа: {conv_id})"
                
            if key not in categories:
                categories[key] = 0
            categories[key] += 1
            
        # Сортируем категории по количеству записей
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
        # Format the output
        result = ["📋 Список сохраненной информации:"]
        for cat, count in sorted_cats:
            result.append(f"- {cat}: {count} записей")
            
        return "\n".join(result)

    def _store_to_rag(self, data: str, key: str, category: str) -> str:
        """Сохранение в RAG систему (если доступна)"""
        try:
            rag_dir = self.memory_path
            if not os.path.isdir(rag_dir):
                return ""
            # Сохраняем каждый фрагмент как отдельный json
            os.makedirs(rag_dir, exist_ok=True)
            fname = f"{category}_{key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fpath = os.path.join(rag_dir, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump({"key": key, "data": data, "category": category, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
            return f"RAG: сохранено в {fpath}"
        except Exception as e:
            return f"RAG: ошибка сохранения: {e}"

    def _search_in_rag(self, query: str, category: str) -> str:
        """Поиск в RAG системе (если доступна)"""
        try:
            rag_dir = self.memory_path
            if not os.path.isdir(rag_dir):
                return ""
            results = []
            for fname in os.listdir(rag_dir):
                if not fname.endswith('.json'):
                    continue
                fpath = os.path.join(rag_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        rec = json.load(f)
                        if (query.lower() in rec.get('key', '').lower() or query.lower() in rec.get('data', '').lower()):
                            if category == "all" or rec.get('category') == category:
                                snippet = rec.get('data', '')[:200] + "..." if len(rec.get('data', '')) > 200 else rec.get('data', '')
                                results.append(f"RAG: {rec.get('key')} ({rec.get('category')}): {snippet}")
                except Exception:
                    continue
            return "\n".join(results[:5]) if results else ""
        except Exception as e:
            return f"RAG: ошибка поиска: {e}"


# Экспорт инструментов
__all__ = [
    "GopiAIMemoryTool"
]


if __name__ == "__main__":
    # Тест инструментов
    print("🧪 Тестирование GopiAI Memory Tools...")
    
    # Тест памяти
    memory = GopiAIMemoryTool()
    
    # Сохранение
    result = memory._run("store", "test_key", "Это тестовая информация для проверки памяти", "research", 8)
    print(f"Store test: {result}")
    
    # Поиск
    result = memory._run("search", "тестовая")
    print(f"Search test: {result}")
    
    # Список
    result = memory._run("list", "research")
    print(f"List test: {result}")
    
    print("✅ Все инструменты готовы!")
