# Конфигурация Mem0 с отключенным GPU для faiss
MEM0_CONFIG = {
    "vector_store": {
        "provider": "faiss",
        "config": {
            "metric": "cosine",
            "gpu": False,  # Принудительно отключаем GPU
            "use_gpu": False,
            "device": "cpu"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "embedding_dims": 1536
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "max_tokens": 1000
        }
    },
    "version": "v1.1"
}
