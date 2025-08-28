from typing import Any, Optional

# Не тянем внешние зависимости для статического анализа
# и не импортируем embedchain на уровне модуля

# Пытаемся импортировать локальный Adapter, затем fallback на пакетный
try:
    from .rag_tool import Adapter  # type: ignore
except Exception:
    try:
        from crewai_tools.tools.rag.rag_tool import Adapter  # type: ignore
    except Exception as e:
        raise ImportError(
            "Не удалось импортировать Adapter ни из локального '.rag_tool', ни из 'crewai_tools.tools.rag.rag_tool'. "
            f"Оригинальная ошибка: {e}"
        )


class PDFEmbedchainAdapter(Adapter):
    # Не привязываем тип жестко к внешнему пакету на уровне модуля
    embedchain_app: Any
    summarize: bool = False
    src: Optional[str] = None

    def _ensure_app(self) -> None:
        if getattr(self, "embedchain_app", None) is None:
            raise ImportError(
                "embedchain App не инициализирован. Передайте корректный экземпляр App в embedchain_app."
            )

    def query(self, question: str) -> str:
        self._ensure_app()
        where = (
            {"app_id": self.embedchain_app.config.id, "source": self.src}
            if self.src
            else None
        )
        result, sources = self.embedchain_app.query(
            question, citations=True, dry_run=(not self.summarize), where=where
        )
        if self.summarize:
            return result
        return "\n\n".join([source[0] for source in sources])

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._ensure_app()
        self.src = args[0] if args else None
        self.embedchain_app.add(*args, **kwargs)
