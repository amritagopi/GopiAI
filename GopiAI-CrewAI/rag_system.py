# --- START OF FILE rag_system.py (OUT-OF-PROCESS RAG PROXY) ---

import os
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import List, Dict, Optional, TYPE_CHECKING, Any

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Загрузка конфигурации ---
from rag_config import MEMORY_BASE_DIR, CHATS_FILE_PATH, VECTOR_INDEX_PATH, EMBEDDING_MODEL

# Ранее txtai импортировался напрямую и создавал конфликты зависимостей.
# В этой реализации всё выполняется в отдельном процессе, поэтому здесь не импортируем txtai.
if TYPE_CHECKING:
    EmbeddingsType = Any
else:
    EmbeddingsType = Any


import sys

def _resolve_txtai_python() -> Path:
    # Use CrewAI environment python if available
    current_dir = Path(__file__).parent
    crewai_python = current_dir / "venv" / "bin" / "python"
    if crewai_python.exists():
        return crewai_python
    # Fallback to current interpreter
    return Path(sys.executable)

TXTAI_PYTHON = _resolve_txtai_python()
WORKER_PATH = Path(__file__).with_name("rag_worker.py")

class _WorkerProc:
    """Подпроцесс воркера с JSONL-взаимодействием по stdin/stdout."""
    def __init__(self, python_path: Path, worker_script: Path):
        self.python_path = python_path
        self.worker_script = worker_script
        self.proc: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()

    def start(self) -> bool:
        try:
            if self.proc and self.proc.poll() is None:
                return True
            if not self.python_path.exists():
                
                return False
            if not self.worker_script.exists():
                logger.error(f"rag_worker.py not found: {self.worker_script}")
                return False
            self.proc = subprocess.Popen(
                [str(self.python_path), "-u", str(self.worker_script)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", bufsize=1, cwd=str(self.worker_script.parent)
            )
            # ждём первую готовность
            line = self._readline(timeout=20.0)
            if not line:
                logger.error("RAG worker didn't send ready line")
                # Попробуем неблокирующе прочитать stderr для диагностики (с таймаутом)
                try:
                    err_sample = self._readerr(timeout=1.0) if self.proc and self.proc.stderr else None
                    if err_sample:
                        logger.error(f"RAG worker stderr (sample): {err_sample.strip()}")
                except Exception:
                    pass
                # Останавливаем воркер на случай залипания (fail-open)
                try:
                    self.stop()
                except Exception:
                    pass
                return False
            logger.info(f"RAG worker started: {line.strip()}")
            return True
        except Exception as e:
            logger.error(f"Failed to start RAG worker: {e}", exc_info=True)
            self.proc = None
            return False

    def _readline(self, timeout: float = 5.0) -> Optional[str]:
        if not self.proc or not self.proc.stdout:
            return None
        result: Dict[str, Optional[str]] = {"line": None}
        def _reader():
            try:
                result["line"] = self.proc.stdout.readline()
            except Exception:
                result["line"] = None
        th = threading.Thread(target=_reader, daemon=True)
        th.start()
        th.join(timeout)
        return result["line"]

    def _readerr(self, timeout: float = 1.0) -> Optional[str]:
        if not self.proc or not self.proc.stderr:
            return None
        result: Dict[str, Optional[str]] = {"line": None}
        def _reader():
            try:
                result["line"] = self.proc.stderr.readline()
            except Exception:
                result["line"] = None
        th = threading.Thread(target=_reader, daemon=True)
        th.start()
        th.join(timeout)
        return result["line"]

    def request(self, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        with self.lock:
            if not self.proc or self.proc.poll() is not None:
                if not self.start():
                    return {"ok": False, "error": "worker not running"}
            assert self.proc is not None
            try:
                if not self.proc.stdin:
                    return {"ok": False, "error": "stdin closed"}
                self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
                self.proc.stdin.flush()
                line = self._readline(timeout=timeout)
                if not line:
                    return {"ok": False, "error": "no response from worker"}
                try:
                    return json.loads(line)
                except Exception as e:
                    return {"ok": False, "error": f"invalid worker response: {e}", "raw": line}
            except Exception as e:
                return {"ok": False, "error": f"request failed: {e}"}

    def stop(self) -> None:
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass
        finally:
            self.proc = None

class RAGSystem:
    """
    Proxy RAG system: API compatible, operations are performed in a separate process.
    """
    _instance: Optional['RAGSystem'] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        logger.info("--- Инициализация RAGSystem (Proxy, out-of-process) ---")
        self.embeddings: Optional[EmbeddingsType] = None  # только для совместимости атрибутов
        self.worker = _WorkerProc(TXTAI_PYTHON, WORKER_PATH)

        self._ensure_memory_structure()
        ok = self._initialize_worker()
        if not ok:
            logger.warning("RAG worker initialization failed, RAG will be disabled.")
        self._initialized = True

    def _ensure_memory_structure(self):
        """Checks and creates necessary folders and files for memory to work."""
        try:
            logger.info("Checking memory structure in directory: {}".format(MEMORY_BASE_DIR))
            
            # 1. Create base directory /memory
            MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
            
            # 2. Create directory for vectors /memory/vectors
            VECTOR_INDEX_PATH.mkdir(parents=True, exist_ok=True)
            
            # 3. Check and create chats.json if it doesn't exist
            if not CHATS_FILE_PATH.exists():
                logger.warning("File {} not found. Creating a new empty file.".format(CHATS_FILE_PATH))
                with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f) # Create file with an empty list
            
            logger.info("[OK] Memory folder and file structure is in order.")
            
        except Exception as e:
            logger.error("Failed to create memory structure: {}".format(e), exc_info=True)
            raise # If we can't create folders, it's pointless to continue

    def _initialize_worker(self) -> bool:
        if not self.worker.start():
            return False
        resp = self.worker.request({
            "cmd": "init",
            "memory_dir": str(MEMORY_BASE_DIR),
            "vectors_dir": str(VECTOR_INDEX_PATH),
            "chats_file": str(CHATS_FILE_PATH),
            "model": EMBEDDING_MODEL
        }, timeout=30.0)
        if not resp.get("ok"):
            logger.error(f"Worker init failed: {resp}")
            return False
        logger.info(f"RAG worker initialized. Count: {resp.get('data', {}).get('count')}")
        return True

    def reindex_all_chats(self):
        resp = self.worker.request({"cmd": "reindex"}, timeout=120.0)
        if not resp.get("ok"):
            logger.error(f"Reindex failed: {resp}")
        else:
            logger.info(f"Reindex ok: {resp.get('data')}")

    # ... (методы search и get_context_for_prompt остаются без изменений) ...
    def search(self, query: str, limit: int = 3) -> List[Dict]:
        resp = self.worker.request({"cmd": "search", "query": query, "limit": limit}, timeout=20.0)
        if not resp.get("ok"):
            logger.error(f"Search failed: {resp}")
            return []
        return [{"text": t} for t in (resp.get("data") or [])]

    def get_context_for_prompt(self, query: str, limit: int = 3) -> str:
        """Строка контекста от воркера."""
        resp = self.worker.request({"cmd": "get_context", "query": query, "limit": limit}, timeout=20.0)
        if not resp.get("ok"):
            logger.error(f"get_context failed: {resp}")
            return "No relevant context found in memory."
        return resp.get("data") or "No relevant context found in memory."
    
    def get_document_count(self) -> int:
        """Получает количество индексированных документов от воркера."""
        try:
            resp = self.worker.request({"cmd": "count"}, timeout=10.0)
            if resp.get("ok"):
                return resp.get("data", 0)
            else:
                logger.warning(f"Failed to get document count: {resp}")
                return 0
        except Exception as e:
            logger.warning(f"Error getting document count: {e}")
            return 0

# --- Singleton Instance ---
_rag_system_instance: Optional[RAGSystem] = None

def get_rag_system() -> RAGSystem:
    """Фабричная функция для получения единственного экземпляра RAGSystem."""
    global _rag_system_instance
    if _rag_system_instance is None:
        logger.info("Создание первого и единственного экземпляра RAGSystem.")
        _rag_system_instance = RAGSystem()
    return _rag_system_instance
    
# --- END OF FILE rag_system.py ---
