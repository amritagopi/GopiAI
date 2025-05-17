"""
Тестирование интеграции текстового редактора с ReasoningAgent
"""

import os
import asyncio
import tempfile
from pathlib import Path

from app.agent.text_editor_access import TextEditorAccess
from app.agent.reasoning import ReasoningAgent
from app.config import config

async def test_text_editor_integration():
    """
    Тестирует интеграцию текстового редактора с ReasoningAgent
    """
    print("Тестирование интеграции текстового редактора с ReasoningAgent...")

    # Создаем временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        # Инициализируем агента
        agent = ReasoningAgent()
        try:
            # Инициализируем агента с минимальной конфигурацией для теста
            await agent.initialize(skip_serena_check=True)

            # Создаем текущий план (нужен для работы разрешений)
            agent.current_plan = "Test plan for text editor integration"

            # Одобряем план (чтобы разрешить действия среднего уровня)
            agent.approve_plan()

            # Создаем тестовый файл в директории workspace вместо временной
            test_file_path = "workspace/test_file.txt"
            test_content = "Line 1: This is a test file.\nLine 2: For text editor integration.\nLine 3: End of test file."

            # Записываем содержимое в файл
            write_result = await agent.write_text_file(test_file_path, test_content)
            print(f"Write result: {write_result['success']}")

            # Читаем содержимое файла
            read_result = await agent.read_text_file(test_file_path)
            print(f"Read result: {read_result['success']}")
            print(f"Content: {read_result.get('content', '')}")

            # Поиск в файле
            search_result = await agent.search_in_text_file(test_file_path, "test")
            print(f"Search result: {search_result['success']}")
            print(f"Matches: {search_result.get('match_count', 0)}")

            # Добавляем содержимое в конец файла
            append_result = await agent.append_to_text_file(test_file_path, "\nLine 4: Appended line.")
            print(f"Append result: {append_result['success']}")

            # Читаем обновленное содержимое
            read_result = await agent.read_text_file(test_file_path)
            print(f"Updated content: {read_result.get('content', '')}")

            # Редактируем строки
            edit_result = await agent.edit_text_file_lines(test_file_path, 2, 2, "Line 2: REPLACED LINE")
            print(f"Edit result: {edit_result['success']}")

            # Вставляем строку
            insert_result = await agent.insert_at_line_in_text_file(test_file_path, 3, "Line 2.5: Inserted line.")
            print(f"Insert result: {insert_result['success']}")

            # Читаем финальное содержимое
            read_result = await agent.read_text_file(test_file_path)
            print(f"Final content: {read_result.get('content', '')}")

            # Проверяем историю файла
            history_result = await agent.get_file_history(test_file_path)
            print(f"History entries: {len(history_result.get('history', []))}")

            # Поиск файлов по расширению
            Path(os.path.join(temp_dir, "test_file2.txt")).touch()
            Path(os.path.join(temp_dir, "test_file.md")).touch()

            find_result = await agent.find_files_by_extension(["txt"], temp_dir)
            print(f"Found files: {find_result.get('count', 0)}")

            # Создаем diff
            original = "Line 1\nLine 2\nLine 3"
            modified = "Line 1\nLine 2 modified\nLine 3\nLine 4"
            diff_result = await agent.create_diff(original, modified)
            print(f"Diff result: {diff_result['success']}")
            print(f"Diff: {diff_result.get('diff', '')}")

        finally:
            # Очищаем ресурсы
            await agent.cleanup()

    print("Тестирование завершено!")

if __name__ == "__main__":
    # Запускаем тест
    asyncio.run(test_text_editor_integration())
