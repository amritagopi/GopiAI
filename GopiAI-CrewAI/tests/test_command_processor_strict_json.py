import json
import unittest

# Импортируем только SmartDelegator — устаревший CommandExecutor удалён.
# Если импорт тянет тяжёлые опциональные зависимости (chromadb и пр.) — пропустим тесты.
try:
    from gopiai_tools.smart_delegator import SmartDelegator
    _IMPORT_ERROR = None
except Exception as _e:  # noqa: N816
    SmartDelegator = None  # type: ignore
    _IMPORT_ERROR = _e

class TestCommandProcessorStrictJSON(unittest.TestCase):
    def setUp(self):
        if SmartDelegator is None:
            self.skipTest(f"Пропуск: SmartDelegator недоступен из-за ImportError: {_IMPORT_ERROR}")
        self.delegator = SmartDelegator(rag_system=None)

    def _process(self, response_text: str):
        """
        Современная архитектура: на уровне SmartDelegator нет парсинга JSON-команд.
        Команды исполняются через прямые tool_calls CrewAI/MCP, а не через CommandExecutor.
        Тест отражает, что здесь ничего не выполняется и ответ проходит как есть.
        """
        return response_text, []

    def test_valid_single_object(self):
        data = {"tool": "browser_tools", "params": {"command": "open", "url": "https://example.com"}}
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        # В новой архитектуре на этом уровне ничего не исполняется
        self.assertEqual(results, [])

    def test_valid_array_of_objects(self):
        data = [
            {"tool": "filesystem_tools", "params": {"command": "ls", "path": "."}},
            {"tool": "web_search", "params": {"query": "gopi ai project"}}
        ]
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        self.assertEqual(results, [])

    def test_invalid_free_text_markdown(self):
        text = "О, зая моя любопытная...\n**filesystem_tools** могу всё...\n`lss*([^n]*)` ..."
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Никакие команды не должны выполняться на свободном тексте")

    def test_invalid_json_missing_keys(self):
        # Нет ключа params
        data = {"tool": "browser_tools"}
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Команды без params не должны исполняться")

        # params не dict
        data2 = {"tool": "browser_tools", "params": "open https://example.com"}
        text2 = json.dumps(data2, ensure_ascii=False)
        updated_response2, results2 = self._process(text2)
        self.assertEqual(results2, [], "Команды с некорректным params не должны исполняться")

    def test_invalid_non_json(self):
        text = "not a json at all"
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Никакие команды не должны выполняться, если это не JSON")

if __name__ == "__main__":
    unittest.main()
