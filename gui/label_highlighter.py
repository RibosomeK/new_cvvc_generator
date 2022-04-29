from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextDocument
from PySide6.QtCore import QRegularExpression


def format(color: str, style: str = "") -> QTextCharFormat:
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if "bold" in style:
        _format.setFontWeight(700)
    if "italic" in style:
        _format.setFontItalic(True)

    return _format


LABEL_STYLES: dict[str, QTextCharFormat] = {
    "operators": format("red"),
    "numbers": format("purple", "italic"),
    "alias": format("black", "bold"),
    "wav": format("black", "italic"),
}


class LabelHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)

    def highlightBlock(self, text: str) -> None:
        for expression, format in self.rules:
            expression_match = expression.globalMatch(text)
            while expression_match.hasNext():
                match = expression_match.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class OtoHighlighter(LabelHighlighter):
    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)

        self.operators: list[str] = ["="]

        rules: list[tuple[str, QTextCharFormat]] = []
        rules.extend([(r"%s" % o, LABEL_STYLES["operators"]) for o in self.operators])
        rules.append(
            (
                r"[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*,-?[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*",
                LABEL_STYLES["numbers"],
            )
        )
        rules.append((r"\S+\.wav", LABEL_STYLES["wav"]))
        rules.append((r"(?<==).*?(?=,)", LABEL_STYLES["alias"]))

        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self.rules.extend(
            [(QRegularExpression(pattern), format) for pattern, format in rules]
        )


class VsdxmfHighlighter(LabelHighlighter):
    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)

        rules: list[tuple[str, QTextCharFormat]] = []
        rules.append(
            (
                r"[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*,-?[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*,[0-9]+\.?[0-9]*",
                LABEL_STYLES["numbers"],
            )
        )
        rules.append((r"(?<=\,).*?\.wav", LABEL_STYLES["wav"]))
        rules.append((r"#.*?(?=,)", LABEL_STYLES["wav"]))
        # beginning alias
        rules.append((r"(?<!\S) \S+?(?=,)", LABEL_STYLES["alias"]))
        # ending alias
        rules.append((r"(?<!.)\S+ (?=,)", LABEL_STYLES["alias"]))
        # cv or vc alias
        rules.append((r"(?<!.)\S+ [^,]+?(?=,)", LABEL_STYLES["alias"]))
        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self.rules.extend(
            [(QRegularExpression(pattern), format) for pattern, format in rules]
        )
