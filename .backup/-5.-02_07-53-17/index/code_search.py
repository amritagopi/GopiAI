# code_search.py
from llama_index.core import StorageContext, load_index_from_storage
import sys
import json

def search_code(index_dir, query, limit=5):
    """Выполняет поиск по уже созданному индексу"""
    try:
        # Загружаем существующий индекс
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
        
        # Создаем движок запросов
        query_engine = index.as_query_engine(similarity_top_k=limit)
        
        # Выполняем поиск
        response = query_engine.query(query)
        
        # Форматируем результаты
        results = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                results.append({
                    "score": float(node.score) if hasattr(node, 'score') else None,
                    "file": node.metadata.get("file_name", "unknown"),
                    "content": node.text[:300] + "..." if len(node.text) > 300 else node.text
                })
        
        return {
            "query": query,
            "response": str(response),
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python code_search.py index_dir query")
        sys.exit(1)
    
    index_dir = sys.argv[1]
    query = " ".join(sys.argv[2:])
    result = search_code(index_dir, query)
    print(json.dumps(result, indent=2))