import sys

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


def format(color, style=""):
    """Возвращает QTextCharFormat с заданным цветом и стилем."""
    _color = QColor.fromString(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if "bold" in style:
        _format.setFontWeight(QFont.Weight.Bold)
    if "italic" in style:
        _format.setFontItalic(True)
    return _format


# Определяем стили для разных элементов синтаксиса
STYLES = {
    "keyword": format("#569CD6", "bold"),  # Синий, жирный (как в VSCode)
    "operator": format("#D4D4D4"),  # Почти белый
    "brace": format("#D4D4D4"),  # Почти белый
    "defclass": format("#4EC9B0", "bold"),  # Бирюзовый, жирный для def/class
    "string": format("#CE9178"),  # Оранжевый для строк
    "string2": format("#CE9178"),  # Оранжевый для других строк
    "comment": format("#6A9955", "italic"),  # Зеленый, курсив для комментариев
    "self": format("#9CDCFE"),  # Голубой для self
    "numbers": format("#B5CEA8"),  # Светло-зеленый для чисел
    "decorator": format("#D7BA7D"),  # Желтоватый для декораторов
}


class PythonHighlighter(QSyntaxHighlighter):
    """Класс для подсветки синтаксиса Python."""

    keywords = [
        "and",
        "as",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
        "True",
        "False",
        "None",
    ]

    operators = [
        "=",
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "\\+",
        "-",
        "\\*",
        "/",
        "//",
        "%",
        "%=",
        "\\+=",
        "-=",
        "\\*=",
        "/=",
        "//=",
        "\\*\\*",  # Возведение в степень
        "&",
        "\\|",
        "\\^",
        "~",
        "<<",
        ">>",
    ]

    braces = [
        "\\{",
        "\\}",
        "\\(",
        "\\)",
        "\\[",
        "\\]",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        rules = []

        # Ключевые слова
        rules += [
            (r"\b" + w + r"\b", 0, STYLES["keyword"])
            for w in PythonHighlighter.keywords
            if w not in ["def", "class"]
        ]
        rules += [
            (r"\bdef\b", 0, STYLES["defclass"]),
            (r"\bclass\b", 0, STYLES["defclass"]),
        ]
        rules += [(r"\bself\b", 0, STYLES["self"])]

        # Операторы и скобки
        rules += [(o, 0, STYLES["operator"]) for o in PythonHighlighter.operators]
        rules += [(b, 0, STYLES["brace"]) for b in PythonHighlighter.braces]

        # Правило для строк (включая тройные кавычки)
        # Одинарные и двойные кавычки
        # Используем правильное экранирование и регулярки для raw-строк
        rules += [(r'"([^"\\]|\\.)*"', 0, STYLES["string"])]  # Двойные кавычки
        rules += [(r"'([^\'\\]|\\.)*'", 0, STYLES["string"])]  # Одинарные кавычки

        # Тройные кавычки обрабатываются ниже

        # Декораторы
        rules += [(r"@[a-zA-Z_][a-zA-Z0-9_]*", 0, STYLES["decorator"])]

        # Числа
        rules += [(r"\b[+-]?[0-9]+[lL]?\b", 0, STYLES["numbers"])]
        rules += [(r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b", 0, STYLES["numbers"])]
        rules += [
            (r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b", 0, STYLES["numbers"])
        ]

        # Комментарии
        rules += [(r"#[^\n]*", 0, STYLES["comment"])]

        # Имена функций/классов
        rules += [(r"(?<=\bdef\s+)(\w+)", 1, STYLES["defclass"])]
        rules += [(r"(?<=\bclass\s+)(\w+)", 1, STYLES["defclass"])]

        self.highlighting_rules = [
            (QRegularExpression(pattern), index, fmt) for pattern, index, fmt in rules
        ]

        # Для многострочных строк
        self.tri_single = QRegularExpression(r"'''")
        self.tri_double = QRegularExpression(r'"""')

    def highlightBlock(self, text):
        # Основные правила
        for expression, nth, format in self.highlighting_rules:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(nth), match.capturedLength(nth), format
                )

        self.setCurrentBlockState(0)

        # Многострочные строки
        in_multiline = self.match_multiline(text, self.tri_single, 1, STYLES["string2"])
        if not in_multiline:
            self.match_multiline(text, self.tri_double, 2, STYLES["string2"])

    def match_multiline(self, text, delimiter, in_state, style):
        start_index = 0
        if self.previousBlockState() == in_state:
            match = delimiter.match(text, 0)
            end_index = match.capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(in_state)
                self.setFormat(0, len(text), style)
                return True
            else:
                length = end_index + match.capturedLength()
                self.setFormat(0, length, style)
                start_index = length
        else:
            match = delimiter.match(text, 0)
            start_index = match.capturedStart()
            if start_index == -1:
                return False  # Не начинается с многострочной строки

        while start_index >= 0:
            match = delimiter.match(
                text, start_index + delimiter.pattern().count("")
            )  # Ищем следующий разделитель
            end_index = match.capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(in_state)
                self.setFormat(start_index, len(text) - start_index, style)
                break
            else:
                length = end_index - start_index + match.capturedLength()
                self.setFormat(start_index, length, style)
                start_index = match.capturedStart() + match.capturedLength()
                # Ищем следующее начало строки
                match = delimiter.match(text, start_index)
                start_index = match.capturedStart()

        return True
