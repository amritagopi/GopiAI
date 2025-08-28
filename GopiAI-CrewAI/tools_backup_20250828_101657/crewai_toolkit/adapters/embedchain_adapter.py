from typing import Any, TYPE_CHECKING

# Опциональный импорт: тип доступен только при статической проверке (Pyright/Mypy),
# чтобы избежать ошибки "Не удается разрешить импорт 'embedchain'" при отсутствии пакета.
if TYPE_CHECKING:
    try:
        from embedchain import App  # type: ignore
    except Exception:
        # В блоке TYPE_CHECKING это безвредно: статический анализ продолжит работу.
        pass

# Попытка локального импорта Adapter с fallback:
# 1) Локальный путь внутри проекта
# 2) Официальный пакет crewai-tools (если установлен)
try:
    from .rag_tool import Adapter  # type: ignore
except Exception:
    try:
        from crewai_tools.tools.rag.rag_tool import Adapter  # type: ignore
    except Exception as e:
        # Оставляем понятную ошибку только при реальном использовании файла,
        # а не на этапе импорта всего проекта.
        raise ImportError(
            "Не удалось импортировать Adapter. "
            "Проверьте наличие локального модуля '.rag_tool' или установите пакет 'crewai-tools'.\n"
            "Пример: pip install crewai-tools"
        ) from e


def _ensure_embedchain_loaded() -> None:
    """
    Проверяет наличие пакета embedchain в рантайме и подсказывает установку при отсутствии.
    """
    try:
        import importlib
        # Пытаемся загрузить модуль, не делая его обязательным при статической проверке
        importlib.import_module("embedchain")
    except Exception as e:
        raise ImportError(
            "Пакет 'embedchain' не установлен или недоступен. "
            "Установите его: pip install embedchain"
        ) from e


class EmbedchainAdapter(Adapter):
    # Аннотация строкой во избежание жёсткой зависимости в рантайме.
    embedchain_app: "App"  # type: ignore[name-defined]
    summarize: bool = False

    def query(self, question: str) -> str:
        _ensure_embedchain_loaded()
        result, sources = self.embedchain_app.query(
            question, citations=True, dry_run=(not self.summarize)
        )
        if self.summarize:
            return result
        return "\n\n".join([source[0] for source in sources])

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        _ensure_embedchain_loaded()
        self.embedchain_app.add(*args, **kwargs)
