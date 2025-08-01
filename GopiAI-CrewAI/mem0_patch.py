# АГРЕССИВНЫЙ ПАТЧ для полного отключения mem0 и faiss GPU проблем
import os
import sys

print("[PATCH] Применяем агрессивный патч для mem0/faiss...")

# Устанавливаем переменные окружения для принудительного отключения GPU
os.environ['FAISS_NO_AVX2'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['FAISS_OPT_LEVEL'] = 'generic'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'

# Создаем заглушки для всех проблемных модулей
class MockMemory:
    def __init__(self, *args, **kwargs):
        pass
    def add(self, *args, **kwargs): return None
    def search(self, *args, **kwargs): return []
    def get(self, *args, **kwargs): return None
    def delete(self, *args, **kwargs): return None
    @classmethod
    def from_config(cls, config): return cls()

class MockMemoryClient:
    def __init__(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): return None
    def search(self, *args, **kwargs): return []
    def get(self, *args, **kwargs): return None
    def delete(self, *args, **kwargs): return None

class MockFaiss:
    @staticmethod
    def read_index(*args, **kwargs): return MockFaissIndex()
    @staticmethod
    def write_index(*args, **kwargs): pass
    @staticmethod
    def index_factory(*args, **kwargs): return MockFaissIndex()
    @staticmethod
    def get_num_gpus(): return 0
    @staticmethod
    def omp_set_num_threads(n): pass

class MockFaissIndex:
    def __init__(self): self.ntotal = 0
    def add(self, *args): pass
    def search(self, *args): return [], []
    def train(self, *args): pass

# КРИТИЧЕСКИ ВАЖНО: Блокируем импорты ДО того, как они могут быть загружены
sys.modules['faiss'] = MockFaiss()
sys.modules['mem0'] = type('MockMem0', (), {
    'Memory': MockMemory,
    'MemoryClient': MockMemoryClient
})()

# Блокируем векторные хранилища mem0
sys.modules['mem0.vector_stores.faiss'] = type('MockFaissStore', (), {})()

# Блокируем txtai с faiss
sys.modules['txtai.ann.faiss'] = type('MockTxtaiFaiss', (), {
    'Faiss': type('MockTxtaiFaissClass', (), {
        '__init__': lambda self, *args, **kwargs: None,
        'load': lambda self, *args, **kwargs: None,
        'index': lambda self, *args, **kwargs: None,
        'search': lambda self, *args, **kwargs: ([], [])
    })
})()

# Создаем заглушку для txtai без faiss
class MockTxtaiEmbeddings:
    def __init__(self, *args, **kwargs):
        print("[PATCH] txtai инициализирован без faiss")
        self.config = {}
    def index(self, *args, **kwargs): pass
    def search(self, *args, **kwargs): return []
    def transform(self, *args, **kwargs): return []
    def save(self, *args, **kwargs): pass
    def load(self, *args, **kwargs): pass

sys.modules['txtai'] = type('MockTxtai', (), {
    'Embeddings': MockTxtaiEmbeddings
})()

# Пытаемся пропатчить уже загруженные модули
try:
    import faiss
    print("[PATCH] ВНИМАНИЕ: faiss уже был загружен, пытаемся пропатчить...")
    # Заменяем проблемные функции
    faiss.read_index = MockFaiss.read_index
    faiss.write_index = MockFaiss.write_index
    faiss.get_num_gpus = lambda: 0
    print("[PATCH] faiss успешно пропатчен")
except ImportError:
    print("[PATCH] faiss не был загружен - отлично!")
except Exception as e:
    print(f"[PATCH] Ошибка при патче faiss: {e}")

# Пытаемся пропатчить mem0
try:
    import mem0
    print("[PATCH] ВНИМАНИЕ: mem0 уже был загружен, заменяем на заглушки...")
    mem0.Memory = MockMemory
    mem0.MemoryClient = MockMemoryClient
    print("[PATCH] mem0 успешно пропатчен")
except ImportError:
    print("[PATCH] mem0 не был загружен - отлично!")
except Exception as e:
    print(f"[PATCH] Ошибка при патче mem0: {e}")

print("[PATCH] Агрессивный mem0/faiss патч применен - все GPU функции заблокированы!")
