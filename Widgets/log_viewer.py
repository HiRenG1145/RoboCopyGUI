"""日志显示组件 — Fluent 风格 TextBrowser，只读、等宽字体、自动滚动。"""

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QWidget
from qfluentwidgets import TextBrowser


def _monospace_font() -> QFont:
    """选择系统中可用的等宽字体（优先支持 CJK 的字体）。"""
    families = [
        "Cascadia Code",
        "Consolas",
        "Courier New",
        "SimSun",
        "monospace",
    ]
    available = set(QFontDatabase.families())
    for name in families:
        if name in available:
            break
    else:
        name = families[-1]  # 最后的保底

    font = QFont(name, 10)
    font.setStyleHint(QFont.Monospace)
    return font


class LogViewer(TextBrowser):
    """Fluent 风格实时日志查看器（基于 TextBrowser，自带平滑滚动）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.document().setMaximumBlockCount(5000)

        self.setFont(_monospace_font())

        self.setPlaceholderText("运行 RoboCopy 后，实时日志将显示在这里...")

    # ── API ──────────────────────────────────────────────────────

    def append_log(self, text: str) -> None:
        """追加一行日志，自动滚到底部。"""
        self.append(text.rstrip())
        bar = self.verticalScrollBar()
        if bar:
            bar.setValue(bar.maximum())

    def clear_log(self) -> None:
        """清空所有日志。"""
        self.clear()
