import re

class ChatWidget:
    def _extract_code_from_selection(self, text: str) -> str:
        """
        Извлекает код из выделенного текста.

        Обрабатывает случаи, когда код обернут в маркеры markdown.

        Args:
            text: Выделенный текст

        Returns:
            Извлеченный код
        """
        # Проверяем, есть ли маркеры markdown для кода
        markdown_code_match = re.search(r'```(?:\w*\n)?([\s\S]*?)```', text)
        if markdown_code_match:
            return markdown_code_match.group(1)

        # Иначе возвращаем текст как есть
        return text
