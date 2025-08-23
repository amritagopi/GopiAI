#!/usr/bin/env python
"""
RAG Worker (out-of-process) for GopiAI-CrewAI.


REQ: {"cmd": "init", "memory_dir": "...", "vectors_dir": "...", "chats_file": "...", "model": "..."}
REQ: {"cmd": "reindex"}
REQ: {"cmd": "search", "query": "...", "limit": 3}
REQ: {"cmd": "get_context", "query": "...", "limit": 3}

RESP: {"ok": true, "data": ...} or {"ok": false, "error": "..."}

Notes:
- This process never imports GopiAI code except paths provided in init payload.
- txtai[faiss] must be installed in this environment.
"""

import sys
import os
import json
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

# Defensive: ensure output is line-buffered
sys.stdout.reconfigure(encoding="utf-8", newline="\n")
sys.stderr.reconfigure(encoding="utf-8", newline="\n")

def jprint(obj: Dict[str, Any]) -> None:
    """Print JSON line to stdout and flush"""
    try:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    except Exception:
        # last-resort: write to stderr
        sys.stderr.write("FAILED JSON WRITE\n")
        sys.stderr.flush()

# Import txtai
try:
    from txtai.embeddings import Embeddings
    TXT_AVAILABLE = True
except Exception as e:
    TXT_AVAILABLE = False
    # Не выходим сразу, а продолжаем работу в режиме заглушки

class RAGEngine:
    def __init__(self) -> None:
        self.embeddings: Optional[Embeddings] = None
        self.memory_dir: Optional[Path] = None
        self.vectors_dir: Optional[Path] = None
        self.chats_file: Optional[Path] = None
        self.model: str = "sentence-transformers/all-MiniLM-L6-v2"

    def _safe_count(self) -> int:
        try:
            return self.embeddings.count() if self.embeddings else 0
        except Exception:
            return 0

    def init(self, memory_dir: str, vectors_dir: str, chats_file: str, model: str) -> Dict[str, Any]:
        if not TXT_AVAILABLE:
            return {"ok": False, "error": "txtai not available in worker env"}

        try:
            self.memory_dir = Path(memory_dir)
            self.vectors_dir = Path(vectors_dir)
            self.chats_file = Path(chats_file)
            self.model = model or self.model

            # Ensure structure
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            self.vectors_dir.mkdir(parents=True, exist_ok=True)
            if not self.chats_file.exists():
                self.chats_file.write_text("[]", encoding="utf-8")

            # Init embeddings
            config = {"path": self.model, "content": True}
            self.embeddings = Embeddings(config)

            # Load index if present
            if (self.vectors_dir / "config.json").exists():
                try:
                    self.embeddings.load(str(self.vectors_dir))
                except Exception as e:
                    # Reset broken index
                    for item in self.vectors_dir.glob("*"):
                        try:
                            if item.is_dir():
                                import shutil
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                item.unlink(missing_ok=True)
                        except Exception:
                            pass
                    self.embeddings = Embeddings(config)

            # If empty, trigger reindex
            if self._safe_count() == 0:
                self.reindex()

            return {"ok": True, "data": {"count": self._safe_count()}}
        except Exception as e:
            return {"ok": False, "error": f"init failed: {e}", "trace": traceback.format_exc()}

    def reindex(self) -> Dict[str, Any]:
        try:
            if not (self.embeddings and self.chats_file and self.vectors_dir):
                return {"ok": False, "error": "worker not initialized"}

            payload = json.loads(self.chats_file.read_text(encoding="utf-8"))
            # Build valid docs
            docs = []
            for idx, msg in enumerate(payload):
                if not isinstance(msg, dict):
                    continue
                content = (msg.get("content") or "").strip()
                if not content:
                    continue
                if "⏳ Обрабатываю запрос" in content:
                    continue
                if "Произошла ошибка" in content:
                    continue
                doc_id = msg.get("id") or f"msg_{idx}"
                # Store only plain content; we still can search across it
                docs.append((doc_id, content, None))

            if not docs:
                # initialize empty index
                self.embeddings.index([("dummy_id", {"content": "dummy_text"}, None)])
                self.embeddings.delete(["dummy_id"])
                self.embeddings.save(str(self.vectors_dir))
                return {"ok": True, "data": {"count": self._safe_count(), "indexed": 0}}

            # try batch index
            try:
                self.embeddings.index(docs)
            except Exception:
                # fallback index one-by-one to avoid format issues
                for d in docs:
                    try:
                        self.embeddings.index([d])
                    except Exception:
                        pass
            self.embeddings.save(str(self.vectors_dir))
            return {"ok": True, "data": {"count": self._safe_count(), "indexed": len(docs)}}
        except Exception as e:
            return {"ok": False, "error": f"reindex failed: {e}", "trace": traceback.format_exc()}

    def search(self, query: str, limit: int = 3) -> Dict[str, Any]:
        try:
            if not self.embeddings:
                return {"ok": False, "error": "worker not initialized"}
            results = self.embeddings.search(query, limit)
            # Normalize results to simple list of strings
            out = []
            for r in results:
                try:
                    if isinstance(r, dict) and "text" in r:
                        out.append(r["text"])
                    elif isinstance(r, (list, tuple)) and len(r) > 1:
                        out.append(str(r[1]))
                    else:
                        out.append(str(r))
                except Exception:
                    out.append(str(r))
            return {"ok": True, "data": out}
        except Exception as e:
            return {"ok": False, "error": f"search failed: {e}", "trace": traceback.format_exc()}

    def get_context(self, query: str, limit: int = 3) -> Dict[str, Any]:
        s = self.search(query, limit)
        if not s.get("ok"):
            return s
        lines = ["CONTEXT FROM MEMORY:"]
        for t in s.get("data", []):
            lines.append(f"- {t}")
        return {"ok": True, "data": "\n".join(lines)}
    
    def get_count(self) -> Dict[str, Any]:
        """Возвращает количество индексированных документов."""
        try:
            count = self._safe_count()
            return {"ok": True, "data": count}
        except Exception as e:
            return {"ok": False, "error": f"count failed: {e}", "trace": traceback.format_exc()}

ENGINE = RAGEngine()

def handle(req: Dict[str, Any]) -> Dict[str, Any]:
    cmd = (req.get("cmd") or "").lower()
    if cmd == "init":
        return ENGINE.init(
            memory_dir=req.get("memory_dir", ""),
            vectors_dir=req.get("vectors_dir", ""),
            chats_file=req.get("chats_file", ""),
            model=req.get("model", "sentence-transformers/all-MiniLM-L6-v2"),
        )
    if cmd == "reindex":
        return ENGINE.reindex()
    if cmd == "search":
        return ENGINE.search(req.get("query", ""), int(req.get("limit", 3)))
    if cmd == "get_context":
        return ENGINE.get_context(req.get("query", ""), int(req.get("limit", 3)))
    if cmd == "count":
        return ENGINE.get_count()
    return {"ok": False, "error": f"unknown cmd: {cmd}"}

def main():
    # Inform readiness - всегда отправляем ready line, даже если txtai недоступен
    if TXT_AVAILABLE:
        jprint({"ok": True, "event": "worker_started", "pid": os.getpid(), "txtai_available": True})
    else:
        jprint({"ok": True, "event": "worker_started", "pid": os.getpid(), "txtai_available": False, "warning": "txtai not available, RAG disabled"})
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            jprint({"ok": False, "error": f"invalid json: {e}"})
            continue
        try:
            resp = handle(req)
        except Exception as e:
            resp = {"ok": False, "error": f"handler exception: {e}", "trace": traceback.format_exc()}
        jprint(resp)

if __name__ == "__main__":
    main()
